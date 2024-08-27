import concurrent.futures
import datetime
import itertools
import json
import logging
import os
import time
from collections import deque
from dataclasses import asdict, astuple, dataclass
from decimal import Decimal

from mysql.connector import MySQLConnection, connect
from mysql.connector.pooling import MySQLConnectionPool


@dataclass
class Checkpoint:
    row: dict
    processed: int
    different: int


@dataclass
class ComparisonTask:
    batch_id: int
    source_rows: list[dict]
    different: list[dict]


def init_logger(name: str | None = None) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    log_file_configs = [
        {"filename": f"{name}.log", "level": logging.DEBUG},
    ]

    for config in log_file_configs:
        handler = logging.FileHandler(config["filename"])
        handler.setLevel(config["level"])
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def hash_dict(d):
    return frozenset(d.items())


def find_missing_in_b(a, b):
    b_hashes = {hash_dict(d) for d in b}

    missing_in_b = [d for d in a if hash_dict(d) not in b_hashes]

    return missing_in_b


def get_table_rows_number(con: MySQLConnection, database: str, table: str) -> int:
    with con.cursor() as cur:
        cur.execute("SELECT table_rows FROM information_schema.tables WHERE table_schema = %s AND table_name = %s", (database, table))
        (rows,) = cur.fetchone()
        return rows


def get_table_structure(con: MySQLConnection, database: str, table: str) -> list[tuple[str, str]]:
    with con.cursor() as cur:
        cur.execute(
            "SELECT column_name, CAST(data_type as char(255)) FROM information_schema.columns WHERE table_schema = %s AND table_name = %s ORDER BY ordinal_position",
            (database, table),
        )
        return cur.fetchall()


def get_table_keys(con: MySQLConnection, database: str, table: str) -> list[tuple[str, str]]:
    operation = """
        SELECT tis.index_name, titc.constraint_type, tic.column_name, tic.data_type
        FROM information_schema.table_constraints titc
        JOIN information_schema.statistics tis ON titc.table_schema = tis.table_schema AND titc.table_name = tis.table_name AND titc.constraint_name = tis.index_name
        JOIN information_schema.columns tic ON tis.table_schema = tic.table_schema AND tis.table_name = tic.table_name AND tis.column_name = tic.column_name
        WHERE titc.constraint_type IN ('PRIMARY KEY', 'UNIQUE')
        AND titc.table_schema = %s
        AND titc.table_name = %s
    """

    with con.cursor() as cur:
        cur.execute(operation, (database, table))
        rows = cur.fetchall()

    keys = [(row[2], row[3]) for row in rows if row[1] == "PRIMARY KEY"] or [(row[2], row[3]) for row in rows if row[1] == "UNIQUE" and row[0] == rows[0][0]]

    if not keys:
        raise Exception("does not have primary key or unique keys.")

    return keys


def get_elapsed_time(st: float, ndigits=None) -> int | float:
    return round(time.time() - st, ndigits)


def extract_keyvals(row: dict, keys: list[tuple[str, str]]):
    _keys = [item[0] for item in keys]
    new_dict = {}
    for key in row:
        if key in _keys:
            new_dict[key] = row[key]

    return new_dict


class MysqlTableCompare:
    def __init__(
        self,
        src_dsn: dict,
        dst_dsn: dict,
        src_database: str,
        src_table: str,
        dst_database: str,
        dst_table: str,
        parallel: int = 1,
        limit_size: int = 2000,
        fetch_size: int = 200,
    ) -> None:
        self.source_dsn = src_dsn
        self.target_dsn = dst_dsn

        self.parallel = parallel

        self.limit_size = limit_size
        self.fetch_size = fetch_size

        self.src_database = src_database
        self.src_table = src_table
        self.dst_database = dst_database
        self.dst_table = dst_table

        self.start_timestamp = time.time()

        self.compare_name: str = f"{self.src_database}.{self.src_table}"
        if self.src_database == self.dst_database and self.src_table != self.dst_table:
            self.compare_name += f".{self.dst_table}"
        elif self.src_database != self.dst_database:
            self.compare_name += f".{self.dst_database}.{self.dst_table}"

        self.checkpoint_file = f"{self.compare_name}.ckpt.json"
        self.done_file = f"{self.compare_name}.done"
        self.different_file = f"{self.compare_name}.diff.log"

        if self.limit_size % self.fetch_size != 0:
            raise Exception("The remainder of the fetch_size divided by the shard_size must be equal to 0.")

    def write_different(self, rows: list[dict]):
        with open(self.different_file, "a", encoding="utf8") as f:
            for row in rows:
                f.write(f"{row}\n")

    def write_checkpoint(self):
        with open(self.checkpoint_file, "w", encoding="utf8") as f:
            json.dump(asdict(self.checkpoint), f, default=str)

    def read_checkpoint(self):
        if not os.path.exists(self.checkpoint_file):
            return Checkpoint(None, 0, 0)

        with open(self.checkpoint_file, "r", encoding="utf8") as f:
            ckpt: Checkpoint = Checkpoint(**json.load(f))

        for coln, colt in self.source_table_keys:
            if coln in ckpt.row:
                if colt == "date":
                    ckpt.row[coln] = datetime.datetime.strptime(ckpt.row[coln], "%Y-%m-%d")
                elif colt == "decimal":
                    ckpt.row[coln] = Decimal(ckpt.row[coln])
        return ckpt

    def get_queery_full_table_statement_params(self, ckpt_row: dict = None):
        _keyval = ckpt_row
        # select * from where 1 = 1 and ((a > xxx) or (a = xxx and b > yyy) or (a = xxx and b = yyy and c > zzz)) order by a,b,c limit checksize
        _key_colns = ", ".join([f"`{col[0]}`" for col in self.source_table_keys])

        for _, column_type in self.source_table_keys:
            if column_type in ["int", "double", "char", "date", "decimal", "varchar", "bigint", "tinyint", "smallint"]:
                pass
            else:
                raise ValueError(f"Data type: [{column_type}] is not supported yet.")

        where_conditions = []
        for end_idx in range(len(self.source_table_keys)):
            condition_parts = []
            for i, (column_name, _) in enumerate(self.source_table_keys[: end_idx + 1]):
                operator = ">" if i == end_idx else "="
                condition_parts.append(f"`{column_name}` {operator} %s")
            where_conditions.append(" and ".join(condition_parts))
        where_clause = "WHERE" + "(" + ") or (".join(where_conditions) + ")"

        statement_with_condition = f"SELECT * FROM {self.src_database}.{self.src_table} {where_clause} ORDER BY {_key_colns} LIMIT {self.limit_size}"
        statement_without_condition = f"SELECT * FROM {self.src_database}.{self.src_table} ORDER BY {_key_colns} LIMIT {self.limit_size}"

        _params: list = []
        if _keyval:
            for end_idx in range(len(self.source_table_keys)):
                for i, (column_name, _) in enumerate(self.source_table_keys[: end_idx + 1]):
                    _params.append(_keyval[column_name])

        statement = statement_with_condition if _params else statement_without_condition

        return statement, _params

    def query_rows(self, con: MySQLConnectionPool, query_statement: str, query_params) -> list[dict]:
        with con.get_connection() as con:
            con: MySQLConnection
            with con.cursor(dictionary=True, buffered=True) as cur:
                cur.execute(query_statement, tuple(query_params))
                return cur.fetchall()

    def compare_full_table(self):
        _keyval = self.checkpoint.row

        while True:
            query_statement, query_params = self.get_queery_full_table_statement_params(_keyval)
            print(f"query {query_statement}, params {query_statement}")

            source_rows = []
            target_rows = []

            _start1 = time.time()

            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                future_source = executor.submit(self.query_rows, self.source_conpool, query_statement, query_params)
                future_target = executor.submit(self.query_rows, self.target_conpool, query_statement, query_params)

                source_rows = future_source.result()
                target_rows = future_target.result()

            print(f"query source & target rows {get_elapsed_time(_start1, 2)}s.")

            if len(source_rows) == 0:
                break
            else:
                _keyval = extract_keyvals(source_rows[-1], self.source_table_keys)
                _start = time.time()
                diff_rows = find_missing_in_b(source_rows, target_rows)
                print(f"find_missing_in_b {get_elapsed_time(_start, 2)}s.")
                if len(diff_rows) >= 1:
                    self.write_different(diff_rows)
                self.checkpoint.row = _keyval
                self.checkpoint()
                print(f"Missing elements in b: {len(diff_rows)}")
                print(f"keyval: {_keyval}")

    def run(self) -> None:
        self.logger = init_logger(self.compare_name)

        if os.path.exists(self.done_file):
            self.logger.info(f"The comparison is complete and '{self.done_file}' exists.")
            return

        self.logger.info("init check.")

        with connect(**self.source_dsn) as source_con, connect(**self.target_dsn) as target_con:
            source_table_struct: list[tuple[str, str]] = get_table_structure(source_con, self.src_database, self.src_table)
            target_table_struct: list[tuple[str, str]] = get_table_structure(target_con, self.dst_database, self.dst_table)

            self.logger.info(f"source table structure: {source_table_struct}.")
            self.logger.info(f"target table structure: {target_table_struct}.")

            table_struct_diff = set(source_table_struct) - set(target_table_struct)
            if not source_table_struct or table_struct_diff:
                raise Exception("source and target table structure diff.")

            self.logger.info("source and target table structure same.")

            self.source_table_keys = get_table_keys(source_con, self.src_database, self.src_table)

            self.logger.info(f"source table keys: {self.source_table_keys}.")

            self.source_table_rows_number = max(1, get_table_rows_number(source_con, self.src_database, self.src_table))
            self.logger.info(f"source table rows number: {self.source_table_rows_number}.")

        self.checkpoint = self.read_checkpoint()
        self.processed_rows_number = self.checkpoint.processed
        self.different_rows_number = self.checkpoint.different

        self.logger.info(f"from checkpoint: {self.checkpoint}")

        self.logger.info("source table connect pool create.")
        self.source_conpool = MySQLConnectionPool(pool_name="source_conpool", pool_size=self.parallel, **self.source_dsn)

        self.logger.info("target table connect pool create.")
        self.target_conpool = MySQLConnectionPool(pool_name="target_conpool", pool_size=self.parallel, **self.target_dsn)
        self.compare_full_table()  # main

        self.logger.info(
            f"compare completed, processed rows: {self.processed_rows_number}, different: {self.different_rows_number},  elapsed time: {get_elapsed_time(self.start_timestamp, 2)}s."
        )

        open(self.done_file, "w").close()

        if os.path.exists(self.checkpoint_file):
            os.remove(self.checkpoint_file)

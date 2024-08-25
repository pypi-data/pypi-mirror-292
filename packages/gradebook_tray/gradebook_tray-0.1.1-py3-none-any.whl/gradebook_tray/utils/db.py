import sqlite3
from collections import OrderedDict
from collections.abc import Callable
from datetime import datetime
from functools import partial
from itertools import zip_longest
from sqlite3 import connect
from types import GenericAlias
from typing import NamedTuple, TypeVar, Union, Generic

from .log import get_logger
from .util import tolerant_float, tolerant_datetime

logger = get_logger(__name__)

DateTime = Union[str, datetime]

T = TypeVar("T")
E = TypeVar("E", bound=NamedTuple)


class DifferenceStorage(Generic[E]):
    _storage_map: dict[NamedTuple, "DifferenceStorage"] = {}
    _identity = lambda ts, snapshot: (ts, snapshot)
    _translation = {
        int: int,
        float: tolerant_float,
        str: str,
        bool: bool,
        datetime: partial(tolerant_datetime, fmt="iso"),
    }

    def __new__(cls, named_tuple: NamedTuple, *args, **kwargs):
        if named_tuple not in cls._storage_map:
            cls._storage_map[named_tuple] = super().__new__(cls)
        return cls._storage_map[named_tuple]

    def __init__(
        self,
        named_tuple: type[E],
        db_path: str,
        *,
        primary_key: str = "",
        not_null_cols=None,
        unique_cols=None,
        check_same_thread=False,
    ):
        """Initializes a DifferenceStorage object

        Args:
            named_tuple (E): The NamedTuple that will be stored in the database
            db_path (str): The path to the database file
            primary_key (str, optional): Primary key of the namedtuple sheet. Defaults to "".
            not_null_cols (list[str], optional): The columns that should not be bull. Defaults to [].
            unique_cols (list[str], optional): The columns that should be unique. Defaults to [].
        """

        if unique_cols is None:
            unique_cols = list()
        if not_null_cols is None:
            not_null_cols = list()

        self._db_path = db_path
        self._named_tuple = named_tuple
        self._table = named_tuple.__name__
        self._con = connect(db_path, check_same_thread=check_same_thread)
        self._primary_key = primary_key
        self._not_null_cols = set(not_null_cols)
        self._unique_cols = set(unique_cols)

        self._foreign_keys = OrderedDict()
        """
        A dictionary of foreign keys in the form of {column: (type, table)}
        """
        self._foreign_tables = OrderedDict()
        """
        A dictionary of foreign tables in the form of {table: column}
        """
        self._external_refs = set()
        """
        A set of external references (i.e., have foreign key relationships)
        """
        self._cursor = self._con.cursor()
        self._no_commit = -2048  # TODO: Optimize the commit and transaction handling
        self._initialize()

    def close(self):
        self._con.close()

    def sync(self, remote_items: list[E]):
        local_items = self.current_snapshot()
        remote_items = {item[self._primary_key_idx]: item for item in remote_items}

        self._no_commit += 1

        local_ids = {item[self._primary_key_idx] for item in local_items}
        remote_ids = {item[self._primary_key_idx] for item in remote_items.values()}

        self.add_all(*[remote_items[id_] for id_ in remote_ids - local_ids])
        self.remove_all(*(local_ids - remote_ids))
        self.update_all(*[remote_items[id_] for id_ in local_ids & remote_ids])

        self._no_commit -= 1
        self._commit()

    def remove_all(self, *primary_keys):
        if len(primary_keys) == 0:
            return
        self._no_commit += 1
        for primary_key in primary_keys:
            self.remove(primary_key)
        self._no_commit -= 1
        self._commit()

    def remove(self, primary_key):
        # Unlink all external object
        for field in self._external_refs:
            assoc_db = self._storage_map[self._fields[field].__args__[0]]
            assoc_db.remove_all(
                *[
                    getattr(assoc_obj, assoc_db._primary_key)
                    for assoc_obj in assoc_db._fetch_assoc_named_tuples(
                        self, primary_key
                    )
                ]
            )
        # Now, remove the object itself
        self._execute(
            f"DELETE FROM {self._table} WHERE {self._primary_key} = ?",
            primary_key,
        )
        self._commit()

    def update_all(self, *args: Union[tuple[E, list], E]):
        if len(args) == 0:
            return
        self._no_commit += 1
        if len(args[0]) == 2:
            for obj, foreign_keys in args:
                self.update(obj, *foreign_keys)
        else:
            for obj in args:
                self.update(obj)
        self._no_commit -= 1
        self._commit()

    def update(self, obj: E, *foreign_keys):
        primary_key = getattr(obj, self._primary_key)
        vals = []
        for idx, field in enumerate(self._fields):
            if field == self._primary_key:
                continue
            if field in self._external_refs:
                self._storage_map[self._fields[field].__args__[0]].update_all(
                    *[(assoc, [primary_key]) for assoc in getattr(obj, field)]
                )
                continue
            if field in self._foreign_keys:
                continue  # data object will not contain foreign keys
            vals.append((field, getattr(obj, field)))

        cols = ", ".join(
            [
                f"{field} = ?"
                for field in list(map(lambda x: x[0], vals))
                + list(self._foreign_keys.keys())
            ]
        )
        self._execute(
            f"UPDATE {self._table} SET {cols} WHERE {self._primary_key} = ?",
            *(val for _, val in vals),
            *foreign_keys,
            primary_key,
        )
        self._commit()

    def add_all(self, *args: Union[tuple[E, list], E], allow_update=True):
        if len(args) == 0:
            return
        self._no_commit += 1
        if len(args[0]) == 2:
            for obj, foreign_keys in args:
                self.add(
                    obj,
                    *foreign_keys,
                    allow_update=allow_update,
                )
        else:
            for obj in args:
                self.add(obj)
        self._no_commit -= 1
        self._commit()

    def add(self, obj: E, *foreign_keys, allow_update=True):
        vals = []
        primary_key = obj[self._primary_key_idx]
        logger.debug(
            "Adding %s with primary key %s and foreign key(s) %s",
            str(obj.__class__),
            primary_key,
            foreign_keys,
        )
        for idx, field in enumerate(self._fields):
            if field in self._external_refs:
                if len(obj[idx]) > 0:
                    self._storage_map[type(obj[idx][0])].add_all(
                        *[(assoc, [primary_key]) for assoc in obj[idx]]
                    )
                continue
            if field in self._foreign_keys:
                continue  # data object will not contain foreign keys
            vals.append(getattr(obj, field))

        if allow_update:
            self._execute(
                f"INSERT OR REPLACE INTO {self._table} "
                f"VALUES ({', '.join(['?' for _ in range(len(vals) + len(foreign_keys))])})",
                *vals,
                *foreign_keys,
            )
        else:
            self._execute(
                (
                    f"INSERT INTO {self._table} "
                    f"VALUES ({', '.join(['?' for _ in range(len(vals) + len(foreign_keys))])})"
                ),
                *vals,
                *foreign_keys,
            )
        self._commit()

    def current_snapshot(self) -> list[E]:
        """
        Returns the current snapshot of the database

        Returns: A list of NamedTuples representing the current snapshot

        """
        select = f"SELECT * FROM {self._table} ORDER BY rowid"
        self._execute(select)
        return [self._to_named_tuple(item) for item in self._cursor.fetchall()]

    def snapshots(
        self,
        to: DateTime = datetime.max,
        agg: Callable[[datetime, list[E]], T] = _identity,
    ) -> list[T]:
        """Returns a list of snapshots of the database at different points in time

        Args:
            to (DateTime, optional): The maximum span of the snapshots. Defaults to datetime.max.
            agg (Callable[[datetime, dict], T], optional): The aggregate functon that takes a timestamp and the snapshot at the time. Defaults to _identity.

        Returns:
            list[T]: A list of aggregated results
        """

        history_items = self._select(to)
        results = []
        snapshot = OrderedDict()

        if agg is DifferenceStorage._identity:
            logger.warning("No aggregation function provided, returning raw snapshots")

        for item in history_items:
            id_, timestamp, operation, *fields = item
            timestamp = datetime.fromisoformat(timestamp)
            primary_key = fields[self._primary_key_idx]
            data = self._to_named_tuple(fields[: self._end_data_idx + 1])
            if operation == "add":
                snapshot[primary_key] = data
            elif operation == "update":
                snapshot[primary_key] = data
            elif operation == "delete":
                snapshot.pop(primary_key)
            results.append(agg(timestamp, list(snapshot.values())))
        return results

    def __getitem__(self, key) -> E:
        """
        Fetches a row from the **snapshot** database by primary key and returns it as a NamedTuple.

        Args:
            key: The primary key of the row to fetch

        Returns: The row as a NamedTuple
        """
        return self._fetch_named_tuple(key)

    def __repr__(self):
        return f"DifferenceStorage({self._table})"

    def _select(self, to: DateTime = datetime.max):
        select = f"SELECT * FROM {self._table}_history WHERE history_item_timestamp <= ? ORDER BY history_item_timestamp"
        self._execute(select, to)
        return self._cursor.fetchall()

    def _initialize(self):
        fields = self._named_tuple.__annotations__
        self._fields = OrderedDict(fields)
        self._primary_key_type = fields[self._primary_key]

        translate = {
            int: "INTEGER",
            float: "REAL",
            str: "TEXT",
            bool: "INTEGER",
            datetime: "TEXT",
        }
        columns = []
        for idx, (field, type_) in enumerate(fields.items()):
            if isinstance(type_, GenericAlias) and type_.__origin__ is list:
                e = type_.__args__[0]
                # TODO: Consider using JSON instead of a separate table
                assert (
                    issubclass(e, tuple)
                    and hasattr(e, "_fields")
                    and e in self._storage_map
                ), (
                    "List elements must be NamedTuples that have already been "
                    "registered with DifferenceStorage"
                )
                self._storage_map[e]._add_foreign_key(
                    f"{self._table.lower()}_id",
                    translate[self._primary_key_type],
                    self._table,
                    self._primary_key,
                )
                self._external_refs.add(field)
                continue
            else:
                col = f"{field} {translate[type_]}"

            if field == self._primary_key:
                col += " PRIMARY KEY"
                self._primary_key_idx = idx
            if field in self._not_null_cols:
                col += " NOT NULL"
            if field in self._unique_cols:
                col += " UNIQUE"
            columns.append(col)
        self._columns = columns

        mk_snapshot_db = (
            f"CREATE TABLE IF NOT EXISTS {self._table} ({', '.join(columns)})"
        )
        logger.debug(
            "Creating table %s with columns %s",
            self._table,
            columns,
        )
        self._execute(mk_snapshot_db)
        cols = ", ".join([c.replace(" PRIMARY KEY", "") for c in columns])
        mk_history_db = (
            f"CREATE TABLE IF NOT EXISTS {self._table}_history ("
            f"history_item_id INTEGER PRIMARY KEY, "
            f"history_item_timestamp TEXT, "
            f"history_item_operation TEXT, "  # add, update, delete
            f"{cols}"
            ")"
        )
        self._execute(mk_history_db)
        self._commit()

        self._start_data_idx = 3
        self._end_data_idx = len(columns) - 1

        self._initialize_triggers()

    def _initialize_triggers(self):
        self._execute(f"DROP TRIGGER IF EXISTS {self._table}_add_trigger")
        self._execute(f"DROP TRIGGER IF EXISTS {self._table}_update_trigger")
        self._execute(f"DROP TRIGGER IF EXISTS {self._table}_delete_trigger")
        cols = ", ".join(
            [
                f"NEW.{field}"
                for field in self._fields
                if field not in self._external_refs
            ]
        )
        mk_add_trigger = (
            f"CREATE TRIGGER IF NOT EXISTS {self._table}_add_trigger "
            f"AFTER INSERT ON {self._table} "
            f"BEGIN "
            f"INSERT INTO {self._table}_history "
            f"SELECT NULL, datetime('now'), 'add', {cols}; "
            f"END"
        )
        self._execute(mk_add_trigger)
        when = " OR ".join(
            [
                f"NEW.{field} IS NOT OLD.{field}"  # NOTE: handle NULL values
                for field in self._fields
                if field != self._primary_key and field not in self._external_refs
            ]
        )
        mk_update_trigger = (
            f"CREATE TRIGGER IF NOT EXISTS {self._table}_update_trigger "
            f"AFTER UPDATE ON {self._table} "
            f"WHEN {when} "
            f"BEGIN "
            f"INSERT INTO {self._table}_history "
            f"SELECT NULL, datetime('now'), 'update', {cols}; "
            f"END"
        )
        self._execute(mk_update_trigger)
        cols = ", ".join(
            [
                f"OLD.{field}"
                for field in self._fields
                if field not in self._external_refs
            ]
        )
        mk_delete_trigger = (
            f"CREATE TRIGGER IF NOT EXISTS {self._table}_delete_trigger "
            f"AFTER DELETE ON {self._table} "
            f"BEGIN "
            f"INSERT INTO {self._table}_history "
            f"SELECT NULL, datetime('now'), 'delete', {cols}; "
            f"END"
        )
        self._execute(mk_delete_trigger)
        self._commit()

    def _add_foreign_key(
        self,
        column: str,
        ref_type: str,
        ref_table: str,
        ref_column: str,
    ):
        logger.debug(
            f"Adding foreign key {self._table}.{column} -> {ref_table}.{ref_column}"
        )
        self._columns.append(
            f"{column} {ref_type} REFERENCES {ref_table} ({ref_column})"
        )
        self._fields[column] = ref_type
        self._foreign_keys[column] = (ref_type, ref_table)
        self._foreign_tables[ref_table] = column

        try:
            self._execute(
                f"ALTER TABLE {self._table} "
                f"ADD COLUMN {column} {ref_type} "
                f"REFERENCES {ref_table} ({ref_column}); "
            )
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                logger.debug(
                    "Column %s already exists in %s, skipping", column, self._table
                )
            else:
                raise e
        try:
            self._execute(
                f"ALTER TABLE {self._table}_history "
                f"ADD COLUMN {column} {ref_type} "
                f"REFERENCES {ref_table} ({ref_column}); "
            )
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                logger.debug(
                    "Column %s already exists in %s, skipping", column, self._table
                )
            else:
                raise e
        logger.debug(
            f"Columns are now {self._columns} and fields are now {self._fields}"
        )
        logger.debug(f"Updating triggers for {self._table} to include {column}")
        self._initialize_triggers()

    def _fetch_named_tuple(self, primary_key) -> E:
        self._execute(
            f"SELECT * FROM {self._table}  WHERE {self._primary_key} = ?",
            primary_key,
        )
        result = self._cursor.fetchone()
        if result is None:
            raise KeyError(f"No row with primary key {primary_key}")
        return self._to_named_tuple(result)

    def _fetch_assoc_named_tuples(
        self,
        storage: "DifferenceStorage",
        ref_key,
    ) -> list[E]:
        self._execute(
            f"SELECT * FROM {self._table} WHERE {self._foreign_tables[storage._table]} = ?",
            ref_key,
        )
        return [self._to_named_tuple(row) for row in self._cursor.fetchall()]

    def _to_named_tuple(self, row) -> E:
        """
        Converts a row from the database to a NamedTuple

        Args:
            row: The row to convert. It should only contain the fields in the NamedTuple

        Returns: The row as a NamedTuple
        """

        fields = self._fields
        assert len(row) == len(fields) - len(
            self._external_refs
        ), f"Row length {len(row)} does not match field length {len(fields)}"
        vals = {}
        for idx, (field, type_, value) in enumerate(
            zip_longest(
                fields.keys(),
                fields.values(),
                row,
            )
        ):
            if field in self._foreign_keys:
                continue
            if field in self._external_refs:
                vals[field] = self._storage_map[
                    type_.__args__[0]
                ]._fetch_assoc_named_tuples(
                    self,
                    row[self._primary_key_idx],
                )
            else:
                try:
                    vals[field] = DifferenceStorage._translation[type_](value)
                except ValueError:
                    logger.error(
                        "Could not convert '%s' to %s at index %s for field %s",
                        value,
                        type_,
                        idx,
                        field,
                    )
                    raise ValueError
        return self._named_tuple(**vals)

    def _execute(self, command: str, *args):
        logger.debug("Executing command %s with args %s", command, args, stacklevel=2)
        self._cursor.execute(command, args)

    def _commit(self):
        if self._no_commit <= 0:
            self._con.commit()

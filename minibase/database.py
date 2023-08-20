import mysql.connector.connection as connection
import mysql.connector.pooling as pooling
import mysql.connector.errors

from minibase.dotdict import DotDict

class Database:
    def __init__(self, config: dict, pool_size: int = 10, id_field: str = "id") -> None:
        self.config = config
        self.pool_size = pool_size
        self.pool = None
        self.id_field = id_field
        self.tables = {}

    def connect(self) -> DotDict:
        self.pool = pooling.MySQLConnectionPool(
            pool_name = "main",
            pool_size = self.pool_size,
            auth_plugin = "mysql_native_password",
            autocommit = True,
            **self.config
        )
        return self.refresh()

    def refresh(self) -> DotDict:
        tables = self.execute("show tables")
        for table in tables:
            name = table[0]
            fields = self.execute(f"desc {name}")
            self.tables[name] = {
                field[0]: field[1] for field in fields
            }
        return DotDict(self.tables)

    def fetch_conn(self) -> connection.MySQLConnection:
        conn = self.pool.get_connection()
        return conn

    def execute(self, query: str, values: list = [], get_id: bool = False) -> object:
        conn = self.fetch_conn()
        cursor = conn.cursor()
        try:
            if len(values) > 0:
                values = [str(value).replace("'", "\'") for value in values]
                cursor.execute(query, values)
            else:
                cursor.execute(query)
            if get_id:
                return cursor.lastrowid
            else:
                return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def niceify(self, table: dict, output: list, remove_id: bool = False) -> list:
        name = list(table.keys())[0]
        fields = self.fetch_fields(name, remove_id = remove_id)
        return [dict(zip(fields, value)) for value in output]

    def joins(self, ids: list, tables: list) -> dict:
        names = [list(table.keys())[0] for table in tables]
        fields = [self.fetch_fields(name) for name in names]
        query = f"SELECT * FROM {names[0]}"
        # query = " ".join([f"JOIN {names[i + 1]} on {ids[i]:}"
        return None

    def fetch_fields(self, table: str, remove_id: bool = False) -> list:
        fields = list(self.tables[table].keys())
        if remove_id:
            fields.remove(self.id_field)
        return fields

    def create(self, table: dict, values: dict, duplicate_check: str = "name", auto_increment: bool = False) -> tuple:
        name = list(table.keys())[0]
        fields = self.fetch_fields(name, remove_id = auto_increment)
        spacers = ("%s, " * len(fields)).rstrip(", ")
        fields = str(tuple(fields)).replace("'", "")
        frame = f"INSERT INTO {name} {fields} VALUES ({spacers})"
        values_list = list(values.values())
        try:
            return (True, self.execute(frame, values_list, get_id = True))
        except mysql.connector.errors.IntegrityError:
            duplicate = values[duplicate_check]
            return (False, self.execute(f"SELECT {self.id_field} FROM {name} WHERE {duplicate_check} = %s", [duplicate])[0][0])

    def read(self, table: dict, uid: object) -> list:
        name = list(table.keys())[0]
        frame = f"SELECT * FROM {name} WHERE {self.id_field} = %s"
        results = self.execute(frame, [uid])
        fields = self.fetch_fields(name)
        return [dict(zip(fields, row)) for row in results][0]

    def update(self, table: dict, uid: object, column: str, value: str) -> bool:
        name = list(table.keys())[0]
        frame = f"UPDATE {name} SET {column} = %s WHERE {self.id_field} = {uid}"
        try:
            self.execute(frame, [value])
            return True
        except mysql.connector.errors.IntegrityError:
            return False

    def delete(self, table: dict, uid: object) -> None:
        name = list(table.keys())[0]
        frame = f"DELETE FROM {name}  WHERE {self.id_field} = {uid}"
        self.execute(frame)

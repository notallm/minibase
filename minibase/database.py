import mysql.connector.connection as connection
import mysql.connector.pooling as pooling

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

    def fetch_fields(self, table: str, remove_id: bool = False) -> list:
        fields = list(self.tables[table].keys())
        if remove_id:
            fields.remove(self.id_field)
        return fields

    def create(self, table: dict, values: dict, auto_increment: bool = False) -> int:
        name = list(table.keys())[0]
        fields = self.fetch_fields(name, remove_id = auto_increment)
        spacers = ("%s, " * len(fields)).rstrip(", ")
        fields = str(tuple(fields)).replace("'", "")
        frame = f"INSERT INTO {name} {fields} VALUES ({spacers})"
        values = list(values.values())
        return self.execute(frame, values, get_id = True)

    def read(self, table: dict, uid: object) -> list:
        name = list(table.keys())[0]
        frame = f"SELECT * FROM {name} WHERE {self.id_field} = %s"
        results = self.execute(frame, [uid])
        fields = self.fetch_fields(name)
        return [dict(zip(fields, row)) for row in results][0]

    def update(self, table: dict, uid: object, column: str, value: str) -> None:
        name = list(table.keys())[0]
        frame = f"UPDATE {name} SET {column} = %s WHERE {self.id_field} = {uid}"
        self.execute(frame, [value])

    def delete(self, table: dict, uid: object) -> None:
        name = list(table.keys())[0]
        frame = f"DELETE FROM {name}  WHERE {self.id_field} = {uid}"
        self.execute(frame)

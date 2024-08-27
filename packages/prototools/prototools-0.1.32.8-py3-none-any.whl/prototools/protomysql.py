try:
    import mysql.connector as mysql
except:
    pass
from operator import not_


def get_q(obj) -> str:
    return ", ".join(
        f"{attr} = '{value}'" for attr, value in obj.__dict__.items()
    )


def execute(
    function,
    function_condition,
    message,
    expression=lambda x: not_(x),
    condition=False,
    alt_function=None,
    alt_message="",
) -> None:
    data, msg = function()
    if expression(data):
        print(message.format(msg))
        return
    if not condition:
        function_condition(msg)
        print(alt_message)
    else:
        print(alt_function(*data))


class Incrementor:
    _count = 0

    def __init__(self) -> None:
        __class__._count += 1

    @property
    def count(self):
        return self._count

    @count.setter
    def count(self, value):
        self._count = value


def get_data(obj: object) -> dict:
    """Get the attributes and values of an object."""
    return {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}


class ProtoMySQL:
    """Simple MySQL wrapper
    """

    def __init__(self, **kwargs) -> None:
        self.conf = kwargs
        self.conf["charset"] = kwargs.get("charset", "utf8")
        self.conf["host"] = kwargs.get("host", "localhost")
        self.conf["port"] = kwargs.get("port", 3306)
        self.connect()

    def connect(self):
        try:
            self.conn = mysql.connect(
                database=self.conf["database"],
                host=self.conf["host"],
                user=self.conf["user"],
                password=self.conf["password"],
            )
            self.cur = self.conn.cursor()
        except:
            print("MySQL connection failed")
            raise

    def query(self, sql, params=None):
        """Run a raw query"""
        try:
            self.cur.execute(sql, params)
        except mysql.OperationalError as e:
            if e[0] == 2006:
                self.connect()
                self.cur.execute(sql, params)
            else:
                raise
        except:
            print("Query failed")
            raise
        return self.cur

    def commit(self):
        return self.conn.commit()

    def insert(self, table, data):
        q = self._serialize_insert(data)
        sql = "INSERT INTO %s (%s) VALUES(%s)" % (table, q[0], q[1])
        return self.query(sql, tuple(data.values()))

    def add(self, table, data):
        if not isinstance(data, dict):
            print("'data' must be a dict instance")
        query = "INSERT INTO {0} ({1}) VALUES ({2});".format(
            table, ",".join(data.keys()), ",".join(["?"] * len(data))
        )
        self.cur.execute(query, list(data.values()))
        self.conn.commit()

    def delete(self, table, columns):
        try:
            query = "DELETE FROM {0} WHERE {1};".format(table, columns)
            self.cur.execute(query)
            self.conn.commit()
        except mysql.OperationalError as e:
            print("Error writing to database:", e)

    def update(self, table, columns, condition):
        try:
            query = "UPDATE %s SET %s WHERE %s;" % (table, columns, condition)
            self.cur.execute(query)
            self.conn.commit()
        except mysql.OperationalError as e:
            print("Error writing to database:", e)

    def select(self, table, q):
        query = "SELECT * FROM {0} WHERE {1}".format(table, q)
        self.cur.execute(query)
        return self.cur.fetchone()

    def get_all(self, table):
        query = "SELECT * from {0};".format(table)
        self.cur.execute(query)
        return self.cur.fetchall()

    def close(self):
        if self.conn:
            self.conn.commit()
            self.cur.close()
            self.conn.close()

    def _serialize_insert(self, data):
        keys = ",".join(data.keys())
        vals = ",".join("%s" for _ in data)
        return keys, vals

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    _delete = delete
    update_ = update

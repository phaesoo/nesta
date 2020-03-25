import MySQLdb
import pandas.io.sql as psql


class MySQLClientError(Exception):
    pass


class MySQLClient:
    def __init__(self, autocommit=False):
        self._conn = None
        self._cursor = None
        self._autocommit = None

    def __del__(self):
        try:
            self._cursor.close()
            self._conn.close()
        except:
            pass

    def init(self, host, port, db, username, password, **kwargs):
        assert isinstance(host, str)
        assert isinstance(port, int)
        assert isinstance(db, str)
        assert isinstance(username, str)
        assert isinstance(password, str)

        self._config = dict(
            host=host,
            port=port,
            db=db,
            user=username,
            passwd=password
        )

    def _init_connection(self):
        self._conn = MySQLdb.connect(**self._config)
        if self._autocommit:
            self._conn.autocommit(True)
        self._cursor = self._conn.cursor()

    def _check_init(self):
        if self._config is None:
            raise MySQLClientError("Client has not been initialized: init()")

    def commit(self):
        self._check_init()
        if self._conn is None:
            self._init_connection()
        self._conn.commit()

    def rollback(self):
        self._check_init()
        if self._conn is None:
            self._init_connection()
        self._conn.rollback()

    def read_sql(self, sql, **kwargs):
        self._check_init()
        if self._conn is None:
            self._init_connection()
        return psql.read_sql(sql, **kwargs)

    def execute(self, sql, parameter=None):
        self._check_init()
        if self._conn is None:
            self._init_connection()
        self._cursor.execute(sql, parameter)

    def executemany(self, sql, parameter=None):
        self._check_init()
        if self._conn is None:
            self._init_connection()
        self._cursor.executemany(sql, parameter)

    def fetchone(self, sql, parameter=None):
        self._check_init()
        if self._conn is None:
            self._init_connection()

        self._cursor.execute(sql, parameter)
        return self._cursor.fetchone()

    def fetchall(self, sql, parameter=None):
        self._check_init()
        if self._conn is None:
            self._init_connection()
        self._cursor.execute(sql, parameter)
        return self._cursor.fetchall()

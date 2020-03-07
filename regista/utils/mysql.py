import MySQLdb
import pandas.io.sql as psql


class MySQLClient:
    def __init__(self, host, port, dbname, user, password):
        self._conn = MySQLdb.connect(
            host=host,
            port=port,
            db=dbname,
            user=user,
            passwd=password
        )
        self._cursor = self._conn.cursor()

    def __del__(self):
        self._cursor.close()
        self._conn.close()

    def read_sql(self, sql, **kwargs):
        if self._conn is None:
            self.__init__()

        try:
            result = psql.read_sql(sql, **kwargs)
        except:
            self._conn.rollback()
            raise
        else:
            self._conn.commit()
            return result

    def execute(self, sql, parameter=None):
        if self._conn is None:
            self.__init__()

        try:
            self._cursor.execute(sql, parameter)
        except:
            self._conn.rollback()
            raise
        else:
            self._conn.commit()

    def executemany(self, sql, parameter=None):
        if self._conn is None:
            self.__init__()

        try:
            self._cursor.executemany(sql, parameter)
        except:
            self._conn.rollback()
            raise
        else:
            self._conn.commit()

    def fetchone(self, sql, parameter=None):
        if self._conn is None:
            self.__init__()

        try:
            self._cursor.execute(sql, parameter)
        except:
            self._conn.rollback()
            raise
        else:
            self._conn.commit()
            return self._cursor.fetchone()

    def fetchall(self, sql, parameter=None):
        if self._conn is None:
            self.__init__()
        try:
            self._cursor.execute(sql, parameter)
        except:
            self._conn.rollback()
            raise
        else:
            self._conn.commit()
            return self._cursor.fetchall()

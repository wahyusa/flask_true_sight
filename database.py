from __future__ import annotations
from TrueSightEngine import Logger
import sqlalchemy

from connect_unix import connect_unix_socket


logger = Logger()


class Database:

    def __init__(self, host, user, password, database, conn_name, runOnLocal=0) -> None:
        print(runOnLocal)
        if runOnLocal == 0:
            self.current_db = connect_unix_socket()
        else:
            self.current_db = sqlalchemy.create_engine(
                sqlalchemy.engine.url.URL.create(
                    drivername="mysql+pymysql",
                    host=host,
                    username=user,
                    password=password,
                    database=database
                )
            )
        self.conn = self.current_db.connect()
        self.db_name = database

    def sql_escape_str(self, string: str) -> str:
        return self.conn.converter.escape(string)

    def get(self, table):
        query = 'SELECT * FROM `' + table + '`'
        try:
            c = self.conn.execute(query)
            if c.rowcount > 0:
                print("Rows produced by statement '{}':".format(
                    query))
                return c.fetchall()
        except Exception as ex:
            logger.error("MYSQL SELECT", ex)
        return ()

    def get_where(self, table, condition: dict):
        cond_query = list()
        for _ in condition.keys():
            cond_query.append(_ + "=%s")
        query = 'SELECT * FROM `' + table + \
            '` WHERE ' + ' AND '.join(cond_query)
        try:
            c = self.conn.execute(query, list(condition.values()))
            if c.rowcount > 0:
                print("Rows produced by statement '{}':".format(
                    str(c.context.__dict__)))
                return c.fetchall()
        except Exception as ex:
            logger.error("MYSQL SELECT", ex)
        return ()

    def update(self, table, parameters: dict):
        param = list()
        for _ in parameters.keys():
            param.append(_ + "=%s")
        query = 'UPDATE `' + table + \
            '` SET ' + ','.join(param)
        try:
            c = self.conn.execute(query, [x for x in parameters.values()])
            print("Number of rows affected by statement '{}': {}".format(
                query, c.rowcount))
            self.conn.commit()
        except Exception as ex:
            logger.error("MYSQL UPDATE", ex)
        return ()

    def update_where(self, table, parameters: dict, where: dict):
        param = list()
        for _ in parameters.keys():
            param.append(_ + "=%s")
        condition = list()
        for _ in where.keys():
            condition.append(_ + "=%s")
        query = 'UPDATE `' + table + \
            '` SET ' + ','.join(param) + ' WHERE ' + ' AND '.join(condition)
        where = list(where.values())
        parameters = list(parameters.values())
        parameters.extend(where)
        try:
            c = self.conn.execute(query, [x for x in parameters])
            if c.rowcount > 0:
                print("Number of rows affected by statement '{}': {}".format(
                    query, c.rowcount))
        except Exception as ex:
            logger.error("MYSQL UPDATE", ex)

        return ()

    def insert(self, table, values: dict):
        fields = list()
        for field in values.keys():
            fields.append(field)
        query = 'INSERT INTO `' + table + \
            '` (' + ','.join(fields) + ') VALUES (' + \
                ','.join(['%s'] * len(values.keys())) + ")"
        try:
            c = self.conn.execute(query, [x for x in values.values()])
            if c.rowcount > 0:
                print("Number of rows affected by statement '{}': {}".format(
                    query, c.rowcount))
        except Exception as ex:
            logger.error("MYSQL UPDATE", ex)
        return ()

    def query(self, query: str):
        try:
            c = self.conn.execute(query)
            if c.rowcount > 0:
                print("Rows produced by statement '{}':".format(
                    query))
                return c.fetchall()
            else:
                print("Number of rows affected by statement '{}': {}".format(
                    query, c.rowcount))
        except Exception as ex:
            logger.error("MYSQL QUERY", ex)
        return ()


class Model:

    def __init__(self) -> None:
        pass

    def get(self) -> dict:
        return self.__dict__

    def empty():
        return Model()

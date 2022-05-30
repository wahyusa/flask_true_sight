from __future__ import annotations
from TrueSightEngine import Logger
import pymysql

logger = Logger()


class Database:
    def __init__(self, host, user, password, database, conn_name) -> None:
        unix_socket = '/cloudsql/{}'.format(conn_name)
        self.conn = pymysql.connect(host=host,user=user, password=password, db=database, unix_socket=unix_socket)
        self.db_name = database

    def sql_escape_str(self, string: str) -> str:
        return self.conn.converter.escape(string)

    def get(self, table):
        c = self.conn.cursor()
        query = 'SELECT * FROM `' + table + '`'
        try:
            if c.execute(query) == 1:
                print("Rows produced by statement '{}':".format(
                    query))
                return c.fetchall()
        except Exception as ex:
            logger.error("MYSQL SELECT", ex)
        return ()

    def get_where(self, table, condition: dict):
        c = self.conn.cursor()
        cond_query = list()
        for _ in condition.keys():
            cond_query.append(_ + "=%s")
        query = 'SELECT * FROM `' + table + \
            '` WHERE ' + ' AND '.join(cond_query)
        try:
            if c.execute(query, list(condition.values())) == 1:
                print("Rows produced by statement '{}':".format(
                    query))
                return c.fetchall()
        except Exception as ex:
            logger.error("MYSQL SELECT", ex)
        return ()

    def update(self, table, parameters: dict):
        c = self.conn.cursor()
        param = list()
        for _ in parameters.keys():
            param.append(_ + "=%s")
        query = 'UPDATE `' + table + \
            '` SET ' + ','.join(param)
        try:
            if c.execute(query, [x for x in parameters.values()]) == 1:
                print("Number of rows affected by statement '{}': {}".format(
                    query, c.rowcount))
                self.conn.commit()
        except Exception as ex:
            logger.error("MYSQL UPDATE", ex)
        return ()

    def update_where(self, table, parameters: dict, where: dict):
        c = self.conn.cursor()
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
            if c.execute(query, [x for x in parameters]) == 1:
                print("Number of rows affected by statement '{}': {}".format(
                    query, c.rowcount))
                self.conn.commit()
        except Exception as ex:
            logger.error("MYSQL UPDATE", ex)

        return ()

    def insert(self, table, values: dict):
        c = self.conn.cursor()
        fields = list()
        for field in values.keys():
            fields.append(field)
        query = 'INSERT INTO `' + table + \
            '` (' + ','.join(fields) + ') VALUES (' + \
                ','.join(['%s'] * len(values.keys())) + ")"
        try:
            if c.execute(query, [x for x in values.values()]) == 1:
                print("Number of rows affected by statement '{}': {}".format(
                    query, c.rowcount))
                self.conn.commit()
        except Exception as ex:
            logger.error("MYSQL UPDATE", ex)
        return ()

    def query(self, query: str):
        c = self.conn.cursor()
        try:
            if c.execute(query):
                if c.with_rows:
                    print("Rows produced by statement '{}':".format(
                        query))
                    return c.fetchall()
                else:
                    print("Number of rows affected by statement '{}': {}".format(
                        query, c.rowcount))
                    self.conn.commit()
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

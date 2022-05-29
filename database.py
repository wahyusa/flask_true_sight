from __future__ import annotations
import mysql.connector


class Database:
    def __init__(self, host, user, password, database) -> None:
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            autocommit=True
        )
        self.db_name = database

    def sql_escape_str(self, string: str) -> str:
        return self.conn.converter.escape(string)

    def get(self, table):
        c = self.conn.cursor()
        query = 'SELECT * FROM `' + table + '`'
        for result in c.execute(query, multi=True):
            if result.with_rows:
                print("Rows produced by statement '{}':".format(
                    result.statement))
                return result.fetchall()
            else:
                print("Number of rows affected by statement '{}': {}".format(
                    result.statement, result.rowcount))
        return ()

    def get_where(self, table, condition: dict):
        c = self.conn.cursor()
        cond_query = list()
        for _ in condition.keys():
            cond_query.append(_ + "=%s")
        query = 'SELECT * FROM `' + table + \
            '` WHERE ' + ' AND '.join(cond_query)
        print(list(condition.values()))
        for result in c.execute(query, list(condition.values()), multi=True):
            if result.with_rows:
                print("Rows produced by statement '{}':".format(
                    result.statement))
                return result.fetchall()
            else:
                print("Number of rows affected by statement '{}': {}".format(
                    result.statement, result.rowcount))
        return ()

    def update(self, table, parameters: dict):
        c = self.conn.cursor()
        param = list()
        for _ in parameters.keys():
            param.append(_ + "=%s")
        query = 'UPDATE `' + table + \
            '` SET ' + ','.join(param)

        for result in c.execute(query, [x for x in parameters.values()], multi=True):
            if result.with_rows:
                print("Rows produced by statement '{}':".format(
                    result.statement))
                return result.fetchall()
            else:
                print("Number of rows affected by statement '{}': {}".format(
                    result.statement, result.rowcount))
                self.conn.commit()
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
        for result in c.execute(query, [x for x in parameters], multi=True):
            if result.with_rows:
                print("Rows produced by statement '{}':".format(
                    result.statement))
                return result.fetchall()
            else:
                print("Number of rows affected by statement '{}': {}".format(
                    result.statement, result.rowcount))
                self.conn.commit()
        return ()

    def insert(self, table, values: dict):
        c = self.conn.cursor()
        fields = list()
        for field in values.keys():
            fields.append(field)
        query = 'INSERT INTO `' + table + \
            '` (' + ','.join(fields) + ') VALUES (' + \
                ','.join(['%s'] * len(values.keys())) + ")"
        for result in c.execute(query, [x for x in values.values()], multi=True):
            if result.with_rows:
                print("Rows produced by statement '{}':".format(
                    result.statement))
                return result.fetchall()
            else:
                print("Number of rows affected by statement '{}': {}".format(
                    result.statement, result.rowcount))
                self.conn.commit()
        return ()

    def query(self, query: str):
        c = self.conn.cursor()
        for result in c.execute(query):
            if result.with_rows:
                print("Rows produced by statement '{}':".format(
                    result.statement))
                return result.fetchall()
            else:
                print("Number of rows affected by statement '{}': {}".format(
                    result.statement, result.rowcount))
                self.conn.commit()
        return ()


class Nullable:
    def __init__(self, dataType) -> None:
        self.type = dataType


class Model:

    def __init__(self) -> None:
        pass

    def get(self) -> dict:
        return self.__dict__

    def empty():
        return Model()

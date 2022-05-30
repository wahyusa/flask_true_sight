from __future__ import annotations
from TrueSightEngine import Logger
import sqlalchemy
import os
from connect_connector import connect_with_connector
from connect_tcp import connect_tcp_socket
from connect_unix import connect_unix_socket

logger = Logger()


class Database:

    def __init__(self, host, user, password, database, conn_name) -> None:

        # socket_dir = '/cloudsql'

        # self.conn = sqlalchemy.create_engine(
        #     sqlalchemy.engine.url.URL.create(
        #         drivername="mysql+pymysql",
        #         username=user,
        #         password=password,
        #         database=database,
        #         query={
        #             "unix_socket": "{}/{}".format(
        #                 socket_dir,
        #                 conn_name)
        #         }
        #     )
        # )

        self.conn = self.init_connection_pool().connect()
        self.db_name = database

    # Source https://github.com/GoogleCloudPlatform/python-docs-samples/blob/main/cloud-sql/mysql/sqlalchemy/app.py
    def init_connection_pool(self) -> sqlalchemy.engine.base.Engine:
        # use a TCP socket when INSTANCE_HOST (e.g. 127.0.0.1) is defined
        if os.environ.get("INSTANCE_HOST"):
            return connect_tcp_socket()

        # use a Unix socket when INSTANCE_UNIX_SOCKET (e.g. /cloudsql/project:region:instance) is defined
        if os.environ.get("INSTANCE_UNIX_SOCKET"):
            return connect_unix_socket()

        # use the connector when INSTANCE_CONNECTION_NAME (e.g. project:region:instance) is defined
        if os.environ.get("INSTANCE_CONNECTION_NAME"):
            return connect_with_connector()

        raise ValueError(
            "Missing database connection type. Please define one of INSTANCE_HOST, INSTANCE_UNIX_SOCKET, or INSTANCE_CONNECTION_NAME"
        )

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
                    query))
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

# [START alchemy_connect_unix]
import sqlalchemy


def connect_unix(db_user, db_pass, db_name, socket_path):
    pool = sqlalchemy.create_engine(
        sqlalchemy.engine.url.URL.create(
            drivername="mysql+pymysql",
            username=db_user,
            password=db_pass,
            database=db_name,
            query={"unix_socket": socket_path},
        ),
        # [START_EXCLUDE]
        pool_size=5,
        max_overflow=2,
        pool_timeout=30,
        pool_recycle=1800,
        # [END_EXCLUDE]
    )
    return pool
# [END alchemy_connect_unix]

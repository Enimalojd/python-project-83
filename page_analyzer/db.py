from contextlib import contextmanager
from psycopg2 import pool
from config import DATABASE_URL


def create_connection_pool():
    return pool.SimpleConnectionPool(1,
                                    10,
                                    DATABASE_URL)


@contextmanager
def get_connection_pool():
    global connect
    if not connect:
        connect = create_connection_pool()
    try:
        conn = connect.getconn()
        yield conn
        conn.commit()
    finally:
        connect.putconn(conn)


connect = create_connection_pool()

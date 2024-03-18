from psycopg2 import pool
from config import (DATABASE_NAME, DATABASE_PASS,
                    DATABASE_USER, DATABASE_HOST, DATABASE_PORT)


connection = pool.SimpleConnectionPool(
    1,
    10,
    user=DATABASE_USER,
    password=DATABASE_PASS,
    host=DATABASE_HOST,
    port=DATABASE_PORT,
    database=DATABASE_NAME
)

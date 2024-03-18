from psycopg2 import pool
from config import DATABASE_URL


connection = pool.SimpleConnectionPool(
    1,
    10,
    DATABASE_URL
)

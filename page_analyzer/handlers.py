from datetime import date
from .db import get_connection_pool


def get_all_urls():
    with get_connection_pool() as conn:
        with conn.cursor() as curs:
            curs.execute("""SELECT urls.id, urls.name, url_checks.created_at, url_checks.status_code
                            FROM urls LEFT JOIN (
                                SELECT DISTINCT ON (url_id) url_id, created_at, status_code
                                FROM url_checks
                                ORDER BY url_id, created_at DESC) AS url_checks ON urls.id = url_checks.url_id
                            ORDER BY urls.id DESC ;""")
            return curs.fetchall()


def check_url_existence(url):
    with get_connection_pool() as conn:
        with conn.cursor() as curs:
            curs.execute("""SELECT id FROM urls WHERE name = (%s);""", (url,))
            return curs.fetchone()


def add_new_url(url):
    with get_connection_pool() as conn:
        with conn.cursor() as curs:
            curs.execute("""INSERT INTO urls (name, created_at)
                         VALUES (%s, %s) RETURNING id;""",
                         (url, date.today()))
            return curs.fetchone()


def get_url_data(url_id):
    with get_connection_pool() as conn:
        with conn.cursor() as curs:
            curs.execute("""SELECT id, name, created_at
                         FROM urls WHERE id = (%s);""",
                         (int(url_id),))
            url = curs.fetchall()
            curs.execute("""SELECT id, created_at, status_code, h1, title,
                         description FROM url_checks WHERE url_id = (%s)
                         ORDER BY id DESC;""",
                         (url[0][0],))
            checks = curs.fetchall()
            data = (url, checks)
            return data


def get_url_name_by_id(url_id):
    with get_connection_pool() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT name FROM urls WHERE id = %s;", (int(url_id),))
            return cur.fetchone()


def insert_new_check(url_id, data):
    with get_connection_pool() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO url_checks (url_id, created_at,
                status_code, h1, title, description)
                VALUES (%s, %s, %s, %s, %s, %s);""", (
                int(url_id), date.today(), data['status'],
                data['h1'], data['title'], data['description']))
            conn.commit()
    return

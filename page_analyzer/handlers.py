from datetime import date
from .db import connection


def get_all_urls():
    conn = connection.getconn()
    with conn:
        with conn.cursor() as curs:
            curs.execute("""
                    SELECT u.id, u.name, uc.created_at, uc.status_code
                    FROM urls u
                    LEFT JOIN (
                        SELECT url_id, created_at, status_code
                        FROM url_checks
                        WHERE (url_id, id) IN (
                            SELECT url_id, MAX(id) AS max_id
                            FROM url_checks
                            GROUP BY url_id
                        )
                    ) uc ON u.id = uc.url_id
                    ORDER BY u.id DESC;
                """)
            connection.putconn(conn)
            return curs.fetchall()


def check_url_existence(url):
    conn = connection.getconn()
    with conn:
        with conn.cursor() as curs:
            curs.execute("""SELECT id FROM urls WHERE name = (%s);""", (url,))
            connection.putconn(conn)
            return curs.fetchone()


def add_new_url(url):
    conn = connection.getconn()
    with conn:
        with conn.cursor() as curs:
            curs.execute("""INSERT INTO urls (name, created_at)
                         VALUES (%s, %s) RETURNING id;""",
                         (url, date.today()))
            connection.putconn(conn)
            return curs.fetchone()


def get_url_data(url_id):
    conn = connection.getconn()
    with conn:
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
            connection.putconn(conn)
            return data


def get_url_name_by_id(url_id):
    conn = connection.getconn()
    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT name FROM urls WHERE id = %s;", (int(url_id),))
            connection.putconn(conn)
            return cur.fetchone()


def insert_new_check(url_id, data):
    conn = connection.getconn()
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO url_checks (url_id, created_at,
                status_code, h1, title, description)
                VALUES (%s, %s, %s, %s, %s, %s);""", (
                int(url_id), date.today(), data['status'],
                data['h1'], data['title'], data['description']))
            conn.commit()
            connection.putconn(conn)

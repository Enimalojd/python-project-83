from datetime import date
import psycopg2
from psycopg2 import OperationalError, pool
from flask import (Flask, render_template, request,
                   redirect, url_for, flash, get_flashed_messages,
                   make_response)
from config import (SECRET_KEY, DATABASE_NAME, DATABASE_PASS,
                    DATABASE_USER, DATABASE_HOST, DATABASE_PORT)
from .validate import validator
from .db_requests import (SELECT_ALL_URLS, CHECK_FOR_MATCHES,
                          ADD_URL, SELECT_DATA, SELECT_PREF,
                          SELECT_CHECK_DATA, SELECT_NAME, INSERT_CHECK)
from .req import get_data
from .parse import url_parse


app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

connection = pool.SimpleConnectionPool(1, 5,
                                           user=DATABASE_USER,
                                           password=DATABASE_PASS,
                                           host=DATABASE_HOST,
                                           port=DATABASE_PORT,
                                           database=DATABASE_NAME)


@app.route('/')
def index():
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages)


@app.get('/urls')
def get_urls():
    messages = get_flashed_messages(with_categories=True)
    try:
        conn = connection.getconn()
        with conn:
            with conn.cursor() as curs:
                curs.execute("SELECT id, name FROM urls ORDER BY id DESC;")
                urls = curs.fetchall()
                checks = []
                for url in urls:
                    curs.execute("SELECT created_at, status_code FROM url_checks WHERE url_id = (%s) ORDER BY id DESC;", (url[0],))
                    last_check = curs.fetchone()
                    if last_check:
                        url = url + (last_check[0], last_check[1])
                        checks.append(url)
                    else:
                        url = url + ('', '')
                        checks.append(url)
                return render_template('urls.html',
                                       messages=messages, urls=checks)
    except OperationalError:
        flash('Ошибка при подключении к базе данных!', 'error')
        return redirect('/')


@app.post('/urls')
def post_urls():
    url = request.form['url']
    errors = validator(url)
    if errors:
        flash(F'{errors["url"]}', 'error')
        return make_response(render_template('index.html'), 422)
    url = url_parse(url)
    try:
        conn = connection.getconn()
        with conn:
            with conn.cursor() as curs:
                curs.execute("SELECT id FROM urls WHERE name = (%s);", (url,))
                url_id = curs.fetchone()
                if url_id:
                    flash('Страница уже существует', 'alert')
                    return redirect(url_for('get_url', id=url_id[0]), code=302)
                curs.execute("INSERT INTO urls (name, created_at) VALUES (%s, %s) RETURNING id;", (url, date.today()))
                url_id = curs.fetchone()
                flash('Страница успешно добавлена', 'success')
                conn.commit()
                return redirect(url_for('get_url', id=url_id[0]), code=302)
    except OperationalError:
        flash('Ошибка при подключении к базе данных!', 'error')
        return redirect('/')


@app.get('/urls/<id>')
def get_url(id):
    messages = get_flashed_messages(with_categories=True)
    try:
        conn = connection.getconn()
        with conn:
            with conn.cursor() as curs:
                curs.execute("SELECT id, name, created_at FROM urls WHERE id = (%s);", (int(id),))
                url = curs.fetchall()
                curs.execute("SELECT id, created_at, status_code, h1, title, description FROM url_checks WHERE url_id = (%s) ORDER BY id DESC;", (url[0][0],))
                checks = curs.fetchall()
        return render_template('new.html', url=url,
                               messages=messages, checks=checks)
    except OperationalError:
        flash('Ошибка при подключении к базе данных!', 'error')
        return redirect(url_for('get_url', id=int(id)), code=302)


@app.post('/urls/<id>/checks')
def post_checks(id):
    try:
        conn = connection.getconn()
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT name FROM urls WHERE (id) = (%s);", (int(id),))
                url = cur.fetchone()
                new_data = get_data(str(url[0]))
                if new_data:
                    cur.execute("INSERT INTO url_checks (url_id, created_at, status_code, h1, title, description) VALUES (%s, %s, %s, %s, %s, %s);", (int(id), date.today(),
                                               new_data['status'],
                                               new_data['h1'],
                                               new_data['title'],
                                               new_data['description']))
                    conn.commit()
                    flash('Страница успешно проверена', 'success')
                    return redirect(url_for('get_url', id=int(id)), code=302)
                flash('Произошла ошибка при проверке', 'error')
                return redirect(url_for('get_url', id=int(id)), code=302)
    except OperationalError:
        flash('Ошибка при подключении к базе данных!', 'error')
        return redirect(url_for('get_url', id=int(id)), code=302)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

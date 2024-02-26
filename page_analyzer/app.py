from datetime import date
import psycopg2
from psycopg2 import OperationalError
from flask import (Flask, render_template, request,
                   redirect, url_for, flash, get_flashed_messages)
from config import SECRET_KEY, DATABASE_URL
from .validate import validator
from .db_requests import (SELECT_ALL_URLS, CHECK_FOR_MATCHES,
                          ADD_URL, SELECT_DATA, SELECT_PREF,
                          SELECT_CHECK_DATA, SELECT_NAME, INSERT_CHECK)
from .req import get_data


app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY


@app.route('/')
def index():
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages)


@app.get('/urls')
def get_urls():
    messages = get_flashed_messages(with_categories=True)
    try:
        conn = psycopg2.connect(DATABASE_URL)
        with conn:
            with conn.cursor() as curs:
                curs.execute(SELECT_ALL_URLS)
                urls = curs.fetchall()
                checks = []
                for url in urls:
                    curs.execute(SELECT_PREF, (url[0],))
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
        return redirect(url_for('index'))
    try:
        conn = psycopg2.connect(DATABASE_URL)
        with conn:
            with conn.cursor() as curs:
                curs.execute(CHECK_FOR_MATCHES, (url,))
                url_id = curs.fetchone()
                if url_id:
                    flash('Такой сайт уже существует!', 'alert')
                    return redirect(url_for('get_url', id=url_id[0]), code=302)
                curs.execute(ADD_URL, (url, date.today()))
                url_id = curs.fetchone()
                flash('Сайт успешно добавлен!', 'success')
                conn.commit()
                return redirect(url_for('get_url', id=url_id[0]), code=302)
    except OperationalError:
        flash('Ошибка при подключении к базе данных!', 'error')
        return redirect('/')


@app.get('/urls/<id>')
def get_url(id):
    messages = get_flashed_messages(with_categories=True)
    try:
        conn = psycopg2.connect(DATABASE_URL)
        with conn:
            with conn.cursor() as curs:
                curs.execute(SELECT_DATA, (int(id),))
                url = curs.fetchall()
                curs.execute(SELECT_CHECK_DATA, (url[0][0],))
                checks = curs.fetchall()
        return render_template('new.html', url=url,
                               messages=messages, checks=checks)
    except OperationalError:
        flash('Ошибка при подключении к базе данных!', 'error')
        return redirect(url_for('get_url', id=int(id)), code=302)


@app.post('/urls/<id>/checks')
def post_checks(id):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        with conn:
            with conn.cursor() as cur:
                cur.execute(SELECT_NAME, (int(id),))
                url = cur.fetchone()
                new_data = get_data(str(url[0]))
                if new_data:
                    cur.execute(INSERT_CHECK, (int(id), date.today(),
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

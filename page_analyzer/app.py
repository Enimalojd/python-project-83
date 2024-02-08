from datetime import date
import psycopg2
from flask import (Flask, render_template, request,
                   redirect, url_for, flash, get_flashed_messages)
from config import SECRET_KEY, DATABASE_URL
from .validate import validator
from .db_requests import (SELECT_ALL_URLS, CHECK_FOR_MATCHES,
                          ADD_URL, SELECT_DATA)


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
    # СЮДА НАПИСАТЬ ОБРАБОТЧИК ОШИБОК ПОДКЛЮЧЕНИЯ К БАЗЕ
    finally:
        conn.close()
    return render_template('urls.html', messages=messages, urls=urls)


@app.post('/urls')
def post_urls():
    url = request.form['url']
    errors = validator(url)
    if errors:
        flash(errors['url'])
        redirect(url_for('/'))
    try:
        conn = psycopg2.connect(DATABASE_URL)
        with conn:
            with conn.cursor() as curs:
                curs.execute(CHECK_FOR_MATCHES, (url,))
                url_id = curs.fetchone()
                if url_id:
                    flash('Такой сайт уже существует!')
                    return redirect(url_for('get_url', id=url_id[0]), code=302)
                else:
                    curs.execute(ADD_URL, (url, date.today()))
                    url_id = curs.fetchone()
                    flash('Сайт успешно добавлен!')
                    return redirect(url_for('get_url', id=url_id[0]), code=302)
    except Exception as e:
        flash('Что-то пошло не так!')
        return redirect('/')


@app.get('/urls/<id>')
def get_url(id):
    messages = get_flashed_messages(with_categories=True)
    conn = psycopg2.connect(DATABASE_URL)
    with conn:
        with conn.cursor() as curs:
            curs.execute(SELECT_DATA, (int(id),))
            url = curs.fetchall()
            print(url)
    return render_template('new.html', url=url, messages=messages)

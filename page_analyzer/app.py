from datetime import date
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages
from config import SECRET_KEY, DATABASE_URL
from .validate import validator



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
                curs.execute("SELECT id, name FROM urls ORDER BY created_at ASC;")
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
                curs.execute("SELECT id FROM urls WHERE name = (%s);", (url,))
                url_id = curs.fetchone()
                if url_id:
                    flash('Такой сайт уже существует!')
                    return redirect(url_for('get_url', id=url_id[0]), code=302)
                else:
                    curs.execute("INSERT INTO urls (name, created_at) VALUES (%s, %s) RETURNING id;", (url, date.today()))
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
            curs.execute("SELECT id, name, created_at FROM urls WHERE id = (%s);", (int(id),))
            url = curs.fetchall()
            print(url)
    return render_template('new.html', url=url, messages=messages)

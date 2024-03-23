from psycopg2 import OperationalError
from flask import (Flask, render_template, request,
                   redirect, url_for, flash, get_flashed_messages,
                   make_response)
from config import SECRET_KEY
from .validate import valid_url
from .urls import extract_page_data
from .urls import url_parse
from .handlers import (get_all_urls, check_url_existence, add_new_url,
                       get_url_data, get_url_name_by_id, insert_new_check)


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
        urls_with_checks = get_all_urls()
        checks = []
        for url_info in urls_with_checks:
            url_id, url_name, created_at, status_code = url_info
            if created_at is not None:
                checks.append((url_id, url_name, created_at, status_code))
            else:
                checks.append((url_id, url_name, '', ''))
        return render_template('urls.html', messages=messages, urls=checks)
    except OperationalError:
        flash('Ошибка при подключении к базе данных!', 'error')
        return redirect('/')


@app.post('/urls')
def post_urls():
    url = request.form['url']
    errors = valid_url(url)
    if errors:
        flash(F'{errors["url"]}', 'error')
        return make_response(render_template('index.html'), 422)
    url = url_parse(url)
    try:
        url_id = check_url_existence(url)
        if url_id:
            flash('Страница уже существует', 'alert')
            return redirect(url_for('get_url', id=url_id[0]), code=302)
        url_id = add_new_url(url)
        flash('Страница успешно добавлена', 'success')
        return redirect(url_for('get_url', id=url_id[0]), code=302)
    except OperationalError:
        flash('Ошибка при подключении к базе данных!', 'error')
        return redirect('/')


@app.get('/urls/<id>')
def get_url(id):
    messages = get_flashed_messages(with_categories=True)
    try:
        url, checks = get_url_data(id)
        return render_template('new.html', url=url, messages=messages,
                               checks=checks)
    except OperationalError:
        flash('Ошибка при подключении к базе данных!', 'error')
        return redirect(url_for('get_url', id=int(id)), code=302)


@app.post('/urls/<id>/checks')
def post_checks(id):
    try:
        url_name = get_url_name_by_id(id)
        if url_name:
            new_data = extract_page_data(str(url_name[0]))
            if new_data:
                insert_new_check(id, new_data)
                flash('Страница успешно проверена', 'success')
            else:
                flash('Произошла ошибка при проверке', 'error')
        else:
            flash('Страница не найдена', 'error')
    except OperationalError:
        flash('Ошибка при подключении к базе данных!', 'error')
    return redirect(url_for('get_url', id=int(id)), code=302)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

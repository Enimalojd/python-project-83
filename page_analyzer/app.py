from flask import Flask
from config import SECRET_KEY


app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY


@app.route('/')
def hello():
    return 'Hello world!'

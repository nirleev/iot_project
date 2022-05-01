from flask import g, Flask, request
import sqlite3
import os

DATABASE = './db.sqlite3'

app = Flask(__name__)

state = "test"

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    cur = get_db().cursor()
    # TODO
    cur.execute()


@app.route('/')
def hello():
    return state

@app.route('/temp', methods=['POST'])
def add_data():
    global state
    data = request.get_data(as_text=True)
    state = data
    return "OK"

if not os.path.exists(DATABASE):
    with app.app_context():
        init_db()

if __name__ == "__main__":
    app.run('0.0.0.0', 8080)
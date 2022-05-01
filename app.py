from flask import g, Flask, request, render_template
import sqlite3
import os

DATABASE = './db.sqlite3'

app = Flask(__name__)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    cur = get_db().cursor()
    # TODO
    cur.execute('CREATE TABLE test (value text);')
    get_db().commit()


@app.route('/')
def hello():
    with app.app_context():
        cur = get_db().cursor()
        cur.execute('select value from test')
        data = cur.fetchall()
        cur.close()
        return render_template('test.html', data=data)

@app.route('/temp', methods=['POST'])
def add_data():
    data = request.get_data(as_text=True)
    with app.app_context():
        cur = get_db().cursor()
        cur.execute('insert into test (value) values (?)', (data,))
        get_db().commit()
    return "OK"

if not os.path.exists(DATABASE):
    with app.app_context():
        init_db()

if __name__ == "__main__":
    app.run('0.0.0.0', 8080)
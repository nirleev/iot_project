import eventlet
from flask import g, Flask, request, render_template
from flask_socketio import SocketIO
import sqlite3
import os

DATABASE = './db.sqlite3'
TABLE = "test"

app = Flask(__name__)
socketio = SocketIO(app)

eventlet.monkey_patch()

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
    cur.execute(f'CREATE TABLE {TABLE} (value text);')
    get_db().commit()


@app.route('/')
def hello():
    with app.app_context():
        cur = get_db().cursor()
        cur.execute(f'select value from {TABLE}')
        data = cur.fetchall()
        cur.close()
        return render_template('test.html', data=data)

@app.route('/temp', methods=['POST'])
def add_data():
    data = request.get_data(as_text=True)
    with app.app_context():
        cur = get_db().cursor()
        cur.execute(f'insert into {TABLE} (value) values (?)', (data,))
        get_db().commit()
    socketio.emit('newdata', {'value': data})
    return "OK"

@app.route('/clear')
def clear():
    with app.app_context():
        cur = get_db().cursor()
        cur.execute(f'delete from {TABLE}')
        get_db().commit()
    return "OK"

if not os.path.exists(DATABASE):
    with app.app_context():
        init_db()

if __name__ == "__main__":
    host='0.0.0.0'
    port = 8080
    print(f'Running on {host}:{port}')
    socketio.run(app, host, port)

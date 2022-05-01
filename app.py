import eventlet
from flask import g, Flask, request, render_template
from flask_socketio import SocketIO
import sqlite3
import os
from datetime import datetime

DATABASE = './db.sqlite3'
TABLE_NAME = 'test'

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
    cur.execute('CREATE TABLE {} (date datetime, temperature int);'.format(TABLE_NAME))
    cur.execute('INSERT INTO {} (date, temperature) VALUES (\'2022-05-01 18:55:50\', 10);'.format(TABLE_NAME))
    get_db().commit()

@app.route('/')
def hello():
    with app.app_context():
        cur = get_db().cursor()
        cur.execute(f'select date, temperature from {TABLE_NAME}')
        data = cur.fetchall()
        cur.close()
        return render_template('test.html', data=data)

@app.route('/temp', methods=['POST'])
def add_data():
    status = validate_data(request.form)
    if status:
        f_date = request.form.get('date')
        f_temp = request.form.get('temperature')
        with app.app_context():
            cur = get_db().cursor()
            cur.execute('insert into test (date, temperature) values (?, ?)', (f_date,
                                                                               f_temp,))
            get_db().commit()
        socketio.emit('newdata', {'date': f_date, 'temp': f_temp})
        return "OK"
    else:
        return "BAD REQUEST"

def validate_data(req):
    date = req.get('date')
    temp = req.get('temperature')

    if date is not None and temp is not None:
        try:
            int(temp)
            datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            return True
        except:
            return False
    else:
        return False

if not os.path.exists(DATABASE):
    with app.app_context():
        init_db()

if __name__ == "__main__":
    host='0.0.0.0'
    port = 8080
    print(f'Running on {host}:{port}')
    socketio.run(app, host, port)

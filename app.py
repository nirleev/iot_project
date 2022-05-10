import eventlet
from flask import g, Flask, request, render_template
from flask_socketio import SocketIO
from flask_httpauth import HTTPBasicAuth
import sqlite3
import os
from datetime import datetime
from werkzeug.security import check_password_hash
from argparse import ArgumentParser
from flask_serial import Serial
from datetime import datetime as dt

DATABASE = './db.sqlite3'
TABLE_NAME = 'test'
USER = 'username'
PASW = 'password_hash'

app = Flask(__name__)
app.secret_key = b'#\x8a\xc7rI\x83\x92\x0eK\xfe=\xd9\x10I\xd4\xfa'
socketio = SocketIO(app)

app.config['SERIAL_TIMEOUT'] = 0.2
# TODO: Device name may be different:
app.config['SERIAL_PORT'] = '/dev/rfcomm0'
app.config['SERIAL_BAUDRATE'] = 9600
app.config['SERIAL_BYTESIZE'] = 8
app.config['SERIAL_PARITY'] = 'N'
app.config['SERIAL_STOPBITS'] = 1

ser = Serial(app)

auth = HTTPBasicAuth()

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


@app.after_request
def add_header(response):
    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'no-store'
    return response

@ser.on_message()
def serial_msg(data: bytes):
    f_temp = data.decode('ascii').strip()
    f_date = dt.now().strftime("%Y-%m-%d %H:%M:%S")
    with app.app_context():
        cur = get_db().cursor()
        cur.execute('insert into test (date, temperature) values (?, ?)', (f_date,
                                                                           f_temp,))
        get_db().commit()
    socketio.emit('newdata', {'date': f_date, 'temp': f_temp})
    return "OK"

@auth.verify_password
def get_pw(username, password):
    with app.app_context():
        cur = get_db().cursor()
        cur.execute(f'select {PASW} from admins where {USER}=?', (username,))
        obj: sqlite3.Row = cur.fetchone()
        if obj:
            hash = obj[PASW]
            if check_password_hash(hash, password):
                return username
        return None


def init_db():
    cur = get_db().cursor()
    users = {'admin': 'pbkdf2:sha256:260000$Om0TWYPSiXwtpXZr$91fe3791b21e82e85a7fa77d0b391ee5fa28fd55940f6c31cadcf6f5b96fe96e'}
    cur.execute(f'CREATE TABLE admins ({USER} text, {PASW} text);')
    for u, p in users.items():
        cur.execute(f'INSERT INTO admins ({USER}, {PASW}) VALUES (\'{u}\', \'{p}\');')
    cur.execute('CREATE TABLE {} (date datetime, temperature int);'.format(TABLE_NAME))
    cur.execute('INSERT INTO {} (date, temperature) VALUES (\'2022-05-01 18:55:50\', 10);'.format(TABLE_NAME))
    get_db().commit()


@app.route('/')
@auth.login_required
def hello():
    with app.app_context():
        cur = get_db().cursor()
        cur.execute(f'select date, temperature from {TABLE_NAME}')
        data = cur.fetchall()
        cur.close()
        return render_template('index.html', data=data)


@app.route('/docs')
def get_docs():
    print('sending docs')
    return render_template('swaggerui.html')


@app.route('/clear')
@auth.login_required
def clear():
    with app.app_context():
        cur = get_db().cursor()
        cur.execute(f'DELETE FROM {TABLE_NAME}')
        get_db().commit()
    return "Database cleared successfully"


@app.route('/temp', methods=['POST'])
@auth.login_required
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

@app.route('/<path:path>')
def static_file(path):
    return app.send_static_file(path)

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

def main():
    host = '0.0.0.0'
    port = 8080
    par = ArgumentParser()
    par.add_argument('-d', action='store_true', dest='debug')
    args = par.parse_args()
    if not args.debug:
        print(f'Running on {host}:{port}')
    socketio.run(app, host, port, debug=args.debug)
    print("Exit")

if __name__ == "__main__":
    main()

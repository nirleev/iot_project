from flask import g, Flask, request
import sqlite3

DATABASE = 'data.db'
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


@app.route('/')
def hello():
    return state

@app.post('/temp')
def add_data():
    global state
    data = request.get_data(as_text=True)
    state = data
    return "OK"

if __name__ == "__main__":
    app.run('0.0.0.0', 8080)
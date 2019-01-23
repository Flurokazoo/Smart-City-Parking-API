from flask import Flask
from flask import g
from flask_restful import reqparse, abort, Api, Resource
import sqlite3

DATABASE = 'C:/sqlite/parking_db.db'

app = Flask(__name__)
api = Api(app)

conn = sqlite3.connect(DATABASE)
cur = conn.cursor()

def dbQuery(query):
    cur.execute(query)
    rows = cur.fetchall()
    return rows

def abort_if_todo_doesnt_exist(todo_id):
    if todo_id not in TODOS:
        abort(404, message="Todo {} doesn't exist".format(todo_id))

parser = reqparse.RequestParser()
parser.add_argument('task')


if __name__ == '__main__':
    app.run(debug=True)
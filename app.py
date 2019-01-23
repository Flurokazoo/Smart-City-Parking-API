from flask import Flask
from flask import g
from flask_restful import reqparse, abort, Api, Resource
import sqlite3

DATABASE = 'C:/sqlite/parking_db.db'

app = Flask(__name__)
api = Api(app)

conn = sqlite3.connect(DATABASE, check_same_thread=False)

def dbQuery(query):
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    print(rows)
    return rows

def abort_if_todo_doesnt_exist(todo_id):
    if todo_id not in TODOS:
        abort(404, message="Todo {} doesn't exist".format(todo_id))

parser = reqparse.RequestParser()
parser.add_argument('task')

class Sector(Resource):
    def get(self, sector_id):
        result = dbQuery('SELECT * FROM entry WHERE cluster_id = ' + sector_id + ' ORDER BY timestamp DESC LIMIT 1')
        return result

api.add_resource(Sector, '/sector/<sector_id>')


if __name__ == '__main__':
    app.run(debug=True)
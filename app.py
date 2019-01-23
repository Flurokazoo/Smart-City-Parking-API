from flask import Flask
from flask import g
from flask import jsonify
from flask_restful import reqparse, abort, Api, Resource
import sqlite3
import json

DATABASE = 'C:/Users/Jasper/Downloads/parking_db.db'

app = Flask(__name__)
api = Api(app)

conn = sqlite3.connect(DATABASE, check_same_thread=False)
cur = conn.cursor()


def dbQuery(query):
    cur.execute(query)
    rows = cur.fetchall()
    return rows

parser = reqparse.RequestParser()
parser.add_argument('task')

class Sector(Resource):
    def get(self, sector_id):
        result = dbQuery('SELECT * FROM entry INNER JOIN sector ON sector.id = entry.cluster_id INNER JOIN coordinate ON coordinate.sector_id = entry.cluster_id WHERE cluster_id = ' + sector_id + ' ORDER BY timestamp DESC')
        if len(result) <= 0:
            abort(404, message="Sector {} doesn't exist".format(sector_id))
        
        items = [dict(zip([key[0] for key in cur.description], row)) for row in result]
        coordinates = []
        threshold = 0
        count = 0
        response = []
   
        for val in items:            
            if count < 1:
                threshold = val['timestamp']
                response.append({
                'data': {
                    'sector_id': val['sector_id'],
                    'density': val['density'],
                    'time': val['timestamp'],
                    }
                })
            if int(val['timestamp']) >= threshold:
                coordinates.append({'latitude': val['latitude'], 'longitude': val['longtitude']})
            else :
                break
            count = count + 1
        response[0]['data']['coordinates'] = coordinates
        return response

api.add_resource(Sector, '/sector/<sector_id>')


if __name__ == '__main__':
    app.run(debug=True)
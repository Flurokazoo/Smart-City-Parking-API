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
        result = dbQuery('SELECT entry.timestamp, entry.density, entry.cluster_id, coordinate.latitude, coordinate.longtitude, sensor.id, sensor.parked FROM entry INNER JOIN coordinate ON coordinate.sector_id = entry.cluster_id INNER JOIN sensor ON sensor.sector_id = entry.cluster_id WHERE cluster_id = ' + sector_id + ' AND entry.timestamp = (SELECT MAX(entry.timestamp) FROM entry)  ORDER BY timestamp DESC')
        if len(result) <= 0:
            abort(404, message="Sector {} doesn't exist".format(sector_id))
        
        items = [dict(zip([key[0] for key in cur.description], row)) for row in result]
        coordinates = []
        sensors = []
        threshold = 0
        count = 0
        response = []
   
        for val in items:      
            skip = False
            sensorExists = False
            if count < 1:
                threshold = val['timestamp']
                response.append({
                'data': {
                    'sector_id': val['cluster_id'],
                    'density': val['density'],
                    'time': val['timestamp'],
                    }
                })
            if val['timestamp'] >= threshold :
                for cor in coordinates:
                    if cor['latitude'] == val['latitude'] and cor['longitude'] == val['longtitude']:
                        skip = True
                        break

                for sen in sensors:
                    if sen['id'] == val['id']:
                        sensorExists = True
                        break
                
                if skip == False:
                    coordinates.append({'latitude': val['latitude'], 'longitude': val['longtitude']})
                if sensorExists == False:
                    sensors.append({'id': val['id'], 'parked': val['parked']})
            else :
                break
            count = count + 1
        response[0]['data']['coordinates'] = coordinates
        response[0]['data']['sensors'] = sensors
        return response

api.add_resource(Sector, '/sector/<sector_id>')

if __name__ == '__main__':
    app.run(debug=True)
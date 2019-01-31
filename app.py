from flask import Flask
from flask import g
from flask import jsonify
from flask import request
from flask_restful import reqparse, abort, Api, Resource
import sqlite3
import json
from datetime import datetime
import time
import math
from geopy.distance import geodesic
import numpy
from decimal import Decimal

DATABASE = 'C:/Users/Jasper/Downloads/parking_db.db'

app = Flask(__name__)
api = Api(app)

conn = sqlite3.connect(DATABASE, check_same_thread=False)
cur = conn.cursor()

parser = reqparse.RequestParser()
parser.add_argument('limit', type=int, help='Parameter "limit" should be of type integer')
parser.add_argument('start', type=int, help='Parameter "start" should be of type integer')
parser.add_argument('end', type=int, help='Parameter "end" should be of type integer')
parser.add_argument('interval', type=int, help='Parameter "interval" should be of type integer')
parser.add_argument('page', type=int, help='Parameter "page" should be of type integer')
parser.add_argument('latitude', type=float, help='Parameter "latitude" should be of type float')
parser.add_argument('longitude', type=float, help='Parameter "longitude" should be of type float')
parser.add_argument('range', type=int, help='Parameter "range" should be of type float')

# Function to query to database, returning all rows
def dbQuery(query):
    cur.execute(query)
    rows = cur.fetchall()
    return rows

#Class for single sector
class Sector(Resource):
    def options(self, sector_id):
        return '', 204, {'Allow': 'GET, OPTIONS'}
    def get(self, sector_id):
        result = dbQuery('SELECT entry.timestamp, entry.density, entry.cluster_id, coordinate.latitude, coordinate.longtitude, sensor.id, sensor.parked FROM entry INNER JOIN coordinate ON coordinate.sector_id = entry.cluster_id INNER JOIN sensor ON sensor.sector_id = entry.cluster_id WHERE cluster_id = ' + sector_id + ' AND entry.timestamp = (SELECT MAX(entry.timestamp) FROM entry)  ORDER BY timestamp DESC')
        if len(result) <= 0:
            abort(404, message="Sector {} doesn't exist".format(sector_id))
        
        items = [dict(zip([key[0] for key in cur.description], row)) for row in result]
        coordinates = []
        sensors = []
        threshold = 0
        count = 0
        response = {}
   
        for val in items:   
            timestamp = int(val['timestamp'] / 1000) 
            readable = datetime.fromtimestamp(timestamp).isoformat()

            skip = False
            sensorExists = False
            if count < 1:
                threshold = val['timestamp']
                response['data'] = {
                'sector_data': {
                    'sector_id': val['cluster_id'],
                    'density': val['density'],
                    'timestamp': timestamp,
                    'date': readable
                    }
                }                
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
        response['data']['coordinates'] = coordinates
        response['data']['sensors'] = sensors
        response['metadata'] = {
            'status_code': 200,
            'current_timestamp': int(time.time()),
            'current_date': datetime.fromtimestamp(int(time.time())).isoformat()
        }
        return response

#Class for all sectors collection
class Sectors(Resource):
    def options(self):
        return '', 204, {'Allow': 'GET, OPTIONS'}
    def get(self):
        response = {}
        response['data'] = []
        coordinates = []
        sectors = []
        sensors = []
        threshold = 0
        count = 0
        root = str(request.url_root)

        idResult = dbQuery('SELECT id FROM sector')
        idItems = [dict(zip([key[0] for key in cur.description], row)) for row in idResult]
        for val in idItems:
            response['data'].append({
                'sector_id': val['id']
            })

        result = dbQuery('SELECT entry.timestamp, entry.density, entry.cluster_id, coordinate.latitude, coordinate.longtitude, sensor.id, sensor.parked FROM entry INNER JOIN coordinate ON coordinate.sector_id = entry.cluster_id INNER JOIN sensor ON sensor.sector_id = entry.cluster_id WHERE entry.timestamp = (SELECT MAX(entry.timestamp) FROM entry)  ORDER BY timestamp DESC')
        items = [dict(zip([key[0] for key in cur.description], row)) for row in result]       
   
        for val in items:   
            timestamp = int(val['timestamp'] / 1000) 
            readable = datetime.fromtimestamp(timestamp).isoformat()
            for res in response['data']:
                index = response['data'].index(res)
                sectorInt = int(res['sector_id'])
                if sectorInt == val['cluster_id']:
                    response['data'][index]['density'] = val['density']
                    response['data'][index]['timestamp'] = timestamp
                    response['data'][index]['date'] = readable
                    response['data'][index]['self_links'] = {
                        "detail": root + "sector/" + str(val['cluster_id']),
                        "history": root + "history/" + str(val['cluster_id'])
                    }
        
        response['metadata'] = {
            'status_code': 200,
            'current_timestamp': int(time.time()),
            'current_date': datetime.fromtimestamp(int(time.time())).isoformat()
        }
        return response

#Class for historical data of specific cluster
class History(Resource):
    def options(self, sector_id):
        return '', 204, {'Allow': 'GET, OPTIONS'}
    def get(self, sector_id):   
        args = parser.parse_args()
        response = {
            "data": {
                "sector_id": sector_id
            },
            "pagination": {},
            "metadata": {}
        }
        root = str(request.url_root)
        if args['page']:
            page = int(args['page'])
        else:
            page = 1
        
        pageLimit = 20
        offset = ((page - 1) * pageLimit)
        response['data']['entries'] = []

        if args['limit']:
            limit = str(args['limit'])    
        else:
            limit = '1000'

        limitUrl = '&limit=' + limit
        #MAX AMOUNT OF FULL PAGES
        fullPageNo = math.floor(int(limit) / pageLimit)  
        #REMAINING ENTRIES ON NON FULL PAGE
        entriesModulo = int(limit) % pageLimit

        nextPage = page + 1
        prevPage = page - 1
        
        if args['start']:
            start = str(args['start'] * 1000)
            startUrl = '&start=' + str(args['start'])
        else:
            start = '0'
            startUrl = ''

        if args['end']:
            end = str(args['end'] * 1000)
            endUrl = '&end=' + str(args['end'])
        else:
            end = int(time.time()) * 1000
            end = str(end)
            endUrl = ''

        if args['interval']:
            interval = str(args['interval'] * 1000)
            intervalUrl = '&interval=' + str(args['interval'])
        else:
            interval = str(3600 * 1000)
            intervalUrl = ''

        if page == (fullPageNo + 1):
            queryLimit = entriesModulo
        elif page > (fullPageNo + 1):
            queryLimit = 0
        else:
            queryLimit = pageLimit

        result = dbQuery("SELECT timestamp, density, AVG(density) AS average FROM entry WHERE cluster_id = " + sector_id + " AND timestamp > " + start + "  AND timestamp < " + end + " GROUP BY ROUND(timestamp / " + interval + ") ORDER BY timestamp DESC LIMIT " + str(queryLimit) + " OFFSET " + str(offset))
        if len(result) <= 0:
            abort(404, message="No results found for sector {} with given parameters".format(sector_id))
        
        items = [dict(zip([key[0] for key in cur.description], row)) for row in result]
        for val in items:
            timestamp = int(val['timestamp'] / 1000) 
            readable = datetime.fromtimestamp(timestamp).isoformat()
            response['data']['entries'].append({
                'density': val['density'],
                'average_density': val['average'],
                'timestamp': timestamp,
                'date': readable
            })       
      
        if prevPage > 0:
            prevPageUrl = root + "history/" + str(sector_id) + "?page=" + str(prevPage) + startUrl + endUrl + intervalUrl + limitUrl
            response['pagination']['prev_url'] = prevPageUrl   
        
        if page * pageLimit < int(limit) and len(items) >= pageLimit:             
            nextPageUrl = root + "history/" + str(sector_id) + "?page=" + str(nextPage) + startUrl + endUrl + intervalUrl + limitUrl
            response['pagination']['next_url'] = nextPageUrl
        response['metadata'] = {
            'status_code': 200,
            'current_timestamp': int(time.time()),
            'current_date': datetime.fromtimestamp(int(time.time())).isoformat()
        }
        return response

#Class for finding nearest sectors
class Distance(Resource):
    def options(self, sector_id):
        return '', 204, {'Allow': 'GET, OPTIONS'}
    def get(self):
        args = parser.parse_args()

        if not args['latitude'] or not args['longitude']:
            abort(400, message="Need both latitude and longitude parameters")

        if args['range']:
            rangeKm = args['range']
        else:
            rangeKm = 1
        response = {}
        response['data'] = []
        average = []

        idResult = dbQuery('SELECT id FROM sector')
        idItems = [dict(zip([key[0] for key in cur.description], row)) for row in idResult]
        for val in idItems:
            average.append({
                'id': val['id'],
                'lat': float(0),
                'long': float(0),
                'count': 0,
                'density': ''                
            })

        result = dbQuery('SELECT entry.density, entry.cluster_id, coordinate.latitude, coordinate.longtitude FROM entry INNER JOIN coordinate ON coordinate.sector_id = entry.cluster_id WHERE entry.timestamp = (SELECT MAX(entry.timestamp) FROM entry)  ORDER BY timestamp DESC')
        items = [dict(zip([key[0] for key in cur.description], row)) for row in result]
        for val in items:
            for i, ave in enumerate(average):
                if int(ave['id']) == int(val['cluster_id']):
                    average[i]['lat'] = float(average[i]['lat']) + float(val['latitude'])
                    average[i]['long'] = float(average[i]['long']) + float(val['longtitude'])
                    average[i]['count'] = int(average[i]['count'] + 1)
                    if not average[i]['density']:
                        average[i]['density'] = val['density']
        for i, ave in enumerate(average):
            average[i]['lat'] = float(round(Decimal(average[i]['lat'] / average[i]['count']), 6))
            average[i]['long'] = float(round(Decimal(average[i]['long'] / average[i]['count']), 6))     

            target = (average[i]['lat'], average[i]['long'])
            current = (float(args['latitude']), float(args['longitude']))
            distance = round(geodesic(target, current).km, 3)
            if int(distance * 1000) <= rangeKm:
                response['data'].append({
                    'sector_id': ave['id'],
                    'distance': distance,
                    'density': average[i]['density'],
                    'destination': {
                        'latitude': average[i]['lat'],
                        'longitude': average[i]['long']
                    }
                })
                
        if not response['data']:
            abort(404, message="No sectors found within range")
        response['metadata'] = {
            'status_code': 200,
            'current_timestamp': int(time.time()),
            'current_date': datetime.fromtimestamp(int(time.time())).isoformat()
        }
        return response

# Add resources to the API
api.add_resource(Sector, '/sector/<sector_id>')
api.add_resource(Sectors, '/sectors')
api.add_resource(History, '/history/<sector_id>')
api.add_resource(Distance, '/distance')

if __name__ == '__main__':
    app.run(debug=True)
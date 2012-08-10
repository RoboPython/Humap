from __future__ import with_statement
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
abort, render_template, flash
from contextlib import closing
import requests
from cgi import escape
import urllib
import json
#import python debugger for debugging
import pdb
import random
import pickle
from bs4 import BeautifulSoup
#keep everything neat and import the maths functs here
from math import radians, cos, sin, asin, sqrt, floor

CONFIG_LOCATION='settings'
DATABASE = '/home/mancub/Dev/maps/maps.db'
#DATABASE = '/home/adam/web/Humap/maps.db'
DEBUG = True
SECRET_KEY = 'Xc93lKE0dQ'
USERNAME = 'admin'
PASSWORD = 'yrs2012'

CACHE = True

"""
    @author Anthony Stansbridge <anthony@anthonystansbridge.co.uk>
    @author Adam Ferguson <fergie57@btinternet.com>
    @author George  <georgec204@gmail.com>
    @author Oliver <blastdoors666@gmail.com>

    @description Flask Bootstrap - See tutorial online (http://flask.pocoo.org/)

""" 
app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()

@app.route('/', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        request.form['to_address']
        request.form['from_address']
        directions_response = get_directions(request.form['from_address'], request.form['to_address'])
        if directions_response == False:
            return render_template('search.html')
        else:
            #randomly generate a filename
            file_name = 'file_name_'+str(int(floor(random.random() * 100000)))
            file_handler = open(file_name, 'w')
            pickle.dump(directions_response, file_handler)

            step_count = len(directions_response.get_steps())

            #calculate the minutes
            total_mins = directions_response.total_duration / 60
            #calculate the remaining seconds
            total_seconds = directions_response.total_duration % 60

            template_data = {
                'to_address': request.form['to_address'], 
                'from_address': request.form['from_address'],
                'directions_data':directions_response, 
                'step_count':step_count, 
                'counter':1,
                'total_mins': total_mins,
                'total_seconds': total_seconds
            }
            return render_template('results.html', template_data = template_data)
    else:
        return render_template('search.html')
"""
    @author Anthony Stansbridge <anthony@anthonystansbridge.co.uk>

    @description Returns the directions based upon the origin string and the destination string

    @params origin:string - The users current location, destination:string - The users destination

""" 
def get_directions(origin, destination):
    # escape the characters to construct the URL

    # if we're using cached requests, send em a dummy!
    if CACHE == True:
        file_name = 'file_name_37691'
        file_handler = open(file_name, 'r')
        unserialized_object = pickle.load(file_handler)
        return unserialized_object
    # get the real deal
    else:
        origin = escape(origin)
        destination = escape(destination)
        # call the google API
        api_call = requests.get('http://maps.googleapis.com/maps/api/directions/json?', params={'origin':origin, 'destination':destination, 'sensor':'false'})
        api_response = api_call.json
        # check the response from google and the status
        if api_response and api_response['status'] == 'OK':
            # parse the results into a new direction
            return Directions(api_response['routes'][0]['legs'][0])
        else:
            return False

"""
    @author Anthony Stansbridge <anthony@anthonystansbridge.co.uk>

    @description Returns a list of Point_of_interest Objects containing data that shows points of interest around the lat/long of the parameters

    @params lat:string/float - latitude coordinates, lng:string/float - longitude coordinates

""" 
def get_pois(lat, lng):
    # set the coordinates for the google API
    coordinates = str(lat) + ',' + str(lng)
    # request results from google
    api_call = requests.get('https://maps.googleapis.com/maps/api/place/search/json?', params={'key':'AIzaSyAKSwnpr9o51WUhFTxAwLzcTY-AeWG7aEs', 'location':coordinates, 'radius':'25', 'sensor':'false', 'types':'point_of_interest|establishment|restaurant|lodging|food|store|church|place_of_worship'})
    api_response = api_call.json
    points_of_interest = []
    if api_response and api_response['status'] == 'OK':
        # parse the results into points of interest
        for result in api_response['results']:
            #return poi classes
            points_of_interest.append(Point_of_interest(result))

        #get the pois from the DB and add to the list of POIs
        points_of_interest.extend(query_pois(lat, lng))
        #get any pois from culture grid and add to the list of POIs
        points_of_interest.extend(query_culturegrid(lat, lng))
        return points_of_interest
    else:
        # return False
        return False

"""
    @author Anthony Stansbridge <anthony@anthonystansbridge.co.uk>

    @description private _distance function is to be used with sqlite, it calculates the distance between lat and lng coordinates based upon the haversine formula

    @params origin_lat:float - latitude coordinate, origin_lng:float - longitude coordinate, dest_lat:float - latitude coordinate, dest_lng:float - longitude coordinate

    @extra this function is added to the sqlite connection upon searching for points of interest,
        reference: http://code.activestate.com/recipes/438802-adding-sqlite-sign-function/
""" 
def _distance(origin_lat, origin_lng, dest_lat, dest_lng):
    #turn coordinates to radians
    origin_lat, origin_lng, dest_lat, dest_lng  = map(radians, [origin_lng, origin_lat, dest_lng, dest_lat])

    #temp variables to clear up clutter for the individual haversine functions
    temp_lng = origin_lng - dest_lng
    temp_lat = origin_lat - dest_lat

    # haversine + cosine of latitude 1 * cosine of latitude 1 * haversine
    a = sin(temp_lat/2)**2 + cos(origin_lat) * cos(dest_lat) * sin(temp_lng/2)**2
    # arc sine (sin-1) of A - could multiply Earths radius here but splitting it up for clarity
    c = 2 * asin(sqrt(a))

    #Earths average radius by variable c then converting the km to meters
    meters = (6367.5 * c)*1000

    return meters

"""
    @author Anthony Stansbridge <anthony@anthonystansbridge.co.uk>

    @description Returns a list of Point_of_interest Objects containing data that is obtained from the database

    @params lat:string/float - latitude coordinates, lng:string/float - longitude coordinates, [optional]radius:int - radius around lat/lng to search for points of interest

    @extra Due to limitations with sqlite not having built in math functions, the _distance function has been created and ported for use within the query
""" 
def query_pois(lat, lng, radius = 25):
    g.db.create_function('distance', 4, _distance)
    result_set = g.db.execute('SELECT lat, lng, icon_location, name, category FROM points_of_interest WHERE distance(lat, lng, ?, ?) < '+str(radius), [lat, lng])
    points_of_interest = []
    for row in result_set.fetchall():
        # assign data to dictionary to format it correctly (should have thought about the structure better)
        pois = {
                    'geometry': { 
                        'location': {
                            'lat': row[0],
                            'lng': row[1]
                        }
                    },
                    'icon':row[2],
                    'name':row[3],
                    'types':row[4]
        }
        #add a new POI to the array
        points_of_interest.append(Point_of_interest(pois))
    return points_of_interest


"""
    @author Anthony Stansbridge <anthony@anthonystansbridge.co.uk>

    @description Returns data from culture grid giving us information on public entities

    @params lat:string/float - latitude coordinates, lng:string/float - longitude coordinates, [optional]radius:int - radius around lat/lng to search for points of interest

"""
def query_culturegrid(lat, lng, radius=25.0):
    radius = radius/1609.344
    culture_grid_url = 'http://www.culturegrid.org.uk/index/select/?q=%7b!spatial%20lat='+str(lat)+'%20long='+str(lng)+'%20radius='+str(radius)+'%20unit=miles%7d%20dcterms.isPartOf:MLAInstitutions&version=2.2&start=0&rows=10&indent=on&sort=geo_distance%20asc&wt=json'
    api_call = requests.get(culture_grid_url, timeout=80)
    api_response = api_call.json
    points_of_interest = []
    if api_response['responseHeader']['status'] == 0:
        for location in api_response['response']['docs']:
            #cant have an empty for
            if location.has_key('dc.title'):
                pois = {
                'geometry': { 
                    'location': {
                        'lat': location['lat'],
                        'lng': location['lng']
                    }
                },
                    'icon':'x',
                    'name':location['dc.title'][0],
                    'types':'x'
                }
                #add a new POI to the array
                points_of_interest.append(Point_of_interest(pois))

    return points_of_interest

"""
    @author Adam Ferguson <fergie57@btinternet.com>

    @description Translates the text input from Googles directions and adds a point of interest to the text helping the user navigate

    @params google_instr:string - Google input string, nearest_POI:Point_of_interest object - contains information about the point of interest

""" 
def nat_language_sim(google_instr,nearest_POI):
    natural_language_gen= [" near ",
                           " past ",
                           " approximate to ",
                           " close to ",
                           " you should pass ",
                           " you should see ",
                           " around "]
    if nearest_POI == False:
        return google_instr                  
    else:
        output_string = BeautifulSoup(google_instr)
        if output_string.div:
            output_string.div.decompose()
            return str(output_string) + "," + random.choice(natural_language_gen) + nearest_POI.name
        else:
            return google_instr + "," + random.choice(natural_language_gen) + nearest_POI.name

"""
    @author Anthony Stansbridge <anthony@anthonystansbridge.co.uk>

    @description Directions class which holds objects containing information required for the user to reach their destination from the starting location

    @params leg:dictionary/list - Returned from the single leg provided by Google Directions API

""" 
class Directions:
    def __init__(self, leg):
        self.this_leg = leg
        # get the distance in meters
        self.total_distance = self.this_leg['distance']['value']
        # get the duration in seconds
        self.total_duration = self.this_leg['duration']['value']
        # get the start coordinates
        self.start_location = self.this_leg['start_location']
        # get the end coordinates
        self.end_location = self.this_leg['end_location']
        self.steps = []
        # loop through all of the steps
        for api_step in self.this_leg['steps']:
            self.steps.append(Step(api_step))

    def get_steps(self, offset = False):

        if offset == False:
            return self.steps
        else:
            return self.steps[int(offset)]

"""
    @author Anthony Stansbridge <anthony@anthonystansbridge.co.uk>

    @description Step class which holds objects and data containing information required for the user to complete a step of their journey

    @params step_data:dictionary/list - Returned from the steps provided by the leg section (See Directions class) & Google Directions API

    @extra extra
""" 
class Step:
    def __init__(self, step_data):
        self.step_data = step_data
        # get the distance for this step in meters
        self.distance = self.step_data['distance']['value']
        # get the duration for this step in meters
        self.duration = self.step_data['duration']['value']
        # get the start location for this step
        self.start_location = Location_step(self.step_data['start_location']['lat'], self.step_data['start_location']['lng'])
        # get the end location for this step
        self.end_location = Location_step(self.step_data['end_location']['lat'], self.step_data['end_location']['lng'])

        #see if there are any POIs at the end location
        if self.end_location.pois and len(self.end_location.pois) > 0:
            in_poi = self.end_location.pois[0]
        else:
            in_poi = False

        # get the HTML instructions provided by google
        self.html_instructions = nat_language_sim(urllib.unquote(self.step_data['html_instructions']), in_poi)

"""
    @author Anthony Stansbridge <anthony@anthonystansbridge.co.uk>

    @description Location_step class which holds the location of either the start of the step or the end of the step, contains information regarding points of interest around the provided lat/lng coordinates

    @params lat:string/float - Latitude of the start/end of the step, lng:string/float - Longitude of the start/end of the step

""" 
class Location_step:
    def __init__(self, lat, lng):
        #get the latitude
        self.lat = lat
        #get the longitude
        self.lng = lng
        #get and format the points of interest
        self.pois = get_pois(self.lat, self.lng)

    def location_pois(self, offset = False):
        if self.pois == False:
            return []
        else:
            if offset == False:
                return self.pois
            else:
                return self.pois[int(offset)]

"""
    @author Anthony Stansbridge <anthony@anthonystansbridge.co.uk>

    @description Point_of_interest class holds information regarding a point of interest in a journey

    @params poi:dictionary - Contains information about the point of interest

""" 
class Point_of_interest:
    def __init__(self, poi):
        self.lat = poi['geometry']['location']['lat']
        self.lng = poi['geometry']['location']['lng']
        self.icon = poi['icon']
        self.name = poi['name']
        self.category = poi['types']

        #self.rating = poi['rating']

"""
    @description Go-Go-Gadget

""" 
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

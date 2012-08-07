import requests
from cgi import escape
import urllib
import json

def get_directions(origin, destination):
	# escape the characters to construct the URL
	origin = escape(origin)
	destination = escape(destination)
	# call the google API
	api_call = requests.get('http://maps.googleapis.com/maps/api/directions/json?', params={'origin':origin, 'destination':destination, 'sensor':'false'})
	api_response = json.loads(api_call.text)
	# check the response from google and the status
	if api_response and api_response['status'] == 'OK':
		# parse the results into a new direction
		return Directions(api_response['routes'][0]['legs'][0])
	else:
		return False

def get_pois(lat, lng):
	# set the coordinates for the google API
	coordinates = str(lat) + ',' + str(lng)
	# request results from google
	api_call = requests.get('https://maps.googleapis.com/maps/api/place/search/json?', params={'key':'AIzaSyAnVJ_cHu9OIst66_nUVobcevGeK9YBH78', 'location':coordinates, 'radius':'10', 'sensor':'false', 'types':'point_of_interest|establishment|restaurant|lodging|food|store|church|place_of_worship'})
	api_response = json.loads(api_call.text)
	points_of_interest = []
	if api_response and api_response['status'] == 'OK':
		# parse the results into points of interest
		for result in api_response['results']:
			#return poi classes
			points_of_interest.append(Point_of_interest(result))
		return points_of_interest
	else:
		# return False
		return points_of_interest



#direction class
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

class Step:
	def __init__(self, step_data):
		self.step_data = step_data
		# get the HTML instructions provided by google
		self.html_instructions = urllib.unquote(self.step_data['html_instructions'])
		# get the distance for this step in meters
		self.distance = self.step_data['distance']['value']
		# get the duration for this step in meters
		self.duration = self.step_data['duration']['value']
		# get the start location for this step
		self.start_location = Location_step(self.step_data['start_location']['lat'], self.step_data['start_location']['lng'])
		# get the end location for this step
		self.end_location = Location_step(self.step_data['end_location']['lat'], self.step_data['end_location']['lng'])

class Location_step:
	def __init__(self, lat, lng):
		#get the latitude
		self.lat = lat
		#get the longitude
		self.lng = lng
		#get and format the points of interest
		self.pois = get_pois(self.lat, self.lng)

	def location_pois(self, offset = False):
		if offset == False:
			return self.pois
		else:
			return self.pois[int(offset)]

class Point_of_interest:
	def __init__(self, poi):
		self.lat = poi['geometry']['location']['lat']
		self.lng = poi['geometry']['location']['lng']
		self.icon = poi['icon']
		self.name = poi['name']
		self.category = poi['types']
		#self.rating = poi['rating']


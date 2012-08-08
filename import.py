import sqlite3
import csv
import os

#PATHS = 'C:\Users\Adam\Dropbox\YRS\Hu-Map POI Dumps\\'
PATHS = '/home/mancub/Dev/maps/poi_files/'
DATABASE = '/home/mancub/Dev/maps/maps.db'

db = sqlite3.connect(DATABASE)


def insert_poi(lat, lng, icon, title, category):
    db.execute('INSERT INTO points_of_interest ( lat, lng, icon_location, name, category ) values ( ?, ?, ?, ?, ? )', [lat, lng, icon, title, category])

def get_poi():
	data = db.execute('SELECT * FROM points_of_interest LIMIT 20')
	for row in data.fetchall():
		print row

"""
	@author Adam Ferguson <adam@fergie57@btinternet.com>

	@description Parses POI files contained in the directory set above and adds it to the SQLite database

""" 
def process_files():

	location_filename=[]

	for dirname, dirnames, filenames in os.walk(PATHS):
	    for filename in filenames:
			location_filename.append(filename)

	csv_list = []
	for csv_file in location_filename:
		locations = csv.reader(open(PATHS+csv_file, 'r+'), delimiter=",", quotechar='|')
		for row in locations:
			place_record = {	'lat':row[1],
								'lng':row[0],
								'type':csv_file[:-4]
							}
								
			csv_list.append(place_record)

	return csv_list

"""
	@author Adam Ferguson <fergie57@btinternet.com>

	@description Inserts the POI data from the CSV files

""" 
def process_formatted_list(formatted_list):
	for row in formatted_list:
		insert_poi(row['lat'],row['lng'], 'x', str(row['type']), 'x')

	db.commit()

#formatted_list = process_files()

#process_formatted_list(formatted_list)

#get_poi()
	


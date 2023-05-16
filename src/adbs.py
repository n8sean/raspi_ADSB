
from opensky_api import OpenSkyApi
import pandas as pd
import os
import time
# import yaml
from datetime import datetime
from os.path import exists
import config


## GLOBAL VARs ----
single_ping = False
use_credentials = False
process_minutes = 5*60		# total minutes to ping the airspace: (hours*minutes)
ping_rate = 30				# ping every X seconds

os.chdir(os.path.dirname(__file__))	# set working dorectory


## FUNCTIONS ----
def get_states(df_airspace, states, col_names):
	list_callsign = []
	list_altitude = []

	sky_objects_count = 0
	if not states==None:
		print('Asserting airspace objects to DB...')
		for s in states.states:
			dict_vals = [s.icao24, s.callsign, s.origin_country, s.time_position,
						s.last_contact, s.latitude, s.longitude, s.geo_altitude,
						s.baro_altitude, s.on_ground, s.velocity, s.true_track,
						s.vertical_rate, s.sensors, s.squawk, s.spi,
						s.position_source
						]
			dict = {col_names[0]:dict_vals[0], col_names[1]:dict_vals[1], col_names[2]:dict_vals[2], col_names[3]:dict_vals[3], 
					col_names[4]:dict_vals[4], col_names[5]:dict_vals[5], col_names[6]:dict_vals[6], col_names[7]:dict_vals[7], 
					col_names[8]:dict_vals[8], col_names[9]:dict_vals[9], col_names[10]:dict_vals[10], col_names[11]:dict_vals[11], 
					col_names[12]:dict_vals[12], col_names[13]:dict_vals[13], col_names[14]:dict_vals[14], col_names[15]:dict_vals[15], 
					col_names[16]:dict_vals[16]
					}

			df_dict = pd.DataFrame.from_dict(list(dict.items())).T
			colu_names = list(df_dict.loc[0,:])
			df_dict.columns=colu_names
			df_dict.drop([0], axis=0, inplace=True)

			list_callsign.append(df_dict['callsign'].values[0])
			list_altitude.append(df_dict['geo_altitude'].values[0])

			df_airspace = pd.concat([df_airspace, df_dict], axis=0, ignore_index=True)
			sky_objects_count += 1
		
		this_stamp = format(datetime.fromtimestamp(time.time()), '%T')
		print('\nUpdated: {}'.format(this_stamp))
		for i, j in zip(list_callsign, list_altitude):
			print('Callsign:\t{}\nAltitude\t{}\n---'.format(i, j))

		print('Total objects:', sky_objects_count)
		print('=====')
		return (df_airspace)
	else:
		print('Daily quota exceeded!')
		print('states:', states, '\n')

def save_to_csv(airspace):
	#save a file or append new records to it
	filename = '/airspace.csv'
	filepath = '/data' + filename
	# cwd = os.getcwd() #+ filepath
	cwd = os.path.dirname(os.getcwd())
	cwd = cwd + filepath
	
	if (exists(cwd)):
		mode = 'a'
		header=False
	else:
		mode = 'w'
		header=True

	airspace.to_csv(cwd, mode=mode, index=False, header=header)

## PROCESS DATA ----
# new dataFrame
col_names = ['icao24', 'callsign', 'origin_country', 'time_position', 'last_contact',
			'latitude', 'longitude', 'geo_altitude', 'baro_altitude', 'on_ground',
			'velocity', 'true_track', 'vertical_rate', 'sensors', 'squawk', 'spi',
			'position_source'
			]

## RETURN CREDENTIALS ----
with open('config.py', 'r') as file:
		# adsb_srvc = yaml.safe_load(file)
		username = config.adsb_srvc['user']
		password = config.adsb_srvc['password']


if (use_credentials==True):
	# api = OpenSkyApi(adsb_srvc['user'], adsb_srvc['password'])		# use credentials
	api = openSkyApi(username, password)
else:
	api = OpenSkyApi()

bbox = (47.6603, 47.7848, -122.5274, -122.1747)	# Lake City, WA geographical location
to_feet = 3.28084 #feet per meters

#ping the airspace
if (single_ping==True): 
	os.system('clear')
	print('Collecting airspace objects...')
	states = api.get_states(bbox=bbox)
	if not ((states.states==[] or states==None)):
		airspace = pd.DataFrame(columns=col_names)
		airspace = get_states(airspace, states, col_names)

		(airspace)

	else:
		print('Airspace is clear.')
elif (single_ping==False):
	os.system('clear')
	
	now_time = time.time()
	end_time = now_time + (process_minutes * 60)
	
	while (now_time<end_time):
		states = api.get_states(bbox=bbox)
		if not (states.states==[]):
			airspace = pd.DataFrame(columns=col_names)
			airspace = get_states(airspace, states, col_names)
			save_to_csv(airspace)
			sleep_timer = ping_rate	# seconds
		else:
			now_time_format = format(datetime.fromtimestamp(now_time), '%T')
			print('{}\tAirspace is clear.'.format(now_time_format))
			sleep_timer = ping_rate + 30	# seconds 
		
		time.sleep(sleep_timer)
		now_time = time.time()


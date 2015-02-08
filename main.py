import os
import json
import urllib
from flask import Flask
from sqlalchemy import *
from flask import request
import xml.dom.minidom as minidom
import xml.etree.ElementTree as et

app = Flask(__name__)
_ZILLOW_KEY = 'X1-ZWz1az1bupzbbf_7ucak'
_DEEP_SEARCH_API_BASE = 'http://www.zillow.com/webservice/GetDeepSearchResults.htm?zws-id=%s' % _ZILLOW_KEY

#####################################################################
# DATA INTERFACE
metadata = MetaData()
engine = create_engine('mysql+mysqldb://test:antigone@test.chkvtttzss4o.us-west-2.rds.amazonaws.com/test')
_LAND = Table('Zillow_Land', metadata, autoload=True, autoload_with=engine)
_RENTS = Table('Zillow_Rents', metadata, autoload=True, autoload_with=engine)
_ZHVI = Table('Zillow_Zhvi', metadata, autoload=True, autoload_with=engine)

def execute(engine,query):
	res = engine.execute(query)
	keys = res.keys()
	values = res.fetchall()
	return keys, values

def add_args_to_api_call(apiBase, apiArgs={}):
	apiCall = apiBase+'&'
	for k,v in apiArgs.iteritems():
		apiCall+=str(k) + '=' + str(v) + '&'
	return apiCall[0:-1]

#####################################################################

@app.route("/")
def main():
	return "Hello World!"

@app.route("/land_data")
def land_data():
	query = select([_LAND.c.Price,
		_LAND.c.Latitude,
		_LAND.c.Longitude,
		_LAND.c.City,
		_LAND.c.State,
		_LAND.c.Neighborhood])
	keys,values = execute(engine,query)
	data = [dict(zip(keys,x)) for x in values]
	return json.dumps(data)

@app.route("/land_main")
def land_main():
	try:
		address = request.args.get('address').replace('\s','%20')
		citystatezip = request.args.get('citystatezip')
	except:
		return "Not a valid API call."
	apiCall = add_args_to_api_call(_DEEP_SEARCH_API_BASE, {
		'citystatezip' : citystatezip,
		'address'      : address
		})
	data = urllib.urlopen(apiCall)
	data = minidom.parse(data)
	# get relevant data
	relevantData = {}
	for f in ['citystatezip','address','lotSizeSqFt']:
		relevantData[f] = data.getElementsByTagName(f)[0].firstChild.nodeValue
	return json.dumps(relevantData)

if __name__ == "__main__":
	app.debug=True
	app.run(host='0.0.0.0')
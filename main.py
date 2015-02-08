import os
import json
import urllib
from math import floor
from flask import Flask
from sqlalchemy import *
from flask import request
import xml.dom.minidom as minidom
import xml.etree.ElementTree as et

app = Flask(__name__)
_ZILLOW_KEY = 'X1-ZWz1az1bupzbbf_7ucak'
_DEEP_SEARCH_API_BASE = 'http://www.zillow.com/webservice/GetDeepSearchResults.htm?zws-id=%s' % _ZILLOW_KEY

# BUSINESS ASSUMPTIONS
# TODO: 
_CONSTRUCTION_PRICE_PER_SQ_FT = 150.
_USABLE_LAND_PERCENTAGE = 0.80
_ARCHITECT_COST_PERCENTAGE = 0.08
_ADDITIONAL_FLAT_FEES = 200000.
_AVERAGE_UNIT_SIZE = 700.
_OPERATING_MARGIN = 0.60
_CAP_RATE_SCHEDULE = {
	1000000 : 0.05,
	2000000 : 0.07,
	3000000 : 0.08,
	4000000 : 0.085,
	5000000 : 0.09,
	10000000 : 0.10,
	20000000 : 0.15,
	40000000 : 0.20
}

#####################################################################
# DATA INTERFACE
metadata = MetaData()
engine = create_engine('mysql+mysqldb://test:antigone@test.chkvtttzss4o.us-west-2.rds.amazonaws.com/test')
_LAND = Table('Zillow_Land', metadata, autoload=True, autoload_with=engine)
_RENTS = Table('Zillow_Rents', metadata, autoload=True, autoload_with=engine)
_ZHVI = Table('Zillow_Zhvi', metadata, autoload=True, autoload_with=engine)
_FORECASTS = Table('Zillow_RentForecasts', metadata, autoload=True, autoload_with=engine)

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

@app.route("/")
def main():
	return "Hello World!"

@app.route("/get_land_data_for_map")
def get_land_data_for_map():
	query = select([_LAND.c.Price,
		_LAND.c.Latitude,
		_LAND.c.Longitude,
		_LAND.c.City,
		_LAND.c.State,
		_LAND.c.Neighborhood])
	keys,values = execute(engine,query)
	data = [dict(zip(keys,x)) for x in values]
	return "callback(" + json.dumps(data) + ")"

@app.route("/get_land_data_for_fold")
def get_land_data_for_fold():
	try:
		price = float(request.args.get('price'))
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
	relevantData['neighborhood'] = data.getElementsByTagName('region')[0].getAttribute('name')
	relevantData['price'] = price
	return "callback(" + json.dumps(relevantData) + ")"

#########################################################################
# COMPUTE INTERFACE

@app.route("/compute_construction_cost_and_rois")
def compute_construction_cost_and_rois():
	try:
		price = float(request.args.get('price'))
		region = request.args.get('region')
		floors = float(request.args.get('floors'))
		lotSizeSqFt = float(request.args.get('lotSizeSqFt'))
	except:
		return "Not a valid API call."
	# compute construction cost
	totalSqFt = lotSizeSqFt*floors
	usableSqFt = totalSqFt*_USABLE_LAND_PERCENTAGE
	units = floor(usableSqFt/_AVERAGE_UNIT_SIZE)
	constructionCost = totalSqFt*_CONSTRUCTION_PRICE_PER_SQ_FT*(1+_ARCHITECT_COST_PERCENTAGE) + _ADDITIONAL_FLAT_FEES
	
	# compute current, 5yr and 10yr rent schedule
	rentQuery = select([_FORECASTS.c.get('Date'),_FORECASTS.c.get('Value')]).where(_FORECASTS.c.get('Region') == region)
	keys, rents = execute(engine, rentQuery)
	# set guardrails!!!!!
	for r in rents:
		rentForecastDate = r[0]
		guardrailsOnRent = lambda x: max(min(float(x),5),1)
		cappedRent = guardrailsOnRent(r[1])
		if rentForecastDate == "2014-11-01":
			netRentCurrent = cappedRent*usableSqFt*_OPERATING_MARGIN*12
		elif rentForecastDate == "2015-11-01":
			netRentIn1Year = cappedRent*usableSqFt*_OPERATING_MARGIN*12
		elif rentForecastDate == "2019-11-01":
			netRentIn5Year = cappedRent*usableSqFt*_OPERATING_MARGIN*12
		elif rentForecastDate == "2024-11-01":
			netRentIn10Year = cappedRent*usableSqFt*_OPERATING_MARGIN*12
	
	# compute current, 5yr and 10yr property appreciation schedule
	closestConstructionCost = floor(int(min([abs(x-constructionCost) for x in _CAP_RATE_SCHEDULE.keys()])+constructionCost)/1000000)*1000000
	capRate = _CAP_RATE_SCHEDULE[closestConstructionCost]
	pvCurrent = netRentCurrent / capRate
	homeQuery = select([_ZHVI.c.get('Yo Y'),_ZHVI.c.get('5 Year'),_ZHVI.c.get('10 Year')]).where(_ZHVI.c.get('Region Name') == region)
	keys, homeGrowthRates = execute(engine, homeQuery)
	gr1Year, gr5Years, gr10Years = [float(x) for x in homeGrowthRates[0]]
	pv1Year = pvCurrent*(1+gr1Year)**1
	pv5Years = pvCurrent*(1+gr5Years)**5
	pv10Years = pvCurrent*(1+gr10Years)**10

	# compute 5yr and 10yr roi
	totalReturn1Year = 1.+(netRentCurrent*1.+pv1Year)/(price+constructionCost)
	totalReturn5Year = 1.+(netRentIn5Year*5.+pv5Years)/(price+constructionCost)
	totalReturn10Year = 1.+(netRentIn10Year*10.+pv10Years)/(price+constructionCost)
	annualizedROI1Year  = totalReturn1Year - 1
	annualizedROI5Year  = ((1. + totalReturn5Year)**(1./5.))-1.
	annualizedROI10Year = ((1. + totalReturn10Year)**(1./10.))-1.

	return 'callback(' + json.dumps({
		'annualizedReturns' : [annualizedROI1Year, annualizedROI5Year, annualizedROI10Year],
		'netRents' : [netRentCurrent, netRentIn1Year, netRentIn5Year, netRentIn10Year],
		'growthRates' : [gr1Year, gr5Years, gr10Years],
		'totalReturns' : [totalReturn1Year, totalReturn5Year, totalReturn10Year],
		'propertyValues' : [pvCurrent, pv1Year, pv5Years, pv10Years],
		'constructionCost' : constructionCost,
		'units' : units
	}) + ')'


#########################################################################
# ENTRY POINT
if __name__ == "__main__":
	app.debug=True
	app.run(host='0.0.0.0')
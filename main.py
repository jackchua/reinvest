import os
import json
from flask import Flask
from sqlalchemy import *

app = Flask(__name__)

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
	return "Get land investment data."

if __name__ == "__main__":
	app.debug=True
	app.run(host='0.0.0.0')
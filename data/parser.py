#!/usr/bin/env python

#
# json parser for zillow map metadata
#

import json
import urllib
import random
import re
import time
import mysql

_ZILLOW_KEY='X1-ZWz1az1bupzbbf_7ucak'

def parse_map_data(inputPropertiesFile, outputFile):
	with open(inputPropertiesFile) as inputFile:
		data = json.loads(inputFile.readlines()[0])
		properties = data['map']['properties']
		data = []
	for p in properties:
	    p_id, latitude, longitude, value = p[0:4]
		# save data into csv
	    apiBaseCall='http://www.zillow.com/homes/for_sale/land_type/%s_zpid' % (p_id)
	    urlData = urllib.urlopen(apiBaseCall).readlines()
	    pData = [x for x in urlData if x.find('setCustomVar')!=-1]
	    pData = [re.sub(r'[^A-Za-z0-9\,\s]+','',x).strip() for x in pData]
	    pData = [x for x in pData if len(x.split(', '))==4]
	    pData = [x.split(', ') for x in pData]
	    pData = {x[2] : x[3] for x in pData}
	    pData['Price'] = pData['Price'].replace(',','')+','
	    pData['Latitude'] = str(latitude)+','
	    pData['Longitude'] = str(longitude)+','
	    data.append(pData)
			
	# write data into csv
	with open(outputFile, 'w') as outputFile:
		# write col names
		outputFile.write(','.join(data[0].keys())+'\n')
		# write data
		for line in data:
			outputFile.write(''.join([str(x) for x in line.values()])+'\n')

if __name__ == '__main__':
	parse_map_data('data/LandForSale.json', 'data/output_LandForSale.csv')

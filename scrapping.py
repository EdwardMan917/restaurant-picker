import json
import logging

import requests
import os
from oslash import Left, Right
from oslash.either import Either
from pymongo import MongoClient
from requests import Response


def get_json_data(data: str):
	try:
		return json.loads(data)
	except:
		return 'JSON_CONVERSION_ERROR'


def get_nested_value(source: dict, keys: [str]):
	for key in keys:
		value = source.get(key)
		if not value:
			return
		if isinstance(value, dict):
			source = value
		else:
			return value
	return value


def create_record(location_id: str, location: str):
	
	def fetch_restaurants(ctx: dict):
		resp: dict = requests.get(
			os.getenv("POI_URL"),
			params={
				"uiLang":"zh",
				"uiCity":"hongkong",
				"page":ctx.get('page_num'),
				"districtId":ctx.get('location_id')
			},
			headers={
				"User-Agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Mobile Safari/537.36"
			}
		).__dict__
		status_code = resp.get('status_code')
		if status_code < 400:
			return Right(dict(ctx,resp=resp))
		else:
			return Left(dict(ctx, error_msg=f'Received http response status code: {str(status_code)}'))

	def get_content(ctx: dict):
		data = get_nested_value(ctx, ['resp', '_content'])
		if data:
			return Right(dict(ctx, content=data.decode('utf-8')))
		else:
			return Left(dict(ctx, error_msg='Response has no content'))
	
	def extract_results(ctx: dict):	
		data = get_json_data(ctx.get('content'))
		if not isinstance(data, dict):
			return Left(dict(ctx, error_msg=data))
		restaurants = get_nested_value(data, ['searchResult', 'paginationResult', 'results'])
		if not restaurants:
			return Left(dict(ctx, error_msg='Empty restaurants list'))
		return Right(dict(ctx, restaurants=restaurants))

	def parse_info(ctx: dict):
		records = list()
		for res in ctx.get('restaurants'):
			info = dict(
				poi_id=res.get('poiId'),
				name=res.get('name'),
				district=get_nested_value(res, ['district', 'name']),
				address=res.get('address'),
				price=res.get('priceUI'),
				photo_url=get_nested_value(res, ['doorPhoto', 'url']),
				geolocaton=[res.get('mapLatitude'), res.get('mapLongitude')],
				phones=res.get('phones'),
				dishes=list(),
				categories=list(),
				scores=dict(),
			)

			categories = res.get('categories')
			if categories:
				info['categories'] = [cat.get('name') for cat in categories]
			
			info['scores'] = {
				'smile': res.get('scoreSmile'),
				'cry': res.get('scoreCry')
			}

			tags = res.get('tags')
			if len(tags) > 0:
				for tag in tags:
					info['dishes'].append(tag['name'])

			info['open_hours'] = res.get('poiHours')

			records.append(info)
		return Right(dict(ctx, records=records))		

	
	def save_to_db(collection, records: [dict]):
		collection.insert_many(records)
		return

	try:
		client = MongoClient(os.getenv("MONGO_URL"))
		db = client['restaurants']
		collection = db[location]
		for page_num in range(1,19):
			result = Right(dict(page_num=page_num, location_id=location_id)) | \
				fetch_restaurants | get_content | extract_results | parse_info
			
			if isinstance(result, Right):
				save_to_db(collection, result.value.get('records'))
				print(f'{str(page_num)}-----OK!')
			else:
				client.close()
				print(f'{str(page_num)}-----FAILED!')
				error_code = result.value.get('error_code')
				print(f'Error: {error_code}')
				raise Exception("Record Creation Failed")
		client.close()
	except Exception as e:
		print(e)
		print('Error occured when creating record')
		


if __name__ == '__main__':
	with open('locations.json') as json_file:
		locations = json.load(json_file)
		for location in locations:
			print(location)
			create_record(
				locations[location].get('location_id'), 
				location
			)

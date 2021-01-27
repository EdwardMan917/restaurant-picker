import logging
import os
from dataclasses import dataclass
from random import choice

import requests
from oslash import Left, Right
from oslash.either import Either
from pymongo import MongoClient as Cli

from settings import LOCATIONS


@dataclass
class PoiR:
    poi: dict = None
    error_code: str = None

@dataclass
class StatusR:
    status_data: dict = None
    error_code: str = None


def get_restaurant(location: str=None):

    def create_db_conn(ctx: dict) -> Either:
        try:
            conn = Cli(os.getenv('MONGO_URL'))
            db = conn['restaurants']
            return Right(dict(ctx, db=db))
        except Exception as e:
            print(e)
            return Left(dict(ctx ,error_code='DB_CONNECTION_ERROR'))

    def get_location(ctx: dict) -> Right:
        if not ctx.get('location'):
            return Right(dict(ctx, location=choice(LOCATIONS)))
        return Right(ctx)

    def get_collection(ctx: dict) -> Either:
        db = ctx.get('db')
        location = ctx.get('location')
        collections = db.list_collection_names()
        if location in collections:
            return Right(dict(ctx, collection=db[location]))
        return Left(dict(ctx, error_code='COLLECTION_NOT_FOUND'))

    def pick_poi(ctx: dict) -> Right:
        collection = ctx.get('collection')
        pipeline = [{"$sample":dict(size=1)}]
        poi = list(collection.aggregate(pipeline))[0]
        poi['_id'] = str(poi['_id']) 
        return Right(dict(ctx, poi=poi))


    try:
        ctx = Right(dict(location=location))
        result: Either = ctx | create_db_conn | get_location | get_collection | pick_poi
        
        if isinstance(result, Right):
            return PoiR(poi=result.value.get('poi')).__dict__
        return PoiR(error_code=result.value.get('error_code')).__dict__

    except Exception as e:
        print(e)
        return PoiR(error_code='INTERNAL_SERVER_ERROR').__dict__


def get_status(poi_id: str) -> Either:
    
    def check_status(ctx: dict) -> Either:
        response = requests.get(
            os.getenv('STATUS_URL'),
            params=dict(
                uiCity='hongkong',
                uiLang='zh',
                poiId=ctx.get('poi_id')
            ),
            headers={
				"User-Agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Mobile Safari/537.36"
			}
        )
        
        if not response.status_code == 200:
            return Left(dict(ctx, error_code='ERROR_FROM_OPENRICE'))
        
        return Right(dict(ctx, status_data=response.json()))

     
    try:
        ctx = Right(dict(poi_id=poi_id))
        result: Either = ctx | check_status
        
        if isinstance(result, Right):
            return StatusR(status_data=result.value.get('status_data')).__dict__
        return StatusR(error_code=result.value.get('error_code')).__dict__

    except Exception as e:
        print(e)
        return PoiR(error_code='INTERNAL_SERVER_ERROR').__dict__

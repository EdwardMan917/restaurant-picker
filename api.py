from urllib import parse

from flask_restful import Resource, request

from restaurant import get_restaurant, get_status
from statuscode import get_restaurant_response_code, get_status_response_code


def get_query_params(query_string: str) -> dict:
    if query_string:
        return dict(parse.parse_qsl(query_string))
    return dict()


class GetRestaurant(Resource):
    
    def get(self):
        data = get_query_params(request.environ.get('QUERY_STRING'))
        result: dict = get_restaurant(data.get('location'))
        status_code: int = get_restaurant_response_code(result)
        return result, status_code


class GetStatus(Resource):
    
    def get(self):
        data = get_query_params(request.environ.get('QUERY_STRING'))
        result: dict = get_status(data.get('poi_id'))
        status_code: int = get_status_response_code(result)
        return result, status_code

from flask import Flask
from flask_restful import Api
from flask_cors import CORS


from api import GetRestaurant, GetStatus

app = Flask(__name__)
cors = CORS(app, resources={r"/restaurant": {"origins": "*"}})
api = Api(app)


api.add_resource(GetRestaurant, '/restaurant') # GET
api.add_resource(GetStatus , '/restaurant/status') # GET

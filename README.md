Random Restaurant Picker
===

### Introduction
A flask app that pick restaurant for you randomly in Hong Kong. Data is retrieved from Openrice.

### How to start
Set up a MongoDB account and put Mongo connection url in .env as MONGO_URL. Run the script in `scrapping.py` to create collections and records in the database. 

Then run `./start.sh` to start the service.

### Endpoints

#### Get Restaurant   
**Method:** GET   
**URL:** http://127.0.0.1:5000/restaurant    
**Query Parameters:**    
1. location: String, optional. List of possible locations can be found in settings.py    
    
#### Get Restaurant Status
**Method:** GET   
**URL:** http://127.0.0.1:5000/restaurant/status      
**Query Parameters:**    
1. poi_id: String, required. The ID of a restaurant.   

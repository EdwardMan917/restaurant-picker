from flask import Flask, render_template
from flask_restful import Api
from flask_cors import CORS
import time
from restaurant import get_restaurant, get_status


from api import GetRestaurant, GetStatus

app = Flask(__name__)
cors = CORS(app, resources={r"/restaurant": {"origins": "*"}})
api = Api(app)

# RESTFul APIs
api.add_resource(GetRestaurant, '/restaurant') # GET
api.add_resource(GetStatus , '/restaurant/status') # GET


# Templates
@app.route('/home')
def home():
    poi = get_restaurant().get('poi')
    poi_url = 'https://www.openrice.com/zh/hongkong/r-slugstring-r' + str(poi.get('poi_id'))
    status = get_status(poi.get('poi_id')).get('status_data')
    return render_template(
        'main_page.html', 
        poi=poi,
        poi_url=poi_url,
        status=get_simple_status(status)
    )

@app.template_filter('autoversion')
def static_file_versioning(filename: str):
    version = str(int(time.time()))
    filename += f'?version={version}'
    return filename

def get_simple_status(status: dict) -> dict:
    today_hour = status.get('openingHourInfo', dict()).get('todayHour', dict())
    if not today_hour:
        return dict()
    times = list()
    for time in today_hour.get('times'):
        times.append(time.get('timeDisplayString'))
    simple_status = dict(
        open_now=status.get('openNow'),
        is_uncertain=today_hour.get('isUncertain'),
        times=','.join(times)
    )
    return simple_status
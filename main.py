from urls import app
from dotenv import load_dotenv
import os
load_dotenv(dotenv_path='./.env')




if __name__ == '__main__':
    app.debug = True
    app.run()
    # app.config['DATABASE_NAME'] = 'library.db'
    # host = os.environ.get('IP', '0.0.0.0')
    # port = int(os.environ.get('PORT', 8080))
    # app.run(host=host, port=port)
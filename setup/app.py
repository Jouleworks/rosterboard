import asyncio
import os
import subprocess
from pathlib import Path
from urllib.parse import urlparse

from asgiref.wsgi import WsgiToAsgi
from flask import Flask, request
from flask.templating import render_template

import psycopg2


BASE_DIR = Path(__file__).resolve().parent.parent
app = Flask(__name__)

async def shutdown():
    print("Waiting 3 seconds then shutting down...")
    await asyncio.sleep(3)
    exit(1)

@app.route('/')
def redirect_to_setup():
    return "<script>window.location.href='/setup/';</script>"

@app.route('/fetch/env/')
def fetch_env_variables():
    return {
        "POSTGRES_HOST": os.getenv('POSTGRES_HOST', 'rosterboard-db'),
        "POSTGRES_PORT": os.getenv('POSTGRES_PORT', '5432'),
        "POSTGRES_USER": os.getenv('POSTGRES_USER', 'rosterboard'),
        "POSTGRES_PASSWORD": os.getenv('POSTGRES_PASSWORD', 'rosterboard'),
        "POSTGRES_DB": os.getenv('POSTGRES_DB', 'rosterboard'),
        "REDIS_HOST": os.getenv('REDIS_HOST', 'rosterboard-redis'),
        "REDIS_PORT": os.getenv('REDIS_PORT', '6379'),
    }

@app.route('/setup/')
def setup_landing_page():
    return render_template('landing.html')

@app.route('/setup/wizard/')
def setup_wizard_page():
    return render_template('wizard.html')

@app.route('/test/database/', methods=['POST'])
def test_database():
    content = request.get_json()
    # Perform database operations here
    try:
        result = urlparse(content['database_url'])
        connection = psycopg2.connect(database=result.path[1:], user=result.username, password=result.password, host=result.hostname, port=result.port)
    except psycopg2.OperationalError:
        return {"result": False, "errors": ["Failed to connect to the database. Check Username/password/database details."]}
    except:
        return {"result": False, "errors": ["Failed to connect to the database. Unknown error. If this was not expected, please contact the contributors."]}
    cursor = connection.cursor()
    # Simulate a database operation
    return {"result": True, "errors": []}

@app.route('/install/', methods=['POST'])
async def install_application():
    content = request.get_json()
    # Perform installation operations here

    open(BASE_DIR / 'config' / 'settings.ini', 'w').write(content['config'])

    logs = ["Wrote ./config/settings.ini successfully."]

    subprocess.run(['python', BASE_DIR / 'manage.py', 'migrate'])

    os.environ.setdefault('DJANGO_SUPERUSER_EMAIL', content['superuser']['email'])
    os.environ.setdefault('DJANGO_SUPERUSER_PASSWORD', content['superuser']['password'])
    os.environ.setdefault('DJANGO_SUPERUSER_USERNAME', content['superuser']['username'])

    subprocess.run(['python', BASE_DIR / 'manage.py', 'createsuperuser', '--noinput'])

    asyncio.create_task(shutdown())

    return {"result": True, "logs": logs}

asgi_app = WsgiToAsgi(app)
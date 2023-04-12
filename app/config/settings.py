import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASES = {
    'default': {
        'ENGINE': 'sqlite:///{}'.format(os.path.join('/data', 'db.sqlite3')),
    },
    'test': {
        'ENGINE': 'sqlite:///{}'.format(os.path.join('/data', 'test_db.sqlite3')),
    }
}

SECRET_KEY = os.getenv('SECRET_KEY')

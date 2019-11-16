import os
import datetime
from dotenv import load_dotenv
load_dotenv()


class BaseConfig:

    SQLALCHEMY_DATABASE_URI = 'put ur link here'


    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_EXPIRATION_DELTA = datetime.timedelta(days=25)

    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL',
                                  'redis://localhost:6379')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND',
                                      'redis://localhost:6379')

    try:
        SECRET_KEY = open('../secret.txt').read()
    except:
        print('Warning: You need to generate secret.txt file to use api')


class ProductionConfig(BaseConfig):
    DEBUG = False
    Testing = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True

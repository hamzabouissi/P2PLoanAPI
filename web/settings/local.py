from .base import *


DEBUG = True

ALLOWED_HOSTS = ['142.93.98.17','localhost','p2ploan.taysircloud.com']


INSTALLED_APPS +=['corsheaders',]




DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'p2pdb',
        'USER': 'simple_user',
        'PASSWORD': '6842179530',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


CORS_ORIGIN_ALLOW_ALL = True

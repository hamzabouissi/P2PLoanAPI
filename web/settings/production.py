from base import *

DEBUG = False

ALLOWED_HOSTS = ['142.93.98.17','p2ploan.taysircloud.com']


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'db',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'db',
        'PORT': '5432',
    }
}
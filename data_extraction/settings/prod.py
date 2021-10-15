from data_extraction.settings.base import *

ALLOWED_HOSTS = ['data.barrenger.org']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', 
        'NAME': 'well_data',
        'USER': 'admin',
        'PASSWORD': 'Rn4100rn',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

MEDIA_ROOT = 'storage/'
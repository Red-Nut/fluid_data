from data_extraction.settings.base import *

ALLOWED_HOSTS = ['192.168.0.64', 'localhost']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', 
        'NAME': 'well_data',
        'USER': 'admin',
        'PASSWORD': 'Rn4100rn',
        'HOST': '192.168.0.64',
        'PORT': '3306',
    }
}

MEDIA_ROOT = 'W:/Well_Data/'
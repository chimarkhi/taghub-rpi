from django.conf import settings
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

db_conf = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'temphumidity.db'),
    }
}

settings.configure(
	DATABASES = db_conf,
	INSTALLED_APPS     = ( "app", )
)
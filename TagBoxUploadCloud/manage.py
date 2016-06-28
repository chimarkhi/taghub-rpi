#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from django.conf import settings

db_conf = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        SECRET_KEY = 'z&e##i@sf^c3%%)rfp$-=m-+=^8%weus1t7t8h-!+)*v6t8!y9',
        'NAME': 'temphumidity.db',
    }
}

settings.configure(
    DATABASES = db_conf,
    INSTALLED_APPS     = ( "app", )
)

# Calling django.setup() is required for “standalone” Django u usage
# https://docs.djangoproject.com/en/1.8/topics/settings/#calling-django-setup-is-required-for-standalone-django-usage
import django
django.setup()

if __name__ == '__main__':
    import sys
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

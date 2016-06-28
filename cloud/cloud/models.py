#!/usr/bin/env python

from django.db import models
from django.conf import settings

DJANGO_SETTINGS_MODULE = "cloud.settings"
settings.configure()

#MACID  DEVID  Temperature  Humidity tdate  ttime

class localData(models.Model):
    MACID = models.CharField(max_length=256)
    DEVID = models.CharField(max_length=256)
    Temperature = models.FloatField()
    Humidity = models.FloatField()
    tdate = models.DateTimeField()
    ttime = models.DateTimeField()
    def __str__(self):              # __unicode__ on Python 2
        return self.name

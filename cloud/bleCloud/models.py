from django.db import models
from django.conf import settings

# Create your models here.
DJANGO_SETTINGS_MODULE = "cloud.settings"
settings.configure()

class localData(models.Model):
    MACID = models.CharField(max_length=256)
    DEVID = models.CharField(max_length=256)
    Temperature = models.FloatField()
    Humidity = models.FloatField()
    tdate = models.DateTimeField()
    ttime = models.DateTimeField()
    def __str__(self):              # __unicode__ on Python 2
        return self.name
    class Meta:
        app_label = 'bleCloud'

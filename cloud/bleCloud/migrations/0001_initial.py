# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='localData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('MACID', models.CharField(max_length=256)),
                ('DEVID', models.CharField(max_length=256)),
                ('Temperature', models.FloatField()),
                ('Humidity', models.FloatField()),
                ('tdate', models.DateTimeField()),
                ('ttime', models.DateTimeField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('scriptmanager', '0002_scriptdetails'),
    ]

    operations = [
        migrations.AddField(
            model_name='scripts',
            name='user',
            field=models.ForeignKey(related_name='user_id', default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='scripts',
            name='data_file',
            field=models.FileField(upload_to=b'scripts', blank=True),
        ),
        migrations.AlterField(
            model_name='scripts',
            name='language',
            field=models.ForeignKey(blank=True, to='creation.Language', null=True),
        ),
    ]

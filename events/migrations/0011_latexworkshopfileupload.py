# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import events.models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0010_auto_20150813_1354'),
    ]

    operations = [
        migrations.CreateModel(
            name='LatexWorkshopFileUpload',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=254)),
                ('file_upload', models.FileField(upload_to=events.models.get_email_dir)),
            ],
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0012_tutorialresource_publish_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='Scripts',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.BooleanField(default=False)),
                ('data_file', models.FileField(upload_to=b'scripts')),
                ('language', models.ForeignKey(to='creation.Language')),
                ('tutorial', models.OneToOneField(to='creation.TutorialDetail')),
            ],
        ),
    ]

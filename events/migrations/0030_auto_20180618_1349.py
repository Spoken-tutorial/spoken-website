# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0012_tutorialresource_publish_at'),
        ('events', '0029_mumbaistudents'),
    ]

    operations = [
        migrations.CreateModel(
            name='MediaTestimonials',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('path', models.CharField(max_length=255)),
                ('user', models.CharField(max_length=255)),
                ('content', models.CharField(max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('foss', models.ForeignKey(to='creation.FossCategory')),
            ],
            options={
                'verbose_name': 'Media Testimonials',
                'verbose_name_plural': 'Media Testimonials',
            },
        ),
        migrations.AlterField(
            model_name='testimonials',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2018, 6, 18, 8, 19, 20, 294272, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]

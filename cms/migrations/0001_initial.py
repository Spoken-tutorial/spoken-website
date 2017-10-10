# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Standard Library
import datetime

# Third Party Stuff
from django.conf import settings
from django.db import migrations, models

# Spoken Tutorial Stuff
import cms.models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0019_auto_20170619_1515'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Block',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('body', models.TextField()),
                ('position', models.IntegerField()),
                ('visible', models.BooleanField()),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Block_Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('visible', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('body', models.TextField()),
                ('source_link', models.URLField(max_length=255, null=True, blank=True)),
                ('event_date', models.DateTimeField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Nav',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nav_title', models.CharField(max_length=255)),
                ('permalink', models.CharField(max_length=255)),
                ('position', models.IntegerField()),
                ('target_new', models.BooleanField()),
                ('visible', models.BooleanField()),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('slug', models.CharField(max_length=255)),
                ('picture', models.FileField(null=True, upload_to=cms.models.content_file_name, blank=True)),
                ('body', models.TextField()),
                ('url', models.URLField(null=True, blank=True)),
                ('url_title', models.CharField(max_length=200, null=True, blank=True)),
                ('weight', models.PositiveIntegerField(default=3)),
                ('created', models.DateTimeField()),
                ('updated', models.DateTimeField()),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'New',
            },
        ),
        migrations.CreateModel(
            name='NewsType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('slug', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('body', models.TextField()),
                ('bg_color', models.CharField(max_length=15, null=True, blank=True)),
                ('start_date', models.DateField(default=datetime.datetime.now)),
                ('expiry_date', models.DateField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('css', models.TextField(default=None, null=True, blank=True)),
                ('body', models.TextField()),
                ('js', models.TextField(default=None, null=True, blank=True)),
                ('cols', models.IntegerField(default=9)),
                ('permalink', models.CharField(unique=True, max_length=255)),
                ('formatting', models.BooleanField(default=True)),
                ('target_new', models.BooleanField()),
                ('visible', models.BooleanField()),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('confirmation_code', models.CharField(max_length=255)),
                ('street', models.CharField(max_length=255, null=True, blank=True)),
                ('country', models.CharField(max_length=255, null=True, blank=True)),
                ('pincode', models.PositiveIntegerField(null=True, blank=True)),
                ('phone', models.CharField(max_length=20, null=True)),
                ('picture', models.FileField(null=True, upload_to=cms.models.profile_picture, blank=True)),
                ('thumb', models.FileField(null=True, upload_to=cms.models.profile_picture_thumb, blank=True)),
                ('address', models.TextField(null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('city', models.ForeignKey(to='events.City', null=True)),
                ('district', models.ForeignKey(to='events.District', null=True)),
                ('location', models.ForeignKey(to='events.Location', null=True)),
                ('state', models.ForeignKey(to='events.State', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SiteFeedback',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('message', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='SubNav',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subnav_title', models.CharField(max_length=255)),
                ('permalink', models.CharField(max_length=255)),
                ('position', models.IntegerField()),
                ('target_new', models.BooleanField()),
                ('visible', models.BooleanField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('nav', models.ForeignKey(to='cms.Nav')),
            ],
        ),
        migrations.AddField(
            model_name='news',
            name='news_type',
            field=models.ForeignKey(to='cms.NewsType'),
        ),
        migrations.AddField(
            model_name='news',
            name='state',
            field=models.ForeignKey(blank=True, to='events.State', null=True),
        ),
        migrations.AddField(
            model_name='block',
            name='block_location',
            field=models.ForeignKey(to='cms.Block_Location'),
        ),
    ]

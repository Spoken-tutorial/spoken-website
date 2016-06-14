# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.conf import settings
import cms.models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Block',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
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
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('visible', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('body', models.TextField()),
                ('source_link', models.URLField(null=True, blank=True, max_length=255)),
                ('event_date', models.DateTimeField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Nav',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
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
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('slug', models.CharField(max_length=255)),
                ('picture', models.FileField(null=True, blank=True, upload_to=cms.models.content_file_name)),
                ('body', models.TextField()),
                ('url', models.URLField(null=True, blank=True)),
                ('url_title', models.CharField(null=True, blank=True, max_length=200)),
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
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('slug', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('body', models.TextField()),
                ('bg_color', models.CharField(null=True, blank=True, max_length=15)),
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
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('css', models.TextField(null=True, blank=True, default=None)),
                ('body', models.TextField()),
                ('js', models.TextField(null=True, blank=True, default=None)),
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
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('confirmation_code', models.CharField(max_length=255)),
                ('street', models.CharField(null=True, blank=True, max_length=255)),
                ('country', models.CharField(null=True, blank=True, max_length=255)),
                ('pincode', models.PositiveIntegerField(null=True, blank=True)),
                ('phone', models.CharField(null=True, max_length=20)),
                ('picture', models.FileField(null=True, blank=True, upload_to=cms.models.profile_picture)),
                ('thumb', models.FileField(null=True, blank=True, upload_to=cms.models.profile_picture_thumb)),
                ('address', models.TextField(null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('city', models.ForeignKey(null=True, to='events.City')),
                ('district', models.ForeignKey(null=True, to='events.District')),
                ('location', models.ForeignKey(null=True, to='events.Location')),
                ('state', models.ForeignKey(null=True, to='events.State')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SiteFeedback',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('message', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='SubNav',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
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
            field=models.ForeignKey(null=True, blank=True, to='events.State'),
        ),
        migrations.AddField(
            model_name='block',
            name='block_location',
            field=models.ForeignKey(to='cms.Block_Location'),
        ),
    ]

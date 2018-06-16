# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0017_auto_20180615_2003'),
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
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('foss', models.ForeignKey(to='creation.FossCategory')),
            ],
            options={
                'verbose_name': 'Media Testimonials',
                'verbose_name_plural': 'Media Testimonials',
            },
        ),
    ]

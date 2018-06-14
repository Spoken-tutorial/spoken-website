# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0012_tutorialresource_publish_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='VideoTestimonial',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('location', models.CharField(unique=True, max_length=255)),
                ('embed', models.BooleanField()),
                ('foss_id', models.ForeignKey(to='creation.FossCategory')),
            ],
            options={
                'verbose_name': 'Video Testimonial',
                'verbose_name_plural': 'Video Testimonials',
            },
        ),
    ]

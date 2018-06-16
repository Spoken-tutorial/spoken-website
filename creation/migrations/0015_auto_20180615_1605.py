# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0014_auto_20180613_1349'),
    ]

    operations = [
        migrations.CreateModel(
            name='MediaTestimonials',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('path', models.CharField(max_length=255)),
                ('user', models.CharField(max_length=255)),
                ('content', models.CharField(max_length=255)),
                ('foss', models.ForeignKey(to='creation.FossCategory')),
            ],
            options={
                'verbose_name': 'Media Testimonials',
                'verbose_name_plural': 'Media Testimonials',
            },
        ),
        migrations.RemoveField(
            model_name='videotestimonial',
            name='foss',
        ),
        migrations.DeleteModel(
            name='VideoTestimonial',
        ),
    ]

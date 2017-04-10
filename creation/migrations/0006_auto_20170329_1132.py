# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0005_auto_20170316_1241'),
    ]

    operations = [
        migrations.CreateModel(
            name='BrochureDocument',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('document', models.FileField(upload_to=b'brochures/')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'FOSS Brochure',
                'verbose_name_plural': 'FOSS Brochures',
            },
        ),
        migrations.AlterModelOptions(
            name='fosscategory',
            options={'ordering': ('foss',), 'verbose_name': 'FOSS', 'verbose_name_plural': 'FOSSes'},
        ),
        migrations.AlterModelOptions(
            name='fosssupercategory',
            options={'ordering': ('name',), 'verbose_name': 'FOSS Category', 'verbose_name_plural': 'FOSS Categories'},
        ),
        migrations.AddField(
            model_name='brochuredocument',
            name='foss_course',
            field=models.ForeignKey(to='creation.FossCategory'),
        ),
        migrations.AddField(
            model_name='brochuredocument',
            name='foss_language',
            field=models.ForeignKey(to='creation.Language'),
        ),
    ]

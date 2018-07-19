# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('creation', '0012_tutorialresource_publish_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentDetails',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=20, null=True)),
                ('amount', models.PositiveIntegerField()),
                ('purpose', models.CharField(max_length=20, null=True)),
                ('channelId', models.CharField(max_length=20, null=True)),
                ('status', models.PositiveIntegerField()),
                ('description', models.CharField(max_length=20, null=True)),
                ('userId', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

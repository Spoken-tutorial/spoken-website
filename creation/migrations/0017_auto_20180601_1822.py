# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('creation', '0016_tutorialresource_payment_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='TutorialPayment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.TimeField()),
                ('amount', models.PositiveIntegerField(default=0)),
                ('started', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AlterField(
            model_name='tutorialresource',
            name='payment_status',
            field=models.PositiveSmallIntegerField(default=4, choices=[(0, b'Payment Due'), (1, b'Payment Initiated'), (2, b'Payment Forwarded'), (3, b'Payment Done')]),
        ),
        migrations.AddField(
            model_name='tutorialpayment',
            name='tutorial',
            field=models.ManyToManyField(to='creation.TutorialResource'),
        ),
        migrations.AddField(
            model_name='tutorialpayment',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('creation', '0023_auto_20180604_2049'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentChallan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('challan_code', models.CharField(max_length=255, unique=True, null=True, blank=True)),
                ('amount', models.DecimalField(default=0, max_digits=9, decimal_places=2)),
                ('challan_doc', models.FileField(upload_to=b'')),
                ('challan_status', models.PositiveSmallIntegerField(default=1, choices=[(1, b'In Process'), (2, b'Forwarded'), (3, b'Completed'), (4, b'Confirmed')])),
            ],
        ),
        migrations.CreateModel(
            name='TutorialPayment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user_type', models.PositiveSmallIntegerField(default=3, choices=[(1, b'Script User'), (2, b'Video User'), (3, b'Script & Video User')])),
                ('duration', models.DurationField(default=0)),
                ('amount', models.DecimalField(default=0, max_digits=9, decimal_places=2)),
                ('payment_challan', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='creation.PaymentChallan', null=True)),
                ('tutorial_resource', models.ForeignKey(to='creation.TutorialResource')),
                ('user', models.ForeignKey(related_name='contributor', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='tutorialpayment',
            unique_together=set([('tutorial_resource', 'user')]),
        ),
    ]

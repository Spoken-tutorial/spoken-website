# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0038_auto_20180605_1813'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentHonorarium',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.DecimalField(default=0, max_digits=9, decimal_places=2)),
                ('code', models.CharField(max_length=20, editable=False)),
                ('doc', models.FileField(null=True, upload_to=b'', blank=True)),
                ('status', models.PositiveSmallIntegerField(default=1, choices=[(1, b'In Process'), (2, b'Forwarded'), (3, b'Completed'), (4, b'Confirmed')])),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='tutorialpayment',
            name='payment_challan',
        ),
        migrations.DeleteModel(
            name='PaymentChallan',
        ),
        migrations.AddField(
            model_name='tutorialpayment',
            name='payment_honorarium',
            field=models.ForeignKey(related_name='tutorials', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='creation.PaymentHonorarium', null=True),
        ),
    ]

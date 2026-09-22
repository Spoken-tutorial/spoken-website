# -*- coding: utf-8 -*-


from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('events', '0031_auto_20180720_1500'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentTransactionDetails',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('requestType', models.CharField(max_length=2)),
                ('amount', models.PositiveIntegerField()),
                ('reqId', models.CharField(max_length=50)),
                ('transId', models.CharField(max_length=100)),
                ('refNo', models.CharField(max_length=50)),
                ('provId', models.CharField(max_length=50)),
                ('status', models.CharField(max_length=2)),
                ('msg', models.CharField(max_length=100)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now_add=True)),
                ('paymentdetail', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='events.PaymentDetails')),
                ('userId', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

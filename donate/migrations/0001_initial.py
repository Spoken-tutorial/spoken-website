# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-06-15 07:17
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('creation', '0016_auto_20190918_0536'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CdFossLanguages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('foss', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='payment_foss', to='creation.FossCategory')),
                ('lang', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='creation.Language')),
            ],
        ),
        migrations.CreateModel(
            name='Payee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=255)),
                ('country', models.CharField(max_length=50, null=True)),
                ('state', models.CharField(max_length=50, null=True)),
                ('city', models.CharField(max_length=75, null=True)),
                ('gender', models.CharField(choices=[('', '--- Gender ---'), ('M', 'Male'), ('F', 'Female'), ('O', "Don't wish to disclose")], max_length=6)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('key', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('status', models.BooleanField(default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('expiry', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='payment_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PaymentTransaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requestType', models.CharField(max_length=2)),
                ('amount', models.CharField(max_length=20)),
                ('reqId', models.CharField(max_length=50)),
                ('transId', models.CharField(max_length=100)),
                ('refNo', models.CharField(max_length=50)),
                ('provId', models.CharField(max_length=50)),
                ('status', models.CharField(max_length=2)),
                ('msg', models.CharField(max_length=100)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('paymentdetail', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='payment_transaction', to='donate.Payee')),
            ],
        ),
        migrations.AddField(
            model_name='cdfosslanguages',
            name='payment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='donate.Payee'),
        ),
    ]
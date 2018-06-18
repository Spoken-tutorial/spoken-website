# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('creation', '0012_tutorialresource_publish_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentHonorarium',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.IntegerField(default=0)),
                ('code', models.CharField(max_length=20, editable=False)),
                ('doc', models.FileField(null=True, upload_to=b'', blank=True)),
                ('status', models.PositiveSmallIntegerField(default=1, choices=[(1, b'In Process'), (2, b'Forwarded'), (3, b'Completed'), (4, b'Confirmed')])),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='TutorialPayment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user_type', models.PositiveSmallIntegerField(default=3, choices=[(1, b'Script User'), (2, b'Video User'), (3, b'Script & Video User')])),
                ('seconds', models.PositiveIntegerField(default=0, help_text=b'Tutorial duration in seconds')),
                ('amount', models.IntegerField(default=0)),
                ('status', models.PositiveSmallIntegerField(default=1, choices=[(0, b'Payment Cancelled'), (1, b'Payment Due'), (2, b'Payment Initiated')])),
                ('payment_honorarium', models.ForeignKey(related_name='tutorials', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='creation.PaymentHonorarium', null=True)),
                ('tutorial_resource', models.ForeignKey(to='creation.TutorialResource')),
                ('user', models.ForeignKey(related_name='contributor', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='tutorialpayment',
            unique_together=set([('tutorial_resource', 'user')]),
        ),
    ]

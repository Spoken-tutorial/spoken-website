# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('events', '0030_accountexecutive'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentDetails',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.PositiveIntegerField()),
                ('purpose', models.CharField(max_length=20, null=True)),
                ('status', models.PositiveIntegerField()),
                ('description', models.CharField(max_length=20, null=True)),
                ('gstno', models.CharField(max_length=15, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now_add=True)),
                ('academic_id', models.ForeignKey(to='events.AcademicCenter')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('academic_year', models.PositiveIntegerField()),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='paymentdetails',
            unique_together=set([('academic_id','academic_year')]),
        ),
    ]

# -*- coding: utf-8 -*-


from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('events', '0029_mumbaistudents'),
    ]

    operations = [
        migrations.CreateModel(
            name='Accountexecutive',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.PositiveSmallIntegerField(default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('academic', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to='events.AcademicCenter', null=True)),
                ('appoved_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='accountexecutive_approved_by', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='accountexecutive', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

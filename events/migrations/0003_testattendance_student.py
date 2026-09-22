# -*- coding: utf-8 -*-


from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_auto_20150623_1627'),
    ]

    operations = [
        migrations.AddField(
            model_name='testattendance',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='events.Student', null=True),
        ),
    ]

# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_auto_20150623_1627'),
    ]

    operations = [
        migrations.AddField(
            model_name='testattendance',
            name='student',
            field=models.ForeignKey(to='events.Student', null=True, on_delete=models.deletion.PROTECT),
        ),
    ]

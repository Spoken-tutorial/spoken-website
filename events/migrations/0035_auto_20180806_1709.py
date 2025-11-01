# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0034_auto_20180803_1804'),
    ]

    operations = [
        migrations.AlterField(
            model_name='academiccenter',
            name='status',
            field=models.PositiveSmallIntegerField(),
        ),
    ]

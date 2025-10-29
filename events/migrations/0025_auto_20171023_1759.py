# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0024_auto_20171023_1705'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inductioninterest',
            name='city',
            field=models.CharField(max_length=100),
        ),
    ]

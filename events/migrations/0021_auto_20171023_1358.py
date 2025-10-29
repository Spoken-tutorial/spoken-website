# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0020_inductioninterest'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='inductioninterest',
            options={'ordering': ('city',)},
        ),
        migrations.AlterField(
            model_name='inductioninterest',
            name='age',
            field=models.CharField(max_length=20, choices=[(b'', b'-----'), (b'20to25', b'20 to 25 years'), (b'26to30', b'26 to 30 years'), (b'31to35', b'31 to 35 years'), (b'35andabove', b'Above 35 years')]),
        ),
    ]

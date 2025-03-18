# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0007_auto_20150731_1404'),
    ]

    operations = [
        migrations.AlterField(
            model_name='traininglivefeedback',
            name='training',
            field=models.ForeignKey(to='events.SingleTraining', on_delete=models.deletion.PROTECT),
        ),
    ]

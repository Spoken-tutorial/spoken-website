# -*- coding: utf-8 -*-


from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0007_auto_20150731_1404'),
    ]

    operations = [
        migrations.AlterField(
            model_name='traininglivefeedback',
            name='training',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='events.SingleTraining'),
        ),
    ]

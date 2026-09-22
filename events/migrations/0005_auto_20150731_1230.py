# -*- coding: utf-8 -*-


from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0004_auto_20150727_1632'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trainingfeedback',
            name='training',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='events.TrainingRequest'),
        ),
    ]

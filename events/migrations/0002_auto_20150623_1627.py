# -*- coding: utf-8 -*-


from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='test',
            name='training',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='events.TrainingRequest', null=True),
        ),
    ]

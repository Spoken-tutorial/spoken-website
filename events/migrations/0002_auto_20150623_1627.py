# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='test',
            name='training',
            field=models.ForeignKey(to='events.TrainingRequest', null=True, on_delete=models.deletion.PROTECT),
        ),
    ]

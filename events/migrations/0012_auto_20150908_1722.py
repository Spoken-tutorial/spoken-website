# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0011_latexworkshopfileupload'),
    ]

    operations = [
        migrations.AddField(
            model_name='singletraining',
            name='institution_type',
            field=models.ForeignKey(to='events.InstituteType', null=True, on_delete=models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='singletraining',
            name='state',
            field=models.ForeignKey(to='events.State', null=True, on_delete=models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='singletraining',
            name='total_participant_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='singletrainingattendance',
            name='foss',
            field=models.PositiveIntegerField(default=0),
        ),
    ]

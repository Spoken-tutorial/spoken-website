# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Third Party Stuff
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('certificate', '0003_auto_20160816_1148'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Dwsim_participant',
        ),
        migrations.DeleteModel(
            name='Esim_faculty',
        ),
        migrations.DeleteModel(
            name='eSim_WS',
        ),
        migrations.DeleteModel(
            name='Internship_participant',
        ),
        migrations.DeleteModel(
            name='OpenFOAM_Symposium_participant_2016',
        ),
        migrations.DeleteModel(
            name='OpenFOAM_Symposium_speaker_2016',
        ),
        migrations.DeleteModel(
            name='Osdag_WS',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='user',
        ),
        migrations.DeleteModel(
            name='Scilab_arduino',
        ),
        migrations.DeleteModel(
            name='Scilab_participant',
        ),
        migrations.DeleteModel(
            name='Scilab_speaker',
        ),
        migrations.DeleteModel(
            name='Scilab_workshop',
        ),
        migrations.DeleteModel(
            name='Scipy_participant',
        ),
        migrations.DeleteModel(
            name='Scipy_participant_2015',
        ),
        migrations.DeleteModel(
            name='Scipy_speaker',
        ),
        migrations.DeleteModel(
            name='Scipy_speaker_2015',
        ),
        migrations.DeleteModel(
            name='Tbc_freeeda',
        ),
        migrations.AlterField(
            model_name='drupal_camp',
            name='email',
            field=models.EmailField(max_length=254, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='drupal_ws',
            name='email',
            field=models.EmailField(max_length=254),
        ),
        migrations.DeleteModel(
            name='Profile',
        ),
    ]

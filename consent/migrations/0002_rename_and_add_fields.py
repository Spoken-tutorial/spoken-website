# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('consent', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ConsentVersion',
            new_name='Consent',
        ),
        migrations.AddField(
            model_name='consent',
            name='type',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.RemoveField(
            model_name='consent',
            name='file_name',
        ),
        migrations.AddField(
            model_name='consent',
            name='file',
            field=models.FileField(default='', upload_to='consent/'),
            preserve_default=False,
        ),
    ]

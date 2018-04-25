# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0012_tutorialresource_publish_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='rolerequest',
            name='language',
            field=models.ForeignKey(to='creation.Language', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='rolerequest',
            unique_together=set([('user', 'role_type', 'language')]),
        ),
    ]

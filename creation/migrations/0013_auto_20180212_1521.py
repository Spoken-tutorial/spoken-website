# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0012_rolerequest_language'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='rolerequest',
            unique_together=set([('user', 'role_type', 'language')]),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0035_remove_paymentchallan_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentchallan',
            name='code',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False),
        ),
    ]

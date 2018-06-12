# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0010_fosscategory_show_on_homepage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fosscategory',
            name='show_on_homepage',
            field=models.BooleanField(default=True, help_text=b'If unchecked, this foss will be displayed on series page, instead of home page'),
        ),
    ]

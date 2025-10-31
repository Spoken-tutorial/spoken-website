# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0009_auto_20170612_1543'),
    ]

    operations = [
        migrations.AddField(
            model_name='fosscategory',
            name='show_on_homepage',
            field=models.BooleanField(default=True),
        ),
    ]

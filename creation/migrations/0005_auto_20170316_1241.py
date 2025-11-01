# -*- coding: utf-8 -*-


# Third Party Stuff
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0004_fosscategory_category'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='fosscategory',
            options={'ordering': ('foss',), 'verbose_name_plural': 'FOSS'},
        ),
        migrations.AlterModelOptions(
            name='fosssupercategory',
            options={'ordering': ('name',), 'verbose_name_plural': 'FOSS Category'},
        ),
        migrations.RenameField(
            model_name='fosssupercategory',
            old_name='category',
            new_name='name',
        ),
    ]

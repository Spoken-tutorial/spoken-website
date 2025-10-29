# -*- coding: utf-8 -*-


# Third Party Stuff
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0003_fosssupercategory'),
    ]

    operations = [
        migrations.AddField(
            model_name='fosscategory',
            name='category',
            field=models.ManyToManyField(to='creation.FossSuperCategory', null=True),
        ),
    ]

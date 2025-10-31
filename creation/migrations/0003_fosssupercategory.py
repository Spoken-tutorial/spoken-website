# -*- coding: utf-8 -*-


# Third Party Stuff
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0002_auto_20170107_1845'),
    ]

    operations = [
        migrations.CreateModel(
            name='FossSuperCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('category', models.CharField(unique=True, max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ('category',),
                'verbose_name': 'FOSS Super Category',
            },
        ),
    ]

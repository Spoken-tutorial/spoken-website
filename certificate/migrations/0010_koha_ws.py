# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('certificate', '0009_itp_ws'),
    ]

    operations = [
        migrations.CreateModel(
            name='Koha_WS',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=254)),
                ('college', models.CharField(max_length=500)),
                ('purpose', models.CharField(default=b'KHW', max_length=10)),
            ],
        ),
    ]

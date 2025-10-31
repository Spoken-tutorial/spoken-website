# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0027_inductionfinallist'),
    ]

    operations = [
        migrations.CreateModel(
            name='Drupal2018_email',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=200)),
            ],
        ),
    ]

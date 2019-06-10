# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('certificate', '0007_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='FA_WS',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=254)),
                ('purpose', models.CharField(default=b'FAW', max_length=10)),
            ],
        ),
        migrations.AlterField(
            model_name='event',
            name='purpose',
            field=models.CharField(max_length=25, choices=[(b'DCM', b'DrupalCamp Mumbai'), (b'DRP', b'Drupal Workshop'), (b'FAW', b'FrontAccounting Workshop')]),
        ),
    ]

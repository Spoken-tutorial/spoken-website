# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0026_auto_20171023_1801'),
    ]

    operations = [
        migrations.CreateModel(
            name='InductionFinalList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=200)),
                ('code', models.CharField(default=None, max_length=255)),
                ('batch_code', models.PositiveIntegerField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('eoi_id', models.ForeignKey(default=None, to='events.InductionInterest', on_delete=models.deletion.PROTECT)),
            ],
        ),
    ]

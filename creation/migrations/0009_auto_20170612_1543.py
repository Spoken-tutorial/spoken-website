# -*- coding: utf-8 -*-


# Third Party Stuff
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0008_auto_20170605_1302'),
    ]

    operations = [
        migrations.CreateModel(
            name='BrochurePage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('page', models.FileField(upload_to=b'brochures/')),
                ('page_no', models.PositiveIntegerField()),
            ],
            options={
                'ordering': ('page_no',),
            },
        ),
        migrations.RemoveField(
            model_name='brochuredocument',
            name='document',
        ),
        migrations.AddField(
            model_name='brochurepage',
            name='brochure',
            field=models.ForeignKey(related_name='pages', to='creation.BrochureDocument'),
        ),
        migrations.AlterUniqueTogether(
            name='brochurepage',
            unique_together=set([('brochure', 'page_no')]),
        ),
    ]

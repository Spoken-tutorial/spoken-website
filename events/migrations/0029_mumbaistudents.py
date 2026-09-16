# -*- coding: utf-8 -*-


from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0028_drupal2018_email'),
    ]

    operations = [
        migrations.CreateModel(
            name='MumbaiStudents',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('bid', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='events.StudentBatch')),
                ('stuid', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='events.Student')),
            ],
        ),
    ]

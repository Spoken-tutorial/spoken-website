# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Third Party Stuff
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('certificate', '0002_certificate_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('answer', models.CharField(max_length=1000)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Drupal_camp',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('firstname', models.CharField(max_length=200)),
                ('lastname', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=75, null=True, blank=True)),
                ('attendance', models.PositiveSmallIntegerField(default=0)),
                ('role', models.CharField(max_length=100, null=True, blank=True)),
                ('purpose', models.CharField(default=b'DCM', max_length=10)),
                ('is_student', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Drupal_WS',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=75)),
                ('purpose', models.CharField(default=b'DRP', max_length=10)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Dwsim_participant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=75)),
                ('purpose', models.CharField(default=b'DWS', max_length=10)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Esim_faculty',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=75)),
                ('purpose', models.CharField(default=b'ESM', max_length=10)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='eSim_WS',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=75)),
                ('purpose', models.CharField(default=b'EWS', max_length=10)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FeedBack',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('email', models.CharField(max_length=100)),
                ('phone', models.CharField(max_length=20)),
                ('institution', models.CharField(max_length=100)),
                ('role', models.CharField(max_length=100)),
                ('address', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=50)),
                ('pin_number', models.CharField(max_length=10)),
                ('state', models.CharField(max_length=50)),
                ('purpose', models.CharField(default=b'SLC', max_length=10)),
                ('submitted', models.BooleanField(default=False)),
                ('answer', models.ManyToManyField(to='certificate.Answer')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Internship_participant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=75)),
                ('student_edu_detail', models.CharField(max_length=1000, null=True, blank=True)),
                ('student_institute_detail', models.CharField(max_length=2000, null=True, blank=True)),
                ('superviser_name_detail', models.CharField(max_length=2000, null=True, blank=True)),
                ('project_title', models.CharField(max_length=1000)),
                ('internship_project_duration', models.CharField(max_length=500, null=True, blank=True)),
                ('purpose', models.CharField(default=b'FIC', max_length=10)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OpenFOAM_Symposium_participant_2016',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, null=True, blank=True)),
                ('email', models.CharField(max_length=50, null=True, blank=True)),
                ('purpose', models.CharField(default=b'OFC', max_length=10)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OpenFOAM_Symposium_speaker_2016',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=300)),
                ('email', models.CharField(max_length=300)),
                ('paper', models.CharField(max_length=300)),
                ('purpose', models.CharField(default=b'OFC', max_length=10)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Osdag_WS',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=75)),
                ('purpose', models.CharField(default=b'OWS', max_length=10)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('question', models.CharField(max_length=500)),
                ('purpose', models.CharField(default=b'SLC', max_length=10)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Scilab_arduino',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=75)),
                ('purpose', models.CharField(default=b'SCA', max_length=10)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Scilab_participant',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('ticket_number', models.IntegerField(default=0)),
                ('name', models.CharField(max_length=50, null=True, blank=True)),
                ('email', models.CharField(max_length=50, null=True, blank=True)),
                ('ticket', models.CharField(max_length=50, null=True, blank=True)),
                ('date', models.CharField(max_length=50, null=True, blank=True)),
                ('order_id', models.IntegerField(default=0, null=True, blank=True)),
                ('purpose', models.CharField(default=b'SLC', max_length=10)),
                ('attendance', models.BooleanField(default=False)),
            ],
            options={
                'managed': True,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Scilab_speaker',
            fields=[
                ('id', models.IntegerField(default=0, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=300)),
                ('email', models.CharField(max_length=300)),
                ('ticket', models.CharField(max_length=100)),
                ('paper', models.CharField(max_length=300)),
                ('purpose', models.CharField(default=b'SLC', max_length=10)),
                ('attendance', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Scilab_workshop',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=300)),
                ('ticket_number', models.IntegerField(null=True)),
                ('email', models.CharField(max_length=300)),
                ('workshops', models.CharField(max_length=300)),
                ('purpose', models.CharField(default=b'SLC', max_length=10)),
                ('attendance', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Scipy_participant',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=50, null=True, blank=True)),
                ('email', models.CharField(max_length=50, null=True, blank=True)),
                ('purpose', models.CharField(default=b'SPC', max_length=10)),
                ('attendance', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Scipy_participant_2015',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, null=True, blank=True)),
                ('email', models.CharField(max_length=50, null=True, blank=True)),
                ('purpose', models.CharField(default=b'SPC', max_length=10)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Scipy_speaker',
            fields=[
                ('id', models.IntegerField(default=0, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=300)),
                ('email', models.CharField(max_length=300)),
                ('paper', models.CharField(max_length=300)),
                ('purpose', models.CharField(default=b'SPC', max_length=10)),
                ('attendance', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Scipy_speaker_2015',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=300)),
                ('email', models.CharField(max_length=300)),
                ('paper', models.CharField(max_length=300)),
                ('purpose', models.CharField(default=b'SPC', max_length=10)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tbc_freeeda',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=75)),
                ('college', models.CharField(max_length=200)),
                ('book', models.CharField(max_length=200)),
                ('author', models.CharField(max_length=200)),
                ('role', models.CharField(max_length=50)),
                ('purpose', models.CharField(default=b'FET', max_length=10)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.DeleteModel(
            name='Scilab_import',
        ),
        migrations.AddField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(to='certificate.Question'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='certificate',
            name='paper',
            field=models.CharField(max_length=100, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='certificate',
            name='serial_key',
            field=models.CharField(max_length=200, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='certificate',
            name='short_key',
            field=models.CharField(max_length=50, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='certificate',
            name='verified',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='certificate',
            name='workshop',
            field=models.CharField(max_length=100, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='purpose',
            field=models.CharField(max_length=25, choices=[(b'SLC', b'Scilab Conference'), (b'SPC', b'Scipy Conference'), (b'PTC', b'Python Textbook Companion'), (b'STC', b'Scilab Textbook Companion'), (b'DCM', b'DrupalCamp Mumbai'), (b'FET', b'FreeEda Textbook Companion'), (b'OFC', b'OpenFOAM Symposium'), (b'FIC', b'Fossee Internship'), (b'OWS', b'Osdag Workshop'), (b'EWS', b'eSim Workshop'), (b'DRP', b'Drupal Workshop')]),
            preserve_default=True,
        ),
    ]

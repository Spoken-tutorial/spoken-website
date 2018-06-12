# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0015_stworkshopfeedback_stworkshopfeedbackpost_stworkshopfeedbackpre'),
    ]

    operations = [
        migrations.CreateModel(
            name='LearnDrupalFeedback',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('phonemob', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=100)),
                ('affiliation', models.CharField(max_length=100)),
                ('place', models.CharField(max_length=100)),
                ('agegroup', models.CharField(max_length=50, choices=[(b'', b'-----'), (b'below25', b'below 25'), (b'25to34', b'25 to 34'), (b'35to44', b'35 to 44'), (b'45to54', b'45 to 54'), (b'55to64', b'55 to 64'), (b'65andabove', b'65 and above')])),
                ('currentstatus', models.CharField(max_length=50, choices=[(b'', b'-----'), (b'Student', b'Student'), (b'Individuallearner', b'Individual learner'), (b'Workingprofessional', b'Working professional'), (b'Teacher', b'Teacher'), (b'Administrator', b'Administrator'), (b'Others', b'Others')])),
                ('currentstatus_other', models.CharField(max_length=50)),
                ('is_drupal_in_curriculum', models.CharField(max_length=50, choices=[(b'', b'-----'), (b'Yes', b'Yes'), (b'No', b'No'), (b'NotApplicable ', b'Not Applicable ')])),
                ('need_help_in_organizing', models.CharField(max_length=50, choices=[(b'', b'-----'), (b'Yes', b'Yes'), (b'No', b'No'), (b'NotApplicable ', b'Not Applicable ')])),
                ('when_plan_to_conduct', models.CharField(max_length=50, choices=[(b'', b'-----'), (b'within3months', b'within 3 months'), (b'within6months', b'within 6 months'), (b'within1year', b'within 1 year'), (b'notyetplanned', b'not yet planned')])),
                ('language', models.CharField(max_length=50, choices=[(b'', b'-----'), (b'Hindi', b'Hindi'), (b'English', b'English'), (b'Marathi', b'Marathi'), (b'Urdu', b'Urdu'), (b'Kannanda', b'Kannanda'), (b'Bangali', b'Bangali'), (b'Malyalum', b'Malyalum'), (b'Tamil', b'Tamil'), (b'Telugu', b'Telugu'), (b'Oriya', b'Oriya'), (b'Assamese', b'Assamese'), (b'Gujrati', b'Gujrati')])),
                ('did_undergo_st_training', models.CharField(max_length=50, choices=[(b'', b'-----'), (b'Yes', b'Yes'), (b'No', b'No'), (b'NotApplicable ', b'Not Applicable ')])),
                ('rate_spoken', models.CharField(max_length=20)),
                ('useful_for_placement', models.CharField(max_length=50, choices=[(b'', b'-----'), (b'Yes', b'Yes'), (b'No', b'No'), (b'NotApplicable ', b'Not Applicable ')])),
                ('useful_for_placement_for_students', models.CharField(max_length=50, choices=[(b'', b'-----'), (b'Yes', b'Yes'), (b'No', b'No'), (b'NotApplicable ', b'Not Applicable ')])),
                ('feedback', models.CharField(max_length=500)),
                ('like_to_learn_other_foss', models.CharField(max_length=50, choices=[(b'', b'-----'), (b'Yes', b'Yes'), (b'No', b'No')])),
                ('mention_foss', models.CharField(max_length=100)),
                ('like_to_give_testimonial', models.CharField(max_length=50, choices=[(b'', b'-----'), (b'Yes', b'Yes'), (b'No', b'No')])),
                ('testimonial', models.CharField(max_length=100)),
            ],
        ),
    ]

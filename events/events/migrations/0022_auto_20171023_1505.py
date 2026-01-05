# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0021_auto_20171023_1358'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inductioninterest',
            name='age',
            field=models.CharField(max_length=100, choices=[(b'', b'-----'), (b'20to25', b'20 to 25 years'), (b'26to30', b'26 to 30 years'), (b'31to35', b'31 to 35 years'), (b'35andabove', b'Above 35 years')]),
        ),
        migrations.AlterField(
            model_name='inductioninterest',
            name='designation',
            field=models.CharField(max_length=100, choices=[(b'', b'-----'), (b'Lecturer', b'Lecturer'), (b'AssistantProfessor', b'Assistant Professor'), (b'AssociateProfessor', b'Associate Professor'), (b'Professor', b'Professor'), (b'Other', b'Other')]),
        ),
        migrations.AlterField(
            model_name='inductioninterest',
            name='experience_in_college',
            field=models.CharField(max_length=100, choices=[(b'', b'-----'), (b'Lessthan1year', b'Less than 1 year'), (b'Morethan1yearbutlessthan2years', b'More than 1 year, but less than 2 years'), (b'Morethan2yearsbutlessthan5years', b'More than 2 years but less than 5 years'), (b'Morethan5years', b'More than 5 years')]),
        ),
        migrations.AlterField(
            model_name='inductioninterest',
            name='gender',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'Male', b'Male'), (b'Female', b'Female')]),
        ),
        migrations.AlterField(
            model_name='inductioninterest',
            name='medium_of_studies',
            field=models.CharField(max_length=100, choices=[(b'', b'-----'), (b'English', b'English'), (b'Other', b'Other')]),
        ),
        migrations.AlterField(
            model_name='inductioninterest',
            name='phonemob',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='inductioninterest',
            name='specialisation',
            field=models.CharField(max_length=100, choices=[(b'', b'-----'), (b'Arts', b'Arts'), (b'Science', b'Science'), (b'Commerce', b'Commerce'), (b'EngineeringorComputerScience ', b'Engineering or Computer Science'), (b'Management', b'Management'), (b'Other', b'Other')]),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '__first__'),
        ('events', '0004_auto_20150727_1632'),
    ]

    operations = [
        migrations.CreateModel(
            name='HelpfulFor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('helpful_for', models.CharField(max_length=50, choices=[(b'0', b'Academic Performance'), (b'1', b'Project Assignments'), (b'2', b'To get job interviews'), (b'3', b'To get jobs'), (b'4', b'All of the above')])),
            ],
        ),
        migrations.CreateModel(
            name='OrganiserFeedback',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=100)),
                ('gender', models.CharField(max_length=10, choices=[(b'', b'-----'), (b'Male', b'Male'), (b'Female', b'Female')])),
                ('age', models.CharField(max_length=20, choices=[(b'', b'-----'), (b'<25', b'<25 years'), (b'25-35', b'25-35 years'), (b'35+', b'35 years and above')])),
                ('designation', models.CharField(max_length=20, choices=[(b'', b'-----'), (b'Student', b'Student'), (b'Faculty', b'Faculty'), (b'Staff', b'Staff'), (b'Admin', b'Admin')])),
                ('medium_of_instruction', models.CharField(max_length=50, choices=[(b'', b'-----'), (b'English', b'English'), (b'Vernacular', b'Vernacular'), (b'Mixed', b'Mixed')])),
                ('student_education_language', models.CharField(max_length=50, choices=[(b'', b'-----'), (b'English', b'Mostly English'), (b'Vernacular', b'Mostly Vernacular'), (b'Mixed', b'Mostly Mixed')])),
                ('student_gender', models.CharField(max_length=50, choices=[(b'', b'-----'), (b'Male', b'Mostly Male'), (b'Female', b'Mostly Female'), (b'Mixed', b'Mixed')])),
                ('student_location', models.CharField(max_length=50, choices=[(b'', b'-----'), (b'Urban', b'Mainly Urban'), (b'Rural', b'Mainly Rural'), (b'Mixed', b'Mixed'), (b'Notsure', b'Not sure')])),
                ('duration_of_tutorial', models.CharField(max_length=50, choices=[(b'', b'-----'), (b'<0.5', b'Less than 0.5 hour'), (b'0.5-2', b'0.5 - 2 hour'), (b'2-10', b'2-10 hours'), (b'10+', b'Above 10 hours'), (b'NA', b'Not applicable')])),
                ('side_by_side_yes_no', models.CharField(max_length=50, choices=[(b'', b'-----'), (b'Yes', b'Yes'), (b'No', b'No')])),
                ('side_by_side_method_is', models.CharField(max_length=50, choices=[(b'', b'-----'), (b'0', b'Explaining the video to a neighbor'), (b'1', b'Waiting for mentors explanation'), (b'2', b'Watching and practicing simultaneously'), (b'3', b'Dont know what this method is')])),
                ('in_side_by_side_method', models.CharField(max_length=50, choices=[(b'', b'-----'), (b'0', b'The video has to be maximized'), (b'1', b'The software has to be maximized'), (b'2', b'Both software and video are maximized'), (b'3', b'None of the above are maximized')])),
                ('good_investment', models.CharField(max_length=50, choices=[(b'', b'-----'), (b'Yes', b'Yes'), (b'No', b'No'), (b'Notsure', b'Not sure')])),
                ('is_comfortable_self_learning', models.CharField(max_length=50, choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree'), (b'Noidea', b'No idea')])),
                ('is_classroom_better', models.CharField(max_length=50, choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree'), (b'Noidea', b'No idea')])),
                ('is_student_expectations', models.CharField(max_length=50, choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree'), (b'Noidea', b'No idea')])),
                ('is_help_get_interview', models.CharField(max_length=50, choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree'), (b'Noidea', b'No idea')])),
                ('is_help_get_job', models.CharField(max_length=50, choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree'), (b'Noidea', b'No idea')])),
                ('is_got_job', models.CharField(max_length=50, choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree'), (b'Noidea', b'No idea')])),
                ('relevance', models.CharField(max_length=50, choices=[(b'', b'-----'), (b'Excellent', b'Excellent'), (b'Good', b'Good'), (b'Fair', b'Fair'), (b'Bad', b'Bad'), (b'Verybad', b'Very bad')])),
                ('information_content', models.CharField(max_length=50, choices=[(b'', b'-----'), (b'Excellent', b'Excellent'), (b'Good', b'Good'), (b'Fair', b'Fair'), (b'Bad', b'Bad'), (b'Verybad', b'Very bad')])),
                ('audio_video_quality', models.CharField(max_length=50, choices=[(b'', b'-----'), (b'Excellent', b'Excellent'), (b'Good', b'Good'), (b'Fair', b'Fair'), (b'Bad', b'Bad'), (b'Verybad', b'Very bad')])),
                ('presentation_quality', models.CharField(max_length=50, choices=[(b'', b'-----'), (b'Excellent', b'Excellent'), (b'Good', b'Good'), (b'Fair', b'Fair'), (b'Bad', b'Bad'), (b'Verybad', b'Very bad')])),
                ('overall_rating', models.CharField(max_length=50, choices=[(b'', b'-----'), (b'Excellent', b'Excellent'), (b'Good', b'Good'), (b'Fair', b'Fair'), (b'Bad', b'Bad'), (b'Verybad', b'Very bad')])),
                ('is_training_benefited', models.CharField(max_length=50, choices=[(b'', b'-----'), (b'Yes', b'Yes'), (b'No', b'No'), (b'Notsure', b'Not sure')])),
                ('testimonial', models.CharField(max_length=500)),
                ('any_other_suggestions', models.CharField(max_length=500)),
                ('can_contact', models.CharField(max_length=50, choices=[(b'', b'-----'), (b'Yes', b'Yes'), (b'No', b'No')])),
                ('city', models.ForeignKey(to='events.City')),
                ('district', models.ForeignKey(to='events.District')),
                ('helpful_for', models.ManyToManyField(related_name='events_HelpfulFor_related', to='events.HelpfulFor')),
                ('language', models.ManyToManyField(related_name='events_Language_related', to='creation.Language')),
                ('offered_training_foss', models.ManyToManyField(related_name='events_FossCategory_related', to='creation.FossCategory')),
                ('state', models.ForeignKey(to='events.State')),
            ],
        ),
        migrations.CreateModel(
            name='StudentStream',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('student_stream', models.CharField(max_length=50, choices=[(b'0', b'Engineering'), (b'1', b'Science'), (b'2', b'Arts and Humanities'), (b'3', b'Polytechnic/ Diploma programs'), (b'4', b'Commerce and Business Studies'), (b'5', b'ITI'), (b'6', b'Other')])),
            ],
        ),
        migrations.AddField(
            model_name='singletrainingattendance',
            name='foss',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='trainingfeedback',
            name='training',
            field=models.ForeignKey(to='events.TrainingRequest'),
        ),
        migrations.AlterField(
            model_name='traininglanguagefeedback',
            name='name',
            field=models.CharField(default=None, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='traininglanguagefeedback',
            name='training',
            field=models.ForeignKey(to='events.TrainingRequest'),
        ),
        migrations.AlterField(
            model_name='traininglivefeedback',
            name='training',
            field=models.ForeignKey(to='events.SingleTraining'),
        ),
        migrations.AddField(
            model_name='organiserfeedback',
            name='student_stream',
            field=models.ManyToManyField(related_name='events_StudentStream_related', to='events.StudentStream'),
        ),
        migrations.AddField(
            model_name='organiserfeedback',
            name='trained_foss',
            field=models.ManyToManyField(to='creation.FossCategory'),
        ),
        migrations.AddField(
            model_name='organiserfeedback',
            name='university',
            field=models.ForeignKey(to='events.AcademicCenter'),
        ),
    ]

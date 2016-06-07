# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import events.models


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0001_initial'),
        ('events', '0004_auto_20150727_1632'),
    ]

    operations = [
        migrations.CreateModel(
            name='HelpfulFor',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('helpful_for', models.CharField(choices=[(b'0', b'Academic Performance'), (b'1', b'Project Assignments'), (b'2', b'To get job interviews'), (b'3', b'To get jobs'), (b'4', b'All of the above')], max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='LatexWorkshopFileUpload',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('file_upload', models.FileField(upload_to=events.models.get_email_dir)),
            ],
        ),
        migrations.CreateModel(
            name='OrganiserFeedback',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=100)),
                ('gender', models.CharField(choices=[(b'', b'-----'), (b'Male', b'Male'), (b'Female', b'Female')], max_length=10)),
                ('age', models.CharField(choices=[(b'', b'-----'), (b'<25', b'<25 years'), (b'25-35', b'25-35 years'), (b'35+', b'35 years and above')], max_length=20)),
                ('designation', models.CharField(choices=[(b'', b'-----'), (b'Student', b'Student'), (b'Faculty', b'Faculty'), (b'Staff', b'Staff'), (b'Admin', b'Admin')], max_length=20)),
                ('medium_of_instruction', models.CharField(choices=[(b'', b'-----'), (b'English', b'English'), (b'Vernacular', b'Vernacular'), (b'Mixed', b'Mixed')], max_length=50)),
                ('student_education_language', models.CharField(choices=[(b'', b'-----'), (b'English', b'Mostly English'), (b'Vernacular', b'Mostly Vernacular'), (b'Mixed', b'Mostly Mixed')], max_length=50)),
                ('student_gender', models.CharField(choices=[(b'', b'-----'), (b'Male', b'Mostly Male'), (b'Female', b'Mostly Female'), (b'Mixed', b'Mixed')], max_length=50)),
                ('student_location', models.CharField(choices=[(b'', b'-----'), (b'Urban', b'Mainly Urban'), (b'Rural', b'Mainly Rural'), (b'Mixed', b'Mixed'), (b'Notsure', b'Not sure')], max_length=50)),
                ('duration_of_tutorial', models.CharField(choices=[(b'', b'-----'), (b'<0.5', b'Less than 0.5 hour'), (b'0.5-2', b'0.5 - 2 hour'), (b'2-10', b'2-10 hours'), (b'10+', b'Above 10 hours'), (b'NA', b'Not applicable')], max_length=50)),
                ('side_by_side_yes_no', models.CharField(choices=[(b'', b'-----'), (b'Yes', b'Yes'), (b'No', b'No')], max_length=50)),
                ('side_by_side_method_is', models.CharField(choices=[(b'', b'-----'), (b'0', b'Explaining the video to a neighbor'), (b'1', b'Waiting for mentors explanation'), (b'2', b'Watching and practicing simultaneously'), (b'3', b'Dont know what this method is')], max_length=50)),
                ('in_side_by_side_method', models.CharField(choices=[(b'', b'-----'), (b'0', b'The video has to be maximized'), (b'1', b'The software has to be maximized'), (b'2', b'Both software and video are maximized'), (b'3', b'None of the above are maximized')], max_length=50)),
                ('good_investment', models.CharField(choices=[(b'', b'-----'), (b'Yes', b'Yes'), (b'No', b'No'), (b'Notsure', b'Not sure')], max_length=50)),
                ('is_comfortable_self_learning', models.CharField(choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree'), (b'Noidea', b'No idea')], max_length=50)),
                ('is_classroom_better', models.CharField(choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree'), (b'Noidea', b'No idea')], max_length=50)),
                ('is_student_expectations', models.CharField(choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree'), (b'Noidea', b'No idea')], max_length=50)),
                ('is_help_get_interview', models.CharField(choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree'), (b'Noidea', b'No idea')], max_length=50)),
                ('is_help_get_job', models.CharField(choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree'), (b'Noidea', b'No idea')], max_length=50)),
                ('is_got_job', models.CharField(choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree'), (b'Noidea', b'No idea')], max_length=50)),
                ('relevance', models.CharField(choices=[(b'', b'-----'), (b'Excellent', b'Excellent'), (b'Good', b'Good'), (b'Fair', b'Fair'), (b'Bad', b'Bad'), (b'Verybad', b'Very bad')], max_length=50)),
                ('information_content', models.CharField(choices=[(b'', b'-----'), (b'Excellent', b'Excellent'), (b'Good', b'Good'), (b'Fair', b'Fair'), (b'Bad', b'Bad'), (b'Verybad', b'Very bad')], max_length=50)),
                ('audio_video_quality', models.CharField(choices=[(b'', b'-----'), (b'Excellent', b'Excellent'), (b'Good', b'Good'), (b'Fair', b'Fair'), (b'Bad', b'Bad'), (b'Verybad', b'Very bad')], max_length=50)),
                ('presentation_quality', models.CharField(choices=[(b'', b'-----'), (b'Excellent', b'Excellent'), (b'Good', b'Good'), (b'Fair', b'Fair'), (b'Bad', b'Bad'), (b'Verybad', b'Very bad')], max_length=50)),
                ('overall_rating', models.CharField(choices=[(b'', b'-----'), (b'Excellent', b'Excellent'), (b'Good', b'Good'), (b'Fair', b'Fair'), (b'Bad', b'Bad'), (b'Verybad', b'Very bad')], max_length=50)),
                ('is_training_benefited', models.CharField(choices=[(b'', b'-----'), (b'Yes', b'Yes'), (b'No', b'No'), (b'Notsure', b'Not sure')], max_length=50)),
                ('testimonial', models.CharField(max_length=500)),
                ('any_other_suggestions', models.CharField(max_length=500)),
                ('can_contact', models.CharField(choices=[(b'', b'-----'), (b'Yes', b'Yes'), (b'No', b'No')], max_length=50)),
                ('city', models.ForeignKey(to='events.City')),
                ('district', models.ForeignKey(to='events.District')),
                ('helpful_for', models.ManyToManyField(related_name='events_HelpfulFor_related', to='events.HelpfulFor')),
                ('language', models.ManyToManyField(related_name='events_Language_related', to='creation.Language')),
                ('offered_training_foss', models.ManyToManyField(related_name='events_FossCategory_related', to='creation.FossCategory')),
            ],
        ),
        migrations.CreateModel(
            name='StudentStream',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('student_stream', models.CharField(choices=[(b'0', b'Engineering'), (b'1', b'Science'), (b'2', b'Arts and Humanities'), (b'3', b'Polytechnic/ Diploma programs'), (b'4', b'Commerce and Business Studies'), (b'5', b'ITI'), (b'6', b'Other')], max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name='singletraining',
            name='institution_type',
            field=models.ForeignKey(null=True, to='events.InstituteType'),
        ),
        migrations.AddField(
            model_name='singletraining',
            name='state',
            field=models.ForeignKey(null=True, to='events.State'),
        ),
        migrations.AddField(
            model_name='singletraining',
            name='total_participant_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='singletrainingattendance',
            name='foss',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='state',
            name='has_map',
            field=models.BooleanField(default=1),
        ),
        migrations.AlterField(
            model_name='student',
            name='verified',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='trainingfeedback',
            name='training',
            field=models.ForeignKey(to='events.TrainingRequest'),
        ),
        migrations.AlterField(
            model_name='traininglanguagefeedback',
            name='name',
            field=models.CharField(null=True, default=None, max_length=100),
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
        migrations.AlterField(
            model_name='trainingrequest',
            name='status',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='organiserfeedback',
            name='state',
            field=models.ForeignKey(to='events.State'),
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

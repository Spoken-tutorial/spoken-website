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
            name='OrganiserFeedback',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('gender', models.CharField(max_length=10, choices=[(b'', b'----'), (b'0', b'Male'), (b'1', b'Female')])),
                ('age', models.CharField(max_length=20, choices=[(b'', b'----'), (b'0', b'<25 years'), (b'1', b'25-35 years'), (b'2', b'35 years and above')])),
                ('designation', models.CharField(max_length=20, choices=[(b'', b'----'), (b'0', b'student'), (b'1', b'faculty'), (b'2', b'staff'), (b'3', b'admin')])),
                ('medium_of_instruction', models.CharField(max_length=50, choices=[(b'', b'----'), (b'0', b'english'), (b'1', b'vernacular'), (b'2', b'mixed')])),
                ('student_stream', models.CharField(max_length=50, choices=[(b'0', b'Engineering'), (b'1', b'science'), (b'2', b'Arts and Humanities'), (b'3', b'Polytechnic/ Diploma programs'), (b'4', b'Commerce and Business Studies'), (b'5', b'Schools'), (b'6', b'ITI'), (b'7', b'other (need to give textbox)')])),
                ('student_education_language', models.CharField(max_length=50, choices=[(b'', b'----'), (b'0', b'mostly english'), (b'1', b'mostly vernacular'), (b'2', b'mostly mixed')])),
                ('student_gender', models.CharField(max_length=50, choices=[(b'', b'----'), (b'0', b'mostly Male'), (b'1', b'mostly Female'), (b'2', b'mixed')])),
                ('student_location', models.CharField(max_length=50, choices=[(b'', b'----'), (b'0', b'mainly urban'), (b'1', b'mainly rural'), (b'2', b'mixed'), (b'3', b'not sure')])),
                ('duration_of_tutorial', models.CharField(max_length=50, choices=[(b'', b'----'), (b'0', b'Less than 0.5 hour'), (b'1', b'0.5 - 2 hour'), (b'2', b'2-10 hours'), (b'3', b'Above 10 hours'), (b'4', b'Not applicable')])),
                ('side_by_side_yes_no', models.CharField(max_length=10, choices=[(b'', b'-----'), (b'0', b'YES'), (b'1', b'NO')])),
                ('side_by_side_method_is', models.CharField(max_length=10, choices=[(b'', b'----'), (b'0', b'Explaining the video to a neighbor'), (b'1', b'Waiting for mentors explanation'), (b'2', b'Watching and practicing simultaneously'), (b'3', b'Dont know what this method is')])),
                ('in_side_by_side_method', models.CharField(max_length=10, choices=[(b'', b'----'), (b'0', b'The video has to be maximized'), (b'1', b'The software has to be maximized'), (b'2', b'Both software and video are maximized'), (b'3', b'None of the above are maximized')])),
                ('good_investment', models.CharField(max_length=10, choices=[(b'', b'----'), (b'0', b'Yes'), (b'1', b'No'), (b'2', b'Not Sure')])),
                ('helpful_for', models.CharField(max_length=50, choices=[(b'0', b'Academic Performance'), (b'1', b'Project Assignments'), (b'2', b'To get job interviews'), (b'3', b'To get jobs'), (b'4', b'All of the above')])),
                ('is_comfortable_self_learning', models.CharField(max_length=10, choices=[(b'0', b'Strongly Agree'), (b'1', b'Agree'), (b'2', b'Neutral'), (b'3', b'Disagree'), (b'4', b'Strongly Disagree'), (b'5', b'No idea')])),
                ('is_classroom_better', models.CharField(max_length=50, choices=[(b'0', b'Strongly Agree'), (b'1', b'Agree'), (b'2', b'Neutral'), (b'3', b'Disagree'), (b'4', b'Strongly Disagree'), (b'5', b'No idea')])),
                ('is_student_expectations', models.CharField(max_length=10, choices=[(b'0', b'Strongly Agree'), (b'1', b'Agree'), (b'2', b'Neutral'), (b'3', b'Disagree'), (b'4', b'Strongly Disagree'), (b'5', b'No idea')])),
                ('is_help_get_interview', models.CharField(max_length=50, choices=[(b'0', b'Strongly Agree'), (b'1', b'Agree'), (b'2', b'Neutral'), (b'3', b'Disagree'), (b'4', b'Strongly Disagree'), (b'5', b'No idea')])),
                ('is_help_get_job', models.CharField(max_length=10, choices=[(b'0', b'Strongly Agree'), (b'1', b'Agree'), (b'2', b'Neutral'), (b'3', b'Disagree'), (b'4', b'Strongly Disagree'), (b'5', b'No idea')])),
                ('is_got_job', models.CharField(max_length=10, choices=[(b'0', b'Strongly Agree'), (b'1', b'Agree'), (b'2', b'Neutral'), (b'3', b'Disagree'), (b'4', b'Strongly Disagree'), (b'5', b'No idea')])),
                ('relevance', models.CharField(max_length=10, choices=[(b'0', b'Excellent'), (b'1', b'Good'), (b'2', b'Fair'), (b'3', b'Bad'), (b'4', b'Very bad')])),
                ('information_content', models.CharField(max_length=10, choices=[(b'0', b'Excellent'), (b'1', b'Good'), (b'2', b'Fair'), (b'3', b'Bad'), (b'4', b'Very bad')])),
                ('audio_video_quality', models.CharField(max_length=10, choices=[(b'0', b'Excellent'), (b'1', b'Good'), (b'2', b'Fair'), (b'3', b'Bad'), (b'4', b'Very bad')])),
                ('presentation_quality', models.CharField(max_length=10, choices=[(b'0', b'Excellent'), (b'1', b'Good'), (b'2', b'Fair'), (b'3', b'Bad'), (b'4', b'Very bad')])),
                ('overall_rating', models.CharField(max_length=10, choices=[(b'0', b'Excellent'), (b'1', b'Good'), (b'2', b'Fair'), (b'3', b'Bad'), (b'4', b'Very bad')])),
                ('is_training_benefited', models.CharField(max_length=10, choices=[(b'', b'-----'), (b'0', b'YES'), (b'1', b'NO')])),
                ('testimonial', models.CharField(max_length=10)),
                ('any_other_suggestions', models.CharField(max_length=10)),
                ('can_contact', models.CharField(max_length=10, choices=[(b'', b'-----'), (b'0', b'YES'), (b'1', b'NO')])),
                ('city', models.ForeignKey(to='events.City')),
                ('district', models.ForeignKey(to='events.District')),
                ('language', models.ManyToManyField(related_name='events_Language_related', to='creation.Language')),
                ('offered_training_foss', models.ManyToManyField(to='creation.FossCategory')),
                ('state', models.ForeignKey(to='events.State')),
                ('trained_foss', models.ManyToManyField(to='creation.Language')),
                ('university', models.ForeignKey(to='events.AcademicCenter')),
            ],
        ),
    ]

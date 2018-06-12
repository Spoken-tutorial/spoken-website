# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0009_auto_20150806_1820'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organiserfeedback',
            name='age',
            field=models.CharField(max_length=20, choices=[(b'', b'-----'), (b'<25', b'<25 years'), (b'25-35', b'25-35 years'), (b'35+', b'35 years and above')]),
        ),
        migrations.AlterField(
            model_name='organiserfeedback',
            name='audio_video_quality',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'Excellent', b'Excellent'), (b'Good', b'Good'), (b'Fair', b'Fair'), (b'Bad', b'Bad'), (b'Verybad', b'Very bad')]),
        ),
        migrations.AlterField(
            model_name='organiserfeedback',
            name='can_contact',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'Yes', b'Yes'), (b'No', b'No')]),
        ),
        migrations.AlterField(
            model_name='organiserfeedback',
            name='designation',
            field=models.CharField(max_length=20, choices=[(b'', b'-----'), (b'Student', b'Student'), (b'Faculty', b'Faculty'), (b'Staff', b'Staff'), (b'Admin', b'Admin')]),
        ),
        migrations.AlterField(
            model_name='organiserfeedback',
            name='duration_of_tutorial',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'<0.5', b'Less than 0.5 hour'), (b'0.5-2', b'0.5 - 2 hour'), (b'2-10', b'2-10 hours'), (b'10+', b'Above 10 hours'), (b'NA', b'Not applicable')]),
        ),
        migrations.AlterField(
            model_name='organiserfeedback',
            name='gender',
            field=models.CharField(max_length=10, choices=[(b'', b'-----'), (b'Male', b'Male'), (b'Female', b'Female')]),
        ),
        migrations.AlterField(
            model_name='organiserfeedback',
            name='good_investment',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'Yes', b'Yes'), (b'No', b'No'), (b'Notsure', b'Not sure')]),
        ),
        migrations.AlterField(
            model_name='organiserfeedback',
            name='in_side_by_side_method',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'0', b'The video has to be maximized'), (b'1', b'The software has to be maximized'), (b'2', b'Both software and video are maximized'), (b'3', b'None of the above are maximized')]),
        ),
        migrations.AlterField(
            model_name='organiserfeedback',
            name='information_content',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'Excellent', b'Excellent'), (b'Good', b'Good'), (b'Fair', b'Fair'), (b'Bad', b'Bad'), (b'Verybad', b'Very bad')]),
        ),
        migrations.AlterField(
            model_name='organiserfeedback',
            name='is_classroom_better',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree'), (b'Noidea', b'No idea')]),
        ),
        migrations.AlterField(
            model_name='organiserfeedback',
            name='is_comfortable_self_learning',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree'), (b'Noidea', b'No idea')]),
        ),
        migrations.AlterField(
            model_name='organiserfeedback',
            name='is_got_job',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree'), (b'Noidea', b'No idea')]),
        ),
        migrations.AlterField(
            model_name='organiserfeedback',
            name='is_help_get_interview',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree'), (b'Noidea', b'No idea')]),
        ),
        migrations.AlterField(
            model_name='organiserfeedback',
            name='is_help_get_job',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree'), (b'Noidea', b'No idea')]),
        ),
        migrations.AlterField(
            model_name='organiserfeedback',
            name='is_student_expectations',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree'), (b'Noidea', b'No idea')]),
        ),
        migrations.AlterField(
            model_name='organiserfeedback',
            name='is_training_benefited',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'Yes', b'Yes'), (b'No', b'No'), (b'Notsure', b'Not sure')]),
        ),
        migrations.AlterField(
            model_name='organiserfeedback',
            name='medium_of_instruction',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'English', b'English'), (b'Vernacular', b'Vernacular'), (b'Mixed', b'Mixed')]),
        ),
        migrations.AlterField(
            model_name='organiserfeedback',
            name='overall_rating',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'Excellent', b'Excellent'), (b'Good', b'Good'), (b'Fair', b'Fair'), (b'Bad', b'Bad'), (b'Verybad', b'Very bad')]),
        ),
        migrations.AlterField(
            model_name='organiserfeedback',
            name='presentation_quality',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'Excellent', b'Excellent'), (b'Good', b'Good'), (b'Fair', b'Fair'), (b'Bad', b'Bad'), (b'Verybad', b'Very bad')]),
        ),
        migrations.AlterField(
            model_name='organiserfeedback',
            name='relevance',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'Excellent', b'Excellent'), (b'Good', b'Good'), (b'Fair', b'Fair'), (b'Bad', b'Bad'), (b'Verybad', b'Very bad')]),
        ),
        migrations.AlterField(
            model_name='organiserfeedback',
            name='side_by_side_method_is',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'0', b'Explaining the video to a neighbor'), (b'1', b'Waiting for mentors explanation'), (b'2', b'Watching and practicing simultaneously'), (b'3', b'Dont know what this method is')]),
        ),
        migrations.AlterField(
            model_name='organiserfeedback',
            name='side_by_side_yes_no',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'Yes', b'Yes'), (b'No', b'No')]),
        ),
        migrations.AlterField(
            model_name='organiserfeedback',
            name='student_education_language',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'English', b'Mostly English'), (b'Vernacular', b'Mostly Vernacular'), (b'Mixed', b'Mostly Mixed')]),
        ),
        migrations.AlterField(
            model_name='organiserfeedback',
            name='student_gender',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'Male', b'Mostly Male'), (b'Female', b'Mostly Female'), (b'Mixed', b'Mixed')]),
        ),
        migrations.AlterField(
            model_name='organiserfeedback',
            name='student_location',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'Urban', b'Mainly Urban'), (b'Rural', b'Mainly Rural'), (b'Mixed', b'Mixed'), (b'Notsure', b'Not sure')]),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2025-01-02 09:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0048_auto_20241213_1154'),
    ]

    operations = [
        migrations.RunSQL("SET sql_mode='';"),
        migrations.AlterField(
            model_name='inductioninterest',
            name='college_address',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='inductioninterest',
            name='other_comments',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='learndrupalfeedback',
            name='feedback',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='organiserfeedback',
            name='any_other_suggestions',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='organiserfeedback',
            name='testimonial',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedback',
            name='experience',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedback',
            name='how_make_better',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedback',
            name='like_abt_ws',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedback',
            name='suggestions',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='acquired_knowledge',
            field=models.CharField(choices=[('', '-----'), ('StronglyAgree', 'Strongly Agree'), ('Agree', 'Agree'), ('Neutral', 'Neutral'), ('Disagree', 'Disagree'), ('StronglyDisagree', 'Strongly Disagree'), ('Noidea', 'No idea')], max_length=16),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='adding_func',
            field=models.CharField(choices=[('', '-----'), ('Notconfidentatall', 'Not confident at all'), ('Unconfident', 'Unconfident'), ('Neitherconfidentnorunconfident', 'Neither confident nor unconfident'), ('Confident', 'Confident'), ('Absolutelyconfident', 'Absolutely confident'), ('NotApplicable', 'Not Applicable')], max_length=30),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='age',
            field=models.CharField(max_length=2),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='arrangement',
            field=models.CharField(choices=[('', '-----'), ('Excellent', 'Excellent'), ('Good', 'Good'), ('Fair', 'Fair'), ('Bad', 'Bad'), ('Extremelybad', 'Extremely bad')], max_length=12),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='ask_student_to_use',
            field=models.CharField(choices=[('', '-----'), ('StronglyAgree', 'Strongly Agree'), ('Agree', 'Agree'), ('Neutral', 'Neutral'), ('Disagree', 'Disagree'), ('StronglyDisagree', 'Strongly Disagree'), ('Noidea', 'No idea')], max_length=16),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='asked_ques_forums',
            field=models.CharField(choices=[('', '-----'), ('StronglyAgree', 'Strongly Agree'), ('Agree', 'Agree'), ('Neutral', 'Neutral'), ('Disagree', 'Disagree'), ('StronglyDisagree', 'Strongly Disagree'), ('Noidea', 'No idea')], max_length=16),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='can_learn_other',
            field=models.CharField(choices=[('', '-----'), ('StronglyAgree', 'Strongly Agree'), ('Agree', 'Agree'), ('Neutral', 'Neutral'), ('Disagree', 'Disagree'), ('StronglyDisagree', 'Strongly Disagree'), ('Noidea', 'No idea')], max_length=16),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='clarity_of_speech',
            field=models.CharField(choices=[('', '-----'), ('Excellent', 'Excellent'), ('Good', 'Good'), ('Fair', 'Fair'), ('Bad', 'Bad'), ('Extremelybad', 'Extremely bad')], max_length=12),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='confident',
            field=models.CharField(choices=[('', '-----'), ('StronglyAgree', 'Strongly Agree'), ('Agree', 'Agree'), ('Neutral', 'Neutral'), ('Disagree', 'Disagree'), ('StronglyDisagree', 'Strongly Disagree'), ('Noidea', 'No idea')], max_length=16),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='configuration_management',
            field=models.CharField(choices=[('', '-----'), ('Notconfidentatall', 'Not confident at all'), ('Unconfident', 'Unconfident'), ('Neitherconfidentnorunconfident', 'Neither confident nor unconfident'), ('Confident', 'Confident'), ('Absolutelyconfident', 'Absolutely confident'), ('NotApplicable', 'Not Applicable')], max_length=30),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='content_management',
            field=models.CharField(choices=[('', '-----'), ('Notconfidentatall', 'Not confident at all'), ('Unconfident', 'Unconfident'), ('Neitherconfidentnorunconfident', 'Neither confident nor unconfident'), ('Confident', 'Confident'), ('Absolutelyconfident', 'Absolutely confident'), ('NotApplicable', 'Not Applicable')], max_length=30),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='contents_using_view',
            field=models.CharField(choices=[('', '-----'), ('Notconfidentatall', 'Not confident at all'), ('Unconfident', 'Unconfident'), ('Neitherconfidentnorunconfident', 'Neither confident nor unconfident'), ('Confident', 'Confident'), ('Absolutelyconfident', 'Absolutely confident'), ('NotApplicable', 'Not Applicable')], max_length=30),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='control_display_images',
            field=models.CharField(choices=[('', '-----'), ('Notconfidentatall', 'Not confident at all'), ('Unconfident', 'Unconfident'), ('Neitherconfidentnorunconfident', 'Neither confident nor unconfident'), ('Confident', 'Confident'), ('Absolutelyconfident', 'Absolutely confident'), ('NotApplicable', 'Not Applicable')], max_length=30),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='create_new_content',
            field=models.CharField(choices=[('', '-----'), ('Notconfidentatall', 'Not confident at all'), ('Unconfident', 'Unconfident'), ('Neitherconfidentnorunconfident', 'Neither confident nor unconfident'), ('Confident', 'Confident'), ('Absolutelyconfident', 'Absolutely confident'), ('NotApplicable', 'Not Applicable')], max_length=30),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='creating_basic_content',
            field=models.CharField(choices=[('', '-----'), ('Notconfidentatall', 'Not confident at all'), ('Unconfident', 'Unconfident'), ('Neitherconfidentnorunconfident', 'Neither confident nor unconfident'), ('Confident', 'Confident'), ('Absolutelyconfident', 'Absolutely confident'), ('NotApplicable', 'Not Applicable')], max_length=30),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='creating_dummy_content',
            field=models.CharField(choices=[('', '-----'), ('Notconfidentatall', 'Not confident at all'), ('Unconfident', 'Unconfident'), ('Neitherconfidentnorunconfident', 'Neither confident nor unconfident'), ('Confident', 'Confident'), ('Absolutelyconfident', 'Absolutely confident'), ('NotApplicable', 'Not Applicable')], max_length=30),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='desired_objective',
            field=models.CharField(choices=[('', '-----'), ('StronglyAgree', 'Strongly Agree'), ('Agree', 'Agree'), ('Neutral', 'Neutral'), ('Disagree', 'Disagree'), ('StronglyDisagree', 'Strongly Disagree'), ('Noidea', 'No idea')], max_length=16),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='diff_watch_practice',
            field=models.CharField(choices=[('', '-----'), ('StronglyAgree', 'Strongly Agree'), ('Agree', 'Agree'), ('Neutral', 'Neutral'), ('Disagree', 'Disagree'), ('StronglyDisagree', 'Strongly Disagree'), ('Noidea', 'No idea')], max_length=16),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='doubts_solved_fast',
            field=models.CharField(choices=[('', '-----'), ('StronglyAgree', 'Strongly Agree'), ('Agree', 'Agree'), ('Neutral', 'Neutral'), ('Disagree', 'Disagree'), ('StronglyDisagree', 'Strongly Disagree'), ('Noidea', 'No idea')], max_length=16),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='edit_existing_content',
            field=models.CharField(choices=[('', '-----'), ('Notconfidentatall', 'Not confident at all'), ('Unconfident', 'Unconfident'), ('Neitherconfidentnorunconfident', 'Neither confident nor unconfident'), ('Confident', 'Confident'), ('Absolutelyconfident', 'Absolutely confident'), ('NotApplicable', 'Not Applicable')], max_length=30),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='esy_to_conduct_own',
            field=models.CharField(choices=[('', '-----'), ('StronglyAgree', 'Strongly Agree'), ('Agree', 'Agree'), ('Neutral', 'Neutral'), ('Disagree', 'Disagree'), ('StronglyDisagree', 'Strongly Disagree'), ('Noidea', 'No idea')], max_length=16),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='examples_help',
            field=models.CharField(choices=[('', '-----'), ('StronglyAgree', 'Strongly Agree'), ('Agree', 'Agree'), ('Neutral', 'Neutral'), ('Disagree', 'Disagree'), ('StronglyDisagree', 'Strongly Disagree'), ('Noidea', 'No idea')], max_length=16),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='experience',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='experience_of_learning',
            field=models.CharField(choices=[('', '-----'), ('Excellent', 'Excellent'), ('Good', 'Good'), ('Fair', 'Fair'), ('Bad', 'Bad'), ('Extremelybad', 'Extremely bad')], max_length=12),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='explain',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='faster_on_forums',
            field=models.CharField(choices=[('', '-----'), ('StronglyAgree', 'Strongly Agree'), ('Agree', 'Agree'), ('Neutral', 'Neutral'), ('Disagree', 'Disagree'), ('StronglyDisagree', 'Strongly Disagree'), ('Noidea', 'No idea')], max_length=16),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='finding_modules',
            field=models.CharField(choices=[('', '-----'), ('Notconfidentatall', 'Not confident at all'), ('Unconfident', 'Unconfident'), ('Neitherconfidentnorunconfident', 'Neither confident nor unconfident'), ('Confident', 'Confident'), ('Absolutelyconfident', 'Absolutely confident'), ('NotApplicable', 'Not Applicable')], max_length=30),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='forum_helpful',
            field=models.CharField(choices=[('', '-----'), ('StronglyAgree', 'Strongly Agree'), ('Agree', 'Agree'), ('Neutral', 'Neutral'), ('Disagree', 'Disagree'), ('StronglyDisagree', 'Strongly Disagree'), ('Noidea', 'No idea')], max_length=16),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='forum_motivated',
            field=models.CharField(choices=[('', '-----'), ('StronglyAgree', 'Strongly Agree'), ('Agree', 'Agree'), ('Neutral', 'Neutral'), ('Disagree', 'Disagree'), ('StronglyDisagree', 'Strongly Disagree'), ('Noidea', 'No idea')], max_length=16),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='grp_entity_ref',
            field=models.CharField(choices=[('', '-----'), ('Notconfidentatall', 'Not confident at all'), ('Unconfident', 'Unconfident'), ('Neitherconfidentnorunconfident', 'Neither confident nor unconfident'), ('Confident', 'Confident'), ('Absolutelyconfident', 'Absolutely confident'), ('NotApplicable', 'Not Applicable')], max_length=30),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='guidelines',
            field=models.CharField(choices=[('', '-----'), ('Excellent', 'Excellent'), ('Good', 'Good'), ('Fair', 'Fair'), ('Bad', 'Bad'), ('Extremelybad', 'Extremely bad')], max_length=12),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='helpful_pre_ans_ques',
            field=models.CharField(choices=[('', '-----'), ('StronglyAgree', 'Strongly Agree'), ('Agree', 'Agree'), ('Neutral', 'Neutral'), ('Disagree', 'Disagree'), ('StronglyDisagree', 'Strongly Disagree'), ('Noidea', 'No idea')], max_length=16),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='how_make_better',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='install_own',
            field=models.CharField(choices=[('', '-----'), ('Yes', 'Yes'), ('No', 'No')], max_length=3),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='installation_help',
            field=models.CharField(choices=[('', '-----'), ('Excellent', 'Excellent'), ('Good', 'Good'), ('Fair', 'Fair'), ('Bad', 'Bad'), ('Extremelybad', 'Extremely bad')], max_length=12),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='installig_ad_themes',
            field=models.CharField(choices=[('', '-----'), ('Notconfidentatall', 'Not confident at all'), ('Unconfident', 'Unconfident'), ('Neitherconfidentnorunconfident', 'Neither confident nor unconfident'), ('Confident', 'Confident'), ('Absolutelyconfident', 'Absolutely confident'), ('NotApplicable', 'Not Applicable')], max_length=30),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='instructions_easy_to_follow',
            field=models.CharField(choices=[('', '-----'), ('StronglyAgree', 'Strongly Agree'), ('Agree', 'Agree'), ('Neutral', 'Neutral'), ('Disagree', 'Disagree'), ('StronglyDisagree', 'Strongly Disagree'), ('Noidea', 'No idea')], max_length=16),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='language_complicated',
            field=models.CharField(choices=[('', '-----'), ('StronglyAgree', 'Strongly Agree'), ('Agree', 'Agree'), ('Neutral', 'Neutral'), ('Disagree', 'Disagree'), ('StronglyDisagree', 'Strongly Disagree'), ('Noidea', 'No idea')], max_length=16),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='learn_other_side_by_side',
            field=models.CharField(choices=[('', '-----'), ('StronglyAgree', 'Strongly Agree'), ('Agree', 'Agree'), ('Neutral', 'Neutral'), ('Disagree', 'Disagree'), ('StronglyDisagree', 'Strongly Disagree'), ('Noidea', 'No idea')], max_length=16),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='like_abt_ws',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='like_to_create_st',
            field=models.CharField(choices=[('', '-----'), ('Yes', 'Yes'), ('No', 'No')], max_length=3),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='like_to_create_st_details',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='like_to_part',
            field=models.CharField(choices=[('', '-----'), ('StronglyAgree', 'Strongly Agree'), ('Agree', 'Agree'), ('Neutral', 'Neutral'), ('Disagree', 'Disagree'), ('StronglyDisagree', 'Strongly Disagree'), ('Noidea', 'No idea')], max_length=16),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='logical_sequence',
            field=models.CharField(choices=[('', '-----'), ('StronglyAgree', 'Strongly Agree'), ('Agree', 'Agree'), ('Neutral', 'Neutral'), ('Disagree', 'Disagree'), ('StronglyDisagree', 'Strongly Disagree'), ('Noidea', 'No idea')], max_length=16),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='managing_content',
            field=models.CharField(choices=[('', '-----'), ('Notconfidentatall', 'Not confident at all'), ('Unconfident', 'Unconfident'), ('Neitherconfidentnorunconfident', 'Neither confident nor unconfident'), ('Confident', 'Confident'), ('Absolutelyconfident', 'Absolutely confident'), ('NotApplicable', 'Not Applicable')], max_length=30),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='menu_endpoints',
            field=models.CharField(choices=[('', '-----'), ('Notconfidentatall', 'Not confident at all'), ('Unconfident', 'Unconfident'), ('Neitherconfidentnorunconfident', 'Neither confident nor unconfident'), ('Confident', 'Confident'), ('Absolutelyconfident', 'Absolutely confident'), ('NotApplicable', 'Not Applicable')], max_length=30),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='method_easy',
            field=models.CharField(choices=[('', '-----'), ('StronglyAgree', 'Strongly Agree'), ('Agree', 'Agree'), ('Neutral', 'Neutral'), ('Disagree', 'Disagree'), ('StronglyDisagree', 'Strongly Disagree'), ('Noidea', 'No idea')], max_length=16),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='modify_display_content',
            field=models.CharField(choices=[('', '-----'), ('Notconfidentatall', 'Not confident at all'), ('Unconfident', 'Unconfident'), ('Neitherconfidentnorunconfident', 'Neither confident nor unconfident'), ('Confident', 'Confident'), ('Absolutelyconfident', 'Absolutely confident'), ('NotApplicable', 'Not Applicable')], max_length=30),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='modifying_page_layout',
            field=models.CharField(choices=[('', '-----'), ('Notconfidentatall', 'Not confident at all'), ('Unconfident', 'Unconfident'), ('Neitherconfidentnorunconfident', 'Neither confident nor unconfident'), ('Confident', 'Confident'), ('Absolutelyconfident', 'Absolutely confident'), ('NotApplicable', 'Not Applicable')], max_length=30),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='need_not_post',
            field=models.CharField(choices=[('', '-----'), ('StronglyAgree', 'Strongly Agree'), ('Agree', 'Agree'), ('Neutral', 'Neutral'), ('Disagree', 'Disagree'), ('StronglyDisagree', 'Strongly Disagree'), ('Noidea', 'No idea')], max_length=16),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='network',
            field=models.CharField(choices=[('', '-----'), ('Excellent', 'Excellent'), ('Good', 'Good'), ('Fair', 'Fair'), ('Bad', 'Bad'), ('Extremelybad', 'Extremely bad')], max_length=12),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='not_answer_doubts',
            field=models.CharField(choices=[('', '-----'), ('StronglyAgree', 'Strongly Agree'), ('Agree', 'Agree'), ('Neutral', 'Neutral'), ('Disagree', 'Disagree'), ('StronglyDisagree', 'Strongly Disagree'), ('Noidea', 'No idea')], max_length=16),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='not_have_to_wait',
            field=models.CharField(choices=[('', '-----'), ('StronglyAgree', 'Strongly Agree'), ('Agree', 'Agree'), ('Neutral', 'Neutral'), ('Disagree', 'Disagree'), ('StronglyDisagree', 'Strongly Disagree'), ('Noidea', 'No idea')], max_length=16),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='not_like_method_forums',
            field=models.CharField(choices=[('', '-----'), ('StronglyAgree', 'Strongly Agree'), ('Agree', 'Agree'), ('Neutral', 'Neutral'), ('Disagree', 'Disagree'), ('StronglyDisagree', 'Strongly Disagree'), ('Noidea', 'No idea')], max_length=16),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='not_like_reveal_identity',
            field=models.CharField(choices=[('', '-----'), ('StronglyAgree', 'Strongly Agree'), ('Agree', 'Agree'), ('Neutral', 'Neutral'), ('Disagree', 'Disagree'), ('StronglyDisagree', 'Strongly Disagree'), ('Noidea', 'No idea')], max_length=16),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='not_self_explanatory',
            field=models.CharField(choices=[('', '-----'), ('StronglyAgree', 'Strongly Agree'), ('Agree', 'Agree'), ('Neutral', 'Neutral'), ('Disagree', 'Disagree'), ('StronglyDisagree', 'Strongly Disagree'), ('Noidea', 'No idea')], max_length=16),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='num_of_experts_req',
            field=models.CharField(choices=[('', '-----'), ('1to10', '1 to 10'), ('11to20', '11 to 20'), ('21to30', '21 to 30'), ('31to40', '31 to 40'), ('above40', 'Above 40')], max_length=7),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='other_language',
            field=models.CharField(choices=[('', '-----'), ('StronglyAgree', 'Strongly Agree'), ('Agree', 'Agree'), ('Neutral', 'Neutral'), ('Disagree', 'Disagree'), ('StronglyDisagree', 'Strongly Disagree'), ('Noidea', 'No idea')], max_length=16),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='overall_arrangement',
            field=models.CharField(choices=[('', '-----'), ('Excellent', 'Excellent'), ('Good', 'Good'), ('Fair', 'Fair'), ('Bad', 'Bad'), ('Extremelybad', 'Extremely bad')], max_length=12),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='overall_video_quality',
            field=models.CharField(choices=[('', '-----'), ('Excellent', 'Excellent'), ('Good', 'Good'), ('Fair', 'Fair'), ('Bad', 'Bad'), ('Extremelybad', 'Extremely bad')], max_length=12),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='pace_of_tutorial',
            field=models.CharField(choices=[('', '-----'), ('Excellent', 'Excellent'), ('Good', 'Good'), ('Fair', 'Fair'), ('Bad', 'Bad'), ('Extremelybad', 'Extremely bad')], max_length=12),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='participated_before',
            field=models.CharField(choices=[('', '-----'), ('Yes', 'Yes'), ('No', 'No')], max_length=3),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='people_management',
            field=models.CharField(choices=[('', '-----'), ('Notconfidentatall', 'Not confident at all'), ('Unconfident', 'Unconfident'), ('Neitherconfidentnorunconfident', 'Neither confident nor unconfident'), ('Confident', 'Confident'), ('Absolutelyconfident', 'Absolutely confident'), ('NotApplicable', 'Not Applicable')], max_length=30),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='per_asked_ques_before_tuts',
            field=models.CharField(choices=[('', '-----'), ('StronglyAgree', 'Strongly Agree'), ('Agree', 'Agree'), ('Neutral', 'Neutral'), ('Disagree', 'Disagree'), ('StronglyDisagree', 'Strongly Disagree'), ('Noidea', 'No idea')], max_length=16),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='possible_to_use_therotical',
            field=models.CharField(choices=[('', '-----'), ('StronglyAgree', 'Strongly Agree'), ('Agree', 'Agree'), ('Neutral', 'Neutral'), ('Disagree', 'Disagree'), ('StronglyDisagree', 'Strongly Disagree'), ('Noidea', 'No idea')], max_length=16),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='purpose_of_attending',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='recommend',
            field=models.CharField(choices=[('', '-----'), ('StronglyAgree', 'Strongly Agree'), ('Agree', 'Agree'), ('Neutral', 'Neutral'), ('Disagree', 'Disagree'), ('StronglyDisagree', 'Strongly Disagree'), ('Noidea', 'No idea')], max_length=16),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='referred_forums',
            field=models.CharField(choices=[('', '-----'), ('StronglyAgree', 'Strongly Agree'), ('Agree', 'Agree'), ('Neutral', 'Neutral'), ('Disagree', 'Disagree'), ('StronglyDisagree', 'Strongly Disagree'), ('Noidea', 'No idea')], max_length=16),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='referred_forums_after',
            field=models.CharField(choices=[('', '-----'), ('StronglyAgree', 'Strongly Agree'), ('Agree', 'Agree'), ('Neutral', 'Neutral'), ('Disagree', 'Disagree'), ('StronglyDisagree', 'Strongly Disagree'), ('Noidea', 'No idea')], max_length=16),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='relevance',
            field=models.CharField(choices=[('', '-----'), ('Excellent', 'Excellent'), ('Good', 'Good'), ('Fair', 'Fair'), ('Bad', 'Bad'), ('Extremelybad', 'Extremely bad')], max_length=12),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='satisfied_with_learning_experience',
            field=models.CharField(choices=[('', '-----'), ('StronglyAgree', 'Strongly Agree'), ('Agree', 'Agree'), ('Neutral', 'Neutral'), ('Disagree', 'Disagree'), ('StronglyDisagree', 'Strongly Disagree'), ('Noidea', 'No idea')], max_length=16),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='side_by_side_hold_intrest',
            field=models.CharField(choices=[('', '-----'), ('StronglyAgree', 'Strongly Agree'), ('Agree', 'Agree'), ('Neutral', 'Neutral'), ('Disagree', 'Disagree'), ('StronglyDisagree', 'Strongly Disagree'), ('Noidea', 'No idea')], max_length=16),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='sim_framework_before',
            field=models.CharField(choices=[('', '-----'), ('Yes', 'Yes'), ('No', 'No')], max_length=3),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='site_management',
            field=models.CharField(choices=[('', '-----'), ('Notconfidentatall', 'Not confident at all'), ('Unconfident', 'Unconfident'), ('Neitherconfidentnorunconfident', 'Neither confident nor unconfident'), ('Confident', 'Confident'), ('Absolutelyconfident', 'Absolutely confident'), ('NotApplicable', 'Not Applicable')], max_length=30),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='spfriendly',
            field=models.CharField(choices=[('', '-----'), ('StronglyAgree', 'Strongly Agree'), ('Agree', 'Agree'), ('Neutral', 'Neutral'), ('Disagree', 'Disagree'), ('StronglyDisagree', 'Strongly Disagree'), ('Noidea', 'No idea')], max_length=16),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='styling_using_themes',
            field=models.CharField(choices=[('', '-----'), ('Notconfidentatall', 'Not confident at all'), ('Unconfident', 'Unconfident'), ('Neitherconfidentnorunconfident', 'Neither confident nor unconfident'), ('Confident', 'Confident'), ('Absolutelyconfident', 'Absolutely confident'), ('NotApplicable', 'Not Applicable')], max_length=30),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='suff_instruction_by_prof',
            field=models.CharField(choices=[('', '-----'), ('StronglyAgree', 'Strongly Agree'), ('Agree', 'Agree'), ('Neutral', 'Neutral'), ('Disagree', 'Disagree'), ('StronglyDisagree', 'Strongly Disagree'), ('Noidea', 'No idea')], max_length=16),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='suff_instruction_by_staff',
            field=models.CharField(choices=[('', '-----'), ('StronglyAgree', 'Strongly Agree'), ('Agree', 'Agree'), ('Neutral', 'Neutral'), ('Disagree', 'Disagree'), ('StronglyDisagree', 'Strongly Disagree'), ('Noidea', 'No idea')], max_length=16),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='suggestions',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='table_of_fields_with_views',
            field=models.CharField(choices=[('', '-----'), ('Notconfidentatall', 'Not confident at all'), ('Unconfident', 'Unconfident'), ('Neitherconfidentnorunconfident', 'Neither confident nor unconfident'), ('Confident', 'Confident'), ('Absolutelyconfident', 'Absolutely confident'), ('NotApplicable', 'Not Applicable')], max_length=30),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='taxonomy',
            field=models.CharField(choices=[('', '-----'), ('Notconfidentatall', 'Not confident at all'), ('Unconfident', 'Unconfident'), ('Neitherconfidentnorunconfident', 'Neither confident nor unconfident'), ('Confident', 'Confident'), ('Absolutelyconfident', 'Absolutely confident'), ('NotApplicable', 'Not Applicable')], max_length=30),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='text_readability',
            field=models.CharField(choices=[('', '-----'), ('Excellent', 'Excellent'), ('Good', 'Good'), ('Fair', 'Fair'), ('Bad', 'Bad'), ('Extremelybad', 'Extremely bad')], max_length=12),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='time_for_handson',
            field=models.CharField(choices=[('', '-----'), ('Excellent', 'Excellent'), ('Good', 'Good'), ('Fair', 'Fair'), ('Bad', 'Bad'), ('Extremelybad', 'Extremely bad')], max_length=12),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='used_sw_before',
            field=models.CharField(choices=[('', '-----'), ('Yes', 'Yes'), ('No', 'No')], max_length=3),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='visual_presentation',
            field=models.CharField(choices=[('', '-----'), ('Excellent', 'Excellent'), ('Good', 'Good'), ('Fair', 'Fair'), ('Bad', 'Bad'), ('Extremelybad', 'Extremely bad')], max_length=12),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='wantto_conduct_incollege',
            field=models.CharField(choices=[('', '-----'), ('StronglyAgree', 'Strongly Agree'), ('Agree', 'Agree'), ('Neutral', 'Neutral'), ('Disagree', 'Disagree'), ('StronglyDisagree', 'Strongly Disagree'), ('Noidea', 'No idea')], max_length=16),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='ws_not_useful',
            field=models.CharField(choices=[('', '-----'), ('StronglyAgree', 'Strongly Agree'), ('Agree', 'Agree'), ('Neutral', 'Neutral'), ('Disagree', 'Disagree'), ('StronglyDisagree', 'Strongly Disagree'), ('Noidea', 'No idea')], max_length=16),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedbackpost',
            name='ws_quality',
            field=models.CharField(choices=[('', '-----'), ('Excellent', 'Excellent'), ('Good', 'Good'), ('Fair', 'Fair'), ('Bad', 'Bad'), ('Extremelybad', 'Extremely bad')], max_length=12),
        ),
        migrations.RunSQL("SET sql_mode='STRICT_TRANS_TABLES';"),
    ]
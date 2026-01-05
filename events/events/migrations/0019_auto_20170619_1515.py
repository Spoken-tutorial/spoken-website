# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0018_auto_20170615_1654'),
    ]

    operations = [
        migrations.AddField(
            model_name='stworkshopfeedback',
            name='content_any_comment',
            field=models.CharField(default=None, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stworkshopfeedback',
            name='learning_any_comment',
            field=models.CharField(default=None, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stworkshopfeedback',
            name='training_any_comment',
            field=models.CharField(default=None, max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='stworkshopfeedback',
            name='acquired_knowledge',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree')]),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedback',
            name='desired_objective',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree')]),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedback',
            name='diff_instruction',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree')]),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedback',
            name='difficult_simultaneously',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree')]),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedback',
            name='examples_help',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree')]),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedback',
            name='forum_helpful',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree')]),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedback',
            name='gender',
            field=models.CharField(max_length=10),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedback',
            name='help_improve_performance',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree')]),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedback',
            name='instructions_easy_to_follow',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree')]),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedback',
            name='interface_comfortable',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree')]),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedback',
            name='like_to_part',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree')]),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedback',
            name='logical_sequence',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree')]),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedback',
            name='method_easy',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree')]),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedback',
            name='not_like_method_forums',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree')]),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedback',
            name='not_self_explanatory',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree')]),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedback',
            name='owing_to_forums',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree')]),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedback',
            name='plan_to_use_future',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree')]),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedback',
            name='recommend',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree')]),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedback',
            name='satisfied',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree')]),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedback',
            name='self_learning_intrest',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree')]),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedback',
            name='side_by_side_effective',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree')]),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedback',
            name='suff_instruction',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree')]),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedback',
            name='time_sufficient',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree')]),
        ),
        migrations.AlterField(
            model_name='stworkshopfeedback',
            name='useful_learning',
            field=models.CharField(max_length=50, choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree')]),
        ),
    ]

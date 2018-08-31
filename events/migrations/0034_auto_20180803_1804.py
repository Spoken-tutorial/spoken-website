# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0033_auto_20180724_1712'),
    ]

    operations = [
        migrations.AddField(
            model_name='stworkshopfeedback',
            name='confident_to_apply_knowledge',
            field=models.CharField(default=None, max_length=50, choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree')]),
        ),
        migrations.AddField(
            model_name='stworkshopfeedback',
            name='designation',
            field=models.CharField(default=None, max_length=100),
        ),
        migrations.AddField(
            model_name='stworkshopfeedback',
            name='difficult_instructions_in_tutorial',
            field=models.CharField(default=None, max_length=50, choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree')]),
        ),
        migrations.AddField(
            model_name='stworkshopfeedback',
            name='dont_like_self_learning_method',
            field=models.CharField(default=None, max_length=50, choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree')]),
        ),
        migrations.AddField(
            model_name='stworkshopfeedback',
            name='educational_back',
            field=models.CharField(default=None, max_length=100),
        ),
        migrations.AddField(
            model_name='stworkshopfeedback',
            name='language_diff_to_understand',
            field=models.CharField(default=None, max_length=50, choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree')]),
        ),
        migrations.AddField(
            model_name='stworkshopfeedback',
            name='language_of_tutorial',
            field=models.CharField(default=None, max_length=20),
        ),
        migrations.AddField(
            model_name='stworkshopfeedback',
            name='too_fast',
            field=models.CharField(default=None, max_length=50, choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree')]),
        ),
        migrations.AddField(
            model_name='stworkshopfeedback',
            name='too_slow',
            field=models.CharField(default=None, max_length=50, choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree')]),
        ),
        migrations.AddField(
            model_name='stworkshopfeedback',
            name='translate',
            field=models.CharField(default=None, max_length=50, choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree')]),
        ),
    ]

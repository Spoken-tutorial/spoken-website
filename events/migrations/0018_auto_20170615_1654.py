# -*- coding: utf-8 -*-


from django.db import models, migrations
import datetime
from datetime import timezone
utc = timezone.utc


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0008_auto_20170605_1302'),
        ('events', '0017_trainingrequest_course_type'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stworkshopfeedback',
            old_name='confident',
            new_name='forum_helpful',
        ),
        migrations.RenameField(
            model_name='stworkshopfeedback',
            old_name='name1',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='stworkshopfeedback',
            old_name='other_language',
            new_name='not_like_method_forums',
        ),
        migrations.RemoveField(
            model_name='stworkshopfeedback',
            name='arrangement',
        ),
        migrations.RemoveField(
            model_name='stworkshopfeedback',
            name='installation_difficulties',
        ),
        migrations.RemoveField(
            model_name='stworkshopfeedback',
            name='installation_help',
        ),
        migrations.RemoveField(
            model_name='stworkshopfeedback',
            name='installed',
        ),
        migrations.RemoveField(
            model_name='stworkshopfeedback',
            name='interaction_using_forum',
        ),
        migrations.RemoveField(
            model_name='stworkshopfeedback',
            name='network',
        ),
        migrations.AddField(
            model_name='stworkshopfeedback',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2017, 6, 15, 11, 22, 17, 188664, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stworkshopfeedback',
            name='foss',
            field=models.ForeignKey(default=22, to='creation.FossCategory', on_delete=models.deletion.PROTECT),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stworkshopfeedback',
            name='owing_to_forums',
            field=models.CharField(default=1, max_length=50, choices=[(b'', b'-----'), (b'StronglyAgree', b'Strongly Agree'), (b'Agree', b'Agree'), (b'Neutral', b'Neutral'), (b'Disagree', b'Disagree'), (b'StronglyDisagree', b'Strongly Disagree'), (b'Noidea', b'No idea')]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stworkshopfeedback',
            name='venue',
            field=models.CharField(default=0, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stworkshopfeedback',
            name='workshop_date',
            field=models.DateField(default=datetime.datetime(2017, 6, 15, 11, 24, 8, 676738, tzinfo=utc)),
            preserve_default=False,
        ),
    ]

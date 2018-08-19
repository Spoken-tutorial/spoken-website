# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('creation', '0013_auto_20180818_0845'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContributorRating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rating', models.PositiveIntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])),
                ('language', models.ForeignKey(to='creation.Language')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TutorialsAvailable',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.ForeignKey(to='creation.Language')),
                ('tutorial_detail', models.ForeignKey(to='creation.TutorialDetail')),
            ],
        ),
        migrations.AddField(
            model_name='contributorrole',
            name='tutorial_detail',
            field=models.ForeignKey(to='creation.TutorialDetail', null=True),
        ),
        migrations.AddField(
            model_name='tutorialresource',
            name='assignment_status',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='tutorialresource',
            name='extension_status',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='tutorialresource',
            name='submissiondate',
            field=models.DateTimeField(default=b'2000-01-02', blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='tutorialsavailable',
            unique_together=set([('tutorial_detail', 'language')]),
        ),
        migrations.AlterUniqueTogether(
            name='contributorrating',
            unique_together=set([('user', 'language')]),
        ),
    ]

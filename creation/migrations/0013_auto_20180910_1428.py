# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import datetime


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('creation', '0012_tutorialresource_publish_at'),
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
            name='LanguageManager',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.BooleanField(default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('language', models.ForeignKey(to='creation.Language')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('user', 'language'),
            },
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
            model_name='rolerequest',
            name='language',
            field=models.ForeignKey(to='creation.Language', null=True),
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
            field=models.DateTimeField(default=datetime.datetime(2000, 1, 2, 12, 0), blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='contributorrole',
            unique_together=set([('user', 'tutorial_detail', 'language')]),
        ),
        migrations.AlterUniqueTogether(
            name='rolerequest',
            unique_together=set([('user', 'role_type', 'language')]),
        ),
        migrations.AlterUniqueTogether(
            name='tutorialsavailable',
            unique_together=set([('tutorial_detail', 'language')]),
        ),
        migrations.AlterUniqueTogether(
            name='languagemanager',
            unique_together=set([('user', 'language')]),
        ),
        migrations.AlterUniqueTogether(
            name='contributorrating',
            unique_together=set([('user', 'language')]),
        ),
    ]

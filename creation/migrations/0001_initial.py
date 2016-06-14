# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminReviewerNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('message', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='AdminReviewLog',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('status', models.PositiveSmallIntegerField()),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ArchivedVideo',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('version', models.PositiveSmallIntegerField(default=0)),
                ('video', models.CharField(max_length=255)),
                ('atype', models.PositiveSmallIntegerField(default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Collaborate',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('contact_number', models.CharField(null=True, max_length=20)),
                ('institution_name', models.CharField(max_length=255)),
                ('foss_name', models.CharField(max_length=255)),
                ('are_you_one', models.CharField(max_length=255)),
                ('howmuch_time', models.PositiveIntegerField()),
                ('availability_constraints', models.TextField(null=True, blank=True)),
                ('is_reviewer', models.BooleanField()),
                ('contribs_foss', models.TextField(null=True, blank=True)),
                ('educational_qualifications', models.TextField(null=True, blank=True)),
                ('prof_experience', models.CharField(null=True, blank=True, max_length=255)),
                ('lang_contributor', models.BooleanField()),
                ('lead_st', models.BooleanField()),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ContributeTowards',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='ContributorLog',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('component', models.CharField(max_length=255)),
                ('status', models.PositiveSmallIntegerField()),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ContributorNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('message', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ContributorRole',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('status', models.BooleanField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Contributor Role',
            },
        ),
        migrations.CreateModel(
            name='DomainReviewerNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('message', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='DomainReviewerRole',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('status', models.BooleanField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Domain Reviewer Role',
            },
        ),
        migrations.CreateModel(
            name='DomainReviewLog',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('component', models.CharField(max_length=255)),
                ('status', models.PositiveSmallIntegerField()),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='FossAvailableForTest',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('status', models.BooleanField(default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='FossAvailableForWorkshop',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('status', models.BooleanField(default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='FossCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('foss', models.CharField(unique=True, max_length=255)),
                ('description', models.TextField()),
                ('status', models.BooleanField(max_length=2)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'FOSS Categorie',
                'ordering': ('foss',),
            },
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('code', models.CharField(default=b'en', max_length=10)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Level',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('level', models.CharField(max_length=255)),
                ('code', models.CharField(max_length=10)),
            ],
            options={
                'verbose_name': 'Tutorial Level',
            },
        ),
        migrations.CreateModel(
            name='NeedImprovementLog',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('review_state', models.PositiveSmallIntegerField()),
                ('component', models.CharField(max_length=50)),
                ('comment', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='OperatingSystem',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='PlaylistInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('playlist_id', models.CharField(max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('foss', models.ForeignKey(to='creation.FossCategory')),
                ('language', models.ForeignKey(to='creation.Language')),
            ],
            options={
                'verbose_name': 'Playlist Info',
            },
        ),
        migrations.CreateModel(
            name='PlaylistItem',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('item_id', models.CharField(max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('playlist', models.ForeignKey(to='creation.PlaylistInfo')),
            ],
            options={
                'verbose_name': 'Playlist Item',
            },
        ),
        migrations.CreateModel(
            name='PublicReviewLog',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='PublishTutorialLog',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='QualityReviewerNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('message', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='QualityReviewerRole',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('status', models.BooleanField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('foss_category', models.ForeignKey(to='creation.FossCategory')),
                ('language', models.ForeignKey(to='creation.Language')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Quality Reviewer Role',
            },
        ),
        migrations.CreateModel(
            name='QualityReviewLog',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('component', models.CharField(max_length=255)),
                ('status', models.PositiveSmallIntegerField()),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='RoleRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('role_type', models.IntegerField(default=0)),
                ('status', models.PositiveSmallIntegerField(default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('approved_user', models.ForeignKey(null=True, blank=True, related_name='approved_user', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='user')),
            ],
        ),
        migrations.CreateModel(
            name='SuggestExample',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('topic_title', models.CharField(max_length=255)),
                ('example_description', models.TextField()),
                ('script_writer', models.BooleanField()),
                ('is_reviewer', models.BooleanField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SuggestTopic',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('topic_title', models.CharField(max_length=255)),
                ('brief_description', models.TextField()),
                ('example_suggestion', models.BooleanField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('difficulty_level', models.ForeignKey(to='creation.Level')),
                ('operating_system', models.ManyToManyField(to='creation.OperatingSystem')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TutorialCommonContent',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('slide', models.CharField(max_length=255)),
                ('slide_status', models.PositiveSmallIntegerField(default=0)),
                ('code', models.CharField(max_length=255)),
                ('code_status', models.PositiveSmallIntegerField(default=0)),
                ('assignment', models.CharField(max_length=255)),
                ('assignment_status', models.PositiveSmallIntegerField(default=0)),
                ('prerequisite_status', models.PositiveSmallIntegerField(default=0)),
                ('keyword', models.TextField()),
                ('keyword_status', models.PositiveSmallIntegerField(default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('assignment_user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='assignments')),
                ('code_user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='codes')),
                ('keyword_user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='keywords')),
            ],
            options={
                'verbose_name': 'Tutorial Common Content',
            },
        ),
        migrations.CreateModel(
            name='TutorialDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('tutorial', models.CharField(max_length=255)),
                ('order', models.IntegerField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('foss', models.ForeignKey(to='creation.FossCategory')),
                ('level', models.ForeignKey(to='creation.Level')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Tutorial Detail',
            },
        ),
        migrations.CreateModel(
            name='TutorialMissingComponent',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('component', models.PositiveSmallIntegerField()),
                ('report_type', models.BooleanField(default=0)),
                ('remarks', models.TextField(null=True, blank=True)),
                ('inform_me', models.BooleanField(default=0)),
                ('email', models.CharField(null=True, blank=True, max_length=255)),
                ('reply_status', models.BooleanField(default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='TutorialMissingComponentReply',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('reply_message', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('missing_component', models.ForeignKey(to='creation.TutorialMissingComponent')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TutorialResource',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('outline', models.TextField()),
                ('outline_status', models.PositiveSmallIntegerField(default=0)),
                ('script', models.URLField(max_length=255)),
                ('script_status', models.PositiveSmallIntegerField(default=0)),
                ('timed_script', models.URLField(max_length=255)),
                ('video', models.CharField(max_length=255)),
                ('video_id', models.CharField(null=True, blank=True, default=None, max_length=255)),
                ('playlist_item_id', models.CharField(null=True, blank=True, default=None, max_length=255)),
                ('video_thumbnail_time', models.TimeField(default=b'00:00:00')),
                ('video_status', models.PositiveSmallIntegerField(default=0)),
                ('status', models.PositiveSmallIntegerField(default=0)),
                ('version', models.PositiveSmallIntegerField(default=0)),
                ('hit_count', models.PositiveIntegerField(default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('common_content', models.ForeignKey(to='creation.TutorialCommonContent')),
                ('language', models.ForeignKey(to='creation.Language')),
                ('outline_user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='outlines')),
                ('script_user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='scripts')),
                ('tutorial_detail', models.ForeignKey(to='creation.TutorialDetail')),
                ('video_user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='videos')),
            ],
        ),
        migrations.AddField(
            model_name='tutorialmissingcomponent',
            name='tutorial_resource',
            field=models.ForeignKey(to='creation.TutorialResource'),
        ),
        migrations.AddField(
            model_name='tutorialmissingcomponent',
            name='user',
            field=models.ForeignKey(null=True, blank=True, related_name='raised_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='tutorialcommoncontent',
            name='prerequisite',
            field=models.ForeignKey(null=True, blank=True, related_name='prerequisite', to='creation.TutorialDetail'),
        ),
        migrations.AddField(
            model_name='tutorialcommoncontent',
            name='prerequisite_user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='prerequisite'),
        ),
        migrations.AddField(
            model_name='tutorialcommoncontent',
            name='slide_user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='slides'),
        ),
        migrations.AddField(
            model_name='tutorialcommoncontent',
            name='tutorial_detail',
            field=models.OneToOneField(related_name='tutorial_detail', to='creation.TutorialDetail'),
        ),
        migrations.AddField(
            model_name='qualityreviewlog',
            name='tutorial_resource',
            field=models.ForeignKey(to='creation.TutorialResource'),
        ),
        migrations.AddField(
            model_name='qualityreviewlog',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='qualityreviewernotification',
            name='tutorial_resource',
            field=models.ForeignKey(to='creation.TutorialResource'),
        ),
        migrations.AddField(
            model_name='qualityreviewernotification',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='publishtutoriallog',
            name='tutorial_resource',
            field=models.ForeignKey(to='creation.TutorialResource'),
        ),
        migrations.AddField(
            model_name='publishtutoriallog',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='publicreviewlog',
            name='tutorial_resource',
            field=models.ForeignKey(to='creation.TutorialResource'),
        ),
        migrations.AddField(
            model_name='publicreviewlog',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='needimprovementlog',
            name='tutorial_resource',
            field=models.ForeignKey(to='creation.TutorialResource'),
        ),
        migrations.AddField(
            model_name='needimprovementlog',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='fossavailableforworkshop',
            name='foss',
            field=models.ForeignKey(to='creation.FossCategory'),
        ),
        migrations.AddField(
            model_name='fossavailableforworkshop',
            name='language',
            field=models.ForeignKey(to='creation.Language'),
        ),
        migrations.AddField(
            model_name='fossavailablefortest',
            name='foss',
            field=models.ForeignKey(to='creation.FossCategory'),
        ),
        migrations.AddField(
            model_name='fossavailablefortest',
            name='language',
            field=models.ForeignKey(to='creation.Language'),
        ),
        migrations.AddField(
            model_name='domainreviewlog',
            name='tutorial_resource',
            field=models.ForeignKey(to='creation.TutorialResource'),
        ),
        migrations.AddField(
            model_name='domainreviewlog',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='domainreviewerrole',
            name='foss_category',
            field=models.ForeignKey(to='creation.FossCategory'),
        ),
        migrations.AddField(
            model_name='domainreviewerrole',
            name='language',
            field=models.ForeignKey(to='creation.Language'),
        ),
        migrations.AddField(
            model_name='domainreviewerrole',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='domainreviewernotification',
            name='tutorial_resource',
            field=models.ForeignKey(to='creation.TutorialResource'),
        ),
        migrations.AddField(
            model_name='domainreviewernotification',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='contributorrole',
            name='foss_category',
            field=models.ForeignKey(to='creation.FossCategory'),
        ),
        migrations.AddField(
            model_name='contributorrole',
            name='language',
            field=models.ForeignKey(to='creation.Language'),
        ),
        migrations.AddField(
            model_name='contributorrole',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='contributornotification',
            name='tutorial_resource',
            field=models.ForeignKey(to='creation.TutorialResource'),
        ),
        migrations.AddField(
            model_name='contributornotification',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='contributorlog',
            name='tutorial_resource',
            field=models.ForeignKey(to='creation.TutorialResource'),
        ),
        migrations.AddField(
            model_name='contributorlog',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='collaborate',
            name='contribute_towards',
            field=models.ManyToManyField(to='creation.ContributeTowards'),
        ),
        migrations.AddField(
            model_name='collaborate',
            name='language',
            field=models.ForeignKey(to='creation.Language'),
        ),
        migrations.AddField(
            model_name='collaborate',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='archivedvideo',
            name='tutorial_resource',
            field=models.ForeignKey(to='creation.TutorialResource'),
        ),
        migrations.AddField(
            model_name='archivedvideo',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='adminreviewlog',
            name='tutorial_resource',
            field=models.ForeignKey(to='creation.TutorialResource'),
        ),
        migrations.AddField(
            model_name='adminreviewlog',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='adminreviewernotification',
            name='tutorial_resource',
            field=models.ForeignKey(to='creation.TutorialResource'),
        ),
        migrations.AddField(
            model_name='adminreviewernotification',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='tutorialresource',
            unique_together=set([('tutorial_detail', 'language')]),
        ),
        migrations.AlterUniqueTogether(
            name='tutorialdetail',
            unique_together=set([('foss', 'tutorial', 'level')]),
        ),
        migrations.AlterUniqueTogether(
            name='rolerequest',
            unique_together=set([('user', 'role_type')]),
        ),
        migrations.AlterUniqueTogether(
            name='qualityreviewerrole',
            unique_together=set([('user', 'foss_category', 'language')]),
        ),
        migrations.AlterUniqueTogether(
            name='playlistitem',
            unique_together=set([('playlist', 'item_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='playlistinfo',
            unique_together=set([('foss', 'language')]),
        ),
        migrations.AlterUniqueTogether(
            name='fossavailableforworkshop',
            unique_together=set([('foss', 'language')]),
        ),
        migrations.AlterUniqueTogether(
            name='fossavailablefortest',
            unique_together=set([('foss', 'language')]),
        ),
        migrations.AlterUniqueTogether(
            name='domainreviewerrole',
            unique_together=set([('user', 'foss_category', 'language')]),
        ),
        migrations.AlterUniqueTogether(
            name='contributorrole',
            unique_together=set([('user', 'foss_category', 'language')]),
        ),
    ]

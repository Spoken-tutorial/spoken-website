# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0012_tutorialresource_publish_at'),
        ('events', '0035_auto_20180806_1709'),
    ]

    operations = [
        migrations.CreateModel(
            name='MediaTestimonials',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('path', models.CharField(max_length=255)),
                ('user', models.CharField(max_length=255)),
                ('content', models.CharField(max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('foss', models.ForeignKey(to='creation.FossCategory', on_delete=models.deletion.PROTECT)),
            ],
            options={
                'verbose_name': 'Media Testimonials',
                'verbose_name_plural': 'Media Testimonials',
            },
        ),
        migrations.AlterField(
            model_name='testimonials',
            name='created',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]

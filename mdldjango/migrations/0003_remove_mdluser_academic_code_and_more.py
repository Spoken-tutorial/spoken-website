# Generated by Django 5.1.6 on 2025-03-18 11:20

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("mdldjango", "0002_auto_20190531_0547"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="mdluser",
            name="academic_code",
        ),
        migrations.RemoveField(
            model_name="mdluser",
            name="age_range",
        ),
        migrations.RemoveField(
            model_name="mdluser",
            name="aim",
        ),
        migrations.RemoveField(
            model_name="mdluser",
            name="flag",
        ),
        migrations.RemoveField(
            model_name="mdluser",
            name="gender",
        ),
        migrations.RemoveField(
            model_name="mdluser",
            name="icq",
        ),
        migrations.RemoveField(
            model_name="mdluser",
            name="invigilator",
        ),
        migrations.RemoveField(
            model_name="mdluser",
            name="msn",
        ),
        migrations.RemoveField(
            model_name="mdluser",
            name="organizer",
        ),
        migrations.RemoveField(
            model_name="mdluser",
            name="skype",
        ),
        migrations.RemoveField(
            model_name="mdluser",
            name="url",
        ),
        migrations.RemoveField(
            model_name="mdluser",
            name="yahoo",
        ),
    ]

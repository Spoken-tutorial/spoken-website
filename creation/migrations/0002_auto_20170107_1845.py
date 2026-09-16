# -*- coding: utf-8 -*-


# Third Party Stuff
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('creation', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tutorialcommoncontent',
            name='additional_material',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='tutorialcommoncontent',
            name='additional_material_status',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='tutorialcommoncontent',
            name='additional_material_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='additional_material', default=None, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]

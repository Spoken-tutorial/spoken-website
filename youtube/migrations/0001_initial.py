# -*- coding: utf-8 -*-


# Third Party Stuff
#import oauth2client.django_orm
from oauthlib.oauth2 import ClientCredentialsGrant

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    # operations = [
    #     migrations.CreateModel(
    #         name='CredentialsModel',
    #         fields=[
    #             ('id', models.OneToOneField(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
    #             ('credential', ClientCredentialsGrant(null=True)),
    #         ]
    #         ,
    #     ),
    # ]

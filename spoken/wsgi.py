"""
WSGI config for spoken project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

# Standard Library
import os

# Third Party Stuff
from django.core.wsgi import get_wsgi_application

os.environ["DJANGO_SETTINGS_MODULE"] = "spoken.settings"

application = get_wsgi_application()

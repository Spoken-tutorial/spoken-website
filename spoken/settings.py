"""
Django settings for spoken project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from os.path import *
from config import *
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SCRIPT_URL = SCRIPT_URL

STVIDEOS_DIR = STVIDEOS_PATH
SEARCH_INDEX_DIR = os.path.join(BASE_DIR, INDEX_PATH)
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'l0j--m7k_7v4pr&wg7^)f8ptu^gcs7ec5eu9=x8k_@+20c^ym#'

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
    'django.contrib.auth.hashers.UnsaltedMD5PasswordHasher',
)

# email errors and 404
SERVER_EMAIL = 'error-report@spoken-tutorial.org'
ADMINS = (
    ('Administrator', 'administrator@spoken-tutorial.org'),
    ('vishnuraj', 'vishnukraj007@gmail.com'),
)

MANAGERS = (
    ('Administrator', 'administrator@spoken-tutorial.org'),
    ('vishnuraj', 'vishnukraj007@gmail.com'),
)

ADMINISTRATOR_EMAIL = ADMINISTRATOR_EMAIL

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = DEBUG_MODE
COMPRESS_ENABLED = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.redirects',
    'django_extensions',
    'widget_tweaks',
    'captcha',
    'nicedit',
    'report_builder',
    'compressor',

    'cms',
    'cdeep',
    'creation',
    'statistics',
    'cdcontent',
    'events',
    'mdldjango',
    'masquerade',
    'youtube',
    'reports',
)

MIDDLEWARE_CLASSES = (
    #'django.middleware.cache.UpdateCacheMiddleware',
    'htmlmin.middleware.HtmlMinifyMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.common.BrokenLinkEmailsMiddleware',
    'masquerade.middleware.MasqueradeMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
    #'django.middleware.cache.FetchFromCacheMiddleware',
    'htmlmin.middleware.MarkRequestMiddleware',
)

ROOT_URLCONF = 'spoken.urls'

WSGI_APPLICATION = 'spoken.wsgi.application'

# for django.contrib.sites
SITE_ID = 1

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',    # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': DB,                        # Or path to database file if using sqlite3.

        # The following settings are not used with sqlite3:
        'USER': DB_USER,
        'PASSWORD': DB_PASS,
        'HOST': '',                            # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                            # Set to empty string for default.
    },
    'moodle': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': MDB,                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': MDB_USER,
        'PASSWORD': MDB_PASS,
        'HOST': '',                  # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                  # Set to empty string for default.
    },
    'cdeep': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': CDB,                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': CDB_USER,
        'PASSWORD': CDB_PASS,
        'HOST': '',                  # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                  # Set to empty string for default.
    },
    'workshop_info': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': WDB,                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': WDB_USER,
        'PASSWORD': WDB_PASS,
        'HOST': '',                  # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                  # Set to empty string for default.
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Calcutta'

USE_I18N = True

USE_L10N = True

USE_TZ = TZ_STATUS

#events settings
ONLINE_TEST_URL = ONLINE_TEST_URL
KEEP_LOGGED_DURATION = 604800
# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/') # Absolute path to the media.

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_ROOT = BASE_DIR + '/static/'

STATIC_URL = '/static/'

COMPRESS_ROOT = STATIC_ROOT
COMPRESS_URL = STATIC_URL

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    BASE_DIR + '/static/',
)

STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    #BASE_DIR + '/static/',
)

#debugging 
#INSTALLED_APPS = INSTALLED_APPS + ('debug_toolbar',)
INTERNAL_IPS = ('127.0.0.1',)

#Moodle Auth
#AUTH_USER_MODEL = 'mdldjango.Users'
DATABASE_ROUTERS = ['mdldjango.router.MdlRouter', 'cdeep.router.CdeepRouter', 'workshop.router.WorkshopRouter']
#AUTHENTICATION_BACKENDS = ( 'mdldjango.backend.MdlBackend', )

# Reports
REPORT_BUILDER_INCLUDE = []
REPORT_BUILDER_EXCLUDE = ['user'] # Allow all models except User to be accessed
REPORT_BUILDER_ASYNC_REPORT = False
#template
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request"
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

COMPRESS_CSS_FILTERS = (
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.CSSMinFilter',
)
"""CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake'
    }
}"""

HTML_MINIFY = HTML_MINIFY
RECAPTCHA_PUBLIC_KEY = '6Le8qf8SAAAAABV9wYBW99Jotv-EygJXIhMa_n54'
RECAPTCHA_PRIVATE_KEY = '6Le8qf8SAAAAAF9CkucURPapw2vaDPrU4qMzfg73'
RECAPTCHA_USE_SSL = True
ACADEMIC_DURATION = 5

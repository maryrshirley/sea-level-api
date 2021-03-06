"""
Django settings for sea-level api, common to all environments.

The policy here is that if a setting is truly environment-specific, such
as DEBUG, we should set it to the most secure option here, and let other
environments override. Sometimes the most secure is not to include it,
like SECRET_KEY

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys
from os.path import abspath, dirname, join as pjoin

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

DSN = os.environ.get('DSN', None)


BASE_DIR = abspath(pjoin(dirname(__file__), '..'))

sys.path.append(pjoin(BASE_DIR, 'apps'))
sys.path.append(pjoin(BASE_DIR, 'libs'))

SECRET_KEY = os.environ.get('SECRET_KEY', None)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = TEMPLATE_DEBUG = False

ADMINS = (
    ('Heroku Admins', 'herokuadmins@sealevelresearch.com'),
)

MANAGERS = (
    ('Heroku Managers', 'herokmanagers@sealevelresearch.com'),
)

# https://docs.djangoproject.com/en/1.7/ref/settings/#server-email
SERVER_EMAIL = 'heroku@sealevelresearch.com'

# Amazon SES settings
EMAIL_HOST = 'email-smtp.us-west-2.amazonaws.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False


ALLOWED_HOSTS = [
    'api.sealevelresearch.com',
    'api-staging.sealevelresearch.com',
    'sea-level-api.herokuapp.com',
    'sea-level-api-staging.herokuapp.com',
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'nopassword',


    'api.apps.predictions',
    'api.apps.locations',
    'api.apps.observations',
    'api.apps.sea_levels',
    'api.apps.status',
    'api.apps.debug',
    'api.apps.surge_model_converter',
    'api.apps.tide_gauges',
    'api.apps.users',
    'api.apps.authentication',
    'api.apps.vessel',
    'api.apps.schedule',
    'api.apps.notifications',

    'api.libs.minute_in_time',
]

if DSN:
    import raven
    RAVEN_RELEASE = os.environ.get('SOURCE_VERSION', None)

    if not RAVEN_RELEASE:
        RAVEN_RELEASE = raven.fetch_git_sha(BASE_DIR + '/..')

    RAVEN_CONFIG = {
        'dsn': DSN,
        'release': RAVEN_RELEASE,
    }
    INSTALLED_APPS.append('raven.contrib.django.raven_compat')

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'api.urls'

WSGI_APPLICATION = 'api.wsgi.application'

TEMPLATE_DIRS = (
    pjoin(BASE_DIR, 'template'),
)

# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

# eg postgres://user3123:pass123@database.foo.com:6212/db982398

if 'DATABASE_URL' in os.environ:
    DATABASE_URL = urlparse(os.environ['DATABASE_URL'])
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': DATABASE_URL.path[1:],
            'USER': DATABASE_URL.username,
            'PASSWORD': DATABASE_URL.password,
            'HOST': DATABASE_URL.hostname,
            'PORT': DATABASE_URL.port,
        }
    }
else:
    DATABASES = None

# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:00Z'
SLUG_REGEX = '[a-z0-9-]+'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/

STATIC_URL = '/static/'

REST_FRAMEWORK = {
    # Use hyperlinked styles by default.
    # Only used if the `serializer_class` attribute is not set on a view.
    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rest_framework.serializers.HyperlinkedModelSerializer',

    'DATETIME_INPUT_FORMATS': [DATETIME_FORMAT],

    # http://www.django-rest-framework.org/api-guide/authentication
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),

    # http://www.django-rest-framework.org/api-guide/permissions
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly'
    ]
}

# Cross-origin Resource Sharing (CORS)
# See https://github.com/ottoyiu/django-cors-headers/ and
#     http://www.html5rocks.com/en/tutorials/cors/

CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_METHODS = (
    'GET',
    'OPTIONS',
)

CORS_ALLOW_CREDENTIALS = False

CORS_PREFLIGHT_MAX_AGE = 3 * 3600

EMAIL_AUTHENTICATION_BACKENDS = \
    ['api.apps.authentication.backends.email.EmailBackend']
AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend'] \
    + EMAIL_AUTHENTICATION_BACKENDS

NOPASSWORD_HIDE_USERNAME = True
NOPASSWORD_TWILIO_SID = os.environ.get('NOPASSWORD_TWILIO_SID', None)
NOPASSWORD_TWILIO_AUTH_TOKEN = os.environ.get('NOPASSWORD_TWILIO_AUTH_TOKEN',
                                              None)
DEFAULT_FROM_NUMBER = os.environ.get('DEFAULT_FROM_NUMBER', None)
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', None)

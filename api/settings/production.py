from .common import *

import os

STATIC_ROOT = os.path.join(BASE_DIR, 'static_collected')
STATIC_URL = '/static/'

# Logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': ("[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s]"
                       " %(message)s"),
            'datefmt': "%d-%b-%y %H:%M:%S"
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,  # also handle in parent handler
        },

        'django.db.backends': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },

        'api.apps': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'api.libs': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

if os.environ.get('EMERGENCY_DEBUG', 'false') == 'true':
    DEBUG = True
    TEMPLATE_DEBUG = True
    INSTALLED_APPS += ('debug_toolbar.apps.DebugToolbarConfig',)
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK':
        'api.settings.production.show_toolbar_callback'
    }


def show_toolbar_callback(request):
    return DEBUG is True

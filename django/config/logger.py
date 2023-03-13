import logging
import os
import json_log_formatter
import logging
from django.utils.timezone import now

from config import settings

from .settings_prom import  BASE_DIR
from .settings_prom import DEBUG

# Usage in other modules:
#
#     from djangoproject.logger import log
#     log.info('some output')
#
# Note, doing this manually in other modules results in nicer output:
#
#     import logging
#     log = logging.getLogger(__name__)
#     log.info('some output')

# the basic logger other apps can import
log = logging.getLogger(__name__)

# the minimum reported level
if DEBUG:
    min_level = 'DEBUG'
else:
    min_level = 'INFO'

# the minimum reported level for Django's modules
# optionally set to DEBUG to see database queries etc.
# or set to min_level to control it using the DEBUG flag
min_django_level = 'INFO'







class CustomisedJSONFormatter(json_log_formatter.JSONFormatter):
    def json_record(self, message: str, extra: dict, record: logging.LogRecord):
        context = extra
        django = {
            'app': 'django',
            'name': record.name,
            'filename': record.filename,
            'funcName': record.funcName,
            'msecs': record.msecs,
        }
        if record.exc_info:
            django['exc_info'] = self.formatException(record.exc_info)
        return {
            'message': message,
            'timestamp': now(),
            'level': record.levelname,
            'context': context,
            'django': django
        }

# logging dictConfig configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # keep Django's default loggers
    'formatters': {
        # see full list of attributes here:
        # https://docs.python.org/3/library/logging.html#logrecord-attributes
        'simple': {
            'format': '[%(asctime)s] %(levelname)s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'verbose': {
            '()': 'config.common.djangocolors_formatter.DjangoColorsFormatter',
            'format': '[%(asctime)s] %(levelname)s [module:%(name)s; func:%(funcName)s; line:%(lineno)d] message:%(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'timestampthread': {
            'format': "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s] [%(name)-20.20s]  %(message)s",
        },
        "json": {
            '()': CustomisedJSONFormatter,
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'logfile': {
            # optionally raise to INFO to not fill the log file too quickly
            'level': min_level,  # this level or higher goes to the log file
            'class': 'logging.handlers.RotatingFileHandler',
            # IMPORTANT: replace with your desired logfile name!
            'filename': os.path.join(BASE_DIR, 'sev_sed.log'),
            'maxBytes': 50 * 10 ** 6,  # will 50 MB do?
            'backupCount': 100,  # keep this many extra historical files
            'formatter': 'timestampthread'
        },
        'console': {
            'level': min_level,  # this level or higher goes to the console
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'logstash': {
            'level': min_level,
            'class': 'logstash.TCPLogstashHandler',
            'host': 'logstash',
            'port': 5044,  # TCP port
            'version': 1,
            'message_type': 'logstash',  # 'type' field in logstash message. Default value: 'logstash'.
            'fqdn': True,  # Fully qualified domain name. Default value: false.
            ##'tags': ['django'],  # list of tags. Default: None.
            # 'formatter': 'json',
        },
    },
    'loggers': {
        'core': {
            'handlers': ['logfile', 'console','logstash'],
            'level': min_level,  # this level or higher goes to the console,
        },
        'document': {
            'handlers': ['logfile', 'console','logstash'],
            'level': min_level,  # this level or higher goes to the console,
        },
        'contracts': {
            'handlers': ['logfile', 'console','logstash'],
            'level': min_level,  # this level or higher goes to the console,
        },
        'sevovvintegration': {
            'handlers': ['logfile', 'console','logstash'],
            'level': min_level,  # this level or higher goes to the console,
        },
        'django': {  # configure all of Django's loggers
            'handlers': ['logfile', 'console','logstash'],
            'level': min_django_level,  # this level or higher goes to the console
            'propagate': False,  # don't propagate further, to avoid duplication
        },
        # 'django.db.backends': {  # configure all of Django's loggers
        #     'handlers': [ 'console'],
        #     'level': 'DEBUG',  # this level or higher goes to the console
        #     'propagate': False,  # don't propagate further, to avoid duplication
        # },
        # root configuration – for all of our own apps
        # (feel free to do separate treatment for e.g. brokenapp vs. sth else)
        '': {
            'handlers': ['logfile', 'console','logstash'],
            'level': min_django_level,  # this level or higher goes to the console,
        },
    },
}

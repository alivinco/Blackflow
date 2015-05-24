__author__ = 'alivinco'

config = {
    'version': 1,
    'disable_existing_loggers': False,  # this fixes the problem
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': "standard"
        },
        'info_file_handler': {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "standard",
            "filename": "info.log",
            "maxBytes": 3000000,
            "backupCount": 2,
            "encoding": "utf8"
        },

        'error_file_handler': {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "standard",
            "filename": "errors.log",
            "maxBytes": 3000000,
            "backupCount": 2,
            "encoding": "utf8"
        }
    },
    'loggers': {

        '':{
            "handlers": ["default", "info_file_handler", "error_file_handler"],
            'level':'DEBUG',
            'propagate': True
        }
    }
}

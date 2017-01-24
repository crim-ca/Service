# -*- coding: utf-8 -*-
"""
Configuration values for worker processes.
"""

# Broker settings ------------------------------------------------------------
BROKER_URL = 'amqp://localhost//'
CELERY_RESULT_BACKEND = 'amqp://'
CELERY_TASK_RESULT_EXPIRES = 7200  # 2 hours.

# Result backend settings ----------------------------------------------------
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']

# Worker settings ------------------------------------------------------------
CELERY_SEND_EVENTS = True
CELERYD_CONCURRENCY = 2
CELERYD_PREFETCH_MULTIPLIER = 1

# Logging settings -----------------------------------------------------------
CELERYD_TASK_LOG_FORMAT = ("[%(asctime)s: %(levelname)s/%(processName)s] "
                           "[%(task_name)s(%(task_id)s)] - %(name)s - "
                           "%(message)s")

CELERYD_LOG_FORMAT = ("[%(asctime)s: %(levelname)s/%(processName)s] "
                      "- %(name)s - %(message)s")

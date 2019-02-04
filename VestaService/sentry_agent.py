import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration

# Uses the SENTRY_DSN environment variable. See sentry documentation.
sentry_sdk.init(integrations=[CeleryIntegration()])

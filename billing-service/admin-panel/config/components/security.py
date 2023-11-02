from config.base_settings import django_security_settings

SECRET_KEY = django_security_settings.secret_key

ALLOWED_HOSTS = django_security_settings.allowed_hosts.split(',')

DEBUG = django_security_settings.debug

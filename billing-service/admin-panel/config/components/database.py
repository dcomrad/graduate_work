from config.base_settings import postgres_settings

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': postgres_settings.dbname,
        'USER': postgres_settings.user,
        'PASSWORD': postgres_settings.password,
        'HOST': postgres_settings.host,
        'PORT': postgres_settings.port,
        'OPTIONS': {
            'options': postgres_settings.options,
        },
    }
}

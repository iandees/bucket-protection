import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'khkpwoifqiumbnoyopwe')
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'simple')
    CACHE_REDIS_URL = os.environ.get('REDIS_URL')
    DEBUG = os.environ.get('DEBUG', True)

    DEFAULT_PAGE = 'index.html'
    S3_BUCKET = os.environ.get('S3_BUCKET')
    S3_INDEX_DOCUMENT = os.environ.get("S3_INDEX_DOCUMENT")
    VERBOSE_SQLALCHEMY = False
    SSLIFY_ENABLE = False
    SENTRY_ENABLE = False

    OAUTH_CREDENTIALS = {}

    if os.environ.get('FACEBOOK_APP_ID'):
        OAUTH_CREDENTIALS['facebook'] = {
            'id': os.environ.get('FACEBOOK_APP_ID'),
            'secret': os.environ.get('FACEBOOK_APP_SECRET'),
        }

    if os.environ.get('GOOGLE_APP_ID'):
        OAUTH_CREDENTIALS['google'] = {
            'id': os.environ.get('GOOGLE_APP_ID'),
            'secret': os.environ.get('GOOGLE_APP_SECRET'),
        }

    if os.environ.get('SLACK_APP_ID'):
        OAUTH_CREDENTIALS['slack'] = {
            'id': os.environ.get('SLACK_APP_ID'),
            'secret': os.environ.get('SLACK_APP_SECRET'),
            'team_id': os.environ.get('SLACK_TEAM_ID'),
        }

    SENTRY_DSN = os.environ.get('SENTRY_DSN')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        if app.config.get('VERBOSE_SQLALCHEMY'):
            import logging
            from logging import StreamHandler
            stream_handler = StreamHandler()
            stream_handler.setLevel(logging.INFO)
            sql_logger = logging.getLogger('sqlalchemy.engine')
            sql_logger.addHandler(stream_handler)
            sql_logger.setLevel(logging.INFO)


class TestingConfig(Config):
    TESTING = True


class HerokuConfig(Config):
    SSL_DISABLE = bool(os.environ.get('SSL_DISABLE'))

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # handle proxy server headers
        from werkzeug.contrib.fixers import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)

        # log to stderr
        import logging
        from logging import StreamHandler
        stream_handler = StreamHandler()
        stream_handler.setLevel(logging.WARNING)
        app.logger.addHandler(stream_handler)


class ProductionConfig(HerokuConfig):
    DEBUG = False
    TESTING = False
    SSLIFY_ENABLE = True
    SENTRY_ENABLE = False


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}

import logging
from flask import Flask, g, render_template
from flask_caching import Cache
from flask_login import LoginManager
from app.config import config

cache = Cache()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    logger = app.logger
    logger.setLevel(logging.INFO)
    stream_handler = logging.StreamHandler()
    logger.addHandler(stream_handler)

    login_manager.init_app(app)
    cache.init_app(app)

    if not app.debug and not app.testing and app.config.get('SSLIFY_ENABLE'):
        app.logger.info("Using SSLify")
        from flask_sslify import SSLify
        sslify = SSLify(app)

    sentry = None
    if not app.debug and not app.testing and app.config.get('SENTRY_ENABLE'):
        app.logger.info("Using Sentry")
        from raven.contrib.flask import Sentry
        sentry = Sentry(app)

    @app.errorhandler(500)
    def internal_server_error(error):
        return render_template(
            '500.html',
            event_id=g.sentry_event_id,
            public_dsn=sentry.client.get_public_dsn('https') if sentry else None
        )

    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    from .passthrough import passthrough_bp
    app.register_blueprint(passthrough_bp)

    return app

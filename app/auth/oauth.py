from rauth import OAuth1Service, OAuth2Service
from flask import current_app, url_for, request, redirect, session, json
import requests


providers = {}


class OAuthSignIn(object):
    def __init__(self, provider_name, config):
        self.provider_name = provider_name
        self.consumer_id = config['id']
        self.consumer_secret = config['secret']

    def authorize(self):
        pass

    def callback(self):
        pass

    def get_callback_url(self):
        return url_for('auth.oauth_callback',
                       provider=self.provider_name,
                       _external=True,
                       _scheme='https')

    @classmethod
    def get_provider(self, provider_name):
        if provider_name in providers:
            return providers[provider_name]

        provider_class = provider_classes.get(provider_name)

        if not provider_class:
            # We don't have a class for the requested provider
            providers[provider_name] = None
            return None

        oauth_config = current_app.config.get('OAUTH_CREDENTIALS')
        provider_config = oauth_config.get(provider_name)

        if not provider_config:
            # The provider is not configured
            providers[provider_name] = None
            return None

        provider = provider_class(provider_config)
        providers[provider_name] = provider
        return provider


class SlackSignIn(OAuthSignIn):
    def __init__(self, config):
        super(SlackSignIn, self).__init__('slack', config)
        self.service = OAuth2Service(
            name='slack',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url='https://slack.com/oauth/authorize',
            access_token_url='https://slack.com/api/oauth.access',
            base_url='https://slack.com/api/'
        )

    def authorize(self):
        return redirect(self.service.get_authorize_url(
            scope='identity.basic',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )

    def callback(self):
        if 'code' not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
            data={'code': request.args['code'],
                  'redirect_uri': self.get_callback_url()},
            decoder=json.loads,
        )
        me = oauth_session.get(
            'users.identity',
            params={'token': oauth_session.access_token}
        ).json()
        return (
            'slack$' + me['user']['id'],
            me['user']['name'],
            None
        )


class FacebookSignIn(OAuthSignIn):
    def __init__(self, config):
        super(FacebookSignIn, self).__init__('facebook', config)
        self.service = OAuth2Service(
            name='facebook',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url='https://graph.facebook.com/oauth/authorize',
            access_token_url='https://graph.facebook.com/oauth/access_token',
            base_url='https://graph.facebook.com/'
        )

    def authorize(self):
        return redirect(self.service.get_authorize_url(
            scope='email',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )

    def callback(self):
        if 'code' not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
            data={'code': request.args['code'],
                  'grant_type': 'authorization_code',
                  'redirect_uri': self.get_callback_url()},
            decoder=json.loads,
        )
        me = oauth_session.get('me?fields=id,email').json()
        return (
            'facebook$' + me['id'],
            me.get('email').split('@')[0],  # Facebook does not provide
                                            # username, so the email's user
                                            # is used instead
            me.get('email')
        )


class GoogleSignIn(OAuthSignIn):
    def __init__(self, config):
        super(GoogleSignIn, self).__init__('google', config)
        google_params = requests.get('https://accounts.google.com/.well-known/openid-configuration').json()
        self.service = OAuth2Service(
            name='google',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url=google_params.get('authorization_endpoint'),
            base_url=google_params.get('userinfo_endpoint'),
            access_token_url=google_params.get('token_endpoint')
        )

    def authorize(self):
        return redirect(self.service.get_authorize_url(
            scope='email',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )

    def callback(self):
        if 'code' not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
                data={'code': request.args['code'],
                      'grant_type': 'authorization_code',
                      'redirect_uri': self.get_callback_url()},
                decoder=json.loads
        )
        me = oauth_session.get('').json()
        return (
            'google$' + me['sub'],
            me['name'],
            me['email']
        )


provider_classes = {
    'slack': SlackSignIn,
    'google': GoogleSignIn,
    'facebook': FacebookSignIn,
}

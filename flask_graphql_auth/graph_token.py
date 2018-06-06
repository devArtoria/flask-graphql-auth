import jwt
from uuid import uuid4
from flask import current_app
import datetime


class GraphQLAuth(object):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        Register this extension with the flask app.

        :param app: A flask application
        """
        # Save this so we can use it later in the extension
        if not hasattr(app, 'extensions'):  # pragma: no cover
            app.extensions = {}
        app.extensions['flask-graphql-auth'] = self

        self._set_default__configuration_options(app)

    @staticmethod
    def _set_default__configuration_options(app):
        """
        Sets the default configuration options used by this extension
        """
        app.config.setdefault('JWT_TOKEN_ARGUMENT_NAME', "token")  # Name of token argument in GraphQL request resolver

        app.config.setdefault('JWT_ACCESS_TOKEN_EXPIRES', datetime.timedelta(minutes=15))
        app.config.setdefault('JWT_REFRESH_TOKEN_EXPIRES', datetime.timedelta(days=30))

        app.config.setdefault('JWT_SECRET_KEY', None)

        app.config.setdefault('JWT_IDENTITY_CLAIM', 'identity')
        app.config.setdefault('JWT_USER_CLAIMS', 'user_claims')

    @staticmethod
    def _create_basic_token_data(identity, token_type):
        uid = str(uuid4())
        now = datetime.datetime.utcnow()

        token_data = {
            "type": token_type,
            "iat": now,
            "nbf": now,
            "jti": uid,
            "exp": now + current_app.config['JWT_ACCESS_TOKEN_EXPIRES'],
            current_app.config['JWT_IDENTITY_CLAIM']: identity
        }

        return token_data

    def _create_access_token(self, identity, user_claims):
        token_data = self._create_basic_token_data(identity=identity,
                                                   token_type='access')

        if user_claims:
            token_data.update({
                current_app.config['JWT_USER_CLAIMS']: user_claims
            })

        return jwt.encode(token_data,
                          current_app.config['JWT_SECRET_KEY'],
                          'HS256',
                          json_encoder=current_app.json_encoder).decode('utf-8')

    def _create_refresh_token(self, identity):
        token_data = self._create_basic_token_data(identity=identity,
                                                   token_type='refresh')

        encoded_token = jwt.encode(token_data,
                                   current_app.config['JWT_SECRET_KEY'],
                                   'HS256',
                                   json_encoder=current_app.json_encoder).decode('utf-8')

        return encoded_token


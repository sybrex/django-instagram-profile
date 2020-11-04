from configparser import RawConfigParser
from django.conf import settings
import os


_env_path = settings.BASE_DIR + '/env.ini'

if os.path.exists(_env_path):
    env = RawConfigParser()
    env.read(_env_path)
    _settings = env['instagram']
else:
    _settings = settings.INSTAGRAM_PROFILE


INSTAGRAM_ACCOUNT = _settings['account']
INSTAGRAM_AUTH_URL = _settings['auth_url']
INSTAGRAM_ACCESS_TOKEN_URL = _settings['access_token_url']
INSTAGRAM_APP_ID = _settings['app_id']
INSTAGRAM_SECRET = _settings['secret']
INSTAGRAM_REDIRECT_URL = _settings['redirect_url']
INSTAGRAM_MEDIA_URL = _settings['media_url']

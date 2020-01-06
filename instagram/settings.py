from configparser import RawConfigParser
from django.conf import settings


env = RawConfigParser()
env.read(settings.BASE_DIR + '/env.ini')

INSTAGRAM_ACCOUNT = env['instagram']['account']
INSTAGRAM_AUTH_URL = env['instagram']['auth_url']
INSTAGRAM_ACCESS_TOKEN_URL = env['instagram']['access_token_url']
INSTAGRAM_APP_ID = env['instagram']['app_id']
INSTAGRAM_SECRET = env['instagram']['secret']
INSTAGRAM_REDIRECT_URL = env['instagram']['redirect_url']
INSTAGRAM_MEDIA_URL = env['instagram']['media_url']

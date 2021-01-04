from django.conf import settings


INSTAGRAM_AUTH_URL = 'https://api.instagram.com/oauth/authorize'
INSTAGRAM_ACCESS_TOKEN_URL = 'https://api.instagram.com/oauth/access_token'
INSTAGRAM_LONG_LIVED_ACCESS_TOKEN_URL = 'https://graph.instagram.com/access_token'
INSTAGRAM_REFRESH_ACCESS_TOKEN_URL = 'https://graph.instagram.com/refresh_access_token'
INSTAGRAM_MEDIA_URL = 'https://graph.instagram.com'
INSTAGRAM_ACCOUNT = None
INSTAGRAM_APP_ID = settings.INSTAGRAM_PROFILE['app_id']
INSTAGRAM_SECRET = settings.INSTAGRAM_PROFILE['secret']
INSTAGRAM_REDIRECT_URL = settings.INSTAGRAM_PROFILE['redirect_url']

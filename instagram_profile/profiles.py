from datetime import timedelta

from instagram_profile.client import convert_auth_code_to_long_lived_token, refresh_long_lived_access_token
from instagram_profile.models import Profile


def update_access_token(profile: Profile, auth_code: str=None, days_buffer=30):
    # If we have an auth_code use it to get a long lived access token and store that in the profile object
    if auth_code:
        result = convert_auth_code_to_long_lived_token(auth_code)
        if result.access_token:
            profile.access_token = result.access_token
            profile.expires_at = result.expires_at
            profile.save()
        else:
            return result.error

    # If we have a long lived access token refresh it if it will expiry soon
    elif profile.access_token and profile.expires_in <= timedelta(days=days_buffer):
        result = refresh_long_lived_access_token(profile.access_token)
        if result.access_token:
            profile.access_token = result.access_token
            profile.expires_at = result.expires_at
            profile.save()
        else:
            return result.error

    # Otherwise, do not do anything as we already have access or can't get access

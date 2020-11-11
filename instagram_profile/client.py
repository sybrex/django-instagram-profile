import json
from datetime import datetime, timedelta
from typing import Optional, NamedTuple
from urllib.parse import urlencode

import requests
from django.utils import timezone

from . import settings


class AccessTokenResult(NamedTuple):
    access_token: Optional[str]
    expires_at: Optional[datetime]
    error: Optional[str]


def get_authorize_url(profile_pk: int):
    query = {
        'app_id': settings.INSTAGRAM_APP_ID,
        'redirect_uri': settings.INSTAGRAM_REDIRECT_URL,
        'scope': 'user_profile,user_media',
        'response_type': 'code',
        'state': profile_pk,  # Passing the profile id so that the callback knows which profile to use
    }
    return settings.INSTAGRAM_AUTH_URL + '?' + urlencode(query)


def get_media_feed(access_token):
    if not access_token:
        raise Exception('Invalid authentication code')

    posts = []
    url = settings.INSTAGRAM_MEDIA_URL + '/me/media'
    query = {
        'fields': 'caption,id,media_type,media_url,permalink,thumbnail_url,timestamp,children',
        'access_token': access_token
    }
    res = requests.get(url, params=query)
    if res.status_code == 200:
        feed = json.loads(res.text)
        for item in feed['data']:
            post = convert_media(item)
            if 'children' in item:
                post['children'] = []
                for child in item['children']['data']:
                    data = get_media_details(child['id'], access_token)
                    if data:
                        post['children'].append(data)
            posts.append(post)

    return posts


def get_media_details(id, access_token):
    post = None
    url = settings.INSTAGRAM_MEDIA_URL + '/' + id
    query = {
        'fields': 'id,media_type,media_url,permalink,thumbnail_url,timestamp',
        'access_token': access_token
    }
    res = requests.get(url, params=query)
    if res.status_code == 200:
        post = convert_media(json.loads(res.text))
    return post


def get_auth_url():
    url = settings.INSTAGRAM_AUTH_URL
    query = {
        'app_id': settings.INSTAGRAM_APP_ID,
        'redirect_uri': settings.INSTAGRAM_REDIRECT_URL,
        'scope': 'user_profile,user_media',
        'response_type': 'code'
    }
    return url + '?' + urlencode(query)


def _parse_access_token_response(response: requests.Response, error_msg: str):
    if response.status_code == 200:
        j = json.loads(response.text)
        expires_at = None
        if 'expires_in' in j:
            expires_at = timezone.now() + timedelta(seconds=j['expires_in'])
        return AccessTokenResult(j['access_token'], expires_at, None)
    return AccessTokenResult(None, None, f'{error_msg}: {response.text}')


def get_short_lived_access_token(auth_code):
    r = requests.post(settings.INSTAGRAM_ACCESS_TOKEN_URL, data={
        'app_id': settings.INSTAGRAM_APP_ID,
        'app_secret': settings.INSTAGRAM_SECRET,
        'grant_type': 'authorization_code',
        'redirect_uri': settings.INSTAGRAM_REDIRECT_URL,
        'code': auth_code
    })
    return _parse_access_token_response(r, error_msg='Error retrieving short lived access token')


def get_long_lived_access_token(short_lived_access_token):
    r = requests.get('https://graph.instagram.com/access_token', params={
        'client_secret': settings.INSTAGRAM_SECRET,
        'grant_type': 'ig_exchange_token',
        'access_token': short_lived_access_token,
    })
    return _parse_access_token_response(r, error_msg='Error retrieving long lived access token')


def convert_auth_code_to_long_lived_token(auth_code: str):
    short_lived = get_short_lived_access_token(auth_code)
    if short_lived.access_token:
        return get_long_lived_access_token(short_lived.access_token)
    if short_lived.error:
        return short_lived
    return AccessTokenResult(None, None, 'Error converting auth code to long lived token' + str(short_lived))


def refresh_long_lived_access_token(long_lived_access_token):
    r = requests.get(settings.INSTAGRAM_REFRESH_ACCESS_TOKEN_URL, params={
        'grant_type': 'ig_exchange_token',
        'access_token': long_lived_access_token,
    })
    return _parse_access_token_response(r, error_msg='Error refreshing long lived access token')


def convert_media(data):
    return {
        'media_id': data['id'],
        'caption': data['caption'] if 'caption' in data else '',
        'type': data['media_type'],
        'permalink': data['permalink'],
        'thumbnail': data['thumbnail_url'] if 'thumbnail_url' in data else data['media_url'],
        'created': datetime.strptime(data['timestamp'], '%Y-%m-%dT%H:%M:%S%z')
    }

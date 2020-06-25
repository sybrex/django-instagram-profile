import os
import requests
from shutil import copyfileobj
from PIL import Image
from django.conf import settings
from . import client
from .models import Post
from requests.exceptions import HTTPError


def sync_instagram(auth_code):
    try:
        posts = client.get_media_feed(auth_code)
    except HTTPError as http_err:
        return {
            'status': False,
            'message': f'HTTP error occurred: {http_err}'
        }
    except Exception as err:
        return {
            'status': False,
            'message': f'API error occurred: {err}'
        }

    created = get_last_synced_date()
    for post in posts:
        if created is None or post['created'] > created:
            thumbnail = download_image(post['thumbnail'], post['media_id'])
            if not thumbnail:
                continue

            resize_image(thumbnail)

            children = []
            if post['type'] == Post.TYPE_ALBUM:
                for item in post['children']:
                    child_thumbnail = download_image(item['thumbnail'], item['media_id'])
                    resize_image(child_thumbnail)
                    children.append(child_thumbnail)

            new_post = Post(
                media_id=post['media_id'],
                caption=post['caption'],
                type=post['type'],
                permalink=post['permalink'],
                created=post['created'],
                thumbnail=thumbnail,
                children='\n'.join(children)
            )
            new_post.save()

    return {
        'status': True,
        'message': 'Synced successfully'
    }


def get_last_synced_date():
    try:
        last_db_post = Post.objects.latest('created')
        return last_db_post.created
    except Post.DoesNotExist:
        pass


def download_image(url, name):
    res = requests.get(url, stream=True)
    if res.status_code == 200:
        ext = url.split('?')[0].split('.')[-1]
        base_name = name + '.' + ext
        full_name = os.path.join(settings.MEDIA_ROOT, 'instagram/', base_name)
        if not os.path.exists(full_name):
            with open(full_name, 'wb') as out_file:
                copyfileobj(res.raw, out_file)
        return base_name


def resize_image(base_name):
    full_name = os.path.join(settings.MEDIA_ROOT, 'instagram/', base_name)
    img = Image.open(full_name)
    img.thumbnail((624, 800), Image.ANTIALIAS)
    img.save(full_name, progressive=True, quality=100)

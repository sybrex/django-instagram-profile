import os
import requests
from shutil import copyfileobj
from PIL import Image
from django.conf import settings
from . import client
from .models import Post
from requests.exceptions import HTTPError
from django.core.files.base import ContentFile


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

            # Download the raw bytes of the image.  Abort if something goes wrong.
            thumbnail_bytes = fetch_image(post['thumbnail'])
            if not thumbnail_bytes:
                continue

            # Organise children
            children = []
            if post['type'] == Post.TYPE_ALBUM:
                for item in post['children']:
                    child_thumbnail = download_image(item['thumbnail'], item['media_id'])
                    resize_image(child_thumbnail)
                    children.append(child_thumbnail)

            # Create post
            new_post = Post(
                media_id=post['media_id'],
                caption=post['caption'],
                type=post['type'],
                permalink=post['permalink'],
                created=post['created'],
                children='\n'.join(children),
            )

            # Save the original thumbnail image into the model
            # Can use libraries such as imagekit to resize this image when needed
            name = get_file_name(post['thumbnail'], post['media_id'])
            new_post.thumbnail.save(name, ContentFile(thumbnail_bytes))
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


def get_file_name(url, name):
    ext = url.split('?')[0].split('.')[-1]
    return name + '.' + ext


def fetch_image(url):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        return r.content


def download_image(url, name):
    res = requests.get(url, stream=True)
    if res.status_code == 200:
        base_name = get_file_name(url, name)
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

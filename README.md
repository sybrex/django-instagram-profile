django-instagram-profile
========================
A Django application that allows to fetch individual Instagram user profile media data and save into database.
Instagram media is managed using Django admin console. [Demo](https://viktors.info/logbook)

![Example](/docs/django-instagram-profile.png)

Instagram profile
----------------------
First you need to configure Instagram application following these instructions:
[Instagram Basic Display API](https://developers.facebook.com/docs/instagram-basic-display-api)

Requirements
------------
* [django >= 3.0](https://www.djangoproject.com/)
* [requests](https://pypi.python.org/pypi/requests)
* [pillow](https://pypi.python.org/pypi/Pillow)
* [configparser](https://pypi.org/project/configparser/)

Installation
------------
Install Django and other required packages. It is very handy to use [pipenv](https://pipenv.readthedocs.io/en/latest/) for this.
```bash
pipenv install django requests pillow configparser
```

By default, newly created Django project configuration uses SQLite. If you're using other database engine make sure you configure it properly beforehand. 

Install Instagram profile package:
```bash
pipenv install django-instagram-profile
```

Create env.ini file inside your project directory with the following settings:
```ini
[instagram]
account = instagram_account_name
auth_url = https://api.instagram.com/oauth/authorize
access_token_url = https://api.instagram.com/oauth/access_token
app_id = 123
secret = abc
redirect_url = https://mysite.com/admin/instagram_profile/post/sync
media_url = https://graph.instagram.com
```

Configuration
-------------
Add the application to INSTALLED_APPS:
```python
INSTALLED_APPS = ('instagram_profile',)
```

Create a folder for Instagram media
```
/project_name/media/instagram
```

Configure correct paths for uploaded instagram media in settings.py
```python
SITE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
MEDIA_ROOT = os.path.join(SITE_ROOT, 'media')
MEDIA_URL = '/media/'
```

Add media template context processor in the settings.py
Also add template dir to the list of dirs
```python
TEMPLATES = [
    {
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.media', # add this line
            ],
        },
    },
]
```

Add url to display instagram media feed in urls.py
```python
urlpatterns = [
    path('instagram/', include('instagram_profile.urls')), # add this line
]
```

To serve media files during development need to add following lines to urls.py
```python
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

Run the database migrations
```bash
python manage.py migrate
```

Releases
--------
* 0.1.1 Alpha version

django-instagram-profile
========================


A Django application that syncs one or more users Instagram posts to your project's database and media storage.

- Uses [Instagram Basic Display API](https://developers.facebook.com/docs/instagram-basic-display-api) to fetch a users feed
- Button in Django Admin to authenticate user
- Supports multiple Instagram accounts
- Stores long-lived access code in database to allow on-going sync without user interaction 
*(NB: This code is currently in proof-of-concept status.  Before using in production, you will probably want to update this field to be encrypted or stored somewhere else that is encrypted)*
- Management command for background sync with crontab (`./manage.py sync_instagram_posts`)
 
Instagram media is managed using Django admin console. [Demo django project](https://github.com/sybrex/django-instagram-demo)

# Setup & configuration

## 1. Install django-instagram-profile

```bash
poetry add django-instagram-profile
```

or using Pip

```bash
pip install django-instagram-profile
```

Dependencies will be installed automatically
 
## 2. Create a Facebook/Instagram App

Follow [this guide](https://developers.facebook.com/docs/instagram-basic-display-api/getting-started).

If your app is intended for the general public to authenticate, then you will need to publish your app.
Otherwise, you can get away with leaving your app in [developer mode](https://developers.facebook.com/docs/apps#development-mode) and [adding your users as testers](https://developers.facebook.com/docs/instagram-basic-display-api/getting-started/#step-3--add-an-instagram-test-user).

To add a test user:

- In the app admin, go Products > Basic Display > User Token Generator > Add or remove Instagram testers
- In the users Instagram account login, go Settings > Apps and Websites > Tester Invites.  Then accept the invite.

## 3. Add the application to INSTALLED_APPS:
```python
INSTALLED_APPS = (
    # ...
    'instagram_profile',
)
```

## 4. Update your Django settings with your new app's client id, secret, & redirect url. Eg. 
```python

INSTAGRAM_PROFILE = {
    # You will get these from your registered instagram app
    'app_id': '123456789012345',
    'secret': '1234567890123456789012345678901234',
    'redirect_url': 'https://www.example.com/your-admin/instagram_profile/profile/authorized',        
}
```

**OR** if you prefer, create env.ini file inside your project directory with the following settings:
```ini
[instagram]
app_id = 123
secret = abc
redirect_url = https://www.example.com/your-admin/instagram_profile/profile/authorized
```

## 4. Migrate database

Run the database migrations
```bash
./manage.py migrate
```

## 5. Configure media (if you already haven't)

Depending on your storage backend and current project you may need to configure media.  
Your project probably already has this configured.

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

To serve media files during development need to add following lines to urls.py
```python
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## 6. Configure public views (optional)

django-instagram-profile comes with some public views to show your instagram posts. 
Depending on your project needs you may or may not want to use them.

If you want to utilise these them add url to display instagram media feed in urls.py:

```python
urlpatterns = [
    # ...
    path('instagram/', include('instagram_profile.urls')), # add this line
]
```

# Usage

## Adding an account

If you have not publicly published your app, you will first need to setup your instagram user as a test user as described above.

Add a new profile in the Django admin, only setting the **username** field.  `(Instagram Sync > Profiles > Add)`

After clicking "Save & Continue Editing", click "Authorize" in the top right of the profile form (depending on your needs, this might need to be done by your Instagram user).  This will redirect you/them to Instagram.  Accept all permissions.


## Sync posts manually

Once you are authorized, you can sync posts by:

- Clicking the "Sync" button on the Profile form.  This will only sync this profile's posts.
- Clicking the "Sync" button on the list of posts.  This will sync posts for all profiles.

## Sync posts in the background

Run this command.  You'll probably want to set up a crontab (or similar) to run this regularly. 

```bash
./manage.py sync_instagram_posts
```

The long-term access codes will be automatically renewed if they will expire within 30 days.  So if this command is run more frequently than every 30 days, authentication should continue in-definitely.

## Using post data in other ways

You can interface with the `Post` model however you like.  We recommend the excellent [django-imagekit](https://github.com/matthewwithanm/django-imagekit/) library, which will allow you to resize and change these images for however you like in your own code.

# Releases
* 1.0.0 Multi-account, django.contrib.storage, background-sync, and much more
* 0.1.3 Use text field for instagram captions 
* 0.1.1 Handling invalid auth code exception
* 0.1.0 Alpha version

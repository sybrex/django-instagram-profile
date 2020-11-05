from datetime import timedelta

from django.db import models
from django.utils import timezone


class Profile(models.Model):

    class Meta:
        db_table = 'instagram_profile'
        ordering = ['username']

    username = models.CharField(max_length=256)
    access_token = models.CharField(max_length=256, blank=True, help_text='The long lived access token')
    expires_at = models.DateTimeField(null=True, blank=True, help_text='The expiry of the stored long lived access token')
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.username:
            return '@{}'.format(self.username)
        return 'New profile'

    @property
    def expires_in(self):
        if self.expires_at:
            return self.expires_at - timezone.now()
        return timedelta(seconds=0)

    @property
    def access_valid(self):
        return self.access_token and self.expires_at and self.expires_at > timezone.now()


class Post(models.Model):

    class Meta:
        db_table = 'instagram_posts'
        ordering = ['-created']

    TYPE_IMAGE = 'IMAGE'
    TYPE_VIDEO = 'VIDEO'
    TYPE_ALBUM = 'CAROUSEL_ALBUM'
    MEDIA_TYPES = [
        (TYPE_IMAGE, 'Image'),
        (TYPE_ALBUM, 'Album'),
        (TYPE_VIDEO, 'Video')
    ]

    profile = models.ForeignKey(Profile, null=True, blank=True, on_delete=models.SET_NULL)
    media_id = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=MEDIA_TYPES, default=TYPE_IMAGE)
    permalink = models.CharField(max_length=256)
    caption = models.TextField(default='')
    thumbnail = models.ImageField(max_length=256, default='', upload_to='instagram/')
    children = models.TextField(default='')
    created = models.DateTimeField()

    def children_list(self):
        return self.children.split('\n')

    def __str__(self):
        return self.media_id + ' ' + self.type + ' ' + self.caption

from urllib.parse import urlencode

from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, re_path
from django.utils.safestring import mark_safe

from . import settings
from .models import Post, Profile
from .profiles import update_access_token
from .services import sync_instagram


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'expires_at', 'expires_in')
    search_fields = ('username',)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            re_path('^(\d+)/sync/?$', self.admin_site.admin_view(self.sync), name='instagram_sync_profile')
        ]
        return my_urls + urls

    def sync(self, request, object_id):
        profile = get_object_or_404(Profile, id=object_id)
        if profile.access_valid:
            result = sync_instagram(profile)
            status = messages.SUCCESS if result['status'] else messages.ERROR
            messages.add_message(request, status, result['message'])
            return HttpResponseRedirect(reverse('admin:instagram_profile_post_changelist'))
        else:
            query = {
                'app_id': settings.INSTAGRAM_APP_ID,
                'redirect_uri': settings.INSTAGRAM_REDIRECT_URL,
                'scope': 'user_profile,user_media',
                'response_type': 'code',
                'state': object_id,  # Passing the profile id so that the callback knows which profile to use
            }
            return HttpResponseRedirect(settings.INSTAGRAM_AUTH_URL + '?' + urlencode(query))


class PostAdmin(admin.ModelAdmin):
    list_display = ('media_id', 'created', 'caption', 'type', 'permalink_display')
    list_filter = ('type', 'created', 'profile')
    search_fields = ('media_id', 'caption')
    date_hierarchy = 'created'

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            re_path('^sync/?$', self.admin_site.admin_view(self.sync), name='instagram_sync')
        ]
        return my_urls + urls

    def sync(self, request):
        # This view does a number of different things based on the state of the access

        # If there is a code, this must be the auth callback redirect from Instagram
        auth_code = request.GET.get('code')
        if auth_code:
            profile = get_object_or_404(Profile, id=request.GET.get('state'))

            err = update_access_token(profile, auth_code=auth_code)
            if err:
                messages.error(request, err)
                return HttpResponseRedirect(reverse('admin:instagram_profile_profile_change', args=[profile.id]))

            result = sync_instagram(profile)
            status = messages.SUCCESS if result['status'] else messages.ERROR
            messages.add_message(request, status, result['message'])
            return HttpResponseRedirect(reverse('admin:instagram_profile_post_changelist'))

        # Otherwise redirect to instagram to get an auth code
        else:
            query = {
                'app_id': settings.INSTAGRAM_APP_ID,
                'redirect_uri': settings.INSTAGRAM_REDIRECT_URL,
                'scope': 'user_profile,user_media',
                'response_type': 'code'
            }
            return HttpResponseRedirect(settings.INSTAGRAM_AUTH_URL + '?' + urlencode(query))

    def permalink_display(self, obj):
        if obj.permalink:
            return mark_safe('<a href="{}" target="_blank">{}'.format(
                obj.permalink,
                obj.permalink.replace('https://www.instagram.com', '')
            ))
    permalink_display.short_description = 'Permalink'


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Post, PostAdmin)

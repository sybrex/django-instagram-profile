from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, re_path
from django.utils import timezone
from django.utils.safestring import mark_safe

from .client import get_authorize_url
from .models import Post, Profile
from .profiles import update_access_token
from .services import sync_instagram


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'expires_at', 'expires_in')
    search_fields = ('username',)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            re_path('^authorized/?$', self.admin_site.admin_view(self.authorize_callback), name='instagram_authorize_callback'),
            re_path('^(\d+)/authorize/?$', self.admin_site.admin_view(self.authorize_profile), name='instagram_authorize'),
            re_path('^(\d+)/sync/?$', self.admin_site.admin_view(self.sync), name='instagram_sync'),
        ]
        return my_urls + urls

    def authorize_profile(self, request, object_id):
        profile = get_object_or_404(Profile, id=object_id)
        if profile.access_valid:
            messages.warning(request, 'This profile is already authorized')
            return HttpResponseRedirect(reverse('admin:instagram_profile_profile_change', args=[profile.id]))
        else:
            return HttpResponseRedirect(get_authorize_url(object_id))

    def authorize_callback(self, request):
        # If there is a code, this must be the auth callback redirect from Instagram
        auth_code = request.GET.get('code')
        if auth_code:
            profile = get_object_or_404(Profile, id=request.GET.get('state'))

            err = update_access_token(profile, auth_code=auth_code)
            if err:
                messages.error(request, err)
                return HttpResponseRedirect(reverse('admin:instagram_profile_profile_change', args=[profile.id]))

            messages.success(request, f'Successfully authorized for next {profile.expires_in.days} days and will be automatically extended as needed.')
            return HttpResponseRedirect(reverse('admin:instagram_profile_profile_change', args=[profile.id]))

        # Otherwise redirect to instagram to get an auth code
        else:
            messages.warning(request, 'No code available.  Try again')
            return HttpResponseRedirect(reverse('admin:instagram_profile_profile_changelist'))

    def sync(self, request, object_id):
        profile = get_object_or_404(Profile, id=object_id)
        redirect_to = reverse('admin:instagram_profile_profile_change', args=[profile.id])
        if profile.access_valid:
            result = sync_instagram(profile)
            status = messages.SUCCESS if result['status'] else messages.ERROR
            messages.add_message(request, status, result['message'])
            return HttpResponseRedirect(redirect_to)
        else:
            messages.error(request, 'This profile has not been authorized.')
            return HttpResponseRedirect(redirect_to)


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
        for profile in Profile.objects.exclude(access_token=''):
            if profile.expires_at > timezone.now():
                result = sync_instagram(profile)
                status = messages.SUCCESS if result['status'] else messages.ERROR
                messages.add_message(request, status, result['message'])
            else:
                messages.warning(request, f'Authorization expired for {profile}.')

        return HttpResponseRedirect(reverse('admin:instagram_profile_post_changelist'))

    def permalink_display(self, obj):
        if obj.permalink:
            return mark_safe('<a href="{}" target="_blank">{}'.format(
                obj.permalink,
                obj.permalink.replace('https://www.instagram.com', '')
            ))
    permalink_display.short_description = 'Permalink'


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Post, PostAdmin)

from django.contrib import admin
from django.urls import reverse, re_path
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.utils.safestring import mark_safe
from urllib.parse import urlencode


from .models import Post
from .services import sync_instagram
from . import settings


class PostAdmin(admin.ModelAdmin):
    list_display = ('media_id', 'created', 'caption', 'type', 'permalink_display')
    list_filter = ('type', 'created')
    search_fields = ('media_id', 'caption')
    date_hierarchy = 'created'

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            re_path('^sync/?$', self.admin_site.admin_view(self.sync), name='instagram_sync')
        ]
        return my_urls + urls

    def sync(self, request):
        code = request.GET.get('code')
        if code:
            result = sync_instagram(code)
            status = messages.SUCCESS if result['status'] else messages.ERROR
            messages.add_message(request, status, result['message'])
            return HttpResponseRedirect(reverse('admin:instagram_profile_post_changelist'))
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


admin.site.register(Post, PostAdmin)

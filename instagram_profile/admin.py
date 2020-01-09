from django.contrib import admin
from django.urls import path, reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from urllib.parse import urlencode
from .models import Post
from .services import sync_instagram
from . import settings


class PostAdmin(admin.ModelAdmin):
    list_display = ('media_id', 'created', 'caption', 'type', 'permalink')
    ordering = ['created']

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('sync', self.admin_site.admin_view(self.sync), name='instagram_sync')
        ]
        return my_urls + urls

    def sync(self, request):
        code = request.GET.get('code')
        if code:
            result = sync_instagram(code)
            status = messages.SUCCESS if result['status'] else messages.ERROR
            messages.add_message(request, status, result['message'])
            return HttpResponseRedirect(reverse('admin:app_list', kwargs={'app_label': 'instagram_profile'}) + 'post')
        else:
            query = {
                'app_id': settings.INSTAGRAM_APP_ID,
                'redirect_uri': settings.INSTAGRAM_REDIRECT_URL,
                'scope': 'user_profile,user_media',
                'response_type': 'code'
            }
            return HttpResponseRedirect(settings.INSTAGRAM_AUTH_URL + '?' + urlencode(query))


admin.site.register(Post, PostAdmin)

from django.shortcuts import render
from .models import Post


def feed(request):
    data = Post.objects.all()[:50]
    return render(request, 'instagram_profile/feed.html', {'feed': data})

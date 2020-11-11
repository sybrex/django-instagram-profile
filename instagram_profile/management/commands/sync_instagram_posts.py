from django.core.management.base import BaseCommand
from django.utils import timezone

from instagram_profile.models import Profile
from instagram_profile.services import sync_instagram


class Command(BaseCommand):
    help = "Sync all authorized Instagram posts"

    def handle(self, *args, **options):

        def log(level, msg):
            if level >= options['verbosity']:
                print(msg)

        for profile in Profile.objects.exclude(access_token=''):
            if profile.expires_at > timezone.now():
                result = sync_instagram(profile)
                if result['status']:
                    log(1, result['message'])
                else:
                    log(0, result['message'])
            else:
                log(0, f'Authorization expired for {profile}.')

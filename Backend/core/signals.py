from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models import UserProfile


@receiver(post_save, sender=get_user_model())
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = UserProfile.objects.create(user=instance)
        try:
            print("user email: ", profile.user.email)
            if profile.user.email and str(profile.user.email).endswith("@dkv.global"):
                profile.is_editor = True
                profile.save()
        except Exception as e:
            print(e)
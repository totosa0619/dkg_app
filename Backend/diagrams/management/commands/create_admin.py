from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


User = get_user_model()

class Command(BaseCommand):
    help = "Creates a user with static credentials."

    def handle(self, *args, **options):
        password = "admin"
        username = "admin"
        email = "admin@dkv.com"

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f"User '{email}' already exists."))
        else:
            user = User.objects.create_superuser(password=password, email=email, first_name="admin", last_name="admin", username=username)
            user.is_verified=True
            user.save()
            self.stdout.write(self.style.SUCCESS(f"User '{email}' created successfully."))

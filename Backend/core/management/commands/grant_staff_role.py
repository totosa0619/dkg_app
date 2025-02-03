from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

User = get_user_model()

class Command(BaseCommand):
    help = 'Grant staff role to users with a specific corporate email and add them to a specific group (eg. "python manage.py grant_staff_role gmail.com all-charts-access")'
    

    def add_arguments(self, parser):
        parser.add_argument('email_domain', type=str, help='The corporate email domain to filter users')
        parser.add_argument('group_name', type=str, help='The name of the group to add the users to')

    @transaction.atomic
    def handle(self, *args, **kwargs):
        email_domain = kwargs['email_domain']
        group_name = kwargs['group_name']

        try:
            group = Group.objects.get(name=group_name)
        except ObjectDoesNotExist:
            self.stderr.write(self.style.ERROR(f'Group "{group_name}" does not exist.'))
            return

        users = User.objects.filter(email__iendswith=f'@{email_domain}')
        
        if not users.exists():
            self.stdout.write(self.style.WARNING(f'No users found with email domain "@{email_domain}".'))
            return

        updated_users_count = 0

        for user in users:
            if not user.is_staff:
                user.is_staff = True
                user.groups.add(group)
                user.save()
                updated_users_count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated_users_count} user(s) with staff role and added to group "{group_name}".'))

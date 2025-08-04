import os
from django.core.management.base import BaseCommand
from core.models import CustomUser

class Command(BaseCommand):
    help = 'Create a superuser with predefined credentials'

    def handle(self, *args, **options):
        mobile_no = os.getenv('SUPERUSER_MOBILE', '+918074960679')
        password = os.getenv('SUPERUSER_PASSWORD', 'admin')
        email = os.getenv('SUPERUSER_EMAIL', 'admin@gmail.com')

        if CustomUser.objects.filter(mobile_no=mobile_no).exists():
            self.stdout.write(self.style.WARNING(f'Superuser with mobile {mobile_no} already exists'))
            return

        CustomUser.objects.create_superuser(
            mobile_no=mobile_no,
            password=password,
            email=email,
            first_name='Admin',
            last_name='User'
        )
        self.stdout.write(self.style.SUCCESS(f'Superuser {mobile_no} created successfully'))
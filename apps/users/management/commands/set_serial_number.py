import uuid

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django_countries.data import COUNTRIES
from django_countries.fields import Country as DjCountry

from apps.users.models import Country, Identity, generate_serial_number

User = get_user_model()


class Command(BaseCommand):
    def handle(self, *args, **options):
        for identity in Identity.objects.all():
            identity.identifier = uuid.uuid1()
            identity.serial_number = generate_serial_number()
            identity.save()

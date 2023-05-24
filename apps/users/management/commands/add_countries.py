from django.core.management import BaseCommand
from django_countries.data import COUNTRIES
from django_countries.fields import Country as DjCountry

from apps.users.models import Country


class Command(BaseCommand):
    def handle(self, *args, **options):
        country_codes = reversed(list(COUNTRIES.keys()))
        for code in country_codes:
            country = DjCountry(code=code)
            Country.objects.create(country=country)

        self.stdout.write('Done.')

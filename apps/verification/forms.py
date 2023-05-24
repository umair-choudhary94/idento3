from django import forms
from django_countries.fields import CountryField


class VerificationForm(forms.Form):
    country = CountryField()
    document_type = CountryField()

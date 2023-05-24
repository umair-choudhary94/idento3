from django.db import models

from apps.users.models import SingletonModel


class Newsletter(models.Model):
    subscriber = models.EmailField('Email', max_length=64)
    is_active = models.BooleanField(default=True)

    created = models.DateTimeField('Created', auto_now_add=True)
    updated = models.DateTimeField('Updated', auto_now=True)

    class Meta:
        verbose_name = 'Newsletter'
        verbose_name_plural = 'Newsletters'

    def __str__(self):
        return self.subscriber


class SiteSetting(SingletonModel):
    website_title = models.CharField('Website Title', max_length=32)
    meta = models.CharField('Meta', max_length=32)
    keyword = models.CharField('Keyword', max_length=32)
    logo = models.ImageField('Logo', upload_to='logos', null=True, blank=True)
    icon = models.ImageField('Icon', upload_to='logos', null=True, blank=True)

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return 'Site Settings'

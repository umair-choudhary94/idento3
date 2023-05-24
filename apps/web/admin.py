from django.contrib import admin

from apps.web.models import Newsletter


class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['subscriber', 'is_active', 'created', 'updated']


admin.site.register(Newsletter, NewsletterAdmin)

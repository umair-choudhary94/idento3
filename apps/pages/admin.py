from django.contrib import admin

from apps.pages.models import Page


# Register your models here.
class PageAdmin(admin.ModelAdmin):
    list_display = ['title', 'link_position', 'active', 'created', 'updated']


admin.site.register(Page, PageAdmin)

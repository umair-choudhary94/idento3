"""identipo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path

from apps.dashboard.admin import dashboard_admin_site
from apps.dashboard.views import reports_view, redirect_view
from apps.limited.admin import limited_dashboard_site
from apps.web.views import LoginView


urlpatterns = [
                  # re_path(r'^dashboard/$', redirect_view, name='redirect'),

                  path('dashboard/', dashboard_admin_site.urls),
                  # re_path('^dashboard/$', redirect_view, name='redirect'),

                  path('user/', limited_dashboard_site.urls),
                  path('admin/', admin.site.urls),
                  path('', include('apps.dashboard.urls')),
                  path('verification/', include('apps.verification.urls')),
                  path('', include('apps.web.urls')),

                  path('payments/', include('apps.payments.urls')),
                  path('reports/', include('apps.reports.urls')),
                  path('users/', include('apps.users.urls')),
                  # path('admin_tools_stats/', include('admin_tools_stats.urls')),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

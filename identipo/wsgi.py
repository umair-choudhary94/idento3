import os
import sys

# assuming your django settings file is at '/home/identipo/mysite/mysite/settings.py'
# and your manage.py is is at '/home/identipo/mysite/manage.py'
path = '/home/identipo/identipo/'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'identipo.settings'

# then:
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

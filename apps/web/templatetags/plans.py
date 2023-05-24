from django import template
from django.utils.html import escape, mark_safe

from apps.dashboard.models import Customer, Employee, MyPlan
from apps.payments.models import Payment
from apps.support.models import Ticket
from apps.users.models import Identity

register = template.Library()


@register.filter(name="has_employees")
def has_employees(user):
    return Employee.objects.filter(added_by=user).exists()

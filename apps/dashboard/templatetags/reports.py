from django import template
from django.utils.html import escape, mark_safe

from apps.dashboard.models import Customer, Employee, MyPlan
from apps.payments.models import Payment
from apps.support.models import Ticket
from apps.users.models import Identity

register = template.Library()


@register.filter(name="has_customers")
def has_customers(user):
    return Customer.objects.filter(added_by=user).exists()


@register.filter(name="has_employees")
def has_employees(user):
    return Employee.objects.filter(added_by=user).exists()


@register.filter(name="has_plan")
def has_plan(user):
    return MyPlan.objects.filter(user=user).exists()


@register.filter(name="payments_exist")
def payments_exist(user):
    return Payment.objects.exists()


@register.filter(name="verification_exist")
def verification_exist(user):
    return Identity.objects.exists()


@register.filter(name="tickets_exist")
def tickets_exist(user):
    return Ticket.objects.exists()


@register.filter(name="has_paid_plan")
def has_paid_plan(user):
    return MyPlan.objects.filter(is_active=True).exists()


@register.simple_tag()
def defilter(request, field):
    # request
    query = request.GET.copy()
    if query.get(field):
        query.pop(field)
    return query.urlencode()


@register.filter(name="get_logo")
def get_logo(user):
    person = Employee.objects.filter(user=user).first() or Customer.objects.filter(user=user).first()
    if person and person.added_by.logo:
        return person.added_by.logo.url

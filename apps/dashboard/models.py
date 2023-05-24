from django.contrib.auth import get_user_model
from django.db import models

from apps.payments.models import Plan
from apps.support.models import Ticket
from apps.users.models import Identity

User = get_user_model()


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                blank=True, null=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL,
                                 blank=True, null=True,
                                 related_name='customers')

    created = models.DateTimeField('Created', auto_now_add=True)
    updated = models.DateTimeField('Updated', auto_now=True)

    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'

    def __str__(self):
        return str(self.user.name)


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                blank=True, null=True, related_name='employeez')
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL,
                                 blank=True, null=True,
                                 related_name='employees')

    created = models.DateTimeField('Created', auto_now_add=True)
    updated = models.DateTimeField('Updated', auto_now=True)

    class Meta:
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'

    def __str__(self):
        return str(self.user.name)


class MyPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             blank=True, null=True,
                             related_name='my_plans')
    payment = models.ForeignKey('payments.Payment', blank=True, null=True,
                                on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, blank=True, null=True)
    is_active = models.BooleanField('Is Active', default=False)

    created = models.DateTimeField('Created', auto_now_add=True)
    updated = models.DateTimeField('Updated', auto_now=True)

    class Meta:
        verbose_name = 'My Price Plan'
        verbose_name_plural = 'My Price Plans'

    @staticmethod
    def initiate(user, plan, payment):
        return MyPlan.objects.create(user=user, plan=plan, payment=payment, is_active=True)

    def __str__(self):
        return self.plan.title

    def total_credit(self):
        return self.plan.limit

    total_credit.short_description = 'Total Verifications'

    def remaining_credit(self):
        # if self.user.type == User.TYPE_COMPANY:
        used = Customer.objects.filter(added_by=self.user).count() + Employee.objects.filter(added_by=self.user).count()
        return self.plan.limit - used

    remaining_credit.short_description = 'Remaining'


class MyPayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             blank=True, null=True,
                             related_name='my_payments')

    payment = models.ForeignKey('payments.Payment', blank=True, null=True,
                                on_delete=models.CASCADE)

    created = models.DateTimeField('Created', auto_now_add=True)
    updated = models.DateTimeField('Updated', auto_now=True)

    class Meta:
        verbose_name = 'My Payment'
        verbose_name_plural = 'My Payments'

    def __str__(self):
        return str(self.payment)


class Profile(User):
    class Meta:
        proxy = True

    def __str__(self):
        return self.name.upper()


class Report(models.Model):
    class Meta:
        verbose_name = 'Reports'
        verbose_name_plural = 'Reports'


class Ticket(Ticket):
    class Meta:
        proxy = True
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'


class MyIdentity(Identity):
    class Meta:
        proxy = True
        verbose_name = 'Identity Verification'
        verbose_name_plural = 'Identity Verification'


class Limited(Identity):
    class Meta:
        proxy = True
        verbose_name = 'Identity Verification'
        verbose_name_plural = 'Identity Verification'

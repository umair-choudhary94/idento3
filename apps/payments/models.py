import random
import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import JSONField

User = get_user_model()


def generate_invoice_id():
    return random.randint(100000, 999999)


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT,
                             related_name='payments',
                             verbose_name='User')
    invoice_id = models.PositiveIntegerField('Invoice ID', default=generate_invoice_id)
    ref_id = models.UUIDField(default=uuid.uuid4,
                              unique=True, editable=False,
                              verbose_name='Ref ID')

    plan = models.ForeignKey('Plan', blank=True, null=True, on_delete=models.SET_NULL,
                             verbose_name='Price Plan')
    gateway = models.ForeignKey('Gateway', blank=True, null=True, on_delete=models.SET_NULL,
                                verbose_name='Payment Gateway')

    data = JSONField(null=True, blank=True)

    created = models.DateTimeField('Created', auto_now_add=True)
    updated = models.DateTimeField('Updated', auto_now=True)

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'

    def __str__(self):
        return f'{self.user}'


class Gateway(models.Model):
    GATEWAY_PAYPAL = 'PayPal'
    GATEWAY_STRIPE = 'Stripe'
    GATEWAY_PAYSTACK = 'PayStack'
    GATEWAY_CHOICES = (
        (GATEWAY_PAYPAL, GATEWAY_PAYPAL),
        (GATEWAY_STRIPE, GATEWAY_STRIPE),
        (GATEWAY_PAYSTACK, GATEWAY_PAYSTACK)
    )
    name = models.CharField('Name', max_length=16, choices=GATEWAY_CHOICES, unique=True)
    icon = models.ImageField('Icon', upload_to='icons', null=True, blank=True)
    active = models.BooleanField()

    created = models.DateTimeField('Created', auto_now_add=True)
    updated = models.DateTimeField('Updated', auto_now=True)

    class Meta:
        verbose_name = 'Payment Gateway'
        verbose_name_plural = 'Payment Gateways'

    def __str__(self):
        return f'{self.name}'


class Plan(models.Model):
    title = models.CharField(max_length=16, null=True, unique=True)
    description = models.TextField(max_length=2048, help_text='Enter items separated by comma')

    price = models.PositiveSmallIntegerField(help_text='Euro(€)')
    currency = models.ForeignKey('payments.Currency', blank=True, null=True, on_delete=models.CASCADE)
    limit = models.PositiveSmallIntegerField('Identification Limit', default=0,
                                             help_text='Maximum identification limit per month, for this plan')

    created = models.DateTimeField('Created', auto_now_add=True)
    updated = models.DateTimeField('Updated', auto_now=True)

    class Meta:
        verbose_name = 'Price Plan'
        verbose_name_plural = 'Price Plans'

    def __str__(self):
        return f'{self.title}'

    @property
    def desc(self):
        return self.description.split(',')

    @property
    def plan_title(self):
        return self.title.split(' ')


class Currency(models.Model):
    name = models.CharField('Name', max_length=12)
    code = models.CharField('Code', max_length=3, help_text='example: USD')
    symbol = models.CharField('Symbol', max_length=3, help_text='example: $', blank=True, null=True)

    is_active = models.BooleanField('Is Active', default=True)

    created = models.DateTimeField('Created', auto_now_add=True)
    updated = models.DateTimeField('Updated', auto_now=True)

    class Meta:
        verbose_name = 'Currency'
        verbose_name_plural = 'Currencies'

    def __str__(self):
        return f'{self.code}'

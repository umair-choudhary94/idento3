from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Ticket(models.Model):
    raised_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='raized_by')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    title = models.CharField('Title', max_length=64)
    text = models.TextField('Text', max_length=256)

    STATUS_NEW = 'New'
    STATUS_PENDING = 'Pending'
    STATUS_CLOSED = 'Closed'
    STATUS_CHOICES = (
        (STATUS_NEW, STATUS_NEW),
        (STATUS_PENDING, STATUS_PENDING),
        (STATUS_CLOSED, STATUS_CLOSED)
    )
    status = models.CharField('Status', max_length=16, choices=STATUS_CHOICES, default=STATUS_NEW)

    created = models.DateTimeField('Created', auto_now_add=True)
    updated = models.DateTimeField('Updated', auto_now=True)

    class Meta:
        verbose_name = 'Ticket'
        verbose_name_plural = 'Helpdesk'

    def __str__(self):
        return self.title

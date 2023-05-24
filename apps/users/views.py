from django.contrib.auth import get_user_model
from django.contrib.auth.views import (
    PasswordResetView as DjangoPasswordResetView,
    PasswordResetCompleteView as DjangoPasswordResetCompleteView,
    PasswordResetConfirmView as DjangoPasswordResetConfirmView,
    PasswordChangeView as DjangoPasswordChangeView,
    PasswordResetDoneView as DjangoPasswordResetDoneView
)
from django.urls import reverse_lazy

from apps.users.forms import PasswordResetForm, SetPasswordForm

# from users.forms import PasswordResetForm, SetPasswordForm, CustomAuthenticationForm

User = get_user_model()


class PasswordResetView(DjangoPasswordResetView):
    template_name = 'web/password_reset_form.html'
    success_url = reverse_lazy('web:password_reset_done')
    from_email = 'info@identipo.com'  # FIXME
    html_email_template_name = 'web/password_reset_email.html'
    form_class = PasswordResetForm


class PasswordResetDoneView(DjangoPasswordResetDoneView):
    template_name = 'web/password_reset_done.html'
    # form_class = PasswordResetForm
    # success_url = reverse_lazy('web:password_reset_done')


class PasswordResetConfirmView(DjangoPasswordResetConfirmView):
    template_name = 'web/password_reset_confirm.html'
    success_url = reverse_lazy('web:password_reset_complete')
    form_class = SetPasswordForm

    # def get_context_data(self, **kwargs):
    #     context = super(DjangoPasswordResetConfirmView, self).get_context_data(**kwargs)
    #     return context


class PasswordResetCompleteView(DjangoPasswordResetCompleteView):
    template_name = 'web/password_reset_complete.html'

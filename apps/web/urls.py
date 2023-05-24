from django.urls import path,include

from apps.users.views import PasswordResetView, PasswordResetConfirmView, PasswordResetCompleteView, \
    PasswordResetDoneView
from apps.web.views import *

app_name = 'web'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),

    path('signup/', RegisterView.as_view(), name='register'),
    path('email-verification/', VerificationSentView.as_view(), name='verification_sent'),
    path('verify/', VerifyEmailView.as_view(), name='verify_email'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('password_reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password_reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset/complete/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('api/', APIPageView.as_view(), name='api'),
    path('newsletter/<email>/', subscribe_to_newsletter, name='newsletter'),

    # Payments
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('upgrade/', UpgradeView.as_view(), name='upgrade'),
    path('payment-success/', PaymentSuccessView.as_view(), name='payment_success'),
    path('payment-fail/', UpgradeView.as_view(), name='payment_fail'),

    path('<slug:slug>/', get_page, name='pages'),
    # path('terms-conditions/', TermsConditionsView.as_view(), name='terms_conditions'),
    # path('privacy-policy/', PrivacyPolicyView.as_view(), name='privacy_policy'),
    # path('cookies-policy/', CookiesPolicyView.as_view(), name='cookies_policy'),
    path("payment/",include("apps.payments.urls"))


]

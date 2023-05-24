from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
   
    path('create-payment-intent/<pk>/', StripeIntentView.as_view(), name='create-payment-intent'),
    path('webhooks/stripe/', stripe_webhook, name='stripe-webhook'),
    path('cancel/', CancelView.as_view(), name='cancel'),
    path('success/', SuccessView.as_view(), name='success'),
    path('plans/', ProductLandingPageView.as_view(), name='landing-page'),
    
    path('create-checkout-session/<int:pk>/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),

    # //////////paypal////////////////////////////
    path('initiate/<int:id>/', initiate_payment, name='initiate_payment'),
    path('execute/', execute_payment, name='execute_payment'),

    # /////////////////////Paystack////////////////////////////
    path('initiation/<int:id>/', payment_initiation, name='payment_initiation'),
    path('callback/', payment_callback, name='payment_callback'),


    # //////////////////////Gateways////////////////////////////
    path('gateways/<int:id>/', gateways, name='gateways'),
    path('handlegateways/<int:id>/<int:planid>/', handlegateway, name='handlegateway'),

]

import json
import stripe
from django.core.mail import send_mail
from django.conf import settings
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse,HttpResponseRedirect
from django.views import View
from .models import Plan,Gateway
from paypalrestsdk import Payment
from paystackapi.transaction import Transaction
from django.shortcuts import render,redirect

stripe.api_key = settings.STRIPE_SECRET_KEY


class SuccessView(TemplateView):
    template_name = "success.html"


class CancelView(TemplateView):
    template_name = "cancel.html"


class ProductLandingPageView(TemplateView):
    template_name = "landing.html"

    def get_context_data(self, **kwargs):
        products = Plan.objects.all()
        # product = Product.objects.all()
        context = super(ProductLandingPageView, self).get_context_data(**kwargs)
        context.update({
            "products": products,
            "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY
        })
        return context


class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        product_id = self.kwargs["pk"]
        product = Plan.objects.get(id=product_id)
        YOUR_DOMAIN = "http://127.0.0.1:8000"
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': product.price*100,
                        'product_data': {
                            'name': product.title,
                            # 'images': ['https://i.imgur.com/EHyR2nP.png'],
                        },
                    },
                    'quantity': 1,
                },
            ],
            metadata={
                "product_id": product.id
            },
            mode='payment',
            success_url=YOUR_DOMAIN + '/payment/success/',
            cancel_url=YOUR_DOMAIN + '/payment/cancel/',
        )
        return JsonResponse({
            'id': checkout_session.id
        })

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        customer_email = session["customer_details"]["email"]
        product_id = session["metadata"]["product_id"]

        product = Plan.objects.get(id=product_id)

        # send_mail(
        #     subject="identipo",
        #     message=f"Thanks!",
        #     recipient_list=[customer_email],
        #     from_email="matt@test.com"
        # )

        # TODO - decide whether you want to send the file or the URL
    
    elif event["type"] == "payment_intent.succeeded":
        intent = event['data']['object']

        stripe_customer_id = intent["customer"]
        stripe_customer = stripe.Customer.retrieve(stripe_customer_id)

        customer_email = stripe_customer['email']
        product_id = intent["metadata"]["product_id"]

        product = Plan.objects.get(id=product_id)

        # send_mail(
        #     subject="Identipo",
        #     message=f"Thanks!",
        #     recipient_list=[customer_email],
        #     from_email="matt@test.com"
        # )

    return HttpResponse(status=200)


class StripeIntentView(View):
    def post(self, request, *args, **kwargs):
        try:
            req_json = json.loads(request.body)
            customer = stripe.Customer.create(email=req_json['email'])
            product_id = self.kwargs["pk"]
            product = Plan.objects.get(id=product_id)
            intent = stripe.PaymentIntent.create(
                amount=product.price,
                currency='usd',
                customer=customer['id'],
                metadata={
                    "product_id": product.id
                }
            )
            return JsonResponse({
                'clientSecret': intent['client_secret']
            })
        except Exception as e:
            return JsonResponse({ 'error': str(e) })

# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''Paypal''''''''''''''''''''''



def initiate_payment(request,id):
    plan = Plan.objects.get(id=id)
    YOUR_DOMAIN = "http://127.0.0.1:8000"
    payment = Payment({
        'intent': 'sale',
        'payer': {
            'payment_method': 'paypal'
        },
        'redirect_urls': {
            'return_url': f'{YOUR_DOMAIN}/payment/execute/',
            'cancel_url': f'{YOUR_DOMAIN}/payment/cancel/'
        },
        'transactions': [{
            'amount': {
                'total': plan.price,
                'currency': 'USD'
            },
            'description': 'Test product -- Fetch it from database'
        }]
    })

    if payment.create():
        for link in payment.links:
            if link.method == 'REDIRECT':
                redirect_url = str(link.href)
                return HttpResponseRedirect(redirect_url)
    else:
        return HttpResponse('Payment creation failed')

def execute_payment(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    payment = Payment.find(payment_id)

    if payment.execute({'payer_id': payer_id}):
        # Payment successful
        return HttpResponse('Payment successful')
    else:
        # Payment failed
        return HttpResponse('Payment failed')


# ///////////////////////////////////////Paystack////////////////////////////////////

def payment_initiation(request,id):
    plan = Plan.objects.get(id=id)
    transaction = Transaction.initialize(
        amount=plan.price,  # Amount in kobo (e.g., 10000 for NGN 100)
        email=request.user.email,
        callback_url='http://your-domain.com/payment/callback/'
    )

    authorization_url = transaction['data']['authorization_url']
    return HttpResponseRedirect(authorization_url)

def payment_callback(request):
    reference = request.GET.get('reference')

    transaction = Transaction.verify(reference)

    if transaction['status']:
        # Payment successful
        return HttpResponse('Payment successful')
    else:
        # Payment failed
        return HttpResponse('Payment failed')
    
def gateways(request,id):
    gateways = Gateway.objects.all()
    context = {
        "gateways" : gateways,
        "planid" : id,
    }
    return render(request,"gateway.html",context)
def handlegateway(request,id,planid):
    gateway = Gateway.objects.get(id=id)
    if gateway.name=="PayPal":
        
        return redirect(f"/payment/initiate/{planid}/")
    elif gateway.name=="PayStack":
        
        return redirect(f"/payment/initiation/{planid}/")




from django.contrib.auth import get_user_model, login
from django.contrib.auth.models import Permission, Group
from django.contrib.auth.views import LoginView as DjangoLoginView, LogoutView as DjangoLogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, CreateView

from apps.dashboard.models import MyPlan, MyPayment
from apps.pages.models import Page
from apps.payments.models import Plan, Gateway, Payment
from apps.users.forms import RegisterForm, LoginForm
from apps.users.models import Country
from apps.web.models import Newsletter

User = get_user_model()


class HomeView(TemplateView):
    template_name = 'web/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['header_pages'] = Page.objects.filter(active=True, link_position=Page.POSITION_HEADER)
        context['footer_pages'] = Page.objects.filter(active=True, link_position=Page.POSITION_FOOTER)
        context['plans'] = Plan.objects.all()
        return context


class APIPageView(TemplateView):
    template_name = 'web/api.html'


class RegisterView(SuccessMessageMixin, CreateView):
    template_name = 'web/register.html'
    success_url = reverse_lazy('web:verification_sent')
    form_class = RegisterForm
    success_message = 'Your account has been set up successfully!'

    def get_success_url(self):
        plan = self.get_form_kwargs()['data'].get('plan')
        if plan:
            return reverse_lazy('web:checkout') + f'?success=true&plan={plan}'
        return reverse_lazy('web:verification_sent')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['header_pages'] = Page.objects.filter(active=True, link_position=Page.POSITION_HEADER)
        context['footer_pages'] = Page.objects.filter(active=True, link_position=Page.POSITION_FOOTER)
        context['plans'] = Plan.objects.all()
        context['countries'] = Country.objects.order_by('-created')
        return context

    def form_valid(self, form):
        form_valid = super().form_valid(form)
        if form.is_valid():
            form.instance.generate_token()

            # form.instance.is_staff = True
            form.instance.save()

            form.instance.add_manager_permissions()

            form.instance.send_signup_email()
            login(self.request, form.instance)

        return form_valid


class VerificationSentView(TemplateView):
    template_name = 'web/verification_sent.html'
    success_url = reverse_lazy('web:verification_sent')
    # success_message = 'Your account has been created successfully.'


@method_decorator(csrf_exempt, name='dispatch')
class VerifyEmailView(TemplateView):
    success_url = reverse_lazy('dashboard_admin:index')
    fail_url = reverse_lazy('web:login')

    def get(self, request, *args, **kwargs):
        user = User.objects.filter(token=request.GET.get('token')).first()
        if user is None:
            return redirect(self.fail_url)
        user.is_staff = True  # FIXME
        user.save()

        user.add_manager_permissions()

        login(request, user)

        return redirect(self.success_url)


class LoginView(DjangoLoginView):
    template_name = 'web/login.html'
    form_class = LoginForm

    # redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('dashboard_admin:index')


class LogoutView(DjangoLogoutView):
    template_name = 'web/logout.html'
    fields = '__all__'
    redirect_authenticated_user = True


class CheckoutView(TemplateView):
    template_name = 'web/checkout.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['plan'] = Plan.objects.filter(title=self.request.GET.get('plan')).first()
        context['gateways'] = Gateway.objects.filter(active=True).order_by('created')
        return context


class UpgradeView(TemplateView):
    template_name = 'web/upgrade.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['plans'] = Plan.objects.all()
        return context


class PaymentSuccessView(TemplateView):
    template_name = 'web/payment_success.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            plan = Plan.objects.filter(title=request.GET.get('plan')).first()
            payment = Payment.objects.create(user=request.user, plan=plan)
            MyPayment.objects.create(user=request.user, payment=payment)
            MyPlan.initiate(user=request.user, plan=plan, payment=payment)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_plan = MyPlan.objects.filter(user=self.request.user).last()
        context['my_plan'] = my_plan
        return context


def subscribe_to_newsletter(request, email):
    if not Newsletter.objects.filter(subscriber=email).exists():
        Newsletter.objects.create(subscriber=email)
        return JsonResponse({'message': "Subscribed successfully"})
    return JsonResponse({'message': "Subscribed successfully"})


def get_page(request, slug):
    page = Page.objects.get(slug=slug)
    return render(request, 'web/base_page.html', locals())

class TermsConditionsView(TemplateView):
    template_name = 'terms_conditions.html'

class PrivacyPolicyView(TemplateView):
    template_name = 'privacy_policy.html'

class CookiesPolicyView(TemplateView):
    template_name = 'cookies_policy.html'
# views.py
from django.shortcuts import render

def cookie_banner_view(request):
    return render(request, 'cookie_banner.html')

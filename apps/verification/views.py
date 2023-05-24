from django.contrib.auth import login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, FormView

from apps.users.models import Country, Identity
from apps.verification.forms import VerificationForm

import base64

from django.core.files.base import ContentFile


class VerificationView(FormView):
    form_class = VerificationForm
    template_name = 'verification/second_page.html'

    def get(self, request, *args, **kwargs):
        fields = ['country', 'document_type', 'document', 'selfie']

        identifier = request.GET.get('identifier')
        identity = Identity.objects.filter(identifier=identifier).last()

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['countries'] = [c for c in Country.objects.order_by('-created')]
        context['document_types'] = [f'{d[0]}' for d in Identity.DOCUMENT_TYPE_CHOICES]
        return context


class FirstPageView(TemplateView):
    template_name = 'verification/first_page.html'


class SecondPageView(TemplateView):
    template_name = 'verification/second_page.html'


class ThirdPageView(TemplateView):
    template_name = 'verification/third_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['countries'] = [c for c in Country.objects.order_by('-created')]
        context['document_types'] = [f'{d[0]}' for d in Identity.DOCUMENT_TYPE_CHOICES]
        return context


class FourthPageView(TemplateView):
    template_name = 'verification/fourth_page.html'


class FifthPageView(TemplateView):
    template_name = 'verification/fifth_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        identifier = self.request.GET.get('identifier')
        document_type = self.request.GET.get('document_type')
        identity = Identity.objects.filter(identifier=identifier).last()
        identity.document_type = document_type
        identity.save()
        identity.refresh_from_db()
        context['has_back'] = identity.has_back
        return context


class FifthPageBView(TemplateView):
    template_name = 'verification/fifth_b_page.html'


class SixthPageView(TemplateView):
    template_name = 'verification/sixth_page.html'


class SeventhPageView(TemplateView):
    template_name = 'verification/seventh_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        identifier = self.request.GET.get('identifier')
        identity = Identity.objects.filter(identifier=identifier).last()
        context['identity'] = identity
        context['has_back'] = identity.has_back
        return context


class EighthPageView(TemplateView):
    template_name = 'verification/eighth_page.html'

    def get(self, request, *args, **kwargs):
        identifier = request.GET.get('identifier')
        identity = Identity.objects.filter(identifier=identifier).last()
        identity.card_issuer = Country.objects.filter(country__name=request.GET.get('country')).last()
        identity.document_type = request.GET.get('document_type')
        identity.document = identity.temp_document
        identity.document_back = identity.temp_back
        identity.selfie = identity.temp_selfie

        identity.save()
        identity.refresh_from_db()

        try:
            verification_result = identity.verify()
            identity.status = Identity.STATUS_VERIFIED if verification_result else Identity.STATUS_NOT_VERIFIED

            identity.save()
            identity.refresh_from_db()

            identity.user.is_staff = True
            identity.user.save()

            login(request, user=identity.user)

        except:
            identity.status = Identity.STATUS_NOT_VERIFIED
            identity.save()
            identity.refresh_from_db()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        identifier = self.request.GET.get('identifier')
        identity = Identity.objects.filter(identifier=identifier).last()
        context['identity'] = identity
        return context


@csrf_exempt
def set_temp_document(request):
    if request.POST:
        identifier = request.POST.get('identifier')
        identity = Identity.objects.filter(identifier=identifier).last()
        data = get_file(request.POST.get('data'))
        identity.temp_document = data
        identity.document = data
        identity.save()
        return JsonResponse({'message': f'{identity} updated successfully.'})
    return JsonResponse({'message': 'failed'})


@csrf_exempt
def set_temp_back(request):
    if request.POST:
        identifier = request.POST.get('identifier')
        identity = Identity.objects.filter(identifier=identifier).last()
        data = get_file(request.POST.get('data'))
        identity.temp_back = data
        identity.document_back = data
        identity.save()
        return JsonResponse({'message': f'{identity} updated successfully.'})
    return JsonResponse({'message': 'failed'})


@csrf_exempt
def set_temp_selfie(request):
    if request.POST:
        identifier = request.POST.get('identifier')
        identity = Identity.objects.filter(identifier=identifier).last()
        data = get_file(request.POST.get('data'))
        identity.temp_selfie = data
        identity.selfie = data
        identity.save()

        return JsonResponse({'message': f'{identity} updated successfully.'})
    return JsonResponse({'message': 'failed'})


def get_file(data):
    format, imgstr = data.split(';base64,')
    ext = format.split('/')[-1]
    data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
    return data


@csrf_exempt
def get_countries(request):
    countries = Country.objects.order_by('-created')
    data = []
    for country in countries:
        data.append({"text": country.country.name, "value": country.country.name, "image": country.country.flag})
    return JsonResponse({'data': data})

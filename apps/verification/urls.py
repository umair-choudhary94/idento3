from django.urls import path

from apps.verification.views import FirstPageView, SecondPageView, ThirdPageView, FourthPageView, FifthPageView, \
    SixthPageView, SeventhPageView, EighthPageView, VerificationView, set_temp_document, set_temp_back, set_temp_selfie, \
    FifthPageBView, get_countries

app_name = "verification"
urlpatterns = [
    path('begin/', FirstPageView.as_view(), name='v'),
    path('country/', VerificationView.as_view(), name='second-page'),
    path('type/', ThirdPageView.as_view(), name='third-page'),
    path('guide/', FourthPageView.as_view(), name='fourth-page'),
    path('document/', FifthPageView.as_view(), name='fifth-page'),
    path('fifth-b/', FifthPageBView.as_view(), name='fifth-page-b'),
    path('selfie/', SixthPageView.as_view(), name='sixth-page'),
    path('analyze/', SeventhPageView.as_view(), name='seventh-page'),
    path('finalize/', EighthPageView.as_view(), name='eighth-page'),

    # Ajax
    path('set_temp_document/', set_temp_document, name='temp-doc'),
    path('set_temp_back/', set_temp_back, name='temp-back'),
    path('set_temp_selfie/', set_temp_selfie, name='temp-selfie'),
    path('get_countries/', get_countries, name='get-countries'),
]

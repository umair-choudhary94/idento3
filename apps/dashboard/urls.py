from django.urls import path, re_path

from apps.dashboard.views import profile_view, security_view, reports_view, get_customers_chart, get_filter_options, \
    get_users_chart, get_verifications_chart, get_plan_chart, get_employees_chart, get_tickets_chart, \
    get_payments_chart, initiate_verification, setting_view, redirect_view

app_name = "dashboard"

urlpatterns = [
    path('reports/', reports_view, name='reports'),

    path('profile/', profile_view, name='my_profile'),
    path('setting/', setting_view, name='setting'),
    path('security/', security_view, name='security'),

    path('chart/filter-options/', get_filter_options, name='chart-filter-options'),
    path('chart/users/<int:year>/', get_users_chart, name='chart-users'),
    path('chart/customers/<int:year>/', get_customers_chart, name='chart-customers'),
    path('chart/employees/<int:year>/', get_employees_chart, name='chart-employees'),
    path('chart/payments/<int:year>/', get_payments_chart, name='chart-payments'),
    path('chart/plan/<int:year>/', get_plan_chart, name='chart-plan'),
    path('chart/verifications/<int:year>/', get_verifications_chart, name='chart-verifications'),
    path('chart/tickets/<int:year>/', get_tickets_chart, name='chart-tickets'),
    # path('chart/spend-per-customer/<int:year>/', views.spend_per_customer_chart, name='chart-spend-per-customer'),

    path('verification/initiate/<int:id>/', initiate_verification, name='init-verification'),

]

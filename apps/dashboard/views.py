from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, F, Sum, Avg
from django.db.models.functions import ExtractYear, ExtractMonth, TruncMonth, TruncDay
from django.http import JsonResponse

from apps.dashboard.utils import months, colorPrimary, colorSuccess, colorDanger, generate_color_palette, get_year_dict, \
    colorPending
from apps.dashboard.models import Customer, MyPlan, Employee
from apps.payments.models import Plan, Payment
from apps.support.models import Ticket
from apps.users.models import Identity

User = get_user_model()


def profile_view(request):
    user = User.objects.get(id=request.user.id)

    if user.is_limited:
        return redirect(
            reverse('dashboard_admin:dashboard_profile_change', kwargs={'object_id': user.id}) + "#profile-tab")
    if not user.is_superuser:
        return redirect(
            reverse('dashboard_admin:dashboard_profile_change', kwargs={'object_id': user.id}) + "#profile-tab")
    return redirect(reverse('admin:users_user_change', kwargs={'object_id': user.id}) + "#profile-tab")


def setting_view(request):
    user = User.objects.get(id=request.user.id)

    if not user.is_superuser:
        return redirect(
            reverse('dashboard_admin:dashboard_profile_change', kwargs={'object_id': user.id}) + "#settings-tab")
    return redirect(reverse('admin:users_user_change', kwargs={'object_id': user.id}) + "#settings-tab")


def security_view(request):
    user = User.objects.get(id=request.user.id)
    if not user.is_superuser:
        return redirect(
            reverse('dashboard_admin:dashboard_profile_change', kwargs={'object_id': user.id}) + "#security-tab")
    return redirect(reverse('admin:users_user_change', kwargs={'object_id': user.id}) + "#security-tab")


def reports_view(request):
    return render(request, 'dashboard/reports.html', locals())


def redirect_view(request):
    if request.user.is_superuser:
        return render(request, 'admin/index.html', locals())
    return render(request, 'dashboard/index.html', locals())


@staff_member_required
def get_filter_options(request):
    options = ['2023', '2024']
    return JsonResponse({
        'options': options,
    })


def get_verifications_chart(request, year):
    identities = Identity.objects.annotate(month=TruncMonth("created")).values("month") \
        .annotate(count=Count("id")).order_by("-month")

    verified = identities.filter(status=Identity.STATUS_VERIFIED)
    pending = identities.filter(status=Identity.STATUS_PENDING)
    not_verified = identities.filter(status=Identity.STATUS_NOT_VERIFIED)

    month_data = get_data(identities)
    verification_data = {
        'verified': get_data(verified),
        'pending': get_data(pending),
        'not_verified': get_data(not_verified)
    }

    return JsonResponse({
        'title': f'Verifications Sent',
        'data': {
            'labels': list(month_data.keys()),
            'datasets': [
                {
                    'label': 'Total',
                    'backgroundColor': colorPrimary,
                    'borderColor': colorPrimary,
                    'data': list(month_data.values()),
                },
                {
                    'label': 'Verified',
                    'backgroundColor': colorSuccess,
                    'borderColor': colorSuccess,
                    'data': list(verification_data['verified'].values()),
                },
                {
                    'label': 'Pending',
                    'backgroundColor': colorPending,
                    'borderColor': colorPending,
                    'data': list(verification_data['pending'].values()),
                },
                {
                    'label': 'Not Verified',
                    'backgroundColor': colorDanger,
                    'borderColor': colorDanger,
                    'data': list(verification_data['not_verified'].values()),
                }
            ]
        },
    })


def get_tickets_chart(request, year):
    tickets = Ticket.objects.annotate(month=TruncMonth("created")).values("month") \
        .annotate(count=Count("id")).order_by("-month")
    new = tickets.filter(status=Ticket.STATUS_NEW).count()
    pending = tickets.filter(status=Ticket.STATUS_PENDING).count()
    closed = tickets.filter(status=Ticket.STATUS_CLOSED).count()
    return JsonResponse({
        'title': f'Total Tickets: {tickets.count()}',
        'data': {
            'labels': ['New', 'Pending', 'Closed'],
            'datasets': [{
                'label': 'Total',
                'backgroundColor': [colorSuccess, colorDanger, colorPrimary],
                'borderColor': [colorSuccess, colorDanger, colorPrimary],
                'data': [new, pending, closed],
            }]
        },
    })


def get_plan_chart(request, year):
    my_plan = MyPlan.objects.filter(user=request.user).last()
    return JsonResponse({
        'title': f'Identity Verification Limit: {my_plan.plan.limit}',
        'data': {
            'labels': ['Remaining', 'Used'],
            'datasets': [{
                'label': 'Total',
                'backgroundColor': [colorSuccess, colorDanger],
                'borderColor': [colorSuccess, colorDanger],
                'data': [
                    my_plan.remaining_credit(),
                    my_plan.total_credit() - my_plan.remaining_credit()
                ],
            }]
        },
    })


def get_customers_chart(request, year):
    user_ids = list(Customer.objects.filter(added_by=request.user).values_list('user', flat=True))
    users = User.objects.filter(id__in=user_ids)
    users = users.annotate(month=TruncMonth("date_joined")).values("month") \
        .annotate(count=Count("id")).order_by("-month")

    identities = Identity.objects.filter(user__in=user_ids).annotate(month=TruncMonth("created")).values("month") \
        .annotate(count=Count("id")).order_by("-month")

    verified = identities.filter(status=Identity.STATUS_VERIFIED)
    pending = identities.filter(status=Identity.STATUS_PENDING)
    not_verified = identities.filter(status=Identity.STATUS_NOT_VERIFIED)

    month_data = get_data(users)
    verification_data = {
        'verified': get_data(verified),
        'pending': get_data(pending),
        'not_verified': get_data(not_verified)
    }

    return JsonResponse({
        'title': f'Verifications Sent',
        'data': {
            'labels': list(month_data.keys()),
            'datasets': [
                {
                    'label': 'Total',
                    'backgroundColor': colorPrimary,
                    'borderColor': colorPrimary,
                    'data': list(month_data.values()),
                },
                {
                    'label': 'Verified',
                    'backgroundColor': colorSuccess,
                    'borderColor': colorSuccess,
                    'data': list(verification_data['verified'].values()),
                },
                {
                    'label': 'Pending',
                    'backgroundColor': colorPending,
                    'borderColor': colorPending,
                    'data': list(verification_data['pending'].values()),
                },
                {
                    'label': 'Not Verified',
                    'backgroundColor': colorDanger,
                    'borderColor': colorDanger,
                    'data': list(verification_data['not_verified'].values()),
                }
            ]
        },
    })


def get_payments_chart(request, year):
    payments = Payment.objects.annotate(month=TruncMonth("created")).values("month") \
        .annotate(count=Count("id")).order_by("-month")

    month_data = get_data(payments)

    return JsonResponse({
        'title': f'Total Payments: {payments.count()}',
        'data': {
            'labels': list(month_data.keys()),
            'datasets': [
                {
                    'label': 'Total',
                    'backgroundColor': colorPrimary,
                    'borderColor': colorPrimary,
                    'data': list(month_data.values()),
                },
            ]
        },
    })


def get_employees_chart(request, year):
    user_ids = list(Employee.objects.filter(added_by=request.user).values_list('user', flat=True))
    users = User.objects.filter(id__in=user_ids)
    users = users.annotate(month=TruncMonth("date_joined")).values("month") \
        .annotate(count=Count("id")).order_by("-month")

    identities = Identity.objects.filter(user__in=user_ids).annotate(month=TruncMonth("created")).values("month") \
        .annotate(count=Count("id")).order_by("-month")

    verified = identities.filter(status=Identity.STATUS_VERIFIED)
    pending = identities.filter(status=Identity.STATUS_PENDING)
    not_verified = identities.filter(status=Identity.STATUS_NOT_VERIFIED)

    month_data = get_data(users)
    verification_data = {
        'verified': get_data(verified),
        'pending': get_data(pending),
        'not_verified': get_data(not_verified)
    }

    return JsonResponse({
        'title': f'Verifications Sent',
        'data': {
            'labels': list(month_data.keys()),
            'datasets': [
                {
                    'label': 'Total',
                    'backgroundColor': colorPrimary,
                    'borderColor': colorPrimary,
                    'data': list(month_data.values()),
                },
                {
                    'label': 'Verified',
                    'backgroundColor': colorSuccess,
                    'borderColor': colorSuccess,
                    'data': list(verification_data['verified'].values()),
                },
                {
                    'label': 'Pending',
                    'backgroundColor': colorPending,
                    'borderColor': colorPending,
                    'data': list(verification_data['pending'].values()),
                },
                {
                    'label': 'Not Verified',
                    'backgroundColor': colorDanger,
                    'borderColor': colorDanger,
                    'data': list(verification_data['not_verified'].values()),
                }
            ]
        },
    })


def get_users_chart(request, year):
    users = User.objects.annotate(month=TruncMonth("date_joined")).values("month") \
        .annotate(count=Count("id")).order_by("-month")

    month_data = get_data(users)
    return JsonResponse({
        'title': f'Total Registered Users',
        'data': {
            'labels': list(month_data.keys()),
            'datasets': [
                {
                    'label': 'Total',
                    'backgroundColor': colorPrimary,
                    'borderColor': colorPrimary,
                    'data': list(month_data.values()),
                },
            ]
        },
    })


def get_data(objs):
    data = {}
    for obj in objs:
        data[months[obj['month'].month - 1]] = obj['count']
    month_data = {}
    for month in months:
        month_data[month] = data.get(month, 0)
    return month_data


#
# @staff_member_required
# def spend_per_customer_chart(request, year):
#     purchases = Purchase.objects.filter(time__year=year)
#     grouped_purchases = purchases.annotate(price=F('item__price')).annotate(month=ExtractMonth('time'))\
#         .values('month').annotate(average=Avg('item__price')).values('month', 'average').order_by('month')
#
#     spend_per_customer_dict = get_year_dict()
#
# for group in grouped_purchases:
#     spend_per_customer_dict[months[group['month']-1]] = round(group['average'], 2)

#     return JsonResponse({
#         'title': f'Spend per customer in {year}',
#         'data': {
#             'labels': list(spend_per_customer_dict.keys()),
#             'datasets': [{
#                 'label': 'Amount ($)',
#                 'backgroundColor': colorPrimary,
#                 'borderColor': colorPrimary,
#                 'data': list(spend_per_customer_dict.values()),
#             }]
#         },
#     })
#
#
# @staff_member_required
# def payment_success_chart(request, year):
#     purchases = Purchase.objects.filter(time__year=year)
#
#     return JsonResponse({
#         'title': f'Payment success rate in {year}',
#         'data': {
#             'labels': ['Successful', 'Unsuccessful'],
#             'datasets': [{
#                 'label': 'Amount ($)',
#                 'backgroundColor': [colorSuccess, colorDanger],
#                 'borderColor': [colorSuccess, colorDanger],
#                 'data': [
#                     purchases.filter(successful=True).count(),
#                     purchases.filter(successful=False).count(),
#                 ],
#             }]
#         },
#     })
#
#
# @staff_member_required
# def payment_method_chart(request, year):
#     purchases = Purchase.objects.filter(time__year=year)
#     grouped_purchases = purchases.values('payment_method').annotate(count=Count('id'))\
#         .values('payment_method', 'count').order_by('payment_method')
#
#     payment_method_dict = dict()
#
#     for payment_method in Purchase.PAYMENT_METHODS:
#         payment_method_dict[payment_method[1]] = 0
#
#     for group in grouped_purchases:
#         payment_method_dict[dict(Purchase.PAYMENT_METHODS)[group['payment_method']]] = group['count']
#
#     return JsonResponse({
#         'title': f'Payment method rate in {year}',
#         'data': {
#             'labels': list(payment_method_dict.keys()),
#             'datasets': [{
#                 'label': 'Amount ($)',
#                 'backgroundColor': generate_color_palette(len(payment_method_dict)),
#                 'borderColor': generate_color_palette(len(payment_method_dict)),
#                 'data': list(payment_method_dict.values()),
#             }]
#         },
#     })


def initiate_verification(request, id):
    try:
        user = User.objects.get(id=id)
        Identity.initiate_verification(user)
        user.send_identification_email()
    except Exception as e:
        return JsonResponse({'errorMesssage': str(e)})
    return JsonResponse({'ok': 'All set'})

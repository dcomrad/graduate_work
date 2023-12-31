from django.contrib import admin
from django_object_actions import DjangoObjectActions, action

from utils.api import ApiHelper

from .models import Subscription, Transaction, UserSubscription


class UserFullnameMixin:
    @admin.display(description='Full name')
    def get_user_fullname(self, obj):
        api_helper = ApiHelper()
        user_id = obj.user_id
        response = api_helper.get_user_by_id(user_id)
        return response.body.get('full_name', 'John Doe')


@admin.register(Transaction)
class TransactionAdmin(
    DjangoObjectActions, admin.ModelAdmin, UserFullnameMixin
):
    list_display = (
        'user_id',
        'get_user_fullname',
        'provider',
        'subscription',
        'actual_amount',
        'status',
        'created_at',
    )
    list_filter = (
        'user_id',
        'created_at',
    )
    readonly_fields = (
        'get_user_fullname',
        'actual_amount',
    )
    change_actions = ('refund_transaction',)

    @action(label='Refund', description='Refund this transaction')
    def refund_transaction(self, _, obj):
        api_helper = ApiHelper()
        transaction_id = obj.id
        api_helper.refund_transaction(transaction_id=transaction_id)

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'actual_price',
        'currency',
        'is_active',
        'recurring_interval',
        'recurring_interval_count',
        'permission_rank',
    )
    readonly_fields = ('actual_price',)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(UserSubscription)
class UserSubscriptionAdmin(
    DjangoObjectActions, admin.ModelAdmin, UserFullnameMixin
):
    list_display = (
        'user_id',
        'get_user_fullname',
        'subscription',
        'expired_at',
        'renew_to',
        'is_active',
    )
    list_filter = ('user_id',)
    readonly_fields = ('get_user_fullname',)
    change_actions = ('cancel_user_subscription',)

    @action(
        label='Cancel subscription',
        description='Cancel this user subscription',
    )
    def cancel_user_subscription(self, _, obj):
        api_helper = ApiHelper()
        user_subscription_id = obj.id
        api_helper.cancel_user_subscription(
            user_subscription_id=user_subscription_id,
        )

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

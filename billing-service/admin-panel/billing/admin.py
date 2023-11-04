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
        'get_user_id',
        'get_user_fullname',
        'provider',
        'subscription',
        'amount',
        'status',
        'created_at',
    )
    list_filter = (
        'user_id__user_id',
        'created_at',
    )
    readonly_fields = ('get_user_fullname',)
    change_actions = ('refund_transaction',)

    @admin.display(description='User ID')
    def get_user_id(self, obj):
        return obj.user_id

    @action(label='Refund', description='Refund this transaction')
    def refund_transaction(self, _, obj):
        api_helper = ApiHelper()
        transaction_id = obj.id
        api_helper.refund_transaction(transaction_id=transaction_id)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'price',
        'currency',
        'is_active',
        'recurring_interval',
        'recurring_interval_count',
        'permission_rank',
    )


@admin.register(UserSubscription)
class UserSubscriptionAdmin(
    DjangoObjectActions, admin.ModelAdmin, UserFullnameMixin
):
    list_display = (
        'user_id',
        'get_user_fullname',
        'subscription',
        'expired_at',
        'auto_renewal',
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
        user_id = obj.user_id
        subscription_id = obj.subscription.id
        api_helper.cancel_user_subscription(
            user_id=user_id, subscription_id=subscription_id
        )

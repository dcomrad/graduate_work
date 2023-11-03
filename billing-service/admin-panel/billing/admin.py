from django.contrib import admin

from utils.api import ApiHelper

from .models import Subscription, Transaction, UserSubscription


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
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

    @admin.display(description='User ID')
    def get_user_id(self, obj):
        return obj.user_id

    @admin.display(description='Full name')
    def get_user_fullname(self, obj):
        api_helper = ApiHelper()
        user_id = obj.user_id
        response = api_helper.get_user_by_id(user_id)
        return response.body.get('full_name', '')


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
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'user_id',
        'subscription',
        'expired_at',
        'auto_renewal',
        'is_active',
    )
    list_filter = ('user_id',)

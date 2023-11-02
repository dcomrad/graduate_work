from django.contrib import admin

from .models import Subscription, Transaction, UserSubscription


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'get_user_id',
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

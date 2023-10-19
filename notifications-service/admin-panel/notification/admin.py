from django.contrib import admin
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from notification.datasource import get_users
from notification.mock_users_queryset import CustomChangeList
from notification.models import ExternalUser, Template

admin.site.unregister(Group)


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'title', 'content', 'placeholders',
                    'is_active')
    list_filter = ('type', 'is_active')
    search_fields = ('content',)
    readonly_fields = ('placeholders',)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ExternalUser)
class ExternalUserAdmin(admin.ModelAdmin):
    list_display = ('login', 'full_name', 'email', 'time_zone',
                    'notifications_enabled')
    readonly_fields = ('id', 'login', 'full_name', 'email')
    actions = ('send', 'schedule')
    queryset = get_users()
    # TODO: реализовать сортировку, поиск

    @admin.action(description='Отправить сообщение')
    def send(self, request, queryset):
        ids = (str(item.id) for item in queryset)
        return HttpResponseRedirect(
            f'{reverse("notification:send")}?ids={",".join(ids)}&return={request.path}'  # noqa:E501
        )

    @admin.action(description='Запланировать отправку сообщения')
    def schedule(self, request, queryset):
        ids = (str(item.id) for item in queryset)
        return HttpResponseRedirect(
            f'{reverse("notification:schedule")}?ids={",".join(ids)}&return={request.path}'  # noqa:E501
        )

    def get_queryset(self, request):
        return self.queryset

    def get_changelist(self, request, **kwargs):
        return CustomChangeList

    def get_list(self, request, page_number, page_size):
        data = self.queryset.as_list
        offset = (page_number - 1) * page_size
        return {
            "total": len(data),
            "items": data[offset:offset + page_size],
        }

    def get_object(self, request, object_id, *args, **kwargs):
        return self.queryset.as_dict[object_id]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

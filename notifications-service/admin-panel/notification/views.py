from http import HTTPStatus
from typing import Callable, Type

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from notification.forms import ScheduleForm, SendForm
from notification.logger import logger_factory
from notification.models import Template
from notification.settings import settings
from notification.utils import make_http_request

logger = logger_factory(__name__)

MESSAGE_SENT = 'Уведомление отправлено: {}'
SENDING_ERROR = 'Ошибка при отправке уведомления: {}'

MESSAGE_SCHEDULED = 'Уведомление добавлено в планировщик: {}'
SCHEDULING_ERROR = 'Ошибка при добавлении уведомления в планировщик: {}'


def base_view(
        request,
        template: str,
        form_class: Type[SendForm] | Type[ScheduleForm],
        api_url: Callable,
        success_msg: str,
        error_msg: str
):
    form = form_class(request.POST or None)
    recipients = request.GET.get('ids', '').split(',')

    if form.is_valid():
        notification_template = Template.objects.get(
            id=request.POST.get('template')
        )

        # склеивание имени и значения шаблонных параметров из форм
        _vars = {
            name: value
            for name, value in zip(
                request.POST.getlist('varNameInput', []),
                request.POST.getlist('varValueInput', [])
            )
            if name and value
        }

        # проверка наличия всех шаблонных параметров
        for placeholder in notification_template.placeholders:
            if placeholder == 'user':
                continue

            if placeholder not in _vars and f'{placeholder}_id' not in _vars:
                messages.add_message(
                    request, messages.ERROR, SENDING_ERROR.format(
                        f'Отсутствует переменная {placeholder}'
                    )
                )
                logger.error(f'{placeholder} or {placeholder}_id  not in {_vars}')  # noqa:E501
                return HttpResponseRedirect(
                    request.GET.get('return', '/admin/'))

        # подготовка данных для http запроса
        payload = {
            'template_id': str(notification_template.id),
            'receivers': recipients,
            'type': notification_template.type,
            'vars': _vars
        }

        if form_class is SendForm:
            data = payload
            params = None
        else:
            data = dict(payload=payload)
            params = {'eta': request.POST.get('datetime')}

            if days_of_week := request.POST.getlist('weekdays_repeat', []):
                data['days_of_week'] = days_of_week

        response = make_http_request(
            'POST',
            url=api_url(request.POST.get('priority')),
            data=data,
            params=params
        )
        if response.status_code in [HTTPStatus.OK, HTTPStatus.ACCEPTED]:
            messages.add_message(
                request,
                messages.SUCCESS,
                success_msg.format(response.text)
            )
        else:
            logger.error(f'{response.status_code}: {response.text}')
            messages.add_message(
                request,
                messages.ERROR,
                error_msg.format(f': status_code={response.status_code}')
            )

        return HttpResponseRedirect(request.GET.get('return', '/admin/'))

    context = {
        'users_count': len(recipients),
        'form': form
    }
    return render(request, template, context)


@staff_member_required
def send_view(request):
    return base_view(
        request,
        'send.html',
        SendForm,
        settings.app.send_api_url,
        MESSAGE_SENT,
        SENDING_ERROR
    )


@staff_member_required
def schedule_view(request):
    return base_view(
        request,
        'schedule.html',
        ScheduleForm,
        settings.app.schedule_api_url,
        MESSAGE_SCHEDULED,
        SCHEDULING_ERROR
    )

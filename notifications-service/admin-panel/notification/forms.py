from django import forms
from django.db import models
from notification.models import Template


class PriorityType(models.TextChoices):
    HIGH = 'important', 'Высокий'
    MEDIUM = 'normal', 'Обычный'


class Weekdays(models.TextChoices):
    MONDAY = '1', 'Понедельник'
    TUESDAY = '2', 'Вторник'
    WEDNESDAY = '3', 'Среда'
    THURSDAY = '4', 'Четверг'
    FRIDAY = '5', 'Пятница'
    SATURDAY = '6', 'Суббота'
    SUNDAY = '0', 'Воскресенье'


def get_active_templates():
    templates = Template.objects.filter(is_active=True)
    return [
        (template.id, f'{template.type}: {template.name}')
        for template in templates
    ]


class SendForm(forms.Form):
    priority = forms.ChoiceField(
        choices=PriorityType.choices,
        label='Приоритет уведомления',
    )
    template = forms.ChoiceField(
        choices=get_active_templates,
        label='Выберите шаблон'
    )


class ScheduleForm(SendForm):
    datetime = forms.DateTimeField(
        widget=forms.DateTimeInput(
            format='%d/%m/%y %H:%M',
            attrs={'type': 'datetime-local'}
        ),
        label='Выберите дату и время отправки'
    )
    weekdays_repeat = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=Weekdays.choices,
        label='Выберите дни повторений',
    )

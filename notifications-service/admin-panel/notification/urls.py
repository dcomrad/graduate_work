from django.urls import path
from notification.views import schedule_view, send_view

app_name = 'notification'

urlpatterns = [
    path('send/', send_view, name='send'),
    path('schedule/', schedule_view, name='schedule'),
]

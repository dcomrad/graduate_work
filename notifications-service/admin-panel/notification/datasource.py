import orjson
from notification.models import ExternalUser
from notification.settings import settings
from notification.utils import make_http_request


class CustomQueryset:
    def __init__(self, data):
        self._dict = data
        self._list = list(data.values())

    def filter(self, pk__in):
        return [self._dict[pk] for pk in pk__in]

    @property
    def as_dict(self):
        return self._dict

    @property
    def as_list(self):
        return self._list


def get_users():
    response = make_http_request(
        'GET',
        settings.app.users_api_url,
        headers={'Authorization': f'Bearer {settings.app.jwt_token}'}
    )
    return CustomQueryset({
        str(user['id']): ExternalUser(
            id=user['id'],
            login=user['login'],
            full_name=user['full_name'],
            email=user['email'],
            time_zone=user['time_zone'],
            notifications_enabled=user['notifications_enabled'],
        )
        for user in orjson.loads(response.text)
    })

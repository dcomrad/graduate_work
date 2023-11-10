import functools

from src.core.exceptions import NotFoundException

from .base import ProviderManager
from .stripe import get_stripe_manager

AVAILABLE_PROVIDERS = {
    'stripe':  get_stripe_manager
}

PROVIDER_NOT_FOUND = 'Провайдер {provider} не найден'


@functools.cache
def get_provider_manager(provider_name: str = 'stripe') -> ProviderManager:
    if provider_name not in AVAILABLE_PROVIDERS:
        raise NotFoundException(PROVIDER_NOT_FOUND.format(provider_name))

    return AVAILABLE_PROVIDERS[provider_name]()

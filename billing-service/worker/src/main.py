import asyncio
import datetime
from time import sleep

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from src.config import settings
from src.logger import get_configured_logger
from src.models import UserSubscription
from src.postgres import AsyncSessionLocal
from src.utils import make_http_request

logger = get_configured_logger(__name__)


async def main():
    while True:
        stmt = select(UserSubscription).filter(UserSubscription.expired_at < datetime.date)
        try:
            async with AsyncSessionLocal() as session:
                subscriptions_to_charge = await session.execute(stmt)
        except IntegrityError:
            logger.error('Ошибка доступа к БД')

        charge_list = [
            {
                'user_id': subscription.user_id,
                'subscription_id': subscription.renew_to
            }
            for subscription in subscriptions_to_charge]

        await make_http_request(
            'POST',
            f'{settings.app.billing_api_url}/backoffice/charge/',
            body=charge_list,
            token=settings.app.jwt_token
        )

        sleep(settings.app.refresh_period_s)


if __name__ == '__main__':
    logger.info('Worker started')
    asyncio.run(main())

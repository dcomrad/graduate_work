import asyncio
import datetime
from time import sleep

from sqlalchemy import select
from src.config import settings
from src.logger import get_configured_logger
from src.models import UserSubscription
from src.postgres import AsyncSessionLocal
from src.utils import make_http_request

logger = get_configured_logger(__name__)


async def main():
    while True:
        stmt = select(UserSubscription).filter(UserSubscription.expired_at < datetime.date)
        async with AsyncSessionLocal() as session:
            for row in session.execute(stmt):
                await make_http_request(
                    'POST',
                    f'{settings.app.billing_api_url}/backoffice/charge/{row.user_id}',
                    params={'subscription_id': row.renew_to},
                    token=settings.app.jwt_token
                )

        sleep(settings.app.refresh_period_s)


if __name__ == '__main__':
    logger.info('Worker started')
    asyncio.run(main())

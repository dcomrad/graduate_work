from http import HTTPStatus

from fastapi import APIRouter, Depends, Response
from src.api.v1 import openapi
from src.db.postgres import AsyncSession, get_async_session

router = APIRouter(prefix='/webhooks')


@router.post(
    '/stripe',
    **openapi.webhooks.stripe_webhook.model_dump()
)
async def stripe_webhook(
        session: AsyncSession = Depends(get_async_session)
):
    return Response('OK',  status_code=HTTPStatus.OK)

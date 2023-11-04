from http import HTTPStatus
from fastapi import APIRouter, Depends, Response
from src.db.postgres import get_async_session, AsyncSession
from src.api.v1 import openapi

router = APIRouter(prefix='/webhooks')


@router.post(
    '/stripe',
    **openapi.webhooks.stripe_webhook.model_dump()
)
async def stripe_webhook(
        session: AsyncSession = Depends(get_async_session)
):
    return Response('OK',  status_code=HTTPStatus.OK)

from fastapi import APIRouter
from src.api.v1.endpoints import (backoffice_router,
                                  customer_payment_methods_router,
                                  customer_subscriptions_router,
                                  customer_transactions_router,
                                  subscription_router, webhook_router)

v1_router = APIRouter(prefix='/api/v1')

v1_router.include_router(subscription_router, tags=['Subscriptions'])
v1_router.include_router(webhook_router, tags=['Webhooks'])
v1_router.include_router(backoffice_router, tags=['Back office'])

customer = dict(prefix='/customer', tags=['Customers'])
v1_router.include_router(customer_payment_methods_router, **customer)
v1_router.include_router(customer_subscriptions_router, **customer)
v1_router.include_router(customer_transactions_router, **customer)

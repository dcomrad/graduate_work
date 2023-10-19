from fastapi import APIRouter
from src.api.v1.endpoints import (bookmarks_router, progress_router,
                                  rating_router, reviews_router)

v1_router = APIRouter(prefix='/api/v1')

v1_router.include_router(progress_router, tags=['Progress'])
v1_router.include_router(bookmarks_router, tags=['Bookmarks'])
v1_router.include_router(rating_router, tags=['Movies rating'])
v1_router.include_router(reviews_router, tags=['Reviews'])

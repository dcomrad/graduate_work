from fastapi import APIRouter
from src.api.v1.endpoints import films_router, genres_router, persons_router

v1_router = APIRouter(prefix='/api/v1')

v1_router.include_router(films_router, tags=['Films'])
v1_router.include_router(genres_router, tags=['Genres'])
v1_router.include_router(persons_router, tags=['Persons'])

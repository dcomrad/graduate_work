import argparse
import asyncio

from src.crud import user_crud
from src.db.postgres import AsyncSessionLocal
from src.schemas.user import UserSignup


class SuperuserCreate(UserSignup):
    is_superuser: bool = True


async def main():
    """Создаёт суперпользователя с переданным в CLI логином и паролем."""
    parser = argparse.ArgumentParser(description='Создание суперпользователя')

    parser.add_argument('login', help='Логин')
    parser.add_argument('password', help='Пароль')

    args = parser.parse_args()

    superuser = SuperuserCreate(
        login=args.login,
        password=args.password,
        full_name='Суперпользователь'
    )

    async with AsyncSessionLocal() as async_session:
        await user_crud.create(superuser, async_session)


if __name__ == '__main__':
    asyncio.run(main())

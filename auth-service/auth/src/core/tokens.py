from pydantic import BaseModel
from src.db.redis import RedisTokenStorage
from src.db_models.user import User
from src.jwt import AuthJWT
from src.jwt.permissions import SUPERUSER_PERMISSION


class Token(BaseModel):
    """Схема токена."""
    access: str
    refresh: str


async def get_user_tokens(
        user: User,
        user_agent: str,
        authorize: AuthJWT,
        token_storage: RedisTokenStorage,
) -> Token:
    permissions = SUPERUSER_PERMISSION if user.is_superuser else user.permissions
    tokens = await generate_tokens(user.id, permissions, authorize)

    await token_storage.set_token(
        user=user.id,
        user_agent=user_agent,
        token=await authorize.get_jti(tokens.refresh)
    )

    return tokens


async def generate_tokens(
        subject: int,
        permissions: list[str],
        authorize: AuthJWT
) -> Token:
    """Генерирует пару access и refresh токенов. Записывает в access токен
    список разрешений, согласно аргумента permission."""
    user_claims = {'perm': permissions}
    access_token = await authorize.create_access_token(subject=subject,
                                                       user_claims=user_claims)

    refresh_token = await authorize.create_refresh_token(subject=subject)

    return Token(access=access_token, refresh=refresh_token)

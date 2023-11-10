from pydantic import Field
from pydantic_settings import BaseSettings


class TestsSettings(BaseSettings):
    host: str = Field(validation_alias='BACKEND_HOST', default='localhost')
    port: int = Field(validation_alias='BACKEND_PORT', default=9900)
    admin_token: str = Field(
        validation_alias='ADMIN_JWT_TOKEN', default='default-admin-token'
    )
    user_token: str = Field(
        validation_alias='USER_JWT_TOKEN', default='default-user-token'
    )

    @property
    def service_url(self) -> str:
        return f'http://{self.host}:{self.port}/api/v1'


tests_settings = TestsSettings()

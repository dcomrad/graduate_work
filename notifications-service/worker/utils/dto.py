import enum
import http
import uuid

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class ResponseDTO(BaseModel):
    status: http.HTTPStatus


class TypeEnum(str, enum.Enum):
    email = "email"
    push = "push"
    telegram = "telegram"


class SendQueryPriorityDTO(str, enum.Enum):
    normal = "normal"
    important = "important"


IdType = uuid.UUID | int
JsonType = dict


class SendBodyPayloadDTO(BaseModel):
    template_id: IdType
    recievers: list[IdType]
    type: TypeEnum
    vars: JsonType

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "template_id": "9ab9df5e-c1a8-49fe-aca3-2462fdfc58e8",
                    "recievers": [
                        "d05a3d39-622e-4da9-9a89-850b53ccea4d",
                        "528e7dc0-4998-41ad-8228-23de6fe7d9f0",
                        "e8106412-0cb9-422c-b5c3-0353a010f0a8",
                    ],
                    "vars": {"movie_id": "c05a3d39-622e-4da9-9a89-850b53ccea4d"},
                    "type": "email",
                }
            ]
        }
    }


class SendResponseDTO(ResponseDTO):
    pass


class Settings(BaseSettings):
    smtp_host: str = Field(env="SMTP_HOST")
    smtp_port: int = Field(env="SMTP_PORT")
    smtp_login: str = Field(env="SMTP_LOGIN")
    smtp_password: str = Field(env="SMTP_PASSWORD")
    smtp_from: str = Field(env="SMTP_FROM")


class RabbitSettings(BaseSettings):
    RABBIT_URL: str = Field(env="RABBIT_URL")
    
    class Config:
        env_file = ".env"


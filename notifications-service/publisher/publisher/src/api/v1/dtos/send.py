import enum
import http
import uuid

import pydantic


class ResponseDTO(pydantic.BaseModel):
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


class SendBodyPayloadDTO(pydantic.BaseModel):
    template_id: IdType
    receivers: list[IdType]
    type: TypeEnum
    vars: JsonType

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "template_id": "9ab9df5e-c1a8-49fe-aca3-2462fdfc58e8",
                    "receivers": [
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

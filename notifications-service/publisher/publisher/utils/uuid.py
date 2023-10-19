import uuid

import pydantic


class UUIDMixin(pydantic.BaseModel):
    id: uuid.UUID

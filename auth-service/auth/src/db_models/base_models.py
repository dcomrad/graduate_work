from uuid import uuid4

from sqlalchemy import UUID, Column


class IDMixin:
    """Примесь, используемая для задания поля id у потомков."""
    id = Column(UUID, primary_key=True, default=uuid4)

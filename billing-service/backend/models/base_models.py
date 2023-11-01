from sqlalchemy import Column, UUID
import uuid


class IDMixin:
    """Примесь, используемая для задания поля id у потомков."""
    id = Column(UUID, primary_key=True, default=uuid.uuid4(), unique=True, nullable=False)

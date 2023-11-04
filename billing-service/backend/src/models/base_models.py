# flake8: noqa: E501, VNE003
import uuid

from sqlalchemy import UUID, Column


class IDMixin:
    """Примесь, используемая для задания поля id у потомков."""
    id = Column(UUID, primary_key=True, default=uuid.uuid4(), unique=True, nullable=False)

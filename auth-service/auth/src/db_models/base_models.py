from sqlalchemy import Column, Integer


class IDMixin:
    """Примесь, используемая для задания поля id у потомков."""
    id = Column(Integer, primary_key=True, autoincrement=True)

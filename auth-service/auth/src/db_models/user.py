from sqlalchemy import Boolean, Column, String, Text
from sqlalchemy.orm import relationship
from src.db.postgres import Base
from src.db_models.base_models import IDMixin


class User(Base, IDMixin):
    """Модель пользователя."""
    __tablename__ = 'user'
    login = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(Text)
    email = Column(String(50))
    is_superuser = Column(Boolean, nullable=False, default=False)
    full_name = Column(String(100), nullable=False)
    time_zone = Column(String(100), nullable=False, default='Europe/Moscow')
    notifications_enabled = Column(Boolean, nullable=False, default=True)
    access_history = relationship('AccessHistory', cascade='delete',
                                  order_by="AccessHistory.access_time.desc()")

    @property
    def roles(self):
        """Метод возвращает список ролей пользователя, проходя сквозь m2m
        таблицу."""
        return [role._role for role in self._roles]

    @property
    def permissions(self):
        """Метод возвращает список уникальных разрешений пользователя, проходя
        сквозь m2m таблицу."""
        result = set()

        for role in self.roles:
            result.update({permission.name for permission in role.permissions})

        return list(result)

    _roles = relationship('UserRole', lazy="joined", cascade='all, delete')
    _services = relationship('UserService', lazy="joined", cascade='all, delete')

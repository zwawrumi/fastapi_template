import uuid
from enum import Enum

from sqlalchemy import Column, String, Integer, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship

from backend.authentication.database import Base


class PortalRole(str, Enum):
    ROLE_PORTAL_USER = "ROLE_PORTAL_USER"
    ROLE_PORTAL_ADMIN = "ROLE_PORTAL_ADMIN"
    ROLE_PORTAL_SUPERADMIN = "ROLE_PORTAL_SUPERADMIN"


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    username = Column(String, nullable=True, unique=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String)
    is_active = Column(Boolean(), nullable=True)
    roles = Column(ARRAY(String), nullable=False)

    items = relationship("Item", back_populates="owner")

    @property
    def is_super_admin(self) -> bool:
        return PortalRole.ROLE_PORTAL_SUPERADMIN in self.roles

    @property
    def is_admin(self) -> bool:
        return PortalRole.ROLE_PORTAL_ADMIN in self.roles

    def add_admin_privilege(self):
        if not self.is_admin:
            return self.roles + [PortalRole.ROLE_PORTAL_ADMIN]

    # def add_super_admin_privilege(self):
    #    if not self.is_super_admin:
    #        return self.roles + [PortalRole.ROLE_PORTAL_SUPERADMIN]

    def remove_admin_privilege(self):
        if self.is_admin:
            return {role for role in self.roles if role != PortalRole.ROLE_PORTAL_ADMIN}


class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String, index=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))

    owner = relationship('User', back_populates='items')

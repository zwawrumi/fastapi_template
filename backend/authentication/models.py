import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from backend.authentication.database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    username = Column(String, nullable=True, unique=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String)
    is_active = Column(Boolean(), nullable=True)

    items = relationship("Item", back_populates="owner")


class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String, index=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))

    owner = relationship('User', back_populates='items')

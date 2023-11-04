from typing import Union
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import update, and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User, PortalRole


# business context #


class UserDAL:
    """data access for users"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(
            self, username: str, hashed_password: str, email: str, roles: list[PortalRole]
    ) -> User:
        new_user = User(
            username=username,
            hashed_password=hashed_password,
            email=email,
            is_active=True,
            roles=roles
        )
        self.db_session.add(new_user)
        await self.db_session.flush()
        return new_user

    async def delete_user(self, user_id: UUID) -> Union[UUID, None]:
        query = (
            update(User)
            .where(and_(User.id == user_id, User.is_active == True))
            .values(is_active=False)
            .returning(User.id)
        )
        res = await self.db_session.execute(query)
        deleted_user_id_row = res.fetchone()
        if deleted_user_id_row is not None:
            return deleted_user_id_row[0]

    async def get_user_by_id(self, user_id: UUID) -> Union[User, None]:
        query = select(User).where(User.id == user_id)
        res = await self.db_session.execute(query)
        user_row = res.fetchone()
        if user_row is not None:
            return user_row[0]

    async def update_user(self, user_id: UUID, **kwargs) -> Union[User, None]:
        query = (
            update(User)
            .where(and_(User.id == user_id, User.is_active == True))
            .values(kwargs)
            .returning(User.id)
        )
        res = await self.db_session.execute(query)
        update_user_id = res.fetchone()
        if update_user_id is not None:
            return update_user_id[0]

    async def get_user_by_email(self, email: str) -> Union[User, None]:
        query = select(User).where(User.email == email)
        res = await self.db_session.execute(query)
        user_row = res.fetchone()
        if user_row is not None:
            return user_row[0]


def check_user_permission(target_user: User, current_user: User) -> bool:
    if PortalRole.ROLE_PORTAL_SUPERADMIN in current_user.roles:
        raise HTTPException(
            status_code=406, detail='Superadmin cannot be deleted via API'
        )
    if target_user.id != current_user.id:
        if not {
            PortalRole.ROLE_PORTAL_ADMIN,
            PortalRole.ROLE_PORTAL_SUPERADMIN,
        }.intersection(current_user.roles):
            return False
        if (
                PortalRole.ROLE_PORTAL_SUPERADMIN in target_user.roles
                and PortalRole.ROLE_PORTAL_SUPERADMIN in current_user.roles
        ):
            return False
    return True

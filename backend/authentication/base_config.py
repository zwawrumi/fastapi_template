from typing import Union
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from backend.secure import hash_password
from .manager import UserDAL, PortalRole
from .models import User
from .schemas import UserCreate, ShowUser


async def _create_new_user(body: UserCreate, session) -> ShowUser:
    async with session.begin():
        user_dal = UserDAL(session)
        user = await user_dal.create_user(
            username=body.username,
            email=body.email,
            hashed_password=hash_password(body.password),
            roles=[PortalRole.ROLE_PORTAL_USER, ]
        )
        return ShowUser(
            user_id=user.id,
            username=user.username,
            email=user.email,
            is_active=user.is_active,
        )


async def _delete_user(user_id, session) -> Union[UUID, None]:
    async with session.begin():
        user_dal = UserDAL(session)
        deleted_user_id = await user_dal.delete_user(
            user_id=user_id,
        )
        return deleted_user_id


async def _get_user_by_id(user_id, session) -> Union[User, None]:
    async with session.begin():
        user_dal = UserDAL(session)
        user = await user_dal.get_user_by_id(
            user_id=user_id,
        )
        if user is not None:
            return user


async def _update_user(user_id: UUID, body, db) -> Union[UUID, None]:
    async with db as session:
        async with session.begin():
            user = UserDAL(session)
            update_user_id = await user.update_user(
                user_id=user_id,
                **body
            )
            return update_user_id


async def _get_user_by_email_for_auth(email: str, db: AsyncSession):
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            return await user_dal.get_user_by_email(
                email=email,
            )

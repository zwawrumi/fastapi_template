from datetime import timedelta
from typing import Union
from uuid import UUID

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.logger import logger
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.secure import hash_password, create_access_token
from config import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_TOKEN, ALGORITHM
from .base_config import _create_new_user, _delete_user, _get_user_by_id, _update_user, _get_user_by_email_for_auth
from .database import get_db
from .manager import check_user_permission
from .models import User
from .schemas import (ShowUser, UserCreate, DeleteUser,
                      UpdateUserRequest, UpdatedUserResponse, Token)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/user/token')


async def get_current_user_from_token(
        token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    cred_exceptions = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate'
    )
    try:
        payload = jwt.decode(
            token, SECRET_TOKEN, algorithms=[ALGORITHM]
        )
        email: str = payload.get('sub')
        print('username/email extracted is', email)
        if email is None:
            raise cred_exceptions
    except JWTError:
        raise cred_exceptions
    user = await _get_user_by_email_for_auth(email=email, db=db)
    if user is None:
        raise cred_exceptions
    return user


async def authenticate_user(email: str, password: str, db: AsyncSession) -> Union[User, None]:
    user = await _get_user_by_email_for_auth(email=email, db=db)
    if user is None:
        return
    if not hash_password(password):
        return
    return user


@router.post("/", response_model=ShowUser)
async def create_user(body: UserCreate, db: AsyncSession = Depends(get_db)) -> ShowUser:
    try:
        return await _create_new_user(body, db)
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")


@router.delete('/', response_model=DeleteUser)
async def delete_user(
        user_id: UUID,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_from_token)
):
    user_for_deletion = await _get_user_by_id(user_id, db)
    if user_for_deletion is None:
        raise HTTPException(
            status_code=404, detail=f'User with id {user_id} not found'
        )
    if not check_user_permission(
            target_user=user_for_deletion,
            current_user=current_user
    ):
        raise HTTPException(status_code=403, detail='Forbidden')

    deleted_user_id = await _delete_user(user_id, db)
    if deleted_user_id is None:
        raise HTTPException(status_code=404, detail=f'{user_id} not found')
    return DeleteUser(deleted_user_id=deleted_user_id)


@router.get('/', response_model=ShowUser)
async def get_user_by_id(user_id: UUID, db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(get_current_user_from_token)) -> ShowUser:
    user = await _get_user_by_id(user_id, db)
    if user is None:
        raise HTTPException(status_code=404, detail=f'User with {user_id} not found')
    show_user = ShowUser(
        user_id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active
    )

    return show_user


@router.patch("/", response_model=UpdatedUserResponse)
async def update_user_by_id(
        user_id: UUID,
        body: UpdateUserRequest,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_from_token),
) -> UpdatedUserResponse:
    updated_user_params = body.model_dump(exclude_none=True)
    if not any(updated_user_params.values()):
        raise HTTPException(
            status_code=422,
            detail="At least one parameter for user update info should be provided",
        )
    user_for_update = await _get_user_by_id(user_id, db)
    if user_for_update is None:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} not found."
        )
    if not check_user_permission(
            target_user=user_for_update,
            current_user=current_user
    ):
        raise HTTPException(status_code=403, detail='Forbidden')
    try:
        updated_user_id = await _update_user(user_id=user_id, body=body, db=db)

    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")
    return UpdatedUserResponse(updated_user_id=updated_user_id)


# updated_user_id = await _update_user(user_id=user_id, body=body, db=db)
@router.post('/token', response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password'
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': user.email, 'custom': [1, 2, 3, 4]}, expires_delta=access_token_expires
    )
    return {'access_token': access_token, 'token_type': 'bearer'}


@router.get('/auth_endpoint')
async def under_jwt(current_user: User = Depends(get_current_user_from_token)):
    user_response = ShowUser(
        email=current_user.email,
        is_active=current_user.is_active,
        username=current_user.username,
        user_id=current_user.id
    )
    return {'success': True, 'current_user': user_response}


@router.patch('/admin', response_model=UpdatedUserResponse)
async def grant_admin(
        user_id: UUID,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_from_token),

):
    if not current_user.is_super_admin:
        raise HTTPException(status_code=403, detail='Forbidden')
    if current_user.id == user_id:
        raise HTTPException(
            status_code=400, detail='Cannot manage to itself'
        )
    user_for_promotion = await _get_user_by_id(user_id, db)
    if user_for_promotion.is_super_admin or user_for_promotion.is_admin:
        raise HTTPException(
            status_code=409, detail=f'User with id {user_id} is already admin / super_admin'
        )
    if user_for_promotion is None:
        raise HTTPException(
            status_code=404, detail=f'User with {user_id} not found'
        )
    updated_user = {
        'roles': {*user_for_promotion.add_admin_privilege()}
    }
    try:
        updated_user_id = await _update_user(
            user_id=user_id, body=updated_user, db=db
        )
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f'Database error: {err}')

    return UpdatedUserResponse(updated_user_id=updated_user_id)


@router.delete('/admin', response_model=UpdatedUserResponse)
async def revoke_admin(
        user_id: UUID,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_from_token),

):
    if not current_user.is_super_admin:
        raise HTTPException(status_code=403, detail='Forbidden')
    if current_user.id == user_id:
        raise HTTPException(
            status_code=400, detail='Cannot delete yourself'
        )
    user_for_delete = await _get_user_by_id(user_id, db)
    if not user_for_delete.is_admin:
        raise HTTPException(
            status_code=409, detail=f'User with id {user_id} has not admin privilege'
        )
    if user_for_delete is None:
        raise HTTPException(
            status_code=404, detail=f'User with {user_id} not found'
        )
    updated_user = {
        'roles': user_for_delete.remove_admin_privilege()
    }
    try:
        updated_user_id = await _update_user(
            user_id=user_id, body=updated_user, db=db
        )
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f'Database error: {err}')

    return UpdatedUserResponse(updated_user_id=updated_user_id)

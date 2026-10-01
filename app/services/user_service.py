from app.core.security import (DUMMY_PASSWORD_HASH, hash_password,
                               verify_password)
from app.models.user import User
from app.schemas.user import UserRegister
from starlette.concurrency import run_in_threadpool
from tortoise.exceptions import IntegrityError


class UserAlreadyExistsError(Exception):
    pass


class UserService:
    @staticmethod
    async def register(data: UserRegister) -> User:
        password_hash = await run_in_threadpool(hash_password, data.password)
        try:
            return await User.create(
                username=data.username,
                email=str(data.email),
                password_hash=password_hash,
            )
        except IntegrityError as error:
            raise UserAlreadyExistsError("El usuario o correo ya existe") from error

    @staticmethod
    async def authenticate(username: str, password: str) -> User | None:
        user = await User.get_or_none(username=username.lower())
        valid = await run_in_threadpool(
            verify_password,
            password,
            user.password_hash if user else DUMMY_PASSWORD_HASH,
        )
        if not valid or user is None or not user.is_active:
            return None
        return user

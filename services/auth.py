from arq import ArqRedis
from crud.currency import (
    CRUDCurrency,
    CRUDUserCurrency,
)
from crud.user import CRUDAuthUser
from fastapi import HTTPException, status, Request

from firebase_admin import auth as firebase_auth

from core.exceptions import ResourceExists
from core.externals.mono.mono_client import MonoClient
from crud.account import CRUDAccount
from crud.user import CRUDAuthUser
from schemas.user import RegisterCreate, RegisterPayload


class AuthService:
    def __init__(
        self,
        crud_auth_user: CRUDAuthUser,
        crud_account: CRUDAccount,
        crud_currency: CRUDCurrency,
        crud_user_currency: CRUDUserCurrency,
        mono_client: MonoClient,
        queue_connection: ArqRedis,
    ):
        self.crud_auth_user = crud_auth_user
        self.crud_currency = crud_currency
        self.crud_user_currency = crud_user_currency
        self.crud_account = crud_account
        self.mono_client = mono_client
        self.queue_connection = queue_connection

    async def register(
        self,
        *,
        data_obj: RegisterPayload,
        request: Request,
    ):

        try:
            decoded = firebase_auth.verify_id_token(data_obj.id_token)

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
            )

        user_data = RegisterCreate(
            uid=decoded["uid"],
            email=decoded.get("email"),
            name=data_obj.name,
        )
        if self.crud_auth_user.get_by_email(user_data.email):
            raise ResourceExists(message="Account with email already exists")

        new_user = self.crud_auth_user.create(user_data.model_dump())
        await self.queue_connection.enqueue_job(
            "add_default_currency",
            user_id=new_user.id,
        )
        await self.queue_connection.enqueue_job(
            "add_default_accounts",
            user_id=new_user.id,
        )
        await self.queue_connection.enqueue_job(
            "add_user_default_categories",
            user_id=new_user.id,
        )
        return new_user

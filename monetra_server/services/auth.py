from arq import ArqRedis
from monetra_server.crud.currency import (
    CRUDCurrency,
    CRUDUserCurrency,
)
from monetra_server.crud.user import CRUDAuthUser
from fastapi import HTTPException, status, Request

from firebase_admin import auth as firebase_auth

from monetra_server.core.exceptions import ResourceExists
from monetra_server.core.externals.mono.mono_client import MonoClient
from monetra_server.crud.account import CRUDAccount
from monetra_server.crud.user import CRUDAuthUser
from monetra_server.schemas.user import Payload, RegisterCreate, RegisterPayload
from tarsq import dispatch, status


class AuthService:
    def __init__(
        self,
        crud_auth_user: CRUDAuthUser,
        crud_account: CRUDAccount,
        crud_currency: CRUDCurrency,
        crud_user_currency: CRUDUserCurrency,
        mono_client: MonoClient,
    ):
        self.crud_auth_user = crud_auth_user
        self.crud_currency = crud_currency
        self.crud_user_currency = crud_user_currency
        self.crud_account = crud_account
        self.mono_client = mono_client

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

        obj = Payload(user_id=new_user.id)

        dispatch("initialize_user_data", obj)

        return new_user

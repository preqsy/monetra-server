from fastapi import APIRouter, Depends, status, Request


from api.dependencies.authorization import get_current_user
from api.dependencies.service import get_auth_service
from models.user import User
from schemas.user import RegisterPayload, RegisterResponse
from services import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register", status_code=status.HTTP_201_CREATED, response_model=RegisterResponse
)
async def register(
    data_obj: RegisterPayload,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
):

    return await auth_service.register(data_obj=data_obj, request=request)


@router.get(
    "/me",
    response_model=RegisterResponse,
)
async def get_user(
    user: User = Depends(get_current_user),
):
    return user

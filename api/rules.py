from fastapi import APIRouter, Depends, status

from api.dependencies.authorization import get_current_user
from api.dependencies.service import get_transaction_rule_service
from models.user import User
from schemas.rules import RuleCreate, RuleResponse
from services.rules import TransactionRuleService

router = APIRouter(prefix="/rules", tags=["Rules"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=RuleResponse,
)
async def create_rule(
    rule_data: RuleCreate,
    user: User = Depends(get_current_user),
    service: TransactionRuleService = Depends(get_transaction_rule_service),
):
    return await service.create_rule(data_obj=rule_data, user_id=user.id)


@router.get(
    "/",
    response_model=list[RuleResponse],
)
async def list_rules(
    user: User = Depends(get_current_user),
    service: TransactionRuleService = Depends(get_transaction_rule_service),
):
    return await service.list_rules_by_user_id(user_id=user.id)


@router.delete(
    "/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_rule(
    rule_id: int,
    user: User = Depends(get_current_user),
    service: TransactionRuleService = Depends(get_transaction_rule_service),
):
    await service.delete_rule(rule_id=rule_id, user_id=user.id)

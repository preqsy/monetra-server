from core.exceptions import MissingResource
from crud.category import CRUDUserCategory
from crud.rules import CRUDRules
from schemas.rules import RuleCreate


class TransactionRuleService:
    def __init__(
        self,
        crud_rules: CRUDRules,
        crud_user_category: CRUDUserCategory,
    ):
        self.crud_rules = crud_rules
        self.crud_user_category = crud_user_category

    async def create_rule(self, data_obj: RuleCreate, user_id: int):
        user_category = self.crud_user_category.get_user_category_by_category_id(
            category_id=data_obj.category_id, user_id=user_id
        )
        if not user_category:
            raise MissingResource("User don't have this category")
        data_obj.user_id = user_id
        data_obj.beneficiary_name = data_obj.beneficiary_name.lower()
        return self.crud_rules.create(data_obj)

    async def list_rules_by_user_id(self, user_id: int):
        return self.crud_rules.list_rules_by_user_id(user_id)

    async def delete_rule(self, rule_id: int, user_id: int):
        rule = self.crud_rules.get(rule_id)
        if not rule or rule.user_id != user_id:
            raise MissingResource("Rule not found")
        self.crud_rules.delete(rule)

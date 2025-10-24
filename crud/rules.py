from crud.base import CRUDBase
from models.rules import TransactionRule


class CRUDRules(CRUDBase[TransactionRule]):
    def list_rules_by_user_id(self, user_id: int):
        return (
            self.db.query(TransactionRule)
            .filter(TransactionRule.user_id == user_id)
            .all()
        )

    def list_rules_by_beneficiary_name(self, beneficiary_name: str):
        return (
            self.db.query(TransactionRule)
            .filter(TransactionRule.beneficiary_name == beneficiary_name.lower())
            .all()
        )


def get_crud_rules():
    return CRUDRules(model=TransactionRule)

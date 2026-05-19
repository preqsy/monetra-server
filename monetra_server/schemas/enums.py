from enum import Enum


class MonoReturnStatusEnum(str, Enum):
    FAILED = "failed"
    SUCCESS = "success"


class AccountTypeEnum(str, Enum):
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    DEFAULT_PUBLIC = "default public"
    DEFAULT_PRIVATE = "default private"


class AccountCategoryEnum(str, Enum):
    CREDIT = "credit"
    BALANCE = "balance"


class TransactionTypeEnum(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"
    DEFAULT = "default"


class MonoTransactionTypeEnum(str, Enum):
    DEBIT = "debit"
    CREDIT = "credit"


class CategoryTypeEnum(str, Enum):
    EXPENSE = "expense"
    INCOME = "income"
    GOAL = "goal"
    LIABILITY = "liability"
    ASSET = "asset"


class BudgetPeriodEnum(str, Enum):
    MONTHLY = "monthly"
    WEEKLY = "weekly"
    DAILY = "daily"


class BudgetTypeEnum(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TOTAL = "total"


class PlaidAccountTypeEnum(str, Enum):
    DEPOSITORY = "depository"
    CREDIT = "credit"
    LOAN = "loan"
    INVESTMENT = "investment"
    OTHER = "other"


class AccountProviderEnum(str, Enum):
    MONO = "mono"
    PLAID = "plaid"
    MANUAL = "manual"


class PlannerTypeEnum(str, Enum):
    GOAL = "goal"
    LIABILITY = "liability"
    ASSET = "asset"


class PlannerRoleEnum(str, Enum):
    LENDER = "lender"
    BORROWER = "borrower"


class SubscriptionBillingCycleEnum(str, Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"
    LIFETIME = "lifetime"


class AccountMethodEnum(str, Enum):
    CASH = "cash"
    VISA = "visa"
    MASTERCARD = "mastercard"
    CRYPTO = "crypto"
    BLUE_CARD = "blue card"
    BLACK_CARD = "black card"
    GREEN_CARD = "green card"
    WHITE_CARD = "white card"
    RED_CARD = "red card"
    WALLET = "wallet"
    SAVINGS = "savings"
    GOLD = "gold"
    SAFE = "safe"
    BANK = "bank"
    PIGGY_BANK = "piggy bank"
    INVESTMENT = "investment"
    STARTUP = "startup"
    OTHER = "other"


class ChatRoleEnum(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

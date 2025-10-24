from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from core.config import Settings
from core.llm.agent import FinancialAgent
from core.llm.tools import FinancialTools
from core.llm.conversation import ConversationManager
from crud.transaction import CRUDTransaction
from crud.account import CRUDAccount
from crud.category import CRUDCategory, CRUDUserCategory
from crud.currency import CRUDUserCurrency
from crud.summary import CRUDTotalSummary
from crud.planner import CRUDPlanner
from services.transaction import TransactionService
from services.account import AccountService
from services.summary import AccountSummaryService


class LLMAgentService:
    """Service for managing LLM agent operations"""

    def __init__(
        self,
        db_session: Session,
        settings: Settings,
        crud_transaction: CRUDTransaction,
        crud_account: CRUDAccount,
        crud_category: CRUDCategory,
        crud_user_category: CRUDUserCategory,
        crud_user_currency: CRUDUserCurrency,
        crud_total_summary: CRUDTotalSummary,
        crud_planner: CRUDPlanner,
        transaction_service: TransactionService,
        account_service: AccountService,
        summary_service: AccountSummaryService,
    ):
        self.db_session = db_session
        self.settings = settings
        self.crud_transaction = crud_transaction
        self.crud_account = crud_account
        self.crud_category = crud_category
        self.crud_user_category = crud_user_category
        self.crud_user_currency = crud_user_currency
        self.crud_total_summary = crud_total_summary
        self.crud_planner = crud_planner
        self.transaction_service = transaction_service
        self.account_service = account_service
        self.summary_service = summary_service

        # Initialize conversation manager
        self.conversation_manager = ConversationManager(db_session)

        # Initialize financial tools
        self.financial_tools = FinancialTools(
            crud_transaction=crud_transaction,
            crud_account=crud_account,
            crud_category=crud_category,
            crud_user_category=crud_user_category,
            crud_user_currency=crud_user_currency,
            crud_total_summary=crud_total_summary,
            crud_planner=crud_planner,
            transaction_service=transaction_service,
            account_service=account_service,
            summary_service=summary_service,
        )

        # Initialize financial agent
        self.financial_agent = FinancialAgent(
            openai_api_key=getattr(settings, "OPENAI_API_KEY", ""),
            financial_tools=self.financial_tools,
            conversation_manager=self.conversation_manager,
            model_name=getattr(settings, "OPENAI_MODEL", "gpt-4"),
            temperature=getattr(settings, "OPENAI_TEMPERATURE", 0.1),
        )

    async def process_chat_message(
        self,
        user_id: int,
        message: str,
        session_id: Optional[str] = None,
        conversation_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Process a chat message and return response"""
        return await self.financial_agent.process_message(
            user_id=user_id,
            message=message,
            session_id=session_id,
            conversation_id=conversation_id,
        )

    def get_conversation_history(
        self, conversation_id: int, user_id: int
    ) -> List[Dict[str, Any]]:
        """Get conversation history"""
        return self.financial_agent.get_conversation_history(conversation_id, user_id)

    def get_user_conversations(
        self, user_id: int, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get all conversations for a user"""
        return self.financial_agent.get_user_conversations(user_id, limit)

    def update_conversation_title(
        self, conversation_id: int, user_id: int, title: str
    ) -> bool:
        """Update conversation title"""
        return self.financial_agent.update_conversation_title(
            conversation_id, user_id, title
        )

    def delete_conversation(self, conversation_id: int, user_id: int) -> bool:
        """Delete a conversation"""
        return self.financial_agent.delete_conversation(conversation_id, user_id)

    def create_conversation(
        self, user_id: int, session_id: str, title: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new conversation"""
        conversation = self.conversation_manager.create_conversation(
            user_id=user_id, session_id=session_id, title=title
        )

        return {
            "id": conversation.id,
            "session_id": conversation.session_id,
            "title": conversation.title,
            "created_at": (
                conversation.created_at.isoformat() if conversation.created_at else None
            ),
            "updated_at": (
                conversation.updated_at.isoformat() if conversation.updated_at else None
            ),
        }

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage, AIMessage

from .tools import FinancialTools
from .conversation import ConversationManager


class FinancialAgent:
    """Main financial agent that handles user queries and tool usage"""

    def __init__(
        self,
        openai_api_key: str,
        financial_tools: FinancialTools,
        conversation_manager: ConversationManager,
        model_name: str = "gpt-4",
        temperature: float = 0.1,
    ):
        self.financial_tools = financial_tools
        self.conversation_manager = conversation_manager
        self.model_name = model_name
        self.temperature = temperature

        # Initialize LLM
        self.llm = ChatOpenAI(
            api_key=openai_api_key, model_name=model_name, temperature=temperature
        )

        # Store financial tools for dynamic tool creation
        self.financial_tools = financial_tools

        # Create prompt template
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self._get_system_prompt()),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the financial agent"""
        return """You are a helpful financial assistant AI that helps users understand and analyze their financial data. 

You have access to the following tools:
- get_transactions: Query user transactions with various filters (date range, category, account, type)
- get_accounts: Query user accounts and balances
- get_financial_summary: Get monthly financial summaries (income, expenses, net)
- get_categories: Query transaction categories

Key capabilities:
1. **Transaction Analysis**: Help users understand their spending patterns, income trends, and transaction history
2. **Account Management**: Provide insights about account balances and account types
3. **Financial Summaries**: Generate monthly/yearly financial overviews
4. **Category Insights**: Help users understand their spending by category
5. **Trend Analysis**: Identify patterns in spending and income over time
6. **Budgeting Support**: Help users track expenses against budgets
7. **Financial Planning**: Provide insights for better financial decisions

Guidelines:
- Always be helpful, accurate, and professional
- Use the available tools to get real data before making claims
- Explain financial concepts in simple terms
- Provide actionable insights when possible
- If you need more information, ask clarifying questions
- Be mindful of user privacy and data security
- When showing amounts, always include the currency
- Use proper date formatting (YYYY-MM-DD)
- If a query is unclear, ask for clarification

Remember: You have access to real financial data through the tools. Always use them to provide accurate, data-driven responses."""

    async def process_message(
        self,
        user_id: int,
        message: str,
        session_id: Optional[str] = None,
        conversation_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Process a user message and return a response"""

        # Get or create conversation
        if conversation_id:
            conversation = self.conversation_manager.get_conversation(
                conversation_id, user_id
            )
            if not conversation:
                raise ValueError("Conversation not found or access denied")
        elif session_id:
            conversation = self.conversation_manager.get_conversation_by_session(
                session_id, user_id
            )
            if not conversation:
                conversation = self.conversation_manager.create_conversation(
                    user_id=user_id,
                    session_id=session_id,
                    title=f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                )
        else:
            # Create new conversation with random session ID
            session_id = str(uuid.uuid4())
            conversation = self.conversation_manager.create_conversation(
                user_id=user_id,
                session_id=session_id,
                title=f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            )

        # Add user message to conversation
        self.conversation_manager.add_message(
            conversation_id=conversation.id, role="user", content=message
        )

        # Get conversation context
        chat_history = self.conversation_manager.get_conversation_context(
            conversation_id=conversation.id, max_messages=10
        )

        # Convert to LangChain message format
        messages = []
        for msg in chat_history[:-1]:  # Exclude the last message (current user message)
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))

        # Process with agent
        try:
            # Create tools with user context
            tools = self.financial_tools.get_all_tools()

            # Create agent with user-specific tools
            agent = create_openai_tools_agent(self.llm, tools, self.prompt)
            agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

            # Add user_id to the input for tools to use
            input_data = {
                "input": message,
                "chat_history": messages,
                "user_id": user_id,  # Pass user_id to tools
            }

            response = await agent_executor.ainvoke(input_data)

            # Extract response content
            response_content = response.get(
                "output", "I apologize, but I couldn't process your request."
            )

            # Add assistant message to conversation
            self.conversation_manager.add_message(
                conversation_id=conversation.id,
                role="assistant",
                content=response_content,
            )

            return {
                "conversation_id": conversation.id,
                "session_id": conversation.session_id,
                "response": response_content,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            error_message = f"I apologize, but I encountered an error while processing your request: {str(e)}"

            # Add error message to conversation
            self.conversation_manager.add_message(
                conversation_id=conversation.id, role="assistant", content=error_message
            )

            return {
                "conversation_id": conversation.id,
                "session_id": conversation.session_id,
                "response": error_message,
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
            }

    def get_conversation_history(
        self, conversation_id: int, user_id: int
    ) -> List[Dict[str, Any]]:
        """Get conversation history for a specific conversation"""
        conversation = self.conversation_manager.get_conversation(
            conversation_id, user_id
        )
        if not conversation:
            return []

        messages = self.conversation_manager.get_conversation_messages(conversation_id)

        return [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat(),
            }
            for msg in messages
        ]

    def get_user_conversations(
        self, user_id: int, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get all conversations for a user"""
        conversations = self.conversation_manager.get_user_conversations(user_id, limit)

        return [
            {
                "id": conv.id,
                "session_id": conv.session_id,
                "title": conv.title,
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat() if conv.updated_at else None,
                "message_count": len(conv.messages),
            }
            for conv in conversations
        ]

    def update_conversation_title(
        self, conversation_id: int, user_id: int, title: str
    ) -> bool:
        """Update conversation title"""
        return self.conversation_manager.update_conversation_title(
            conversation_id, title
        )

    def delete_conversation(self, conversation_id: int, user_id: int) -> bool:
        """Delete a conversation"""
        return self.conversation_manager.delete_conversation(conversation_id, user_id)

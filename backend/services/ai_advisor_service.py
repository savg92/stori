"""AI financial advisor service for expense analysis and recommendations."""

import logging
from typing import List, Tuple, Dict, Any, Optional
from langchain_core.language_models.base import BaseLanguageModel
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

from config import get_settings
from core.models import Transaction, AIAdviceRequest, AIAdviceResponse


class AIAdvisorService:
    """Service for AI-powered financial advice and expense analysis."""
    
    def __init__(self):
        self.settings = get_settings()
        self._financial_advice_prompt = self._create_financial_advice_prompt()
    
    def _create_financial_advice_prompt(self) -> PromptTemplate:
        """Create prompt template for financial advice."""
        template = """
You are a helpful financial advisor assistant. Based on the user's expense and income data, provide personalized financial advice.

User's Financial Context:
- Monthly Income: ${monthly_income}
- Monthly Expenses: ${monthly_expenses}
- Expense Categories: {expense_breakdown}
- Recent Transactions: {recent_transactions}

User Question: {question}

Previous Conversation:
{chat_history}

Provide helpful, actionable financial advice. Be specific about spending patterns you notice and suggest practical improvements. 
Keep your response concise but informative.

Financial Advice:
"""
        return PromptTemplate(
            template=template,
            input_variables=[
                "monthly_income", 
                "monthly_expenses", 
                "expense_breakdown", 
                "recent_transactions",
                "question", 
                "chat_history"
            ]
        )
    
    def create_advisor_chain(self, llm: BaseLanguageModel) -> LLMChain:
        """Create an LLM chain for financial advice."""
        return LLMChain(
            llm=llm,
            prompt=self._financial_advice_prompt,
            verbose=True
        )
    
    def get_financial_advice(
        self, 
        llm_chain: LLMChain,
        request: AIAdviceRequest,
        transactions: List[Transaction],
        chat_history: List[Tuple[str, str]] = None
    ) -> AIAdviceResponse:
        """Generate AI-powered financial advice based on user data."""
        
        # Calculate financial metrics
        income_transactions = [t for t in transactions if t.type == "income"]
        expense_transactions = [t for t in transactions if t.type == "expense"]
        
        monthly_income = sum(t.amount for t in income_transactions)
        monthly_expenses = sum(t.amount for t in expense_transactions)
        
        # Group expenses by category
        expense_breakdown = {}
        for transaction in expense_transactions:
            category = transaction.category
            expense_breakdown[category] = expense_breakdown.get(category, 0) + transaction.amount
        
        # Format recent transactions
        recent_transactions = [
            f"{t.type}: ${t.amount} - {t.category} ({t.date})"
            for t in sorted(transactions, key=lambda x: x.date, reverse=True)[:10]
        ]
        
        # Trim chat history to reduce tokens
        max_turns = getattr(self.settings, 'chat_history_max_turns', 5)
        trimmed_history = chat_history[-max_turns:] if chat_history and max_turns > 0 else []
        
        # Format chat history
        formatted_history = "\n".join([
            f"Q: {q}\nA: {a}" for q, a in trimmed_history
        ]) if trimmed_history else "No previous conversation"
        
        # Generate advice
        try:
            result = llm_chain.invoke({
                "monthly_income": monthly_income,
                "monthly_expenses": monthly_expenses, 
                "expense_breakdown": ", ".join([f"{k}: ${v}" for k, v in expense_breakdown.items()]),
                "recent_transactions": "\n".join(recent_transactions),
                "question": request.question,
                "chat_history": formatted_history
            })
            
            advice = result["text"].strip()
            
            return AIAdviceResponse(
                advice=advice,
                session_id=request.session_id,
                context={
                    "monthly_income": monthly_income,
                    "monthly_expenses": monthly_expenses,
                    "savings_rate": ((monthly_income - monthly_expenses) / monthly_income * 100) if monthly_income > 0 else 0,
                    "top_expense_category": max(expense_breakdown.items(), key=lambda x: x[1])[0] if expense_breakdown else None
                }
            )
            
        except Exception as e:
            logging.error(f"Error generating financial advice: {e}")
            return AIAdviceResponse(
                advice="I'm sorry, I'm having trouble generating advice right now. Please try again later.",
                session_id=request.session_id,
                context={}
            )
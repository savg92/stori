"""AI service layer for business logic."""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

from .repository import AIRepository
from .schemas import (
    AdviceInsight,
    AdvicePriority,
    AdviceRequest,
    AdviceType,
    AIAdviceResponse,
    ChatRequest,
    ChatResponse,
    AnalysisRequest,
    AnalysisResult,
)

logger = logging.getLogger(__name__)


class AIService:
    """Service layer for AI operations."""
    
    def __init__(self, repository: AIRepository, llm_provider=None):
        self.repository = repository
        self.llm_provider = llm_provider
        self.logger = logging.getLogger(__name__)
        self._chat_prompt = self._create_chat_prompt()
        
    def _create_chat_prompt(self) -> PromptTemplate:
        """Create a prompt template for AI chat responses."""
        template = """You are a knowledgeable financial advisor with access to the user's actual transaction data. Answer their question with specific details from their financial data.

FINANCIAL DATA:
{financial_context}

USER QUESTION: {question}

INSTRUCTIONS:
1. Always reference specific numbers, dates, and categories from the financial data above
2. Acknowledge the data period and how current/relevant it is (if data is old, mention it)
3. For questions about "lowest expense" or specific analysis, examine ALL categories and provide precise answers
4. Be specific and detailed rather than generic - use actual amounts, percentages, and category names
5. If asking about trends, compare different time periods or categories with real numbers
6. Always provide actionable insights based on the actual data shown

Answer in 2-4 sentences with specific data points:"""
        
        return PromptTemplate(
            template=template,
            input_variables=["financial_context", "question"]
        )
    
    def _create_chat_chain(self):
        """Create LLM chain for chat responses."""
        if not self.llm_provider:
            return None
        return LLMChain(
            llm=self.llm_provider,
            prompt=self._chat_prompt,
            verbose=True
        )
    
    async def get_financial_advice(
        self, 
        user_id: str, 
        request: AdviceRequest
    ) -> AIAdviceResponse:
        """Generate AI-powered financial advice using real data."""
        try:
            # Get financial context from real data
            financial_context = await self.repository.get_financial_context(
                user_id, request.time_period_days
            )
            
            # Generate insights based on real data
            insights = self._generate_insights(financial_context, request)
            
            # Generate fallback advice based on real data
            ai_response = self._generate_fallback_advice(
                financial_context, 
                request, 
                insights
            )
            
            return AIAdviceResponse(
                advice_type=request.advice_type,
                generated_at=datetime.utcnow(),
                insights=insights,
                summary=ai_response['summary'],
                data_analysis=ai_response['data_analysis'],
                recommendations=ai_response['recommendations'],
                confidence_score=ai_response['confidence_score']
            )
            
        except Exception as e:
            logger.error(f"Error generating financial advice: {e}")
            raise
    
    def _generate_insights(
        self, 
        context, 
        request: AdviceRequest
    ) -> List[AdviceInsight]:
        """Generate data-driven insights from real financial data."""
        insights = []
        
        # Basic financial health insights
        if float(context.total_expenses) > float(context.total_income):
            insights.append(AdviceInsight(
                title="Spending Exceeds Income",
                description=f"Your expenses (${context.total_expenses:.2f}) exceed your income (${context.total_income:.2f}).",
                priority=AdvicePriority.HIGH,
                amount_impact=Decimal(str(float(context.total_expenses) - float(context.total_income))),
                confidence_score=0.95,
                actionable_steps=[
                    "Review and reduce non-essential expenses",
                    "Look for additional income opportunities"
                ]
            ))
        
        # Category-specific insights
        if context.top_categories:
            top_category = context.top_categories[0]
            if float(top_category['total_amount']) > float(context.total_expenses) * 0.4:
                insights.append(AdviceInsight(
                    title=f"High Spending in {top_category['category']}",
                    description=f"You're spending ${top_category['total_amount']:.2f} on {top_category['category']}.",
                    priority=AdvicePriority.MEDIUM,
                    category=top_category['category'],
                    amount_impact=Decimal(str(top_category['total_amount'])),
                    confidence_score=0.90,
                    actionable_steps=[
                        f"Set a budget limit for {top_category['category']}",
                        "Track daily expenses in this category"
                    ]
                ))
        
        return insights
    
    def _generate_fallback_advice(
        self, 
        context, 
        request: AdviceRequest, 
        insights: List[AdviceInsight]
    ) -> Dict:
        """Generate advice based on real data analysis."""
        summary = f"Based on your {request.time_period_days}-day financial data, "
        
        if context.net_amount > 0:
            summary += f"you have a positive cash flow of ${context.net_amount:.2f}. "
        else:
            summary += f"you have a negative cash flow of ${abs(context.net_amount):.2f}. "
        
        recommendations = []
        if insights:
            for insight in insights[:3]:
                recommendations.extend(insight.actionable_steps[:2])
        
        data_analysis = {
            'income_expense_ratio': float(context.total_income / context.total_expenses) if context.total_expenses > 0 else 0,
            'top_expense_category': context.top_categories[0]['category'] if context.top_categories else 'N/A',
            'transaction_frequency': context.transaction_count / request.time_period_days,
            'avg_transaction_amount': float(context.total_expenses / context.transaction_count) if context.transaction_count > 0 else 0
        }
        
        return {
            'summary': summary,
            'recommendations': recommendations,
            'data_analysis': data_analysis,
            'confidence_score': 0.85
        }
    
    async def chat_with_ai(self, user_id: str, request: ChatRequest) -> ChatResponse:
        """Chat with AI about financial matters."""
        try:
            # Get financial context if requested
            if request.include_financial_context:
                context = await self.repository.get_financial_context(
                    user_id, request.max_context_days
                )
            else:
                context = None
            
            # Generate response based on context and message
            response = self._generate_chat_response(request.message, context)
            
            return ChatResponse(
                message=response['message'],
                conversation_id=f"chat_{user_id}_{int(datetime.utcnow().timestamp()*1000)}",
                suggested_actions=response.get('suggested_actions', []),
                financial_insights=response.get('financial_insights', []),
                confidence_score=response.get('confidence_score', 0.8)
            )
            
        except Exception as e:
            logger.error(f"Error in chat_with_ai: {e}")
            return ChatResponse(
                message="I'm sorry, I'm having trouble processing your request right now. Please try again later.",
                confidence_score=0.0
            )
    
    async def analyze_financial_data(
        self, 
        user_id: str, 
        request: AnalysisRequest
    ) -> AnalysisResult:
        """Perform AI-powered financial data analysis."""
        try:
            # Get financial context for analysis
            context = await self.repository.get_financial_context(
                user_id, request.context_days
            )
            
            # Perform analysis based on type
            analysis_results = self._perform_analysis(context, request)
            
            return AnalysisResult(
                analysis_type=request.analysis_type,
                results=analysis_results['results'],
                insights=analysis_results['insights'],
                confidence_score=analysis_results.get('confidence_score', 0.85),
                generated_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error in analyze_financial_data: {e}")
            return AnalysisResult(
                analysis_type=request.analysis_type,
                results={'error': 'Analysis failed'},
                insights=['Unable to complete analysis at this time'],
                confidence_score=0.0,
                generated_at=datetime.utcnow()
            )
    
    def _generate_chat_response(self, message: str, context=None) -> Dict:
        """Generate a chat response using the LLM provider or fallback to basic responses."""
        # Try to use LLM provider first
        if self.llm_provider:
            try:
                chat_chain = self._create_chat_chain()
                if chat_chain:
                    # Format financial context for the prompt
                    financial_context = self._format_financial_context(context)
                    
                    # Add a unique timestamp to prevent caching
                    unique_question = f"{message} [timestamp: {datetime.utcnow().isoformat()}]"
                    
                    # Generate response using LLM
                    result = chat_chain.invoke({
                        "financial_context": financial_context,
                        "question": unique_question
                    })
                    
                    ai_response = result["text"].strip()
                    
                    # Extract suggested actions from context if available  
                    suggested_actions = self._extract_suggested_actions(context)
                    financial_insights = self._extract_financial_insights(context)
                    
                    return {
                        'message': ai_response,
                        'suggested_actions': suggested_actions,
                        'financial_insights': financial_insights,
                        'confidence_score': 0.95  # Higher confidence for LLM responses
                    }
            except Exception as e:
                self.logger.warning(f"LLM chat failed, falling back to basic response: {e}")
        
        # Fallback to basic response if LLM fails or unavailable
        return self._generate_fallback_chat_response(message, context)
    def _format_financial_context(self, context) -> str:
        """Format financial context for LLM prompt."""
        if not context:
            return "No financial data available. User should connect their financial accounts for personalized advice."
        
        context_parts = []
        
        # Add current date for temporal awareness
        from datetime import date
        current_date = date.today()
        context_parts.append(f"Current date: {current_date.isoformat()}")
        
        # Add date range with temporal context
        if hasattr(context, 'date_range') and context.date_range:
            if isinstance(context.date_range, dict):
                start_date = context.date_range.get('start_date', '')
                end_date = context.date_range.get('end_date', '')
                
                # Calculate how old the data is
                if end_date:
                    try:
                        end_date_obj = datetime.fromisoformat(end_date).date()
                        days_old = (current_date - end_date_obj).days
                        
                        if days_old > 30:
                            temporal_note = f" (data is {days_old} days old - from {end_date_obj.strftime('%B %Y')})"
                        else:
                            temporal_note = " (recent data)"
                        
                        context_parts.append(f"Data period: {start_date} to {end_date}{temporal_note}")
                    except:
                        context_parts.append(f"Data period: {start_date} to {end_date}")
                else:
                    context_parts.append(f"Data period: {start_date} to {end_date}")
            else:
                context_parts.append(f"Time period: {context.date_range}")
        
        # Add comprehensive financial summary
        if hasattr(context, 'total_income') and hasattr(context, 'total_expenses'):
            net_amount = context.total_income - abs(context.total_expenses)
            savings_rate = (net_amount / context.total_income * 100) if context.total_income > 0 else 0
            
            context_parts.extend([
                f"Total income: ${context.total_income:.2f}",
                f"Total expenses: ${abs(context.total_expenses):.2f}",
                f"Net savings: ${net_amount:.2f}",
                f"Savings rate: {savings_rate:.1f}%"
            ])
        
        # Add transaction summary
        if hasattr(context, 'transaction_count'):
            context_parts.append(f"Number of transactions: {context.transaction_count}")
        
        # Add ALL expense categories with detailed breakdown
        if hasattr(context, 'top_categories') and context.top_categories:
            context_parts.append("\nDETAILED EXPENSE BREAKDOWN:")
            for i, cat in enumerate(context.top_categories, 1):
                avg_amount = cat.get('avg_amount', 0)
                tx_count = cat.get('transaction_count', 0)
                context_parts.append(
                    f"{i}. {cat['category']}: ${abs(cat['total_amount']):.2f} "
                    f"({tx_count} transactions, avg ${avg_amount:.2f} per transaction)"
                )
            
            # Identify lowest expense for specific questions
            if len(context.top_categories) > 1:
                lowest_expense = min(context.top_categories, key=lambda x: x['total_amount'])
                context_parts.append(f"\nLowest expense category: {lowest_expense['category']} at ${abs(lowest_expense['total_amount']):.2f}")
        
        return "\n".join(context_parts) if context_parts else "Limited financial data available."
    
    def _extract_suggested_actions(self, context) -> List[str]:
        """Extract relevant suggested actions based on context."""
        if not context:
            return ["Connect financial data", "Ask general financial advice"]
        
        actions = []
        
        # Add context-specific actions
        if hasattr(context, 'total_income') and hasattr(context, 'total_expenses'):
            net_amount = context.total_income - abs(context.total_expenses)
            savings_rate = (net_amount / context.total_income * 100) if context.total_income > 0 else 0
            
            if savings_rate < 10:
                actions.extend(["Review budget", "Find cost-cutting opportunities"])
            elif savings_rate < 20:
                actions.extend(["Optimize expenses", "Increase savings rate"])
            else:
                actions.extend(["Investment planning", "Long-term financial goals"])
        
        # Add general actions if none specific
        if not actions:
            actions = ["Track expenses", "Set financial goals", "Review spending patterns"]
        
        return actions[:4]  # Limit to 4 actions
    
    def _extract_financial_insights(self, context) -> List[str]:
        """Extract key financial insights from context."""
        if not context:
            return []
        
        insights = []
        
        if hasattr(context, 'total_income') and hasattr(context, 'total_expenses'):
            net_amount = context.total_income - abs(context.total_expenses)
            savings_rate = (net_amount / context.total_income * 100) if context.total_income > 0 else 0
            
            insights.extend([
                f"Savings rate: {savings_rate:.1f}%",
                f"Monthly net: ${net_amount:.2f}",
                f"Expense ratio: {(abs(context.total_expenses) / context.total_income * 100):.1f}%"
            ])
        
        if hasattr(context, 'top_categories') and context.top_categories:
            top_cat = context.top_categories[0]
            insights.append(f"Top category: {top_cat['category']} (${abs(top_cat['total_amount']):.2f})")
        
        return insights[:4]  # Limit to 4 insights
    
    def _generate_fallback_chat_response(self, message: str, context=None) -> Dict:
        """Generate basic chat response when LLM is unavailable."""
        message_lower = message.lower()
        
        response = {
            'message': "",
            'suggested_actions': [],
            'financial_insights': [],
            'confidence_score': 0.6  # Lower confidence for fallback
        }
        
        # Helper function to add date context to responses
        def add_date_context(base_message: str) -> str:
            if context and hasattr(context, 'date_range') and context.date_range:
                return f"{base_message}\n\n*Based on data from {context.date_range}*"
            return base_message
        
        if context and hasattr(context, 'total_income'):
            # Handle spending questions
            if any(word in message_lower for word in ['spend', 'spending', 'expense', 'cost', 'category']):
                base_message = f"Your total expenses are ${abs(context.total_expenses):.2f}. "
                if hasattr(context, 'top_categories') and context.top_categories:
                    top_cat = context.top_categories[0]
                    base_message += f"Your biggest expense category is **{top_cat['category']}** at ${abs(top_cat['total_amount']):.2f}."
                response['message'] = add_date_context(base_message)
                response['suggested_actions'] = ["Review top categories", "Find cost-cutting opportunities", "Set category budgets"]
                response['financial_insights'] = [
                    f"Total expenses: ${abs(context.total_expenses):.2f}",
                    f"Top category: {context.top_categories[0]['category'] if context.top_categories else 'N/A'}"
                ]
            else:
                response['message'] = "I can help you analyze your spending patterns and financial health. What would you like to know?"
                response['suggested_actions'] = self._extract_suggested_actions(context)
                response['financial_insights'] = self._extract_financial_insights(context)
        else:
            response['message'] = "I'd love to help with your financial questions! Connect your financial data so I can provide personalized insights about your spending and savings."
            response['suggested_actions'] = ["Connect financial data", "Ask general financial advice"]
        
        return response
    
    def _perform_analysis(self, context, request: AnalysisRequest) -> Dict:
        """Perform financial analysis based on request type."""
        analysis_type = request.analysis_type
        
        if analysis_type == 'spending_patterns':
            return {
                'results': {
                    'total_spending': float(context.total_expenses),
                    'avg_daily_spending': float(context.total_expenses) / 30,
                    'category_count': len(context.top_categories)
                },
                'insights': [
                    f"Your average daily spending is ${float(context.total_expenses) / 30:.2f}",
                    f"You have transactions across {len(context.top_categories)} categories"
                ],
                'confidence_score': 0.9
            }
        elif analysis_type == 'category_breakdown':
            return {
                'results': {
                    'categories': context.top_categories[:5],
                    'top_category': context.top_categories[0] if context.top_categories else None
                },
                'insights': [
                    f"Your top spending category is {context.top_categories[0]['category'] if context.top_categories else 'unknown'}",
                    f"Total categories analyzed: {len(context.top_categories)}"
                ],
                'confidence_score': 0.85
            }
        else:
            return {
                'results': {'message': f'Analysis type {analysis_type} not yet implemented'},
                'insights': ['This analysis type is under development'],
                'confidence_score': 0.5
            }

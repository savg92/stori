"""AI service layer for business logic."""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional

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
                conversation_id=f"chat_{user_id}_{datetime.utcnow().timestamp()}",
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
        """Generate a chat response based on user message and context."""
        message_lower = message.lower()
        
        response = {
            'message': "",
            'suggested_actions': [],
            'financial_insights': [],
            'confidence_score': 0.8
        }
        
        if context:
            # Handle spending-related questions
            if any(word in message_lower for word in ['spending', 'expense', 'spend', 'category', 'categories', 'biggest']):
                if context.top_categories:
                    top_cats = context.top_categories[:3]
                    
                    if 'biggest' in message_lower or 'top' in message_lower:
                        response['message'] = f"Your biggest spending category is **{top_cats[0]['category']}** at ${abs(top_cats[0]['total_amount']):.2f}."
                        if len(top_cats) > 1:
                            other_cats = ", ".join([f"{cat['category']} (${abs(cat['total_amount']):.2f})" for cat in top_cats[1:]])
                            response['message'] += f" Your other top categories are: {other_cats}."
                    else:
                        categories_text = ", ".join([f"**{cat['category']}**: ${abs(cat['total_amount']):.2f}" for cat in top_cats])
                        response['message'] = f"Here are your top spending categories: {categories_text}. "
                        response['message'] += f"Total expenses: ${abs(context.total_expenses):.2f} across {context.transaction_count} transactions."
                    
                    response['suggested_actions'] = ["Set spending limits", "Track daily expenses", "Compare to last month"]
                    response['financial_insights'] = [
                        f"Top category: {top_cats[0]['category']} (${abs(top_cats[0]['total_amount']):.2f})",
                        f"Total expenses: ${abs(context.total_expenses):.2f}",
                        f"Average per transaction: ${abs(context.total_expenses) / context.transaction_count:.2f}"
                    ]
                else:
                    response['message'] = f"Your total expenses are ${abs(context.total_expenses):.2f} from {context.transaction_count} transactions. I don't have detailed category breakdowns available right now."
                    response['suggested_actions'] = ["Review transaction categories", "Add category labels"]
                    
            # Handle expense reduction questions
            elif any(word in message_lower for word in ['reduce', 'cut', 'lower', 'save money', 'decrease']):
                if context.top_categories:
                    top_cat = context.top_categories[0]
                    response['message'] = f"To reduce expenses, I'd suggest looking at your largest category: **{top_cat['category']}** (${abs(top_cat['total_amount']):.2f}). "
                    
                    if 'rent' in top_cat['category'].lower() or 'housing' in top_cat['category'].lower():
                        response['message'] += "Consider negotiating rent, finding roommates, or exploring different housing options."
                    elif 'food' in top_cat['category'].lower() or 'grocery' in top_cat['category'].lower():
                        response['message'] += "Try meal planning, cooking at home more, or buying generic brands."
                    elif 'transport' in top_cat['category'].lower() or 'gas' in top_cat['category'].lower():
                        response['message'] += "Consider carpooling, public transport, or combining errands into fewer trips."
                    else:
                        response['message'] += "Review if all expenses in this category are necessary and look for alternatives."
                        
                    response['suggested_actions'] = ["Set category budgets", "Track daily spending", "Find alternatives"]
                else:
                    response['message'] = "To reduce your expenses, start by categorizing your transactions to identify patterns. Focus on the largest expense categories first."
                    response['suggested_actions'] = ["Categorize transactions", "Set monthly budgets", "Track daily spending"]
                    
            # Handle income-related questions  
            elif 'income' in message_lower:
                response['message'] = f"Your total income is ${context.total_income:.2f} with expenses of ${abs(context.total_expenses):.2f}, "
                response['message'] += f"leaving you with a net of ${context.net_amount:.2f}."
                response['suggested_actions'] = ["Track income sources", "Plan for income growth", "Optimize tax savings"]
                response['financial_insights'] = [
                    f"Total income: ${context.total_income:.2f}",
                    f"Total expenses: ${abs(context.total_expenses):.2f}",
                    f"Net amount: ${context.net_amount:.2f}"
                ]
                
            # Handle savings/financial health questions
            elif any(word in message_lower for word in ['saving', 'save', 'health', 'summary', 'financial', 'enough']):
                net_amount = context.total_income - abs(context.total_expenses)
                savings_rate = (net_amount / context.total_income * 100) if context.total_income > 0 else 0
                
                if 'enough' in message_lower:
                    if savings_rate >= 20:
                        response['message'] = f"Yes! You're saving {savings_rate:.1f}% of your income (${net_amount:.2f}), which is excellent. The general recommendation is 20% or more."
                    elif savings_rate >= 10:
                        response['message'] = f"You're saving {savings_rate:.1f}% (${net_amount:.2f}), which is good but could be improved. Aim for 20% if possible."
                    else:
                        response['message'] = f"You're currently saving {savings_rate:.1f}% (${net_amount:.2f}). Most experts recommend saving at least 20% of your income."
                else:
                    response['message'] = f"**Financial Health Summary:** You're earning ${context.total_income:.2f} and spending ${abs(context.total_expenses):.2f}. "
                    response['message'] += f"Your savings rate is **{savings_rate:.1f}%** (${net_amount:.2f}). "
                    
                    if savings_rate > 20:
                        response['message'] += "🎉 Excellent savings rate! You're building wealth effectively."
                    elif savings_rate > 10:
                        response['message'] += "👍 Good savings rate with room for improvement."
                    else:
                        response['message'] += "💡 Consider boosting your savings rate for better financial security."
                
                response['suggested_actions'] = ["Set savings goals", "Automate savings", "Review budget monthly"]
                response['financial_insights'] = [
                    f"Savings rate: {savings_rate:.1f}%",
                    f"Monthly savings: ${net_amount:.2f}",
                    f"Expense-to-income ratio: {(abs(context.total_expenses) / context.total_income * 100):.1f}%"
                ]
                
            # Handle trend questions
            elif any(word in message_lower for word in ['trend', 'pattern', 'over time', 'monthly', 'weekly']):
                response['message'] = f"Based on your recent data: ${context.transaction_count} transactions totaling ${abs(context.total_expenses):.2f} in expenses. "
                if context.top_categories:
                    top_cat = context.top_categories[0]
                    response['message'] += f"Your dominant spending pattern is in **{top_cat['category']}** (${abs(top_cat['total_amount']):.2f})."
                response['suggested_actions'] = ["Compare to previous months", "Set monthly goals", "Track weekly spending"]
                
            else:
                response['message'] = "I can help you analyze your spending patterns, savings rate, and financial health. What specific aspect of your finances would you like to explore?"
                response['suggested_actions'] = ["Ask about top categories", "Check savings rate", "Request expense reduction tips"]
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

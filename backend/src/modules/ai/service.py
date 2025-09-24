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
)

logger = logging.getLogger(__name__)


class AIService:
    """Service layer for AI operations."""
    
    def __init__(self, repository: AIRepository):
        self.repository = repository
    
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

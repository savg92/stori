"""AI controller for API endpoints."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from services.supabase_service import SupabaseClient, get_supabase_client
from services.auth_middleware import get_current_user
from services.real_data_service import RealDataService
from providers.llms import LLMProviderFactory
from .repository import AIRepository
from .service import AIService
from .schemas import (
    AdviceRequest,
    AIAdviceResponse,
    AnalysisRequest,
    AnalysisResult,
    ChatRequest,
    ChatResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["ai"])


def get_llm_provider():
    """Dependency to get LLM provider."""
    return LLMProviderFactory.create_llm()


def get_ai_service(
    supabase_client: SupabaseClient = Depends(get_supabase_client),
    llm_provider=Depends(get_llm_provider)
) -> AIService:
    """Dependency to get AI service."""
    repository = AIRepository(supabase_client)
    return AIService(repository, llm_provider)


@router.post("/advice", response_model=AIAdviceResponse)
async def get_financial_advice(
    request: AdviceRequest,
    current_user: dict = Depends(get_current_user),
    service: AIService = Depends(get_ai_service)
):
    """Get AI-powered financial advice based on transaction data."""
    try:
        return await service.get_financial_advice(current_user["user_id"], request)
        
    except Exception as e:
        logger.error(f"Error getting financial advice: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate financial advice")


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    service: AIService = Depends(get_ai_service)
):
    """Chat with AI about financial matters."""
    try:
        return await service.chat_with_ai(current_user["user_id"], request)
        
    except Exception as e:
        logger.error(f"Error in AI chat: {e}")
        raise HTTPException(status_code=500, detail="Failed to process chat request")


@router.post("/analyze", response_model=AnalysisResult)
async def analyze_financial_data(
    request: AnalysisRequest,
    current_user: dict = Depends(get_current_user),
    service: AIService = Depends(get_ai_service)
):
    """Perform AI-powered financial data analysis."""
    try:
        return await service.analyze_financial_data(current_user["user_id"], request)
        
    except Exception as e:
        logger.error(f"Error analyzing financial data: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze financial data")


@router.get("/insights/quick")
async def get_quick_insights(
    days_back: int = 30,
    current_user: dict = Depends(get_current_user),
    service: AIService = Depends(get_ai_service)
):
    """Get quick financial insights for dashboard."""
    try:
        # Get basic financial context
        financial_context = await service.repository.get_financial_context(
            current_user["user_id"], days_back
        )
        
        # Generate quick insights
        insights = []
        
        # Net cash flow insight
        if financial_context.net_amount > 0:
            insights.append({
                'type': 'positive',
                'title': 'Positive Cash Flow',
                'message': f'You saved ${financial_context.net_amount:.2f} over the last {days_back} days',
                'icon': '💰'
            })
        else:
            insights.append({
                'type': 'warning',
                'title': 'Negative Cash Flow',
                'message': f'You overspent by ${abs(financial_context.net_amount):.2f} over the last {days_back} days',
                'icon': '⚠️'
            })
        
        # Top category insight
        if financial_context.top_categories:
            top_cat = financial_context.top_categories[0]
            insights.append({
                'type': 'info',
                'title': 'Top Spending Category',
                'message': f'You spent ${top_cat["total_amount"]:.2f} on {top_cat["category"]}',
                'icon': '📊'
            })
        
        # Transaction frequency insight
        daily_txn_rate = financial_context.transaction_count / days_back
        if daily_txn_rate > 3:
            insights.append({
                'type': 'info',
                'title': 'High Transaction Frequency',
                'message': f'You make {daily_txn_rate:.1f} transactions per day on average',
                'icon': '🔄'
            })
        
        return {
            'insights': insights,
            'period_days': days_back,
            'total_transactions': financial_context.transaction_count,
            'financial_summary': {
                'income': float(financial_context.total_income),
                'expenses': float(financial_context.total_expenses),
                'net': float(financial_context.net_amount)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting quick insights: {e}")
        raise HTTPException(status_code=500, detail="Failed to get quick insights")


@router.get("/health")
async def get_ai_health():
    """Get AI service health and capabilities."""
    try:
        # Check if LLM provider is available
        try:
            llm_provider = LLMProviderFactory.create_llm()
            llm_available = llm_provider is not None
            llm_status = "connected" if llm_available else "not_configured"
        except Exception:
            llm_available = False
            llm_status = "error"
        
        capabilities = [
            "financial_advice",
            "spending_analysis", 
            "anomaly_detection",
            "quick_insights"
        ]
        
        if llm_available:
            capabilities.extend([
                "ai_chat",
                "advanced_analysis",
                "predictions"
            ])
        
        return {
            'status': 'healthy',
            'llm_available': llm_available,
            'llm_status': llm_status,
            'capabilities': capabilities,
            'fallback_mode': not llm_available
        }
        
    except Exception as e:
        logger.error(f"Error checking AI health: {e}")
        return {
            'status': 'error',
            'error': str(e),
            'llm_available': False,
            'capabilities': ['basic_analysis']
        }


# Test endpoints without authentication for development
@router.post("/test/chat")
async def test_chat_with_ai(request: ChatRequest):
    """Test AI chat without authentication."""
    try:
        message = request.message.lower()
        
        if "spending" in message or "expense" in message:
            response = f"""Based on your question about "{request.message}":

Your spending analysis shows excellent financial discipline:
• Monthly expenses: $19,557
• Rent: $12,000 (61% of expenses) 
• Variable expenses: $7,557
• Dining: $1,450 (potential optimization area)

With a 65% savings rate, you're in the top 1% of savers."""

            suggestions = [
                "Consider meal planning to reduce dining costs",
                "Set category-based spending limits",
                "Track daily expenses for better insights"
            ]
            
        elif "income" in message or "save" in message:
            response = f"""Regarding your question: "{request.message}"

Your financial position is exceptional:
• Monthly income: $56,000
• Net savings: $36,443 (65% savings rate)
• Financial health score: 9.2/10

You're well-positioned for wealth building and early financial independence."""

            suggestions = [
                "Maximize retirement contributions",
                "Consider diversified investing",
                "Build 6-month emergency fund"
            ]
            
        else:
            response = f"""Thank you for asking: "{request.message}"

As your AI financial advisor, I see strong financial health:
• High income: $56K monthly
• Controlled spending: $19.5K monthly  
• Exceptional savings: 65% rate

You're on an excellent trajectory toward financial independence."""

            suggestions = [
                "Continue current savings discipline",
                "Explore investment opportunities", 
                "Plan for long-term financial goals"
            ]
        
        return ChatResponse(
            message=response,
            confidence_score=0.87,
            suggested_actions=suggestions,
            financial_insights=[
                f"Analyzed {112} transactions from 2024-01 to 2024-03",
                f"Categories: rent, groceries, dining, utilities, transportation",
                f"User profile: high_earner_excellent_saver"
            ],
            conversation_id=f"test_session_{request.message[:10]}"
        )
        
    except Exception as e:
        logger.error(f"Error in test chat: {e}")
        raise HTTPException(status_code=500, detail="Test chat service unavailable")


@router.get("/test/insights")
async def test_get_insights():
    """Test insights endpoint without authentication."""
    return {
        "insights": [
            "Your 65% savings rate is exceptional - top 1% of all earners",
            "Dining expenses of $1,450/month could be optimized by 15-20%", 
            "You're on track for financial independence in approximately 8 years",
            "Consider maxing out tax-advantaged accounts with your surplus"
        ],
        "financial_score": 9.2,
        "savings_rate": 0.65,
        "monthly_surplus": 36443,
        "generated_at": "2024-03-15T10:30:00Z"
    }


@router.get("/test/database-demo")
async def test_database_integration():
    """Demo the enhanced database integration with realistic user profiles."""
    
    # Simulate different user profiles with realistic financial data
    user_profiles = [
        {
            "profile": "Tech Professional",
            "monthly_income": 85000,
            "monthly_expenses": 42500,
            "savings_rate": 0.50,
            "top_categories": {
                "rent": 21250,      # 25% of income
                "groceries": 6800,  # 8% of income
                "dining": 10200,    # 12% of income
                "transportation": 5100, # 6% of income
                "entertainment": 8500   # 10% of income
            },
            "financial_score": 9.5,
            "insights": [
                "Exceptional savings rate of 50% positions you for early retirement",
                "High income provides significant investment opportunities",
                "Entertainment spending is well-controlled for income level"
            ]
        },
        {
            "profile": "Small Business Owner", 
            "monthly_income": 45000,
            "monthly_expenses": 33750,
            "savings_rate": 0.25,
            "top_categories": {
                "rent": 9000,       # 20% of income
                "groceries": 4500,  # 10% of income
                "business_expenses": 6750, # 15% of income
                "transportation": 3600, # 8% of income
                "dining": 3600      # 8% of income
            },
            "financial_score": 7.8,
            "insights": [
                "Solid 25% savings rate while reinvesting in business",
                "Business expense ratio is healthy for growth phase",
                "Consider separating business and personal expenses more clearly"
            ]
        },
        {
            "profile": "Recent Graduate",
            "monthly_income": 28000,
            "monthly_expenses": 23800,
            "savings_rate": 0.15,
            "top_categories": {
                "rent": 9800,       # 35% of income (typical for entry-level)
                "groceries": 3360,  # 12% of income
                "transportation": 2800, # 10% of income
                "student_loans": 2240,  # 8% of income
                "entertainment": 2240   # 8% of income
            },
            "financial_score": 6.5,
            "insights": [
                "Good start with 15% savings rate despite student loans",
                "High rent percentage is typical for entry-level income",
                "Focus on increasing income as primary wealth-building strategy"
            ]
        }
    ]
    
    # Calculate aggregate insights across all profiles
    total_users = len(user_profiles)
    avg_savings_rate = sum(p["savings_rate"] for p in user_profiles) / total_users
    avg_financial_score = sum(p["financial_score"] for p in user_profiles) / total_users
    
    return {
        "database_status": "enhanced_integration_active",
        "user_profiles": user_profiles,
        "aggregate_insights": {
            "total_profiles": total_users,
            "average_savings_rate": round(avg_savings_rate, 3),
            "average_financial_score": round(avg_financial_score, 2),
            "profile_diversity": "high_income_to_entry_level_coverage"
        },
        "features_demonstrated": [
            "Realistic spending patterns by user type",
            "Income-appropriate expense ratios",
            "Contextual financial advice per profile",
            "Comprehensive financial scoring"
        ],
        "generated_at": "2024-09-24T04:15:00Z"
    }


# Real data endpoints (no authentication for testing)
@router.get("/live/users")
async def get_available_users(supabase: SupabaseClient = Depends(get_supabase_client)):
    """Get list of available users in the database."""
    try:
        data_service = RealDataService(supabase.client)
        users = await data_service.get_available_users()
        return {
            "users": users,
            "count": len(users),
            "message": "Available users for testing live data"
        }
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch users")


@router.get("/live/summary/{user_id}")
async def get_live_financial_summary(
    user_id: str,
    days: int = 30,
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """Get live financial summary for a specific user."""
    try:
        data_service = RealDataService(supabase.client)
        summary = await data_service.get_financial_summary(user_id, days)
        
        if summary['transaction_count'] == 0:
            return {
                "message": f"No transactions found for user {user_id} in the last {days} days",
                "user_id": user_id,
                "summary": summary
            }
        
        return {
            "message": f"Live financial summary for {user_id}",
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"Error getting live summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get financial summary")


@router.post("/live/chat/{user_id}")
async def live_chat_with_ai(
    user_id: str,
    request: ChatRequest,
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """AI chat using real user data."""
    try:
        data_service = RealDataService(supabase.client)
        
        # Get user's real financial data
        summary = await data_service.get_financial_summary(user_id, 90)
        trends = await data_service.get_spending_trends(user_id, 90)
        
        if summary['transaction_count'] == 0:
            return ChatResponse(
                message=f"I don't have any transaction data for user {user_id} yet. Please add some transactions to get personalized advice!",
                confidence_score=1.0,
                suggested_actions=["Add some transactions", "Check back once you have financial data"],
                financial_insights=["No financial data available"],
                conversation_id=f"live_{user_id}_{request.message[:10]}"
            )
        
        message_lower = request.message.lower()
        
        # Generate contextual response based on real data
        if "spending" in message_lower or "expense" in message_lower:
            top_category = summary['top_expense_categories'][0] if summary['top_expense_categories'] else None
            
            response = f"""Based on your actual financial data for "{request.message}":

Your real spending analysis:
• Total expenses: ${summary['total_expenses']:,.2f} (last {summary['period_days']} days)
• Number of transactions: {summary['transaction_count']}
• Savings rate: {summary['savings_rate']:.1%}"""

            if top_category:
                response += f"""
• Top spending category: {top_category['category'].title()} (${top_category['amount']:,.2f} - {top_category['percentage']:.1f}%)"""
            
            if summary['financial_health_score'] >= 7:
                response += f"\n\nYour financial health score is {summary['financial_health_score']:.1f}/10 - excellent!"
            elif summary['financial_health_score'] >= 5:
                response += f"\n\nYour financial health score is {summary['financial_health_score']:.1f}/10 - good with room for improvement."
            else:
                response += f"\n\nYour financial health score is {summary['financial_health_score']:.1f}/10 - needs attention."

            suggestions = [
                f"Review your {top_category['category']} spending" if top_category else "Track your spending patterns",
                "Set up category budgets based on your actual spending",
                "Consider optimizing your largest expense categories"
            ]
            
        elif "income" in message_lower or "save" in message_lower:
            response = f"""Regarding your question about "{request.message}":

Your actual financial position:
• Total income: ${summary['total_income']:,.2f}
• Net savings: ${summary['net_savings']:,.2f}
• Savings rate: {summary['savings_rate']:.1%}
• Financial health: {summary['financial_health_score']:.1f}/10"""

            if summary['savings_rate'] > 0.2:
                response += "\n\nExcellent savings rate! You're doing great."
            elif summary['savings_rate'] > 0.1:
                response += "\n\nGood savings rate with room to improve."
            else:
                response += "\n\nFocus on increasing your savings rate."

            suggestions = [
                "Continue building your emergency fund" if summary['savings_rate'] > 0.1 else "Start with a small emergency fund",
                "Consider automating your savings",
                "Look for ways to optimize your largest expenses"
            ]
            
        elif "trend" in message_lower or "pattern" in message_lower:
            avg_weekly = trends.get('avg_weekly_spending', 0)
            trend_insights = trends.get('insights', [])
            
            response = f"""Your spending trends based on real data:

Weekly spending analysis:
• Average weekly spending: ${avg_weekly:,.2f}
• Total tracked weeks: {len(trends.get('trends', []))}"""

            if trend_insights:
                response += f"\n• Recent insights: {', '.join(trend_insights)}"
            
            suggestions = [
                "Monitor weekly spending patterns",
                "Set weekly spending targets",
                "Track unusual spending spikes"
            ]
            
        else:
            response = f"""Based on your real financial data for "{request.message}":

Financial overview:
• Monthly income: ${summary['total_income']:,.2f}
• Monthly expenses: ${summary['total_expenses']:,.2f}
• Savings rate: {summary['savings_rate']:.1%}
• Health score: {summary['financial_health_score']:.1f}/10

You have {summary['transaction_count']} transactions in our records."""

            suggestions = [
                "Review your spending categories",
                "Set financial goals based on your data",
                "Track your progress month-to-month"
            ]
        
        return ChatResponse(
            message=response,
            confidence_score=0.95,  # High confidence since using real data
            suggested_actions=suggestions,
            financial_insights=[
                f"Analyzed {summary['transaction_count']} real transactions",
                f"Data period: {summary['period_days']} days",
                f"Financial health score: {summary['financial_health_score']:.1f}/10",
                f"Savings rate: {summary['savings_rate']:.1%}"
            ],
            conversation_id=f"live_{user_id}_{request.message[:10]}"
        )
        
    except Exception as e:
        logger.error(f"Error in live AI chat: {e}")
        raise HTTPException(status_code=500, detail="Live AI chat service unavailable")


@router.get("/live/trends/{user_id}")
async def get_live_spending_trends(
    user_id: str,
    days: int = 90,
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """Get live spending trends for a user."""
    try:
        data_service = RealDataService(supabase.client)
        trends = await data_service.get_spending_trends(user_id, days)
        
        return {
            "user_id": user_id,
            "period_days": days,
            "trends": trends,
            "message": f"Live spending trends for {user_id}"
        }
        
    except Exception as e:
        logger.error(f"Error getting live trends: {e}")
        raise HTTPException(status_code=500, detail="Failed to get spending trends")
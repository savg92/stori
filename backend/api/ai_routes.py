"""Simplified AI routes that work without external dependencies."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai", tags=["ai"])


class ChatRequest(BaseModel):
    """Request model for AI chat."""
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for AI chat."""
    response: str
    confidence: float
    context_used: Dict[str, Any]
    suggestions: List[str]
    session_id: str


class AdviceRequest(BaseModel):
    """Request model for financial advice."""
    context: Optional[str] = None
    advice_type: Optional[str] = "general"


class AdviceResponse(BaseModel):
    """Response model for financial advice."""
    advice: str
    insights: List[Dict[str, Any]]
    recommendations: List[str]
    confidence: float


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """Enhanced AI chat with financial context."""
    try:
        # Analyze the user's message for intent
        message = request.message.lower()
        
        # Generate contextual response based on message content
        if "spending" in message or "expense" in message:
            response = f"""Based on your recent financial activity, I can see you're asking about "{request.message}". 

Looking at your data:
• Your largest expense category is rent at $12,000/month
• Groceries account for $2,198/month 
• Dining expenses are $1,450/month

For spending analysis, I'd recommend focusing on controllable categories like dining and shopping where you have more flexibility to optimize."""

            suggestions = [
                "Review your dining expenses for potential savings",
                "Set up category-based budgets",
                "Track daily spending patterns"
            ]
            
        elif "income" in message or "earning" in message:
            response = f"""Regarding your question about "{request.message}":

Your current financial profile shows:
• Monthly income: $56,000
• Total expenses: $19,557  
• Net positive: $75,557

You're in a strong financial position with substantial savings potential."""

            suggestions = [
                "Consider increasing your investment contributions",
                "Explore additional income streams",
                "Review your savings goals"
            ]
            
        elif "budget" in message or "save" in message:
            response = f"""For your question about "{request.message}":

Budget optimization opportunities:
• You save $36,443 monthly (65% savings rate)
• Biggest savings potential in dining/entertainment
• Consider automating your savings

Your high savings rate indicates excellent financial discipline."""

            suggestions = [
                "Set up automatic transfers to savings",
                "Create an emergency fund target", 
                "Explore investment options for excess savings"
            ]
            
        elif "goal" in message or "plan" in message:
            response = f"""Regarding your financial planning question: "{request.message}"

Based on your profile (Young Professional with high income):
• Emergency fund: You could build 6 months expenses ($117K) in 3 months
• Investment potential: $36K+ monthly surplus for investments
• Retirement: On track to retire early with current savings rate

Your financial foundation is extremely strong."""

            suggestions = [
                "Define specific financial milestones",
                "Consider diversified investment strategy",
                "Plan for major life goals (house, family, etc.)"
            ]
            
        else:
            # General financial advice
            response = f"""Thank you for asking: "{request.message}"

As your AI financial advisor, I've analyzed your spending patterns and can provide personalized insights:

Your financial health score: 9/10
• Strong income: $56,000/month
• Controlled spending: $19,557/month  
• Excellent savings rate: 65%

You're in the top tier of financial health with significant opportunities for wealth building."""

            suggestions = [
                "Explore investment diversification",
                "Consider tax optimization strategies", 
                "Review insurance and protection needs"
            ]
        
        return ChatResponse(
            response=response,
            confidence=0.85,
            context_used={
                "transaction_count": 112,
                "date_range": "2024-01 to 2024-03",
                "categories_analyzed": ["rent", "groceries", "dining", "utilities", "transportation"],
                "income_data": True,
                "spending_patterns": True
            },
            suggestions=suggestions,
            session_id=request.session_id or f"session_{datetime.now().timestamp()}"
        )
        
    except Exception as e:
        logger.error(f"Error in AI chat: {e}")
        raise HTTPException(status_code=500, detail="AI service temporarily unavailable")


@router.post("/advice", response_model=AdviceResponse)
async def get_financial_advice(request: AdviceRequest):
    """Get personalized financial advice."""
    try:
        advice_type = request.advice_type or "general"
        
        if advice_type == "spending":
            advice = """Based on your spending analysis, you have excellent financial discipline with a 65% savings rate. 

Key insights:
• Housing (rent): $12,000 - 61% of expenses (high but stable)
• Variable expenses: $7,557 - good optimization potential
• Dining: $1,450 - consider meal planning to reduce

You're already doing very well, with room for minor optimizations in discretionary spending."""
            
            insights = [
                {
                    "category": "Housing", 
                    "amount": 12000,
                    "percentage": 61.3,
                    "status": "high_but_stable"
                },
                {
                    "category": "Dining",
                    "amount": 1450, 
                    "percentage": 7.4,
                    "status": "optimization_opportunity"
                }
            ]
            
            recommendations = [
                "Track daily dining expenses for 2 weeks",
                "Set a monthly dining budget of $1,200",
                "Try meal prep one day per week"
            ]
            
        elif advice_type == "savings":
            advice = """Your savings performance is exceptional at 65% of income ($36,443/month).

This puts you in the top 1% of savers. Focus on:
• Investment diversification
• Tax-advantaged accounts maximization  
• Long-term wealth building strategies

Consider working with a financial advisor for advanced wealth management."""
            
            insights = [
                {
                    "metric": "savings_rate",
                    "value": 0.65,
                    "percentile": 99,
                    "status": "exceptional"
                },
                {
                    "metric": "monthly_surplus", 
                    "value": 36443,
                    "growth_potential": "high",
                    "status": "ready_for_investment"
                }
            ]
            
            recommendations = [
                "Max out 401k and IRA contributions",
                "Explore index fund investing",
                "Consider real estate investment",
                "Build 6-month emergency fund first"
            ]
            
        else:
            advice = """Overall financial health assessment: EXCELLENT

You demonstrate outstanding financial management:
• Income: $56,000/month (high earner)
• Expenses: $19,557/month (well controlled)
• Savings rate: 65% (exceptional)
• Net worth growth: $36,443/month

You're on track for financial independence and early retirement if desired."""
            
            insights = [
                {
                    "score": "financial_health",
                    "value": 9.2,
                    "max": 10.0,
                    "status": "excellent"
                },
                {
                    "projection": "years_to_fi",
                    "value": 8.5,
                    "assumption": "current_rate",
                    "status": "on_track"
                }
            ]
            
            recommendations = [
                "Continue current financial discipline", 
                "Diversify income sources",
                "Plan for tax optimization",
                "Consider advanced investment strategies"
            ]
        
        return AdviceResponse(
            advice=advice,
            insights=insights,
            recommendations=recommendations,
            confidence=0.88
        )
        
    except Exception as e:
        logger.error(f"Error generating advice: {e}")
        raise HTTPException(status_code=500, detail="Advice service temporarily unavailable")


@router.get("/health")
async def ai_health_check():
    """Check AI service health."""
    return {
        "status": "healthy",
        "providers": ["mock_ai"],
        "capabilities": ["chat", "advice", "analysis"],
        "version": "1.0.0"
    }


@router.get("/insights")
async def get_quick_insights():
    """Get quick financial insights."""
    return {
        "insights": [
            "Your savings rate of 65% is in the top 1% of earners",
            "Dining expenses could be optimized by 15% with meal planning",
            "You're on track to achieve financial independence in ~8 years",
            "Consider maxing out tax-advantaged accounts with your surplus"
        ],
        "generated_at": datetime.now().isoformat()
    }
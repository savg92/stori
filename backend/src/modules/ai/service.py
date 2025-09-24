"""AI service layer for business logic."""

import logging
import json
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional

from providers.llms import LLMProviderFactory
from langchain_core.language_models.llms import BaseLanguageModel
from .repository import AIRepository
from services.mock_data_service import MockDataService
from .schemas import (
    AdviceInsight,
    AdvicePriority,
    AdviceRequest,
    AdviceType,
    AIAdviceResponse,
    AnalysisRequest,
    AnalysisResult,
    ChatRequest,
    ChatResponse
)

logger = logging.getLogger(__name__)


class AIService:
    """Service layer for AI operations."""
    
    def __init__(self, repository: AIRepository, llm_provider: Optional[BaseLanguageModel] = None):
        self.repository = repository
        self.llm_provider = llm_provider
        self.mock_service = MockDataService()
    
    async def get_financial_advice(
        self, 
        user_id: str, 
        request: AdviceRequest
    ) -> AIAdviceResponse:
        """Generate AI-powered financial advice."""
        try:
            # Check if this is a mock user
            if self.mock_service.is_mock_user(user_id):
                return self._get_mock_financial_advice(user_id, request)
            
            # Get financial context
            financial_context = await self.repository.get_financial_context(
                user_id, request.time_period_days
            )
            
            # Get additional analysis based on advice type
            additional_data = {}
            if request.advice_type == AdviceType.SPENDING_INSIGHTS:
                additional_data = await self.repository.get_spending_patterns(user_id)
            elif request.advice_type == AdviceType.TREND_ANALYSIS:
                additional_data['anomalies'] = await self.repository.get_anomalies(user_id)
            
            # Generate insights based on data
            insights = await self._generate_insights(
                financial_context, 
                request, 
                additional_data
            )
            
            # Generate AI response if LLM is available
            if self.llm_provider:
                ai_response = await self._generate_ai_advice(
                    financial_context, 
                    request, 
                    insights,
                    additional_data
                )
            else:
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
    
    async def chat_with_ai(
        self, 
        user_id: str, 
        request: ChatRequest
    ) -> ChatResponse:
        """Chat with AI about financial matters."""
        try:
            # Check if this is a mock user
            if self.mock_service.is_mock_user(user_id):
                return self._get_mock_chat_response(user_id, request)
            
            # Get financial context if requested
            financial_context = None
            if request.include_financial_context:
                financial_context = await self.repository.get_financial_context(
                    user_id, request.max_context_days
                )
            
            if self.llm_provider:
                response = await self._generate_chat_response(
                    request, 
                    financial_context
                )
            else:
                response = self._generate_fallback_chat_response(
                    request, 
                    financial_context
                )
            
            return ChatResponse(
                message=response['message'],
                conversation_id=response.get('conversation_id'),
                suggested_actions=response.get('suggested_actions'),
                financial_insights=response.get('financial_insights'),
                confidence_score=response['confidence_score']
            )
            
        except Exception as e:
            logger.error(f"Error in AI chat: {e}")
            raise
    
    async def analyze_financial_data(
        self, 
        user_id: str, 
        request: AnalysisRequest
    ) -> AnalysisResult:
        """Perform financial data analysis."""
        try:
            # Check if this is a mock user
            if self.mock_service.is_mock_user(user_id):
                return self._get_mock_financial_analysis(user_id, request)
            
            results = {}
            insights = []
            
            if request.analysis_type == 'spending_patterns':
                results = await self.repository.get_spending_patterns(
                    user_id, request.context_days
                )
                insights = self._analyze_spending_patterns(results)
            
            elif request.analysis_type == 'anomaly_detection':
                anomalies = await self.repository.get_anomalies(
                    user_id, request.context_days
                )
                results['anomalies'] = anomalies
                insights = self._analyze_anomalies(anomalies)
            
            elif request.analysis_type == 'category_breakdown':
                financial_context = await self.repository.get_financial_context(
                    user_id, request.context_days
                )
                results = {
                    'categories': financial_context.top_categories,
                    'total_expenses': float(financial_context.total_expenses)
                }
                insights = self._analyze_category_breakdown(financial_context.top_categories)
            
            # Generate predictions if requested
            if request.include_predictions and self.llm_provider:
                predictions = await self._generate_predictions(user_id, request.analysis_type)
                results['predictions'] = predictions
            
            return AnalysisResult(
                analysis_type=request.analysis_type,
                results=results,
                insights=insights,
                confidence_score=0.85,  # Default confidence
                generated_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error analyzing financial data: {e}")
            raise
    
    async def _generate_insights(
        self, 
        context, 
        request: AdviceRequest, 
        additional_data: Dict
    ) -> List[AdviceInsight]:
        """Generate data-driven insights."""
        insights = []
        
        # Basic financial health insights
        if context.total_expenses > context.total_income:
            insights.append(AdviceInsight(
                title="Spending Exceeds Income",
                description=f"Your expenses (${context.total_expenses:.2f}) exceed your income (${context.total_income:.2f}) by ${context.total_expenses - context.total_income:.2f}.",
                priority=AdvicePriority.HIGH,
                amount_impact=context.total_expenses - context.total_income,
                confidence_score=0.95,
                actionable_steps=[
                    "Review and reduce non-essential expenses",
                    "Look for additional income opportunities",
                    "Create a strict monthly budget"
                ]
            ))
        
        # Category-specific insights
        if context.top_categories:
            top_category = context.top_categories[0]
            if top_category['total_amount'] > context.total_expenses * 0.4:
                insights.append(AdviceInsight(
                    title=f"High Spending in {top_category['category']}",
                    description=f"You're spending ${top_category['total_amount']:.2f} on {top_category['category']}, which is {(top_category['total_amount']/context.total_expenses*100):.1f}% of your total expenses.",
                    priority=AdvicePriority.MEDIUM,
                    category=top_category['category'],
                    amount_impact=Decimal(str(top_category['total_amount'])),
                    confidence_score=0.90,
                    actionable_steps=[
                        f"Set a budget limit for {top_category['category']}",
                        "Track daily expenses in this category",
                        "Look for cheaper alternatives"
                    ]
                ))
        
        # Trend insights
        if context.recent_trends and len(context.recent_trends) >= 2:
            latest_trend = context.recent_trends[-1]
            if 'change_percent' in latest_trend and latest_trend['change_percent'] > 20:
                insights.append(AdviceInsight(
                    title="Increasing Spending Trend",
                    description=f"Your spending increased by {latest_trend['change_percent']:.1f}% this week compared to last week.",
                    priority=AdvicePriority.MEDIUM,
                    confidence_score=0.80,
                    actionable_steps=[
                        "Identify what caused the spending increase",
                        "Set weekly spending alerts",
                        "Review recent transactions for unnecessary purchases"
                    ]
                ))
        
        return insights
    
    async def _generate_ai_advice(
        self, 
        context, 
        request: AdviceRequest, 
        insights: List[AdviceInsight],
        additional_data: Dict
    ) -> Dict:
        """Generate AI-powered advice using LLM."""
        try:
            # Prepare context for LLM
            llm_context = {
                'financial_summary': {
                    'income': float(context.total_income),
                    'expenses': float(context.total_expenses),
                    'net': float(context.net_amount),
                    'top_categories': context.top_categories[:3]
                },
                'insights': [
                    {
                        'title': insight.title,
                        'description': insight.description,
                        'priority': insight.priority.value
                    } for insight in insights
                ],
                'advice_type': request.advice_type.value,
                'user_context': request.context
            }
            
            prompt = self._build_advice_prompt(llm_context)
            
            # Generate response using LLM
            llm_response = await self.llm_provider.generate_response(
                prompt=prompt,
                max_tokens=500,
                temperature=0.7
            )
            
            # Parse LLM response
            return self._parse_llm_advice_response(llm_response)
            
        except Exception as e:
            logger.error(f"Error generating AI advice: {e}")
            return self._generate_fallback_advice(context, request, insights)
    
    def _generate_fallback_advice(
        self, 
        context, 
        request: AdviceRequest, 
        insights: List[AdviceInsight]
    ) -> Dict:
        """Generate fallback advice when LLM is not available."""
        summary = f"Based on your {request.time_period_days}-day financial data, "
        
        if context.net_amount > 0:
            summary += f"you have a positive cash flow of ${context.net_amount:.2f}. "
        else:
            summary += f"you have a negative cash flow of ${abs(context.net_amount):.2f}. "
        
        recommendations = []
        if insights:
            for insight in insights[:3]:  # Top 3 insights
                recommendations.extend(insight.actionable_steps[:2])  # Top 2 steps each
        
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
            'confidence_score': 0.75
        }
    
    def _build_advice_prompt(self, context: Dict) -> str:
        """Build prompt for LLM advice generation."""
        return f"""
        You are a financial advisor AI. Analyze the following financial data and provide personalized advice.
        
        Financial Summary:
        - Income: ${context['financial_summary']['income']:.2f}
        - Expenses: ${context['financial_summary']['expenses']:.2f}
        - Net: ${context['financial_summary']['net']:.2f}
        
        Top Expense Categories:
        {json.dumps(context['financial_summary']['top_categories'], indent=2)}
        
        Key Insights:
        {json.dumps(context['insights'], indent=2)}
        
        Advice Type: {context['advice_type']}
        User Context: {context.get('user_context', 'None provided')}
        
        Please provide:
        1. A concise summary (2-3 sentences)
        2. 3-5 specific, actionable recommendations
        3. Key financial metrics analysis
        
        Format your response as JSON with keys: summary, recommendations, data_analysis
        """
    
    def _parse_llm_advice_response(self, response: str) -> Dict:
        """Parse LLM response into structured format."""
        try:
            # Try to parse as JSON first
            parsed = json.loads(response)
            return {
                'summary': parsed.get('summary', ''),
                'recommendations': parsed.get('recommendations', []),
                'data_analysis': parsed.get('data_analysis', {}),
                'confidence_score': 0.85
            }
        except json.JSONDecodeError:
            # If not JSON, try to extract information
            lines = response.strip().split('\n')
            return {
                'summary': lines[0] if lines else 'AI analysis completed',
                'recommendations': lines[1:4] if len(lines) > 1 else ['Review your spending patterns'],
                'data_analysis': {'ai_response': response},
                'confidence_score': 0.70
            }
    
    async def _generate_chat_response(
        self, 
        request: ChatRequest, 
        financial_context
    ) -> Dict:
        """Generate AI chat response."""
        # Implementation would use LLM for conversational AI
        return {
            'message': f"I understand you're asking about: {request.message}. Let me help you with that based on your financial data.",
            'confidence_score': 0.80,
            'suggested_actions': ["Review recent transactions", "Check spending categories"],
            'financial_insights': ["Your spending is within normal ranges"]
        }
    
    def _generate_fallback_chat_response(
        self, 
        request: ChatRequest, 
        financial_context
    ) -> Dict:
        """Generate fallback chat response."""
        return {
            'message': f"I received your message: '{request.message}'. Here's some general financial guidance based on your recent activity.",
            'confidence_score': 0.60,
            'suggested_actions': ["Review your budget", "Track your expenses"],
            'financial_insights': ["Consider setting spending limits for major categories"]
        }
    
    def _analyze_spending_patterns(self, patterns: Dict) -> List[str]:
        """Analyze spending patterns and generate insights."""
        insights = []
        
        if patterns.get('daily_averages'):
            # Find highest spending day
            highest_day = max(
                patterns['daily_averages'].items(),
                key=lambda x: x[1].get('average', 0)
            )
            insights.append(f"You tend to spend most on {highest_day[0]}s (${highest_day[1]['average']:.2f} average)")
        
        if patterns.get('amount_distribution'):
            dist = patterns['amount_distribution']
            total_txns = sum(dist.values())
            if total_txns > 0:
                large_pct = (dist['large'] / total_txns) * 100
                if large_pct > 20:
                    insights.append(f"{large_pct:.1f}% of your transactions are large amounts (>$100)")
        
        return insights
    
    def _analyze_anomalies(self, anomalies: List[Dict]) -> List[str]:
        """Analyze anomalies and generate insights."""
        insights = []
        
        if anomalies:
            insights.append(f"Found {len(anomalies)} unusual spending patterns")
            
            # Group by category
            categories = {}
            for anomaly in anomalies:
                cat = anomaly['category']
                if cat not in categories:
                    categories[cat] = 0
                categories[cat] += 1
            
            if categories:
                top_anomaly_cat = max(categories.items(), key=lambda x: x[1])
                insights.append(f"Most anomalies in {top_anomaly_cat[0]} category")
        
        return insights
    
    def _analyze_category_breakdown(self, categories: List[Dict]) -> List[str]:
        """Analyze category breakdown and generate insights."""
        insights = []
        
        if categories:
            top_cat = categories[0]
            insights.append(f"Top spending category: {top_cat['category']} (${top_cat['total_amount']:.2f})")
            
            if len(categories) >= 2:
                total_top_two = categories[0]['total_amount'] + categories[1]['total_amount']
                insights.append(f"Top 2 categories account for ${total_top_two:.2f} in spending")
        
        return insights
    
    async def _generate_predictions(self, user_id: str, analysis_type: str) -> Dict:
        """Generate predictions based on historical data."""
        # Implementation for predictions
        return {
            'next_month_spending': 0,
            'category_trends': [],
            'confidence': 0.7
        }
    
    def _get_mock_financial_advice(self, user_id: str, request: AdviceRequest) -> AIAdviceResponse:
        """Generate financial advice for mock users."""
        # Get mock user profile and transactions
        mock_user = self.mock_service.get_mock_user(user_id)
        transactions = self.mock_service.get_mock_transactions(user_id)
        
        # Calculate basic metrics from mock data
        recent_transactions = [tx for tx in transactions[-30:]]  # Last 30 transactions
        total_income = sum(tx.amount for tx in recent_transactions if tx.type == "income")
        total_expenses = sum(abs(tx.amount) for tx in recent_transactions if tx.type == "expense")
        net_amount = total_income - total_expenses
        
        # Generate insights based on mock user profile
        insights = []
        
        if mock_user.profile_type == "young_professional":
            insights.append(AdviceInsight(
                title="Career-Focused Financial Growth",
                description="As a young professional, focus on building an emergency fund and investing in your career development.",
                priority=AdvicePriority.MEDIUM,
                confidence_score=0.90,
                actionable_steps=[
                    "Save 3-6 months of expenses for emergencies",
                    "Invest in professional development courses",
                    "Start contributing to retirement accounts early"
                ]
            ))
        elif mock_user.profile_type == "family_household":
            insights.append(AdviceInsight(
                title="Family Budget Optimization",
                description="Managing household expenses efficiently while planning for your children's future.",
                priority=AdvicePriority.HIGH,
                confidence_score=0.95,
                actionable_steps=[
                    "Set up education savings accounts for children",
                    "Review family insurance coverage",
                    "Create separate budgets for family activities"
                ]
            ))
        elif mock_user.profile_type == "freelancer":
            insights.append(AdviceInsight(
                title="Irregular Income Management", 
                description="Build financial stability despite variable freelance income.",
                priority=AdvicePriority.HIGH,
                confidence_score=0.88,
                actionable_steps=[
                    "Create a buffer fund for lean months",
                    "Track business expenses for tax deductions",
                    "Set aside money for quarterly taxes"
                ]
            ))
        elif mock_user.profile_type == "retiree":
            insights.append(AdviceInsight(
                title="Fixed Income Optimization",
                description="Make the most of your retirement savings and Social Security benefits.",
                priority=AdvicePriority.MEDIUM,
                confidence_score=0.85,
                actionable_steps=[
                    "Review withdrawal rates from retirement accounts",
                    "Consider healthcare cost planning",
                    "Look into senior discounts for regular expenses"
                ]
            ))
        else:  # student
            insights.append(AdviceInsight(
                title="Student Budget Management",
                description="Learn essential budgeting skills while managing educational expenses.",
                priority=AdvicePriority.MEDIUM,
                confidence_score=0.80,
                actionable_steps=[
                    "Track all educational expenses for tax benefits",
                    "Look for student discounts on regular purchases",
                    "Start building credit responsibly"
                ]
            ))
        
        # Add spending-specific insights
        if total_expenses > total_income:
            insights.append(AdviceInsight(
                title="Spending Alert",
                description=f"Your recent expenses (${total_expenses:.2f}) exceed income (${total_income:.2f}).",
                priority=AdvicePriority.HIGH,
                amount_impact=total_expenses - total_income,
                confidence_score=0.95,
                actionable_steps=[
                    "Review recent transactions for unnecessary spending",
                    "Set up spending alerts on your accounts",
                    "Create a strict weekly budget"
                ]
            ))
        
        # Generate personalized recommendations
        recommendations = []
        for insight in insights:
            recommendations.extend(insight.actionable_steps[:2])
        
        # Generate summary based on profile
        if net_amount > 0:
            summary = f"Great job maintaining a positive cash flow of ${net_amount:.2f}! As a {mock_user.profile_type.replace('_', ' ')}, consider focusing on your specific financial goals."
        else:
            summary = f"Your recent spending shows a deficit of ${abs(net_amount):.2f}. Let's work on strategies specific to your situation as a {mock_user.profile_type.replace('_', ' ')}."
        
        return AIAdviceResponse(
            advice_type=request.advice_type,
            generated_at=datetime.utcnow(),
            insights=insights,
            summary=summary,
            data_analysis={
                "total_income": float(total_income),
                "total_expenses": float(total_expenses),
                "net_amount": float(net_amount),
                "profile_type": mock_user.profile_type,
                "transaction_count": len(recent_transactions)
            },
            recommendations=recommendations,
            confidence_score=0.85
        )
    
    def _get_mock_chat_response(self, user_id: str, request: ChatRequest) -> ChatResponse:
        """Generate chat response for mock users."""
        mock_user = self.mock_service.get_mock_user(user_id)
        
        # Simple keyword-based responses for demo
        message = request.message.lower()
        
        if "budget" in message:
            response_msg = f"As a {mock_user.profile_type.replace('_', ' ')}, I recommend creating a monthly budget that accounts for your specific needs. Would you like me to suggest budget categories based on your spending patterns?"
        elif "save" in message or "savings" in message:
            response_msg = f"Savings strategies for {mock_user.profile_type.replace('_', ' ')} should focus on your unique situation. Based on your profile, I suggest starting with an emergency fund."
        elif "invest" in message:
            response_msg = f"Investment advice varies by life stage. For someone with your {mock_user.profile_type.replace('_', ' ')} profile, let me suggest some appropriate investment options."
        else:
            response_msg = f"I understand you're asking about: '{request.message}'. Based on your profile as a {mock_user.profile_type.replace('_', ' ')}, here's some tailored guidance."
        
        return ChatResponse(
            message=response_msg,
            conversation_id=f"mock_conversation_{user_id}",
            suggested_actions=[
                "Review your recent transactions",
                f"Set up a {mock_user.profile_type.replace('_', ' ')} budget",
                "Check spending by category"
            ],
            financial_insights=[
                f"Your spending aligns with typical {mock_user.profile_type.replace('_', ' ')} patterns",
                "Consider setting monthly savings goals"
            ],
            confidence_score=0.75
        )
    
    def _get_mock_financial_analysis(self, user_id: str, request: AnalysisRequest) -> AnalysisResult:
        """Generate financial analysis for mock users."""
        mock_user = self.mock_service.get_mock_user(user_id)
        transactions = self.mock_service.get_mock_transactions(user_id)
        
        # Filter transactions based on analysis timeframe
        recent_transactions = transactions[-request.context_days:] if request.context_days else transactions
        
        results = {}
        insights = []
        
        if request.analysis_type == 'spending_patterns':
            # Analyze spending by day of week
            day_spending = {}
            for tx in recent_transactions:
                if tx.type == "expense":
                    day = tx.transaction_date.strftime("%A")
                    if day not in day_spending:
                        day_spending[day] = []
                    day_spending[day].append(abs(tx.amount))
            
            day_averages = {
                day: sum(amounts) / len(amounts) if amounts else 0
                for day, amounts in day_spending.items()
            }
            
            results = {
                'daily_averages': day_averages,
                'total_analyzed_transactions': len(recent_transactions),
                'profile_type': mock_user.profile_type
            }
            
            # Generate insights
            if day_averages:
                highest_day = max(day_averages.items(), key=lambda x: x[1])
                insights.append(f"You spend most on {highest_day[0]}s (${highest_day[1]:.2f} average)")
                insights.append(f"Analysis based on {len(recent_transactions)} recent transactions")
        
        elif request.analysis_type == 'anomaly_detection':
            # Simple anomaly detection for demo
            expense_amounts = [abs(tx.amount) for tx in recent_transactions if tx.type == "expense"]
            if expense_amounts:
                avg_expense = sum(expense_amounts) / len(expense_amounts)
                large_transactions = [tx for tx in recent_transactions 
                                   if tx.type == "expense" and abs(tx.amount) > avg_expense * 2]
                
                results = {
                    'anomalies': [
                        {
                            'date': tx.transaction_date.isoformat(),
                            'amount': float(abs(tx.amount)),
                            'category': tx.category,
                            'description': tx.description
                        } for tx in large_transactions
                    ],
                    'threshold': avg_expense * 2,
                    'average_expense': avg_expense
                }
                
                insights.append(f"Found {len(large_transactions)} transactions significantly above average")
                if large_transactions:
                    insights.append(f"Largest unusual expense: ${max(abs(tx.amount) for tx in large_transactions):.2f}")
        
        elif request.analysis_type == 'category_breakdown':
            # Category analysis
            category_totals = {}
            for tx in recent_transactions:
                if tx.type == "expense":
                    if tx.category not in category_totals:
                        category_totals[tx.category] = 0
                    category_totals[tx.category] += abs(tx.amount)
            
            total_expenses = sum(category_totals.values())
            categories = [
                {
                    'category': cat,
                    'total_amount': amount,
                    'percentage': (amount / total_expenses * 100) if total_expenses > 0 else 0
                } 
                for cat, amount in sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
            ]
            
            results = {
                'categories': categories,
                'total_expenses': total_expenses,
                'category_count': len(categories)
            }
            
            if categories:
                insights.append(f"Top spending category: {categories[0]['category']} (${categories[0]['total_amount']:.2f})")
                insights.append(f"Spending across {len(categories)} different categories")
        
        return AnalysisResult(
            analysis_type=request.analysis_type,
            results=results,
            insights=insights,
            confidence_score=0.80,
            generated_at=datetime.utcnow()
        )
        # Placeholder for prediction logic
        return {
            'next_month_estimate': 'Based on trends, estimated spending next month: $800-1200',
            'confidence': 0.70
        }
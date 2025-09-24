"""Standalone AI test server."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Stori AI Test Server",
    description="Testing AI functionality",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    confidence: float
    context_used: Dict[str, Any]
    suggestions: List[str]
    session_id: str


@app.get("/")
async def root():
    return {
        "message": "Stori AI Test Server",
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "ai": "available",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/ai/chat")
async def chat_with_ai(request: ChatRequest):
    """AI chat endpoint with financial context."""
    try:
        message = request.message.lower()
        
        if "spending" in message or "expense" in message:
            response = f"""Based on your question about "{request.message}":

Your spending analysis shows:
• Monthly expenses: $19,557
• Largest category: Rent ($12,000)
• Variable expenses: $7,557
• Dining: $1,450 (optimization opportunity)

You maintain excellent financial discipline with a 65% savings rate."""

            suggestions = [
                "Track daily expenses for better insights",
                "Set category-based spending limits",
                "Review recurring subscriptions"
            ]
            
        elif "income" in message or "budget" in message:
            response = f"""Regarding your question: "{request.message}"

Your financial position:
• Monthly income: $56,000
• Net savings: $36,443 (65% savings rate)
• Financial health score: 9/10

You're in an excellent financial position with strong savings potential."""

            suggestions = [
                "Consider investment opportunities",
                "Build emergency fund",
                "Plan for long-term goals"
            ]
        else:
            response = f"""Thank you for asking: "{request.message}"

As your AI financial advisor, here's what I see:
• Strong income stream: $56K/month
• Controlled spending: $19.5K/month
• Exceptional savings rate: 65%

You're on track for financial independence."""

            suggestions = [
                "Maximize investment contributions",
                "Diversify income sources", 
                "Plan tax optimization"
            ]
        
        return ChatResponse(
            response=response,
            confidence=0.87,
            context_used={
                "transactions": 112,
                "date_range": "2024-01 to 2024-03",
                "categories": ["rent", "groceries", "dining", "utilities"],
                "analysis_type": "comprehensive"
            },
            suggestions=suggestions,
            session_id=request.session_id or f"session_{datetime.now().timestamp()}"
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="AI service unavailable")


@app.get("/api/ai/insights")
async def get_insights():
    """Quick financial insights."""
    return {
        "insights": [
            "Your 65% savings rate is exceptional - top 1% of earners",
            "Dining expenses ($1,450) could be optimized by 15%",
            "On track for financial independence in ~8 years",
            "Consider maxing out retirement contributions"
        ],
        "score": 9.2,
        "generated_at": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting AI Test Server on port 8001...")
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)
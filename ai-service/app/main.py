"""
FastAPI AI service for helpdesk platform.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import openai
import os
from transformers import pipeline
import redis
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Helpdesk AI Service",
    description="AI-powered features for helpdesk platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI models
sentiment_analyzer = pipeline("sentiment-analysis")
categorization_model = pipeline("zero-shot-classification")

# Initialize Redis
redis_client = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, db=1)

# OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")


# Pydantic models
class TicketData(BaseModel):
    subject: str
    description: str
    customer_id: Optional[str] = None
    organization_id: str


class CategorizationRequest(BaseModel):
    subject: str
    description: str
    categories: List[str] = [
        "Technical Support",
        "Billing",
        "General Inquiry",
        "Bug Report",
        "Feature Request",
        "Account Issue"
    ]


class SentimentRequest(BaseModel):
    text: str


class ResponseSuggestionRequest(BaseModel):
    ticket_content: str
    kb_context: List[str] = []
    customer_history: List[str] = []


class ChatbotRequest(BaseModel):
    message: str
    conversation_history: List[Dict[str, str]] = []
    context: Dict[str, Any] = {}


# Health check endpoint
@app.get("/health/")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "ai-service"}


# Ticket categorization
@app.post("/categorize")
async def categorize_ticket(request: CategorizationRequest):
    """Categorize ticket using AI."""
    try:
        # Combine subject and description
        text = f"{request.subject}\n{request.description}"
        
        # Use zero-shot classification
        result = categorization_model(text, request.categories)
        
        return {
            "category": result["labels"][0],
            "confidence": result["scores"][0],
            "all_scores": dict(zip(result["labels"], result["scores"]))
        }
    except Exception as e:
        logger.error(f"Categorization error: {str(e)}")
        raise HTTPException(status_code=500, detail="Categorization failed")


# Sentiment analysis
@app.post("/sentiment")
async def analyze_sentiment(request: SentimentRequest):
    """Analyze sentiment of text."""
    try:
        result = sentiment_analyzer(request.text[:512])  # Limit text length
        return {
            "sentiment": result[0]["label"],
            "score": result[0]["score"],
            "confidence": abs(result[0]["score"])
        }
    except Exception as e:
        logger.error(f"Sentiment analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail="Sentiment analysis failed")


# Response suggestions
@app.post("/suggest-response")
async def suggest_response(request: ResponseSuggestionRequest):
    """Suggest response using AI and knowledge base."""
    try:
        # Prepare context
        kb_context = "\n".join(request.kb_context)
        customer_history = "\n".join(request.customer_history)
        
        # Create prompt for OpenAI
        prompt = f"""
        You are a helpful customer support agent. Use the following information to suggest a response:
        
        Knowledge Base Context:
        {kb_context}
        
        Customer History:
        {customer_history}
        
        Current Ticket:
        {request.ticket_content}
        
        Please provide a helpful, professional response that addresses the customer's concern.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful customer support agent."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        return {
            "suggested_response": response.choices[0].message.content,
            "confidence": 0.8  # Placeholder confidence score
        }
    except Exception as e:
        logger.error(f"Response suggestion error: {str(e)}")
        raise HTTPException(status_code=500, detail="Response suggestion failed")


# Chatbot endpoint
@app.post("/chatbot")
async def chatbot(request: ChatbotRequest):
    """AI chatbot for customer support."""
    try:
        # Prepare conversation context
        messages = [
            {"role": "system", "content": "You are a helpful customer support chatbot. Be friendly and professional."}
        ]
        
        # Add conversation history
        for msg in request.conversation_history:
            messages.append(msg)
        
        # Add current message
        messages.append({"role": "user", "content": request.message})
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=300,
            temperature=0.7
        )
        
        return {
            "response": response.choices[0].message.content,
            "intent": "general_inquiry",  # Placeholder
            "confidence": 0.8
        }
    except Exception as e:
        logger.error(f"Chatbot error: {str(e)}")
        raise HTTPException(status_code=500, detail="Chatbot failed")


# Auto-assignment based on content
@app.post("/auto-assign")
async def auto_assign_ticket(ticket_data: TicketData):
    """Auto-assign ticket based on content analysis."""
    try:
        # Analyze ticket content
        text = f"{ticket_data.subject}\n{ticket_data.description}"
        
        # Get sentiment
        sentiment_result = sentiment_analyzer(text[:512])
        sentiment = sentiment_result[0]["label"]
        
        # Get category
        categories = ["Technical", "Billing", "General", "Bug", "Feature"]
        category_result = categorization_model(text, categories)
        category = category_result["labels"][0]
        
        # Determine priority based on sentiment and content
        priority = "medium"
        if sentiment == "NEGATIVE" or "urgent" in text.lower():
            priority = "high"
        elif "bug" in text.lower() or "error" in text.lower():
            priority = "high"
        
        # Cache results in Redis
        cache_key = f"ticket_analysis:{ticket_data.organization_id}:{ticket_data.customer_id}"
        analysis_data = {
            "sentiment": sentiment,
            "category": category,
            "priority": priority,
            "confidence": category_result["scores"][0]
        }
        redis_client.setex(cache_key, 3600, json.dumps(analysis_data))  # Cache for 1 hour
        
        return analysis_data
    except Exception as e:
        logger.error(f"Auto-assignment error: {str(e)}")
        raise HTTPException(status_code=500, detail="Auto-assignment failed")


# Knowledge base search
@app.post("/search-kb")
async def search_knowledge_base(query: str, organization_id: str):
    """Search knowledge base using AI."""
    try:
        # This would integrate with the main Django app's KB
        # For now, return a placeholder response
        return {
            "results": [
                {
                    "title": "How to reset password",
                    "content": "To reset your password, click on 'Forgot Password'...",
                    "relevance_score": 0.95
                }
            ],
            "query": query
        }
    except Exception as e:
        logger.error(f"KB search error: {str(e)}")
        raise HTTPException(status_code=500, detail="Knowledge base search failed")


# Analytics endpoint
@app.get("/analytics/{organization_id}")
async def get_ai_analytics(organization_id: str):
    """Get AI analytics for organization."""
    try:
        # Get cached analytics from Redis
        cache_key = f"ai_analytics:{organization_id}"
        cached_data = redis_client.get(cache_key)
        
        if cached_data:
            return json.loads(cached_data)
        
        # Generate analytics (placeholder)
        analytics = {
            "total_tickets_analyzed": 1000,
            "average_sentiment": 0.7,
            "top_categories": ["Technical", "Billing", "General"],
            "response_suggestions_used": 85,
            "chatbot_interactions": 200
        }
        
        # Cache for 1 hour
        redis_client.setex(cache_key, 3600, json.dumps(analytics))
        
        return analytics
    except Exception as e:
        logger.error(f"Analytics error: {str(e)}")
        raise HTTPException(status_code=500, detail="Analytics failed")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
"""
Enhanced Customer Experience services for advanced capabilities.
"""

import logging
import asyncio
import aiohttp
import json
from typing import Dict, List, Any, Optional
from django.conf import settings
from django.utils import timezone
from django.db.models import Q, Count, Avg, Sum
from .enhanced_models import (
    CustomerIntelligence,
    HyperPersonalizationEngine,
    CustomerSuccessManagement,
    AdvancedFeedbackSystem,
    CustomerAdvocacyPlatform,
    CustomerInsight,
    PersonalizationRule,
    CustomerSegment,
    CustomerTouchpoint,
)
from apps.accounts.models import User

logger = logging.getLogger(__name__)


class EnhancedCustomerIntelligenceService:
    """Advanced customer intelligence service with 360° view and behavioral analytics."""

    def __init__(self, organization):
        self.organization = organization
        self.openai_api_key = getattr(settings, "OPENAI_API_KEY", None)

    async def analyze_customer_360(self, customer_id: str) -> Dict[str, Any]:
        """Generate 360° customer view."""
        try:
            customer = User.objects.get(id=customer_id, organization=self.organization)

            # Gather data from multiple sources
            customer_data = await self._gather_customer_data(customer)

            # Analyze behavioral patterns
            behavioral_analysis = await self._analyze_behavioral_patterns(customer)

            # Generate insights
            insights = await self._generate_customer_insights(
                customer_data, behavioral_analysis
            )

            # Create customer insight record
            CustomerInsight.objects.create(
                organization=self.organization,
                customer=customer,
                insight_type="behavioral",
                insight_data=insights,
                confidence_score=insights.get("confidence", 0.0),
                source_systems=["tickets", "interactions", "feedback", "usage"],
            )

            return {
                "customer_360": customer_data,
                "behavioral_analysis": behavioral_analysis,
                "insights": insights,
                "generated_at": timezone.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Customer 360 analysis error: {e}")
            return {"error": str(e)}

    async def predict_purchase_intent(self, customer_id: str) -> Dict[str, Any]:
        """Predict customer purchase intent."""
        try:
            customer = User.objects.get(id=customer_id, organization=self.organization)

            # Analyze customer behavior
            behavior_data = await self._analyze_customer_behavior(customer)

            # Predict intent using ML models
            intent_prediction = await self._predict_intent(behavior_data)

            return {
                "customer_id": customer_id,
                "purchase_intent": intent_prediction.get("intent", "low"),
                "confidence": intent_prediction.get("confidence", 0.0),
                "recommended_actions": intent_prediction.get("actions", []),
                "predicted_value": intent_prediction.get("value", 0.0),
                "timeframe": intent_prediction.get("timeframe", "unknown"),
            }

        except Exception as e:
            logger.error(f"Purchase intent prediction error: {e}")
            return {"error": str(e)}

    async def calculate_customer_lifetime_value(
        self, customer_id: str
    ) -> Dict[str, Any]:
        """Calculate customer lifetime value."""
        try:
            customer = User.objects.get(id=customer_id, organization=self.organization)

            # Gather historical data
            historical_data = await self._gather_historical_data(customer)

            # Calculate CLV using multiple methods
            clv_calculations = await self._calculate_clv(historical_data)

            return {
                "customer_id": customer_id,
                "current_clv": clv_calculations.get("current", 0.0),
                "predicted_clv": clv_calculations.get("predicted", 0.0),
                "confidence": clv_calculations.get("confidence", 0.0),
                "factors": clv_calculations.get("factors", []),
                "recommendations": clv_calculations.get("recommendations", []),
            }

        except Exception as e:
            logger.error(f"CLV calculation error: {e}")
            return {"error": str(e)}

    async def _gather_customer_data(self, customer: User) -> Dict[str, Any]:
        """Gather comprehensive customer data."""
        # This would integrate with multiple systems
        return {
            "profile": {
                "id": str(customer.id),
                "email": customer.email,
                "full_name": customer.full_name,
                "role": customer.role,
                "created_at": customer.date_joined.isoformat(),
                "last_active": (
                    customer.last_active_at.isoformat()
                    if customer.last_active_at
                    else None
                ),
            },
            "interactions": {
                "total_tickets": 0,  # Would be calculated from actual data
                "total_interactions": 0,
                "last_interaction": None,
            },
            "behavior": {
                "engagement_score": 0.0,
                "satisfaction_score": 0.0,
                "risk_score": 0.0,
            },
        }

    async def _analyze_behavioral_patterns(self, customer: User) -> Dict[str, Any]:
        """Analyze customer behavioral patterns."""
        # This would use ML models to analyze behavior
        return {
            "engagement_pattern": "high",
            "preferred_channels": ["email", "chat"],
            "interaction_frequency": "daily",
            "satisfaction_trend": "increasing",
            "risk_indicators": [],
        }

    async def _generate_customer_insights(
        self, customer_data: Dict, behavioral_analysis: Dict
    ) -> Dict[str, Any]:
        """Generate customer insights."""
        return {
            "key_insights": [
                "High-value customer with increasing engagement",
                "Prefers self-service channels",
                "Shows signs of potential expansion",
            ],
            "recommendations": [
                "Offer premium support options",
                "Provide self-service resources",
                "Engage for upselling opportunities",
            ],
            "confidence": 0.85,
        }

    async def _analyze_customer_behavior(self, customer: User) -> Dict[str, Any]:
        """Analyze customer behavior for intent prediction."""
        return {
            "recent_activity": "high",
            "engagement_level": "active",
            "support_interactions": 5,
            "feature_usage": "extensive",
        }

    async def _predict_intent(self, behavior_data: Dict) -> Dict[str, Any]:
        """Predict purchase intent using ML models."""
        # This would use actual ML models
        return {
            "intent": "high",
            "confidence": 0.8,
            "actions": ["offer_demo", "schedule_call", "send_proposal"],
            "value": 50000.0,
            "timeframe": "30_days",
        }

    async def _gather_historical_data(self, customer: User) -> Dict[str, Any]:
        """Gather historical customer data."""
        return {
            "total_revenue": 100000.0,
            "transaction_count": 25,
            "average_transaction": 4000.0,
            "retention_rate": 0.95,
        }

    async def _calculate_clv(self, historical_data: Dict) -> Dict[str, Any]:
        """Calculate customer lifetime value."""
        return {
            "current": historical_data.get("total_revenue", 0.0),
            "predicted": historical_data.get("total_revenue", 0.0) * 1.2,
            "confidence": 0.8,
            "factors": ["revenue_history", "retention_rate", "growth_trend"],
            "recommendations": ["increase_engagement", "offer_premium_features"],
        }


class EnhancedPersonalizationService:
    """Hyper-personalization service with dynamic content and AI-driven recommendations."""

    def __init__(self, organization):
        self.organization = organization
        self.openai_api_key = getattr(settings, "OPENAI_API_KEY", None)

    async def personalize_content(
        self, customer_id: str, content_type: str, base_content: str
    ) -> Dict[str, Any]:
        """Personalize content for a specific customer."""
        try:
            customer = User.objects.get(id=customer_id, organization=self.organization)

            # Get customer profile and preferences
            customer_profile = await self._get_customer_profile(customer)

            # Get personalization rules
            personalization_rules = await self._get_personalization_rules(customer)

            # Apply personalization
            personalized_content = await self._apply_personalization(
                base_content, customer_profile, personalization_rules
            )

            return {
                "customer_id": customer_id,
                "content_type": content_type,
                "original_content": base_content,
                "personalized_content": personalized_content,
                "personalization_applied": personalization_rules,
                "confidence": 0.9,
            }

        except Exception as e:
            logger.error(f"Content personalization error: {e}")
            return {"error": str(e)}

    async def generate_recommendations(
        self, customer_id: str, recommendation_type: str
    ) -> Dict[str, Any]:
        """Generate AI-driven recommendations for a customer."""
        try:
            customer = User.objects.get(id=customer_id, organization=self.organization)

            # Analyze customer behavior and preferences
            behavior_analysis = await self._analyze_customer_behavior(customer)

            # Get recommendation models
            recommendation_models = await self._get_recommendation_models(
                recommendation_type
            )

            # Generate recommendations
            recommendations = await self._generate_ai_recommendations(
                behavior_analysis, recommendation_models
            )

            return {
                "customer_id": customer_id,
                "recommendation_type": recommendation_type,
                "recommendations": recommendations,
                "confidence": 0.85,
                "generated_at": timezone.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Recommendation generation error: {e}")
            return {"error": str(e)}

    async def _get_customer_profile(self, customer: User) -> Dict[str, Any]:
        """Get customer profile for personalization."""
        return {
            "demographics": {
                "age_group": "25-34",
                "location": "US",
                "industry": "Technology",
            },
            "preferences": {
                "communication_style": "formal",
                "content_type": "technical",
                "channel_preference": "email",
            },
            "behavior": {
                "engagement_level": "high",
                "feature_usage": "advanced",
                "support_frequency": "low",
            },
        }

    async def _get_personalization_rules(self, customer: User) -> List[Dict[str, Any]]:
        """Get personalization rules for customer."""
        rules = PersonalizationRule.objects.filter(
            organization=self.organization, is_active=True
        ).order_by("-priority")

        return [
            {
                "rule_id": str(rule.id),
                "rule_type": rule.rule_type,
                "conditions": rule.conditions,
                "actions": rule.actions,
                "priority": rule.priority,
            }
            for rule in rules
        ]

    async def _apply_personalization(
        self, content: str, profile: Dict, rules: List[Dict]
    ) -> str:
        """Apply personalization rules to content."""
        personalized_content = content

        # Apply personalization based on rules
        for rule in rules:
            if self._evaluate_rule_conditions(rule["conditions"], profile):
                personalized_content = self._apply_rule_actions(
                    personalized_content, rule["actions"], profile
                )

        return personalized_content

    def _evaluate_rule_conditions(self, conditions: List[Dict], profile: Dict) -> bool:
        """Evaluate if rule conditions are met."""
        # Simple condition evaluation
        for condition in conditions:
            field = condition.get("field")
            operator = condition.get("operator")
            value = condition.get("value")

            if field in profile:
                profile_value = profile[field]
                if not self._compare_values(profile_value, operator, value):
                    return False

        return True

    def _apply_rule_actions(
        self, content: str, actions: List[Dict], profile: Dict
    ) -> str:
        """Apply rule actions to content."""
        for action in actions:
            action_type = action.get("type")
            if action_type == "replace_text":
                content = content.replace(
                    action.get("old_text", ""), action.get("new_text", "")
                )
            elif action_type == "add_personalization":
                personalization = action.get("personalization", "")
                content = f"{content}\n\n{personalization}"

        return content

    def _compare_values(
        self, actual_value: Any, operator: str, expected_value: Any
    ) -> bool:
        """Compare values based on operator."""
        if operator == "equals":
            return actual_value == expected_value
        elif operator == "contains":
            return expected_value in str(actual_value)
        elif operator == "greater_than":
            return actual_value > expected_value
        elif operator == "less_than":
            return actual_value < expected_value
        return False

    async def _analyze_customer_behavior(self, customer: User) -> Dict[str, Any]:
        """Analyze customer behavior for recommendations."""
        return {
            "interaction_history": [],
            "preferences": {},
            "engagement_patterns": {},
            "feature_usage": {},
        }

    async def _get_recommendation_models(
        self, recommendation_type: str
    ) -> List[Dict[str, Any]]:
        """Get recommendation models for type."""
        return [
            {
                "model_name": "collaborative_filtering",
                "model_type": "recommendation",
                "confidence": 0.8,
            },
            {
                "model_name": "content_based",
                "model_type": "recommendation",
                "confidence": 0.7,
            },
        ]

    async def _generate_ai_recommendations(
        self, behavior: Dict, models: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Generate AI-driven recommendations."""
        return [
            {
                "item_id": "feature_1",
                "item_type": "feature",
                "title": "Advanced Analytics",
                "description": "Get deeper insights with advanced analytics",
                "confidence": 0.9,
                "reason": "Based on your usage patterns",
            },
            {
                "item_id": "service_1",
                "item_type": "service",
                "title": "Premium Support",
                "description": "Get priority support with faster response times",
                "confidence": 0.8,
                "reason": "Based on your support history",
            },
        ]


class EnhancedCustomerSuccessService:
    """Customer success management service with onboarding automation and expansion detection."""

    def __init__(self, organization):
        self.organization = organization

    async def automate_onboarding(self, customer_id: str) -> Dict[str, Any]:
        """Automate customer onboarding process."""
        try:
            customer = User.objects.get(id=customer_id, organization=self.organization)

            # Get onboarding configuration
            onboarding_config = await self._get_onboarding_config(customer)

            # Execute onboarding steps
            onboarding_result = await self._execute_onboarding_steps(
                customer, onboarding_config
            )

            return {
                "customer_id": customer_id,
                "onboarding_status": "in_progress",
                "steps_completed": onboarding_result.get("completed_steps", 0),
                "total_steps": onboarding_result.get("total_steps", 0),
                "next_steps": onboarding_result.get("next_steps", []),
                "estimated_completion": onboarding_result.get("estimated_completion"),
            }

        except Exception as e:
            logger.error(f"Onboarding automation error: {e}")
            return {"error": str(e)}

    async def detect_expansion_opportunities(self, customer_id: str) -> Dict[str, Any]:
        """Detect expansion opportunities for a customer."""
        try:
            customer = User.objects.get(id=customer_id, organization=self.organization)

            # Analyze customer usage and behavior
            usage_analysis = await self._analyze_customer_usage(customer)

            # Identify expansion opportunities
            opportunities = await self._identify_expansion_opportunities(usage_analysis)

            return {
                "customer_id": customer_id,
                "expansion_opportunities": opportunities,
                "confidence": 0.8,
                "recommended_actions": [
                    "Schedule expansion call",
                    "Send product demo",
                    "Provide usage report",
                ],
            }

        except Exception as e:
            logger.error(f"Expansion detection error: {e}")
            return {"error": str(e)}

    async def _get_onboarding_config(self, customer: User) -> Dict[str, Any]:
        """Get onboarding configuration for customer."""
        return {
            "steps": [
                {
                    "step_id": "welcome_email",
                    "step_name": "Send Welcome Email",
                    "automated": True,
                    "delay": 0,
                },
                {
                    "step_id": "product_tour",
                    "step_name": "Product Tour",
                    "automated": True,
                    "delay": 1,
                },
                {
                    "step_id": "setup_call",
                    "step_name": "Setup Call",
                    "automated": False,
                    "delay": 3,
                },
            ],
            "success_criteria": [
                "First login completed",
                "Key features used",
                "Support ticket created",
            ],
        }

    async def _execute_onboarding_steps(
        self, customer: User, config: Dict
    ) -> Dict[str, Any]:
        """Execute onboarding steps."""
        completed_steps = 0
        next_steps = []

        for step in config["steps"]:
            if step["automated"]:
                # Execute automated step
                await self._execute_automated_step(customer, step)
                completed_steps += 1
            else:
                next_steps.append(step)

        return {
            "completed_steps": completed_steps,
            "total_steps": len(config["steps"]),
            "next_steps": next_steps,
            "estimated_completion": "7 days",
        }

    async def _execute_automated_step(self, customer: User, step: Dict) -> None:
        """Execute an automated onboarding step."""
        # This would trigger actual automation
        logger.info(
            f"Executing onboarding step: {step['step_name']} for customer {customer.email}"
        )

    async def _analyze_customer_usage(self, customer: User) -> Dict[str, Any]:
        """Analyze customer usage patterns."""
        return {
            "feature_usage": {
                "basic_features": 0.9,
                "advanced_features": 0.3,
                "premium_features": 0.1,
            },
            "engagement_metrics": {
                "login_frequency": "daily",
                "session_duration": "high",
                "feature_adoption": "moderate",
            },
            "growth_indicators": {
                "usage_increase": 0.2,
                "feature_expansion": 0.1,
                "team_growth": 0.0,
            },
        }

    async def _identify_expansion_opportunities(
        self, usage_analysis: Dict
    ) -> List[Dict[str, Any]]:
        """Identify expansion opportunities."""
        opportunities = []

        if usage_analysis["feature_usage"]["premium_features"] < 0.5:
            opportunities.append(
                {
                    "type": "feature_upgrade",
                    "title": "Premium Features",
                    "description": "Customer could benefit from premium features",
                    "confidence": 0.8,
                    "potential_value": 5000.0,
                }
            )

        if usage_analysis["growth_indicators"]["team_growth"] > 0:
            opportunities.append(
                {
                    "type": "seat_expansion",
                    "title": "Additional Seats",
                    "description": "Customer team is growing",
                    "confidence": 0.9,
                    "potential_value": 2000.0,
                }
            )

        return opportunities


class EnhancedFeedbackService:
    """Advanced feedback and survey system with real-time sentiment analysis."""

    def __init__(self, organization):
        self.organization = organization
        self.openai_api_key = getattr(settings, "OPENAI_API_KEY", None)

    async def collect_feedback(
        self, customer_id: str, feedback_type: str, feedback_data: Dict
    ) -> Dict[str, Any]:
        """Collect and process feedback from customer."""
        try:
            customer = User.objects.get(id=customer_id, organization=self.organization)

            # Analyze sentiment in real-time
            sentiment_analysis = await self._analyze_sentiment(
                feedback_data.get("text", "")
            )

            # Process feedback
            processed_feedback = await self._process_feedback(
                feedback_data, sentiment_analysis
            )

            # Generate actionable recommendations
            recommendations = await self._generate_recommendations(processed_feedback)

            return {
                "customer_id": customer_id,
                "feedback_type": feedback_type,
                "sentiment_analysis": sentiment_analysis,
                "processed_feedback": processed_feedback,
                "recommendations": recommendations,
                "processed_at": timezone.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Feedback collection error: {e}")
            return {"error": str(e)}

    async def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of feedback text."""
        if self.openai_api_key:
            # Use OpenAI for sentiment analysis
            prompt = f"""
            Analyze the sentiment of the following customer feedback:
            {text}
            
            Return a JSON response with:
            - sentiment: positive, negative, or neutral
            - confidence: confidence score (0-1)
            - emotions: list of detected emotions
            - key_themes: main themes mentioned
            """

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.openai_api_key}"},
                    json={
                        "model": "gpt-4",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.3,
                    },
                ) as response:
                    data = await response.json()
                    return json.loads(data["choices"][0]["message"]["content"])

        # Fallback to simple sentiment analysis
        return self._simple_sentiment_analysis(text)

    def _simple_sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """Simple sentiment analysis using keyword matching."""
        positive_words = [
            "good",
            "great",
            "excellent",
            "amazing",
            "wonderful",
            "fantastic",
            "love",
            "like",
        ]
        negative_words = [
            "bad",
            "terrible",
            "awful",
            "hate",
            "dislike",
            "horrible",
            "worst",
            "angry",
        ]

        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        if positive_count > negative_count:
            return {
                "sentiment": "positive",
                "confidence": 0.7,
                "emotions": ["satisfaction", "happiness"],
                "key_themes": ["positive_experience"],
            }
        elif negative_count > positive_count:
            return {
                "sentiment": "negative",
                "confidence": 0.7,
                "emotions": ["frustration", "disappointment"],
                "key_themes": ["negative_experience"],
            }
        else:
            return {
                "sentiment": "neutral",
                "confidence": 0.5,
                "emotions": [],
                "key_themes": [],
            }

    async def _process_feedback(
        self, feedback_data: Dict, sentiment_analysis: Dict
    ) -> Dict[str, Any]:
        """Process feedback data."""
        return {
            "original_feedback": feedback_data,
            "sentiment": sentiment_analysis["sentiment"],
            "confidence": sentiment_analysis["confidence"],
            "emotions": sentiment_analysis["emotions"],
            "key_themes": sentiment_analysis["key_themes"],
            "priority": (
                "high" if sentiment_analysis["sentiment"] == "negative" else "medium"
            ),
            "requires_action": sentiment_analysis["sentiment"] == "negative",
        }

    async def _generate_recommendations(
        self, processed_feedback: Dict
    ) -> List[Dict[str, Any]]:
        """Generate actionable recommendations from feedback."""
        recommendations = []

        if processed_feedback["sentiment"] == "negative":
            recommendations.append(
                {
                    "action": "immediate_response",
                    "description": "Send immediate response to address concerns",
                    "priority": "high",
                    "estimated_effort": "low",
                }
            )
            recommendations.append(
                {
                    "action": "follow_up_call",
                    "description": "Schedule follow-up call to discuss issues",
                    "priority": "high",
                    "estimated_effort": "medium",
                }
            )
        elif processed_feedback["sentiment"] == "positive":
            recommendations.append(
                {
                    "action": "thank_customer",
                    "description": "Send thank you message and ask for testimonial",
                    "priority": "medium",
                    "estimated_effort": "low",
                }
            )

        return recommendations


class EnhancedAdvocacyService:
    """Customer advocacy platform service with referral programs and community building."""

    def __init__(self, organization):
        self.organization = organization

    async def manage_referral_program(
        self, customer_id: str, referral_data: Dict
    ) -> Dict[str, Any]:
        """Manage referral program for customer."""
        try:
            customer = User.objects.get(id=customer_id, organization=self.organization)

            # Process referral
            referral_result = await self._process_referral(customer, referral_data)

            # Calculate rewards
            rewards = await self._calculate_rewards(referral_result)

            # Update advocacy metrics
            await self._update_advocacy_metrics(customer, referral_result)

            return {
                "customer_id": customer_id,
                "referral_status": "processed",
                "referral_result": referral_result,
                "rewards": rewards,
                "advocacy_score": await self._calculate_advocacy_score(customer),
            }

        except Exception as e:
            logger.error(f"Referral program management error: {e}")
            return {"error": str(e)}

    async def collect_testimonial(
        self, customer_id: str, testimonial_data: Dict
    ) -> Dict[str, Any]:
        """Collect and process customer testimonial."""
        try:
            customer = User.objects.get(id=customer_id, organization=self.organization)

            # Process testimonial
            testimonial_result = await self._process_testimonial(
                customer, testimonial_data
            )

            # Generate case study if applicable
            case_study = await self._generate_case_study(testimonial_result)

            return {
                "customer_id": customer_id,
                "testimonial_status": "collected",
                "testimonial_result": testimonial_result,
                "case_study": case_study,
                "social_proof_value": await self._calculate_social_proof_value(
                    testimonial_result
                ),
            }

        except Exception as e:
            logger.error(f"Testimonial collection error: {e}")
            return {"error": str(e)}

    async def _process_referral(
        self, customer: User, referral_data: Dict
    ) -> Dict[str, Any]:
        """Process customer referral."""
        return {
            "referral_id": "ref_123",
            "referred_customer": referral_data.get("referred_email"),
            "referral_source": referral_data.get("source", "direct"),
            "referral_value": referral_data.get("value", 0.0),
            "status": "pending",
        }

    async def _calculate_rewards(self, referral_result: Dict) -> Dict[str, Any]:
        """Calculate rewards for referral."""
        return {
            "reward_type": "credit",
            "reward_amount": 100.0,
            "reward_status": "pending",
            "expiration_date": "2024-12-31",
        }

    async def _update_advocacy_metrics(
        self, customer: User, referral_result: Dict
    ) -> None:
        """Update customer advocacy metrics."""
        # This would update advocacy metrics in the database
        logger.info(f"Updating advocacy metrics for customer {customer.email}")

    async def _calculate_advocacy_score(self, customer: User) -> float:
        """Calculate customer advocacy score."""
        return 0.85  # Placeholder score

    async def _process_testimonial(
        self, customer: User, testimonial_data: Dict
    ) -> Dict[str, Any]:
        """Process customer testimonial."""
        return {
            "testimonial_id": "test_123",
            "content": testimonial_data.get("content", ""),
            "rating": testimonial_data.get("rating", 5),
            "status": "approved",
            "publication_date": timezone.now().isoformat(),
        }

    async def _generate_case_study(self, testimonial_result: Dict) -> Dict[str, Any]:
        """Generate case study from testimonial."""
        return {
            "case_study_id": "cs_123",
            "title": "Customer Success Story",
            "content": "Generated case study content",
            "status": "draft",
            "publication_date": None,
        }

    async def _calculate_social_proof_value(self, testimonial_result: Dict) -> float:
        """Calculate social proof value of testimonial."""
        return 0.9  # Placeholder value

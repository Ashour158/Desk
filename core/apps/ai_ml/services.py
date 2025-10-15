"""
AI/ML services for predictive analytics and intelligent automation.
"""

import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from django.utils import timezone
from django.db.models import Q, Count, Avg
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
import json

from .models import (
    MLModel,
    Prediction,
    CustomerInsight,
    AnomalyDetection,
    DemandForecast,
    Recommendation,
)
from apps.tickets.models import Ticket
from apps.accounts.models import User
from apps.organizations.models import Organization

logger = logging.getLogger(__name__)


class PredictiveAnalytics:
    """Predictive analytics service for various ML predictions."""

    def __init__(self, organization: Organization):
        self.organization = organization

    def predict_ticket_routing(self, ticket_data: Dict) -> Dict:
        """Predict the best agent for ticket assignment."""
        try:
            model = self._get_or_create_model("ticket_routing")
            if not model.is_active:
                return {"error": "Model not active"}

            # Prepare features
            features = self._prepare_ticket_features(ticket_data)

            # Make prediction
            prediction = self._predict_with_model(model, features)

            # Get top agents
            top_agents = self._get_top_agents(prediction)

            return {
                "predicted_agent": top_agents[0] if top_agents else None,
                "confidence": prediction.get("confidence", 0.0),
                "alternatives": top_agents[1:3] if len(top_agents) > 1 else [],
            }

        except Exception as e:
            logger.error(f"Error in ticket routing prediction: {str(e)}")
            return {"error": str(e)}

    def predict_customer_churn(self, customer_id: str) -> Dict:
        """Predict customer churn probability."""
        try:
            model = self._get_or_create_model("churn_prediction")
            if not model.is_active:
                return {"error": "Model not active"}

            # Get customer data
            customer_data = self._get_customer_data(customer_id)
            features = self._prepare_customer_features(customer_data)

            # Make prediction
            prediction = self._predict_with_model(model, features)

            # Update customer insight
            self._update_customer_insight(customer_id, prediction)

            return {
                "churn_probability": prediction.get("probability", 0.0),
                "risk_factors": prediction.get("risk_factors", []),
                "recommendations": prediction.get("recommendations", []),
            }

        except Exception as e:
            logger.error(f"Error in churn prediction: {str(e)}")
            return {"error": str(e)}

    def forecast_demand(self, forecast_type: str, days_ahead: int = 30) -> Dict:
        """Forecast demand for various metrics."""
        try:
            model = self._get_or_create_model("demand_forecasting")
            if not model.is_active:
                return {"error": "Model not active"}

            # Get historical data
            historical_data = self._get_historical_data(forecast_type, days_ahead * 2)

            # Prepare features
            features = self._prepare_forecast_features(historical_data, days_ahead)

            # Make prediction
            prediction = self._predict_with_model(model, features)

            # Create forecast record
            forecast = DemandForecast.objects.create(
                organization=self.organization,
                forecast_type=forecast_type,
                forecast_date=timezone.now().date() + timedelta(days=days_ahead),
                predicted_value=prediction.get("value", 0.0),
                confidence_interval_lower=prediction.get("lower_bound", 0.0),
                confidence_interval_upper=prediction.get("upper_bound", 0.0),
                historical_data=historical_data,
                model_used=model,
            )

            return {
                "forecast_date": forecast.forecast_date.isoformat(),
                "predicted_value": forecast.predicted_value,
                "confidence_interval": [
                    forecast.confidence_interval_lower,
                    forecast.confidence_interval_upper,
                ],
                "trend": prediction.get("trend", "stable"),
            }

        except Exception as e:
            logger.error(f"Error in demand forecasting: {str(e)}")
            return {"error": str(e)}

    def detect_anomalies(self) -> List[Dict]:
        """Detect anomalies in system behavior."""
        try:
            model = self._get_or_create_model("anomaly_detection")
            if not model.is_active:
                return []

            # Get recent data
            recent_data = self._get_recent_metrics()

            # Detect anomalies
            anomalies = []
            for metric_type, data in recent_data.items():
                anomaly_score = self._calculate_anomaly_score(data, model)

                if anomaly_score > 0.7:  # Threshold for anomaly
                    anomaly = AnomalyDetection.objects.create(
                        organization=self.organization,
                        anomaly_type=metric_type,
                        severity="high" if anomaly_score > 0.9 else "medium",
                        title=f"Anomaly detected in {metric_type}",
                        description=f"Unusual pattern detected with score {anomaly_score:.2f}",
                        baseline_data=data.get("baseline", {}),
                        anomaly_data=data.get("current", {}),
                        deviation_score=anomaly_score,
                    )
                    anomalies.append(
                        {
                            "id": str(anomaly.id),
                            "type": anomaly.anomaly_type,
                            "severity": anomaly.severity,
                            "score": anomaly_score,
                            "description": anomaly.description,
                        }
                    )

            return anomalies

        except Exception as e:
            logger.error(f"Error in anomaly detection: {str(e)}")
            return []

    def suggest_responses(self, ticket_id: str) -> List[Dict]:
        """Suggest responses for tickets using AI."""
        try:
            model = self._get_or_create_model("response_suggestion")
            if not model.is_active:
                return []

            # Get ticket data
            ticket = Ticket.objects.get(id=ticket_id, organization=self.organization)

            # Get knowledge base context
            kb_context = self._get_kb_context(ticket)

            # Prepare features
            features = {
                "ticket_subject": ticket.subject,
                "ticket_description": ticket.description,
                "ticket_category": ticket.category,
                "ticket_priority": ticket.priority,
                "kb_context": kb_context,
            }

            # Make prediction
            prediction = self._predict_with_model(model, features)

            # Generate suggestions
            suggestions = []
            for suggestion in prediction.get("suggestions", []):
                suggestions.append(
                    {
                        "text": suggestion.get("text", ""),
                        "confidence": suggestion.get("confidence", 0.0),
                        "source": suggestion.get("source", "ai"),
                        "category": suggestion.get("category", "general"),
                    }
                )

            return suggestions

        except Exception as e:
            logger.error(f"Error in response suggestion: {str(e)}")
            return []

    def _get_or_create_model(self, model_type: str) -> MLModel:
        """Get or create ML model for organization."""
        model, created = MLModel.objects.get_or_create(
            organization=self.organization,
            model_type=model_type,
            defaults={
                "name": f"{model_type.replace('_', ' ').title()} Model",
                "algorithm": "random_forest",
                "status": "active" if not created else "training",
            },
        )
        return model

    def _prepare_ticket_features(self, ticket_data: Dict) -> Dict:
        """Prepare features for ticket routing prediction."""
        return {
            "subject_length": len(ticket_data.get("subject", "")),
            "description_length": len(ticket_data.get("description", "")),
            "category": ticket_data.get("category", ""),
            "priority": ticket_data.get("priority", "medium"),
            "channel": ticket_data.get("channel", "web"),
            "customer_tier": ticket_data.get("customer_tier", "standard"),
            "time_of_day": datetime.now().hour,
            "day_of_week": datetime.now().weekday(),
        }

    def _prepare_customer_features(self, customer_data: Dict) -> Dict:
        """Prepare features for customer churn prediction."""
        return {
            "ticket_count": customer_data.get("ticket_count", 0),
            "avg_resolution_time": customer_data.get("avg_resolution_time", 0),
            "satisfaction_score": customer_data.get("satisfaction_score", 0),
            "last_activity_days": customer_data.get("last_activity_days", 0),
            "support_usage_frequency": customer_data.get("support_usage_frequency", 0),
            "account_age_days": customer_data.get("account_age_days", 0),
        }

    def _prepare_forecast_features(
        self, historical_data: List, days_ahead: int
    ) -> Dict:
        """Prepare features for demand forecasting."""
        if not historical_data:
            return {}

        # Calculate trends and patterns
        values = [d["value"] for d in historical_data]
        trend = np.polyfit(range(len(values)), values, 1)[0] if len(values) > 1 else 0

        return {
            "historical_values": values,
            "trend": trend,
            "seasonality": self._calculate_seasonality(values),
            "days_ahead": days_ahead,
            "recent_avg": np.mean(values[-7:]) if len(values) >= 7 else np.mean(values),
        }

    def _predict_with_model(self, model: MLModel, features: Dict) -> Dict:
        """Make prediction using the trained model."""
        # This is a simplified implementation
        # In production, you would load the actual trained model
        try:
            # Simulate prediction based on model type
            if model.model_type == "ticket_routing":
                return self._simulate_ticket_routing_prediction(features)
            elif model.model_type == "churn_prediction":
                return self._simulate_churn_prediction(features)
            elif model.model_type == "demand_forecasting":
                return self._simulate_demand_forecast(features)
            elif model.model_type == "anomaly_detection":
                return self._simulate_anomaly_detection(features)
            elif model.model_type == "response_suggestion":
                return self._simulate_response_suggestion(features)
            else:
                return {"error": "Unknown model type"}

        except Exception as e:
            logger.error(f"Error in model prediction: {str(e)}")
            return {"error": str(e)}

    def _simulate_ticket_routing_prediction(self, features: Dict) -> Dict:
        """Simulate ticket routing prediction."""
        # Simplified simulation - in production, use actual ML model
        confidence = 0.85
        return {
            "confidence": confidence,
            "agent_scores": [
                {"agent_id": "agent1", "score": 0.9},
                {"agent_id": "agent2", "score": 0.7},
                {"agent_id": "agent3", "score": 0.6},
            ],
        }

    def _simulate_churn_prediction(self, features: Dict) -> Dict:
        """Simulate churn prediction."""
        # Simplified simulation
        risk_factors = []
        if features.get("last_activity_days", 0) > 30:
            risk_factors.append("Inactive for 30+ days")
        if features.get("satisfaction_score", 0) < 3:
            risk_factors.append("Low satisfaction score")

        probability = min(0.9, len(risk_factors) * 0.3)

        return {
            "probability": probability,
            "risk_factors": risk_factors,
            "recommendations": [
                "Reach out to customer",
                "Offer support resources",
                "Schedule follow-up call",
            ],
        }

    def _simulate_demand_forecast(self, features: Dict) -> Dict:
        """Simulate demand forecasting."""
        historical_avg = features.get("recent_avg", 100)
        trend = features.get("trend", 0)

        # Simple linear trend projection
        predicted_value = historical_avg + (trend * 30)  # 30 days ahead

        return {
            "value": max(0, predicted_value),
            "lower_bound": max(0, predicted_value * 0.8),
            "upper_bound": predicted_value * 1.2,
            "trend": (
                "increasing" if trend > 0 else "decreasing" if trend < 0 else "stable"
            ),
        }

    def _simulate_anomaly_detection(self, data: Dict) -> float:
        """Simulate anomaly detection."""
        # Simplified anomaly detection
        if "ticket_volume" in data:
            current = data["ticket_volume"].get("current", 0)
            baseline = data["ticket_volume"].get("baseline", 0)
            if baseline > 0:
                deviation = abs(current - baseline) / baseline
                return min(1.0, deviation)
        return 0.0

    def _simulate_response_suggestion(self, features: Dict) -> Dict:
        """Simulate response suggestions."""
        suggestions = [
            {
                "text": "Thank you for contacting us. I understand your concern and will help you resolve this issue.",
                "confidence": 0.9,
                "source": "template",
                "category": "greeting",
            },
            {
                "text": "Let me check your account details and get back to you with a solution.",
                "confidence": 0.8,
                "source": "ai",
                "category": "action",
            },
        ]

        return {"suggestions": suggestions}

    def _get_customer_data(self, customer_id: str) -> Dict:
        """Get customer data for analysis."""
        try:
            customer = User.objects.get(id=customer_id, organization=self.organization)

            # Get ticket statistics
            tickets = Ticket.objects.filter(
                customer=customer, organization=self.organization
            )
            ticket_count = tickets.count()
            avg_resolution_time = tickets.filter(resolved_at__isnull=False).aggregate(
                avg_time=Avg("resolved_at" - "created_at")
            )["avg_time"]

            return {
                "ticket_count": ticket_count,
                "avg_resolution_time": (
                    avg_resolution_time.total_seconds() / 3600
                    if avg_resolution_time
                    else 0
                ),
                "satisfaction_score": 4.0,  # Placeholder
                "last_activity_days": (
                    (timezone.now() - customer.last_login).days
                    if customer.last_login
                    else 0
                ),
                "support_usage_frequency": ticket_count
                / max(1, (timezone.now() - customer.date_joined).days),
                "account_age_days": (timezone.now() - customer.date_joined).days,
            }

        except User.DoesNotExist:
            return {}

    def _get_historical_data(self, metric_type: str, days: int) -> List[Dict]:
        """Get historical data for forecasting."""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        if metric_type == "ticket_volume":
            # Get daily ticket counts
            data = []
            for i in range(days):
                date = start_date + timedelta(days=i)
                count = Ticket.objects.filter(
                    organization=self.organization, created_at__date=date
                ).count()
                data.append({"date": date.isoformat(), "value": count})

        return data

    def _get_recent_metrics(self) -> Dict:
        """Get recent system metrics for anomaly detection."""
        now = timezone.now()
        yesterday = now - timedelta(days=1)

        # Get ticket volume
        current_volume = Ticket.objects.filter(
            organization=self.organization, created_at__gte=yesterday
        ).count()

        # Get baseline (previous week average)
        week_ago = now - timedelta(days=7)
        baseline_volume = (
            Ticket.objects.filter(
                organization=self.organization,
                created_at__gte=week_ago,
                created_at__lt=yesterday,
            ).count()
            / 6
        )  # 6 days

        return {
            "ticket_volume": {"current": current_volume, "baseline": baseline_volume}
        }

    def _calculate_anomaly_score(self, data: Dict, model: MLModel) -> float:
        """Calculate anomaly score for data."""
        # Simplified anomaly detection
        if "ticket_volume" in data:
            current = data["ticket_volume"].get("current", 0)
            baseline = data["ticket_volume"].get("baseline", 0)

            if baseline > 0:
                deviation = abs(current - baseline) / baseline
                return min(1.0, deviation)

        return 0.0

    def _calculate_seasonality(self, values: List[float]) -> float:
        """Calculate seasonality factor."""
        if len(values) < 7:
            return 1.0

        # Simple seasonality calculation
        weekly_avg = np.mean(values[-7:])
        overall_avg = np.mean(values)

        return weekly_avg / overall_avg if overall_avg > 0 else 1.0

    def _get_top_agents(self, prediction: Dict) -> List[str]:
        """Get top agents from prediction."""
        agent_scores = prediction.get("agent_scores", [])
        return [
            agent["agent_id"]
            for agent in sorted(agent_scores, key=lambda x: x["score"], reverse=True)
        ]

    def _update_customer_insight(self, customer_id: str, prediction: Dict):
        """Update customer insight with prediction."""
        try:
            customer = User.objects.get(id=customer_id, organization=self.organization)
            insight, created = CustomerInsight.objects.get_or_create(
                organization=self.organization,
                customer=customer,
                defaults={"health_score": 50.0},
            )

            insight.churn_probability = prediction.get("probability", 0.0)
            insight.is_at_risk = insight.churn_probability > 0.7
            insight.risk_factors = prediction.get("risk_factors", [])
            insight.recommended_actions = prediction.get("recommendations", [])
            insight.save()

        except User.DoesNotExist:
            pass

    def _get_kb_context(self, ticket: Ticket) -> List[str]:
        """Get relevant knowledge base articles for ticket."""
        # Simplified KB context retrieval
        from apps.knowledge_base.models import KBArticle

        articles = KBArticle.objects.filter(
            organization=ticket.organization, is_active=True
        ).order_by("-helpful_count")[:5]

        return [article.title for article in articles]

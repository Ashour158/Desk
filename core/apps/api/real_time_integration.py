"""
Comprehensive real-time integration system for all features.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from django.conf import settings
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import aiohttp
import redis

logger = logging.getLogger(__name__)


class RealTimeIntegration:
    """Comprehensive real-time integration system."""

    def __init__(self):
        self.channel_layer = get_channel_layer()
        self.redis_client = redis.Redis(
            host=getattr(settings, "REDIS_HOST", "localhost"),
            port=getattr(settings, "REDIS_PORT", 6379),
            db=getattr(settings, "REDIS_DB", 0),
        )
        self.websocket_channels = {
            "tickets": "ticket_updates",
            "work_orders": "work_order_updates",
            "technicians": "technician_updates",
            "notifications": "notification_updates",
            "system": "system_updates",
            "features": "feature_updates",
        }

    def send_realtime_update(
        self,
        event_type: str,
        payload: Dict[str, Any],
        organization_id: Optional[int] = None,
        user_id: Optional[int] = None,
        feature: Optional[str] = None,
    ):
        """Send real-time update to connected clients."""
        try:
            message = {
                "type": "websocket.message",
                "event_type": event_type,
                "payload": payload,
                "timestamp": timezone.now().isoformat(),
                "feature": feature,
            }

            # Determine target channels
            channels = self._get_target_channels(organization_id, user_id, feature)

            # Send to all target channels
            for channel in channels:
                async_to_sync(self.channel_layer.group_send)(channel, message)

            # Log the update
            self._log_realtime_update(event_type, payload, organization_id, user_id)

        except Exception as e:
            logger.error(f"Error sending real-time update: {e}")

    def _get_target_channels(
        self,
        organization_id: Optional[int],
        user_id: Optional[int],
        feature: Optional[str],
    ) -> List[str]:
        """Get target channels for real-time updates."""
        channels = []

        if organization_id:
            channels.append(f"org_{organization_id}")

        if user_id:
            channels.append(f"user_{user_id}")

        if feature:
            channels.append(f"feature_{feature}")

        # Always include broadcast channel for system-wide updates
        channels.append("broadcast")

        return channels

    def _log_realtime_update(
        self,
        event_type: str,
        payload: Dict[str, Any],
        organization_id: Optional[int],
        user_id: Optional[int],
    ):
        """Log real-time update for monitoring."""
        log_data = {
            "event_type": event_type,
            "organization_id": organization_id,
            "user_id": user_id,
            "timestamp": timezone.now().isoformat(),
            "payload_size": len(json.dumps(payload)),
        }

        # Store in Redis for monitoring
        self.redis_client.lpush("realtime_logs", json.dumps(log_data))
        self.redis_client.ltrim("realtime_logs", 0, 1000)  # Keep last 1000 logs

    # Feature-specific real-time updates

    def send_ticket_update(
        self,
        ticket_id: int,
        action: str,
        data: Dict[str, Any],
        organization_id: int,
        user_id: Optional[int] = None,
    ):
        """Send ticket update in real-time."""
        payload = {
            "ticket_id": ticket_id,
            "action": action,
            "data": data,
            "user_id": user_id,
        }

        self.send_realtime_update(
            event_type="ticket_update",
            payload=payload,
            organization_id=organization_id,
            user_id=user_id,
            feature="tickets",
        )

    def send_work_order_update(
        self,
        work_order_id: int,
        action: str,
        data: Dict[str, Any],
        organization_id: int,
        user_id: Optional[int] = None,
    ):
        """Send work order update in real-time."""
        payload = {
            "work_order_id": work_order_id,
            "action": action,
            "data": data,
            "user_id": user_id,
        }

        self.send_realtime_update(
            event_type="work_order_update",
            payload=payload,
            organization_id=organization_id,
            user_id=user_id,
            feature="work_orders",
        )

    def send_technician_location_update(
        self, technician_id: int, location: Dict[str, Any], organization_id: int
    ):
        """Send technician location update in real-time."""
        payload = {
            "technician_id": technician_id,
            "location": location,
            "timestamp": timezone.now().isoformat(),
        }

        self.send_realtime_update(
            event_type="technician_location",
            payload=payload,
            organization_id=organization_id,
            feature="technicians",
        )

    def send_notification(
        self,
        notification_type: str,
        message: str,
        user_id: int,
        organization_id: int,
        data: Optional[Dict[str, Any]] = None,
    ):
        """Send real-time notification."""
        payload = {
            "type": notification_type,
            "message": message,
            "data": data or {},
            "timestamp": timezone.now().isoformat(),
        }

        self.send_realtime_update(
            event_type="notification",
            payload=payload,
            organization_id=organization_id,
            user_id=user_id,
            feature="notifications",
        )

    def send_system_status_update(
        self,
        status: str,
        details: Dict[str, Any],
        organization_id: Optional[int] = None,
    ):
        """Send system status update."""
        payload = {
            "status": status,
            "details": details,
            "timestamp": timezone.now().isoformat(),
        }

        self.send_realtime_update(
            event_type="system_status",
            payload=payload,
            organization_id=organization_id,
            feature="system",
        )

    def send_feature_status_update(
        self,
        feature_name: str,
        status: str,
        details: Dict[str, Any],
        organization_id: Optional[int] = None,
    ):
        """Send feature status update."""
        payload = {
            "feature_name": feature_name,
            "status": status,
            "details": details,
            "timestamp": timezone.now().isoformat(),
        }

        self.send_realtime_update(
            event_type="feature_status",
            payload=payload,
            organization_id=organization_id,
            feature="features",
        )

    # WebSocket connection management

    def connect_user(self, user_id: int, organization_id: int, websocket_channel: str):
        """Connect user to real-time updates."""
        try:
            # Add user to organization channel
            async_to_sync(self.channel_layer.group_add)(
                f"org_{organization_id}", websocket_channel
            )

            # Add user to personal channel
            async_to_sync(self.channel_layer.group_add)(
                f"user_{user_id}", websocket_channel
            )

            # Log connection
            self._log_connection(user_id, organization_id, "connected")

        except Exception as e:
            logger.error(f"Error connecting user {user_id}: {e}")

    def disconnect_user(
        self, user_id: int, organization_id: int, websocket_channel: str
    ):
        """Disconnect user from real-time updates."""
        try:
            # Remove user from organization channel
            async_to_sync(self.channel_layer.group_discard)(
                f"org_{organization_id}", websocket_channel
            )

            # Remove user from personal channel
            async_to_sync(self.channel_layer.group_discard)(
                f"user_{user_id}", websocket_channel
            )

            # Log disconnection
            self._log_connection(user_id, organization_id, "disconnected")

        except Exception as e:
            logger.error(f"Error disconnecting user {user_id}: {e}")

    def _log_connection(self, user_id: int, organization_id: int, action: str):
        """Log user connection/disconnection."""
        log_data = {
            "user_id": user_id,
            "organization_id": organization_id,
            "action": action,
            "timestamp": timezone.now().isoformat(),
        }

        self.redis_client.lpush("connection_logs", json.dumps(log_data))
        self.redis_client.ltrim("connection_logs", 0, 1000)

    # Integration with external services

    async def sync_with_ai_service(self, event_type: str, data: Dict[str, Any]):
        """Sync with AI service for real-time processing."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "http://ai-service:8001/realtime/process",
                    json={
                        "event_type": event_type,
                        "data": data,
                        "timestamp": timezone.now().isoformat(),
                    },
                    timeout=5,
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result
                    else:
                        logger.error(f"AI service error: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error syncing with AI service: {e}")
            return None

    async def sync_with_realtime_service(self, event_type: str, data: Dict[str, Any]):
        """Sync with real-time service for additional processing."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "http://realtime-service:8002/realtime/process",
                    json={
                        "event_type": event_type,
                        "data": data,
                        "timestamp": timezone.now().isoformat(),
                    },
                    timeout=5,
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result
                    else:
                        logger.error(f"Real-time service error: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error syncing with real-time service: {e}")
            return None

    # Monitoring and analytics

    def get_realtime_stats(self) -> Dict[str, Any]:
        """Get real-time system statistics."""
        try:
            # Get connection count
            connection_count = len(self.redis_client.keys("connection_*"))

            # Get recent activity
            recent_logs = self.redis_client.lrange("realtime_logs", 0, 10)
            recent_activity = [json.loads(log) for log in recent_logs]

            # Get feature usage
            feature_usage = {}
            for feature in self.websocket_channels.keys():
                usage_count = self.redis_client.llen(f"feature_{feature}_usage")
                feature_usage[feature] = usage_count

            return {
                "connection_count": connection_count,
                "recent_activity": recent_activity,
                "feature_usage": feature_usage,
                "timestamp": timezone.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error getting real-time stats: {e}")
            return {}

    def get_feature_health(self, feature: str) -> Dict[str, Any]:
        """Get health status of a specific feature."""
        try:
            # Check if feature is active
            is_active = self.redis_client.exists(f"feature_{feature}_active")

            # Get recent activity
            recent_activity = self.redis_client.lrange(
                f"feature_{feature}_activity", 0, 5
            )
            activity_data = [json.loads(activity) for activity in recent_activity]

            # Get error count
            error_count = self.redis_client.get(f"feature_{feature}_errors") or 0

            return {
                "feature": feature,
                "is_active": bool(is_active),
                "recent_activity": activity_data,
                "error_count": int(error_count),
                "timestamp": timezone.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error getting feature health for {feature}: {e}")
            return {
                "feature": feature,
                "is_active": False,
                "error": str(e),
                "timestamp": timezone.now().isoformat(),
            }


# Global real-time integration instance
realtime_integration = RealTimeIntegration()

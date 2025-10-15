"""
Real-time integration service for microservices communication.
"""

import asyncio
import json
import aiohttp
import logging
from django.conf import settings

# Configure logging
logger = logging.getLogger(__name__)
from django.utils import timezone
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import IntegrationLog, APIService


class RealTimeConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time updates."""

    async def connect(self):
        """Accept WebSocket connection."""
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"room_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

        # Send initial status
        await self.send(
            text_data=json.dumps(
                {
                    "type": "connection_established",
                    "message": "Connected to real-time updates",
                    "timestamp": timezone.now().isoformat(),
                }
            )
        )

    async def disconnect(self, close_code):
        """Leave room group."""
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """Receive message from WebSocket."""
        try:
            data = json.loads(text_data)
            message_type = data.get("type")

            if message_type == "join_ticket":
                await self.join_ticket_room(data["ticket_id"])
            elif message_type == "leave_ticket":
                await self.leave_ticket_room(data["ticket_id"])
            elif message_type == "typing":
                await self.handle_typing(data)
            elif message_type == "location_update":
                await self.handle_location_update(data)
            elif message_type == "notification":
                await self.handle_notification(data)

        except json.JSONDecodeError:
            await self.send(
                text_data=json.dumps(
                    {"type": "error", "message": "Invalid JSON format"}
                )
            )

    async def join_ticket_room(self, ticket_id):
        """Join a specific ticket room."""
        room_name = f"ticket_{ticket_id}"
        await self.channel_layer.group_add(room_name, self.channel_name)

        await self.send(
            text_data=json.dumps(
                {
                    "type": "joined_ticket",
                    "ticket_id": ticket_id,
                    "message": f"Joined ticket {ticket_id} room",
                }
            )
        )

    async def leave_ticket_room(self, ticket_id):
        """Leave a specific ticket room."""
        room_name = f"ticket_{ticket_id}"
        await self.channel_layer.group_discard(room_name, self.channel_name)

    async def handle_typing(self, data):
        """Handle typing indicator."""
        ticket_id = data.get("ticket_id")
        user_id = data.get("user_id")
        is_typing = data.get("is_typing", False)

        # Broadcast typing status to ticket room
        await self.channel_layer.group_send(
            f"ticket_{ticket_id}",
            {
                "type": "typing_status",
                "user_id": user_id,
                "is_typing": is_typing,
                "timestamp": timezone.now().isoformat(),
            },
        )

    async def handle_location_update(self, data):
        """Handle location update from mobile app."""
        technician_id = data.get("technician_id")
        latitude = data.get("latitude")
        longitude = data.get("longitude")

        # Update technician location in database
        await self.update_technician_location(technician_id, latitude, longitude)

        # Broadcast location update to admin dashboard
        await self.channel_layer.group_send(
            "admin_dashboard",
            {
                "type": "location_update",
                "technician_id": technician_id,
                "latitude": latitude,
                "longitude": longitude,
                "timestamp": timezone.now().isoformat(),
            },
        )

    async def handle_notification(self, data):
        """Handle notification broadcast."""
        notification_type = data.get("notification_type")
        message = data.get("message")
        user_id = data.get("user_id")

        # Broadcast notification to specific user or all users
        if user_id:
            await self.channel_layer.group_send(
                f"user_{user_id}",
                {
                    "type": "notification",
                    "notification_type": notification_type,
                    "message": message,
                    "timestamp": timezone.now().isoformat(),
                },
            )
        else:
            await self.channel_layer.group_send(
                "all_users",
                {
                    "type": "notification",
                    "notification_type": notification_type,
                    "message": message,
                    "timestamp": timezone.now().isoformat(),
                },
            )

    async def typing_status(self, event):
        """Send typing status to WebSocket."""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "typing_status",
                    "user_id": event["user_id"],
                    "is_typing": event["is_typing"],
                    "timestamp": event["timestamp"],
                }
            )
        )

    async def location_update(self, event):
        """Send location update to WebSocket."""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "location_update",
                    "technician_id": event["technician_id"],
                    "latitude": event["latitude"],
                    "longitude": event["longitude"],
                    "timestamp": event["timestamp"],
                }
            )
        )

    async def notification(self, event):
        """Send notification to WebSocket."""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "notification",
                    "notification_type": event["notification_type"],
                    "message": event["message"],
                    "timestamp": event["timestamp"],
                }
            )
        )

    async def ticket_update(self, event):
        """Send ticket update to WebSocket."""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "ticket_update",
                    "ticket_id": event["ticket_id"],
                    "status": event["status"],
                    "message": event["message"],
                    "timestamp": event["timestamp"],
                }
            )
        )

    async def work_order_update(self, event):
        """Send work order update to WebSocket."""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "work_order_update",
                    "work_order_id": event["work_order_id"],
                    "status": event["status"],
                    "message": event["message"],
                    "timestamp": event["timestamp"],
                }
            )
        )

    @database_sync_to_async
    def update_technician_location(self, technician_id, latitude, longitude):
        """Update technician location in database."""
        try:
            from apps.field_service.models import Technician

            technician = Technician.objects.get(id=technician_id)
            technician.current_location = f"POINT({longitude} {latitude})"
            technician.save()
        except Exception as e:
            logger.error(f"Error updating technician location: {e}")


class MicroserviceIntegration:
    """Integration class for microservices communication."""

    def __init__(self):
        self.ai_service_url = getattr(
            settings, "AI_SERVICE_URL", "http://ai-service:8001"
        )
        self.realtime_service_url = getattr(
            settings, "REALTIME_SERVICE_URL", "http://realtime-service:8002"
        )

    async def send_to_ai_service(self, endpoint, data):
        """Send request to AI service."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.ai_service_url}/{endpoint}", json=data
                ) as response:
                    return await response.json()
            except Exception as e:
                logger.error(f"Error communicating with AI service: {e}")
                return None

    async def send_to_realtime_service(self, endpoint, data):
        """Send request to real-time service."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.realtime_service_url}/{endpoint}", json=data
                ) as response:
                    return await response.json()
            except Exception as e:
                logger.error(f"Error communicating with real-time service: {e}")
                return None

    async def categorize_ticket(self, subject, description):
        """Categorize ticket using AI service."""
        data = {"subject": subject, "description": description}
        return await self.send_to_ai_service("categorize", data)

    async def analyze_sentiment(self, text):
        """Analyze sentiment using AI service."""
        data = {"text": text}
        return await self.send_to_ai_service("sentiment", data)

    async def get_ai_suggestions(self, ticket_content, kb_context):
        """Get AI response suggestions."""
        data = {"ticket_content": ticket_content, "kb_context": kb_context}
        return await self.send_to_ai_service("suggest-response", data)

    async def send_notification(self, user_id, message, notification_type="info"):
        """Send real-time notification."""
        data = {
            "user_id": user_id,
            "message": message,
            "notification_type": notification_type,
        }
        return await self.send_to_realtime_service("notifications", data)

    async def broadcast_update(self, update_type, data):
        """Broadcast update to all connected clients."""
        payload = {
            "type": update_type,
            "data": data,
            "timestamp": timezone.now().isoformat(),
        }
        return await self.send_to_realtime_service("broadcast", payload)


# Global microservice integration instance
microservice_integration = MicroserviceIntegration()


async def handle_ticket_update(ticket_id, status, message):
    """Handle ticket update and broadcast to real-time clients."""
    # Update ticket in database
    from apps.tickets.models import Ticket

    try:
        ticket = await database_sync_to_async(Ticket.objects.get)(id=ticket_id)
        ticket.status = status
        await database_sync_to_async(ticket.save)()
    except Exception as e:
        logger.error(f"Error updating ticket: {e}")
        return

    # Broadcast update to real-time clients
    await microservice_integration.broadcast_update(
        "ticket_update", {"ticket_id": ticket_id, "status": status, "message": message}
    )


async def handle_work_order_update(work_order_id, status, message):
    """Handle work order update and broadcast to real-time clients."""
    # Update work order in database
    from apps.field_service.models import WorkOrder

    try:
        work_order = await database_sync_to_async(WorkOrder.objects.get)(
            id=work_order_id
        )
        work_order.status = status
        await database_sync_to_async(work_order.save)()
    except Exception as e:
        logger.error(f"Error updating work order: {e}")
        return

    # Broadcast update to real-time clients
    await microservice_integration.broadcast_update(
        "work_order_update",
        {"work_order_id": work_order_id, "status": status, "message": message},
    )


async def handle_technician_location_update(technician_id, latitude, longitude):
    """Handle technician location update."""
    # Update location in database
    from apps.field_service.models import Technician

    try:
        technician = await database_sync_to_async(Technician.objects.get)(
            id=technician_id
        )
        technician.current_location = f"POINT({longitude} {latitude})"
        await database_sync_to_async(technician.save)()
    except Exception as e:
        logger.error(f"Error updating technician location: {e}")
        return

    # Broadcast location update to admin dashboard
    await microservice_integration.broadcast_update(
        "location_update",
        {"technician_id": technician_id, "latitude": latitude, "longitude": longitude},
    )


# WebSocket routing
websocket_urlpatterns = [
    re_path(r"ws/room/(?P<room_name>\w+)/$", RealTimeConsumer.as_asgi()),
]

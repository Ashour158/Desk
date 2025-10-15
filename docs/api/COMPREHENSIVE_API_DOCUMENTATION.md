# Comprehensive API Documentation

## Table of Contents
1. [API Overview](#api-overview)
2. [Authentication](#authentication)
3. [Core API Endpoints](#core-api-endpoints)
4. [Feature-Specific Endpoints](#feature-specific-endpoints)
5. [Advanced Enterprise Endpoints](#advanced-enterprise-endpoints)
6. [Response Schemas](#response-schemas)
7. [Error Handling](#error-handling)
8. [Rate Limiting](#rate-limiting)
9. [Examples](#examples)

---

## API Overview

### Base URL
```
Production: https://api.helpdesk.com/api/v1/
Development: http://localhost:8000/api/v1/
```

### API Versioning
- Current Version: v1
- Version Header: `Accept: application/vnd.helpdesk.v1+json`

### Content Types
- **Request:** `application/json`
- **Response:** `application/json`

---

## Authentication

### Authentication Methods

#### 1. JWT Token Authentication
```http
Authorization: Bearer <access_token>
```

#### 2. API Key Authentication
```http
X-API-Key: <api_key>
```

#### 3. Session Authentication
```http
Cookie: sessionid=<session_id>
```

### Token Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/users/login/` | Obtain JWT tokens | No |
| POST | `/api/v1/users/refresh/` | Refresh access token | No |
| POST | `/api/v1/users/verify/` | Verify token validity | No |

---

## Core API Endpoints

### 1. User Management

#### User Registration
```http
POST /api/v1/users/register/
```

**Authentication:** Not required

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "organization_slug": "acme-corp"
}
```

**Response Schema:**
```json
{
  "message": "User created successfully",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "full_name": "John Doe",
    "role": "customer",
    "phone": "+1234567890",
    "avatar": null,
    "timezone": "UTC",
    "language": "en",
    "is_verified": false,
    "last_active_at": null,
    "is_agent": false,
    "is_customer": true,
    "is_technician": false,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

**Status Codes:**
- `201` - User created successfully
- `400` - Bad request (validation errors)
- `409` - User already exists

#### User Profile
```http
GET /api/v1/users/profile/
PUT /api/v1/users/profile/
```

**Authentication:** Required (JWT)

**Request Body (PUT):**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "timezone": "America/New_York",
  "language": "en"
}
```

**Response Schema:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "role": "customer",
  "phone": "+1234567890",
  "avatar": null,
  "timezone": "America/New_York",
  "language": "en",
  "is_verified": true,
  "last_active_at": "2024-01-01T12:00:00Z",
  "is_agent": false,
  "is_customer": true,
  "is_technician": false,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

**Status Codes:**
- `200` - Success
- `401` - Unauthorized
- `400` - Bad request

#### Password Change
```http
POST /api/v1/users/change-password/
```

**Authentication:** Required (JWT)

**Request Body:**
```json
{
  "old_password": "oldpassword123",
  "new_password": "newpassword123"
}
```

**Response Schema:**
```json
{
  "message": "Password changed successfully"
}
```

**Status Codes:**
- `200` - Password changed successfully
- `400` - Bad request (invalid old password)
- `401` - Unauthorized

#### Two-Factor Authentication
```http
POST /api/v1/users/2fa/setup/
POST /api/v1/users/2fa/verify/
POST /api/v1/users/2fa/disable/
```

**Authentication:** Required (JWT)

**Request Body (Setup):**
```json
{
  "device_name": "My Phone"
}
```

**Response Schema (Setup):**
```json
{
  "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "secret_key": "JBSWY3DPEHPK3PXP",
  "backup_codes": ["12345678", "87654321", "11223344"]
}
```

**Status Codes:**
- `200` - 2FA setup successful
- `400` - Bad request
- `401` - Unauthorized

### 2. Organization Management

#### Organization List
```http
GET /api/v1/organizations/
```

**Authentication:** Required (JWT)

**Query Parameters:**
- `search` - Search organizations by name
- `subscription_tier` - Filter by subscription tier
- `is_active` - Filter by active status

**Response Schema:**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Acme Corporation",
      "slug": "acme-corp",
      "domain": "acme.com",
      "subscription_tier": "enterprise",
      "settings": {
        "timezone": "America/New_York",
        "language": "en",
        "notifications": true
      },
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

**Status Codes:**
- `200` - Success
- `401` - Unauthorized

#### Organization Detail
```http
GET /api/v1/organizations/{id}/
PUT /api/v1/organizations/{id}/
```

**Authentication:** Required (JWT)

**Request Body (PUT):**
```json
{
  "name": "Acme Corporation",
  "domain": "acme.com",
  "subscription_tier": "enterprise",
  "settings": {
    "timezone": "America/New_York",
    "language": "en",
    "notifications": true
  }
}
```

**Response Schema:**
```json
{
  "id": 1,
  "name": "Acme Corporation",
  "slug": "acme-corp",
  "domain": "acme.com",
  "subscription_tier": "enterprise",
  "settings": {
    "timezone": "America/New_York",
    "language": "en",
    "notifications": true
  },
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

**Status Codes:**
- `200` - Success
- `401` - Unauthorized
- `403` - Forbidden (insufficient permissions)
- `404` - Organization not found

### 3. Ticket Management

#### Ticket List
```http
GET /api/v1/tickets/
```

**Authentication:** Required (JWT)

**Query Parameters:**
- `status` - Filter by status (new, open, pending, resolved, closed)
- `priority` - Filter by priority (low, medium, high, urgent)
- `search` - Search tickets by subject, description, or ticket number
- `assigned_agent` - Filter by assigned agent ID
- `customer` - Filter by customer ID
- `created_after` - Filter tickets created after date
- `created_before` - Filter tickets created before date

**Response Schema:**
```json
{
  "count": 25,
  "next": "http://api.helpdesk.com/api/v1/tickets/?page=2",
  "previous": null,
  "results": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "ticket_number": "TKT-001",
      "subject": "Login Issue",
      "description": "Cannot login to the system",
      "status": "open",
      "priority": "high",
      "customer": {
        "id": 1,
        "email": "customer@example.com",
        "full_name": "John Customer"
      },
      "assigned_agent": {
        "id": 2,
        "email": "agent@example.com",
        "full_name": "Jane Agent"
      },
      "organization": {
        "id": 1,
        "name": "Acme Corporation"
      },
      "tags": ["login", "authentication"],
      "attachments": [],
      "comments": [],
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T12:00:00Z"
    }
  ]
}
```

**Status Codes:**
- `200` - Success
- `401` - Unauthorized

#### Ticket Detail
```http
GET /api/v1/tickets/{id}/
PUT /api/v1/tickets/{id}/
DELETE /api/v1/tickets/{id}/
```

**Authentication:** Required (JWT)

**Request Body (PUT):**
```json
{
  "subject": "Updated Login Issue",
  "description": "Updated description",
  "status": "pending",
  "priority": "medium",
  "assigned_agent": 2,
  "tags": ["login", "authentication", "urgent"]
}
```

**Response Schema:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "ticket_number": "TKT-001",
  "subject": "Updated Login Issue",
  "description": "Updated description",
  "status": "pending",
  "priority": "medium",
  "customer": {
    "id": 1,
    "email": "customer@example.com",
    "full_name": "John Customer"
  },
  "assigned_agent": {
    "id": 2,
    "email": "agent@example.com",
    "full_name": "Jane Agent"
  },
  "organization": {
    "id": 1,
    "name": "Acme Corporation"
  },
  "tags": ["login", "authentication", "urgent"],
  "attachments": [],
  "comments": [
    {
      "id": 1,
      "content": "Working on this issue",
      "author": {
        "id": 2,
        "email": "agent@example.com",
        "full_name": "Jane Agent"
      },
      "is_internal": false,
      "created_at": "2024-01-01T12:00:00Z"
    }
  ],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

**Status Codes:**
- `200` - Success
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Ticket not found

#### Create Ticket
```http
POST /api/v1/tickets/
```

**Authentication:** Required (JWT)

**Request Body:**
```json
{
  "subject": "New Login Issue",
  "description": "Cannot login to the system",
  "priority": "high",
  "tags": ["login", "authentication"],
  "attachments": []
}
```

**Response Schema:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "ticket_number": "TKT-002",
  "subject": "New Login Issue",
  "description": "Cannot login to the system",
  "status": "new",
  "priority": "high",
  "customer": {
    "id": 1,
    "email": "customer@example.com",
    "full_name": "John Customer"
  },
  "assigned_agent": null,
  "organization": {
    "id": 1,
    "name": "Acme Corporation"
  },
  "tags": ["login", "authentication"],
  "attachments": [],
  "comments": [],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Status Codes:**
- `201` - Ticket created successfully
- `400` - Bad request (validation errors)
- `401` - Unauthorized

#### Ticket Comments
```http
GET /api/v1/tickets/{id}/comments/
POST /api/v1/tickets/{id}/comments/
```

**Authentication:** Required (JWT)

**Request Body (POST):**
```json
{
  "content": "This is a comment on the ticket",
  "is_internal": false
}
```

**Response Schema:**
```json
{
  "id": 1,
  "content": "This is a comment on the ticket",
  "author": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John User"
  },
  "is_internal": false,
  "created_at": "2024-01-01T12:00:00Z"
}
```

**Status Codes:**
- `200` - Success (GET)
- `201` - Comment created successfully (POST)
- `400` - Bad request
- `401` - Unauthorized
- `404` - Ticket not found

#### Ticket Statistics
```http
GET /api/v1/tickets/statistics/
```

**Authentication:** Required (JWT)

**Response Schema:**
```json
{
  "total_tickets": 150,
  "open_tickets": 25,
  "pending_tickets": 15,
  "resolved_tickets": 100,
  "closed_tickets": 10,
  "average_resolution_time": "2.5 days",
  "sla_compliance": 95.5,
  "priority_distribution": {
    "low": 30,
    "medium": 50,
    "high": 15,
    "urgent": 5
  },
  "status_distribution": {
    "new": 10,
    "open": 25,
    "pending": 15,
    "resolved": 100,
    "closed": 10
  }
}
```

**Status Codes:**
- `200` - Success
- `401` - Unauthorized

### 4. Knowledge Base

#### Knowledge Base Articles
```http
GET /api/v1/knowledge-base/articles/
POST /api/v1/knowledge-base/articles/
```

**Authentication:** Required (JWT)

**Query Parameters (GET):**
- `category` - Filter by category ID
- `search` - Search articles by title or content
- `status` - Filter by status (draft, published, archived)
- `author` - Filter by author ID

**Request Body (POST):**
```json
{
  "title": "How to Reset Password",
  "content": "Step-by-step guide to reset your password",
  "category": 1,
  "tags": ["password", "reset", "authentication"],
  "status": "published"
}
```

**Response Schema:**
```json
{
  "id": 1,
  "title": "How to Reset Password",
  "content": "Step-by-step guide to reset your password",
  "category": {
    "id": 1,
    "name": "Authentication",
    "description": "Articles about authentication"
  },
  "author": {
    "id": 1,
    "email": "author@example.com",
    "full_name": "John Author"
  },
  "tags": ["password", "reset", "authentication"],
  "status": "published",
  "views": 150,
  "helpful_votes": 12,
  "not_helpful_votes": 2,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

**Status Codes:**
- `200` - Success (GET)
- `201` - Article created successfully (POST)
- `400` - Bad request
- `401` - Unauthorized

#### Knowledge Base Categories
```http
GET /api/v1/knowledge-base/categories/
POST /api/v1/knowledge-base/categories/
```

**Authentication:** Required (JWT)

**Request Body (POST):**
```json
{
  "name": "Technical Support",
  "description": "Technical support articles",
  "parent_category": null
}
```

**Response Schema:**
```json
{
  "id": 1,
  "name": "Technical Support",
  "description": "Technical support articles",
  "parent_category": null,
  "subcategories": [],
  "article_count": 25,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Status Codes:**
- `200` - Success
- `201` - Category created successfully
- `400` - Bad request
- `401` - Unauthorized

### 5. Field Service Management

#### Work Orders
```http
GET /api/v1/work-orders/
POST /api/v1/work-orders/
```

**Authentication:** Required (JWT)

**Request Body (POST):**
```json
{
  "title": "Equipment Maintenance",
  "description": "Regular maintenance of HVAC system",
  "customer": 1,
  "technician": 2,
  "scheduled_date": "2024-01-15T09:00:00Z",
  "priority": "medium",
  "location": {
    "address": "123 Main St",
    "city": "New York",
    "state": "NY",
    "zip_code": "10001",
    "coordinates": {
      "latitude": 40.7128,
      "longitude": -74.0060
    }
  }
}
```

**Response Schema:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "work_order_number": "WO-001",
  "title": "Equipment Maintenance",
  "description": "Regular maintenance of HVAC system",
  "status": "scheduled",
  "priority": "medium",
  "customer": {
    "id": 1,
    "email": "customer@example.com",
    "full_name": "John Customer"
  },
  "technician": {
    "id": 2,
    "email": "tech@example.com",
    "full_name": "Jane Technician"
  },
  "scheduled_date": "2024-01-15T09:00:00Z",
  "completed_date": null,
  "location": {
    "address": "123 Main St",
    "city": "New York",
    "state": "NY",
    "zip_code": "10001",
    "coordinates": {
      "latitude": 40.7128,
      "longitude": -74.0060
    }
  },
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Status Codes:**
- `200` - Success (GET)
- `201` - Work order created successfully (POST)
- `400` - Bad request
- `401` - Unauthorized

#### Technicians
```http
GET /api/v1/technicians/
POST /api/v1/technicians/
```

**Authentication:** Required (JWT)

**Request Body (POST):**
```json
{
  "user": 2,
  "specializations": ["HVAC", "Electrical"],
  "certifications": ["HVAC License", "Electrical License"],
  "availability": {
    "monday": {"start": "09:00", "end": "17:00"},
    "tuesday": {"start": "09:00", "end": "17:00"},
    "wednesday": {"start": "09:00", "end": "17:00"},
    "thursday": {"start": "09:00", "end": "17:00"},
    "friday": {"start": "09:00", "end": "17:00"}
  }
}
```

**Response Schema:**
```json
{
  "id": 1,
  "user": {
    "id": 2,
    "email": "tech@example.com",
    "full_name": "Jane Technician"
  },
  "specializations": ["HVAC", "Electrical"],
  "certifications": ["HVAC License", "Electrical License"],
  "availability": {
    "monday": {"start": "09:00", "end": "17:00"},
    "tuesday": {"start": "09:00", "end": "17:00"},
    "wednesday": {"start": "09:00", "end": "17:00"},
    "thursday": {"start": "09:00", "end": "17:00"},
    "friday": {"start": "09:00", "end": "17:00"}
  },
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Status Codes:**
- `200` - Success
- `201` - Technician created successfully
- `400` - Bad request
- `401` - Unauthorized

---

## Feature-Specific Endpoints

### 1. AI/ML Features

#### Ticket Categorization
```http
POST /api/v1/ai-ml/categorize-ticket/
```

**Authentication:** Required (JWT)

**Request Body:**
```json
{
  "ticket_id": "123e4567-e89b-12d3-a456-426614174000",
  "subject": "Login Issue",
  "description": "Cannot login to the system"
}
```

**Response Schema:**
```json
{
  "category": "Authentication",
  "confidence": 0.95,
  "suggested_tags": ["login", "authentication", "password"],
  "priority_suggestion": "high"
}
```

**Status Codes:**
- `200` - Categorization successful
- `400` - Bad request
- `401` - Unauthorized

#### Sentiment Analysis
```http
POST /api/v1/ai-ml/analyze-sentiment/
```

**Authentication:** Required (JWT)

**Request Body:**
```json
{
  "text": "I'm very frustrated with this issue. It's been going on for days!"
}
```

**Response Schema:**
```json
{
  "sentiment": "negative",
  "confidence": 0.87,
  "emotions": {
    "frustration": 0.8,
    "anger": 0.6,
    "disappointment": 0.4
  }
}
```

**Status Codes:**
- `200` - Analysis successful
- `400` - Bad request
- `401` - Unauthorized

### 2. Advanced Analytics

#### Real-time Analytics
```http
GET /api/v1/advanced-analytics/realtime/
```

**Authentication:** Required (JWT)

**Response Schema:**
```json
{
  "ticket_metrics": {
    "total_tickets": 150,
    "open_tickets": 25,
    "resolved_today": 10,
    "average_resolution_time": "2.5 hours"
  },
  "performance_metrics": {
    "response_time": "1.2s",
    "uptime": "99.9%",
    "error_rate": "0.1%"
  },
  "user_activity": {
    "active_users": 45,
    "new_registrations": 5,
    "login_attempts": 120
  }
}
```

**Status Codes:**
- `200` - Success
- `401` - Unauthorized

#### Custom Reports
```http
GET /api/v1/advanced-analytics/reports/
POST /api/v1/advanced-analytics/reports/
```

**Authentication:** Required (JWT)

**Request Body (POST):**
```json
{
  "name": "Monthly Ticket Report",
  "description": "Monthly ticket statistics",
  "filters": {
    "date_range": {
      "start": "2024-01-01",
      "end": "2024-01-31"
    },
    "status": ["resolved", "closed"]
  },
  "metrics": ["total_tickets", "resolution_time", "sla_compliance"]
}
```

**Response Schema:**
```json
{
  "id": 1,
  "name": "Monthly Ticket Report",
  "description": "Monthly ticket statistics",
  "filters": {
    "date_range": {
      "start": "2024-01-01",
      "end": "2024-01-31"
    },
    "status": ["resolved", "closed"]
  },
  "metrics": ["total_tickets", "resolution_time", "sla_compliance"],
  "data": {
    "total_tickets": 150,
    "resolution_time": "2.5 days",
    "sla_compliance": 95.5
  },
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Status Codes:**
- `200` - Success
- `201` - Report created successfully
- `400` - Bad request
- `401` - Unauthorized

### 3. Mobile & IoT

#### Mobile Apps
```http
GET /api/v1/mobile-iot/mobile-apps/
POST /api/v1/mobile-iot/mobile-apps/
```

**Authentication:** Required (JWT)

**Request Body (POST):**
```json
{
  "name": "Helpdesk Mobile App",
  "platform_type": "react_native",
  "app_configuration": {
    "version": "1.0.0",
    "build_number": 100,
    "features": ["tickets", "notifications", "offline_sync"]
  },
  "offline_capabilities": {
    "enabled": true,
    "sync_interval": 300,
    "data_retention": 7
  }
}
```

**Response Schema:**
```json
{
  "id": 1,
  "name": "Helpdesk Mobile App",
  "platform_type": "react_native",
  "app_configuration": {
    "version": "1.0.0",
    "build_number": 100,
    "features": ["tickets", "notifications", "offline_sync"]
  },
  "offline_capabilities": {
    "enabled": true,
    "sync_interval": 300,
    "data_retention": 7
  },
  "push_notifications": {
    "enabled": true,
    "fcm_key": "AAAA...",
    "apns_certificate": "certificate.p12"
  },
  "total_users": 150,
  "active_users": 120,
  "app_downloads": 500,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Status Codes:**
- `200` - Success
- `201` - Mobile app created successfully
- `400` - Bad request
- `401` - Unauthorized

#### IoT Devices
```http
GET /api/v1/mobile-iot/iot-devices/
POST /api/v1/mobile-iot/iot-devices/
```

**Authentication:** Required (JWT)

**Request Body (POST):**
```json
{
  "name": "Temperature Sensor",
  "device_type": "sensor",
  "model": "TempSense-100",
  "serial_number": "TS-001-2024",
  "location": {
    "building": "Building A",
    "floor": "1st Floor",
    "room": "Server Room",
    "coordinates": {
      "latitude": 40.7128,
      "longitude": -74.0060
    }
  },
  "configuration": {
    "measurement_interval": 60,
    "alert_thresholds": {
      "temperature": {
        "min": 18,
        "max": 25
      }
    }
  }
}
```

**Response Schema:**
```json
{
  "id": 1,
  "name": "Temperature Sensor",
  "device_type": "sensor",
  "model": "TempSense-100",
  "serial_number": "TS-001-2024",
  "location": {
    "building": "Building A",
    "floor": "1st Floor",
    "room": "Server Room",
    "coordinates": {
      "latitude": 40.7128,
      "longitude": -74.0060
    }
  },
  "configuration": {
    "measurement_interval": 60,
    "alert_thresholds": {
      "temperature": {
        "min": 18,
        "max": 25
      }
    }
  },
  "status": "online",
  "last_seen": "2024-01-01T12:00:00Z",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

**Status Codes:**
- `200` - Success
- `201` - IoT device created successfully
- `400` - Bad request
- `401` - Unauthorized

### 4. Advanced Security

#### Security Incidents
```http
GET /api/v1/advanced-security/security-incidents/
POST /api/v1/advanced-security/security-incidents/
```

**Authentication:** Required (JWT)

**Request Body (POST):**
```json
{
  "title": "Suspicious Login Attempt",
  "description": "Multiple failed login attempts from unknown IP",
  "severity": "medium",
  "incident_type": "authentication",
  "affected_systems": ["authentication", "user_management"],
  "source_ip": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "affected_users": [1, 2, 3]
}
```

**Response Schema:**
```json
{
  "id": 1,
  "title": "Suspicious Login Attempt",
  "description": "Multiple failed login attempts from unknown IP",
  "severity": "medium",
  "incident_type": "authentication",
  "status": "open",
  "affected_systems": ["authentication", "user_management"],
  "source_ip": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "affected_users": [
    {
      "id": 1,
      "email": "user1@example.com",
      "full_name": "User One"
    }
  ],
  "assigned_to": null,
  "resolved_at": null,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Status Codes:**
- `200` - Success
- `201` - Security incident created successfully
- `400` - Bad request
- `401` - Unauthorized

#### Security Audits
```http
GET /api/v1/advanced-security/security-audits/
POST /api/v1/advanced-security/security-audits/
```

**Authentication:** Required (JWT)

**Request Body (POST):**
```json
{
  "audit_type": "compliance",
  "scope": "organization",
  "standards": ["ISO27001", "SOC2"],
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "auditor": "Security Team"
}
```

**Response Schema:**
```json
{
  "id": 1,
  "audit_type": "compliance",
  "scope": "organization",
  "standards": ["ISO27001", "SOC2"],
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "auditor": "Security Team",
  "status": "in_progress",
  "findings": [],
  "recommendations": [],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Status Codes:**
- `200` - Success
- `201` - Security audit created successfully
- `400` - Bad request
- `401` - Unauthorized

### 5. Advanced Workflow

#### Workflow Automation
```http
GET /api/v1/advanced-workflow/automations/
POST /api/v1/advanced-workflow/automations/
```

**Authentication:** Required (JWT)

**Request Body (POST):**
```json
{
  "name": "Ticket Auto-Assignment",
  "description": "Automatically assign tickets based on category",
  "trigger": {
    "type": "ticket_created",
    "conditions": {
      "category": "technical_support"
    }
  },
  "actions": [
    {
      "type": "assign_agent",
      "parameters": {
        "agent_id": 2
      }
    },
    {
      "type": "send_notification",
      "parameters": {
        "template": "ticket_assigned",
        "recipients": ["agent", "customer"]
      }
    }
  ],
  "is_active": true
}
```

**Response Schema:**
```json
{
  "id": 1,
  "name": "Ticket Auto-Assignment",
  "description": "Automatically assign tickets based on category",
  "trigger": {
    "type": "ticket_created",
    "conditions": {
      "category": "technical_support"
    }
  },
  "actions": [
    {
      "type": "assign_agent",
      "parameters": {
        "agent_id": 2
      }
    },
    {
      "type": "send_notification",
      "parameters": {
        "template": "ticket_assigned",
        "recipients": ["agent", "customer"]
      }
    }
  ],
  "is_active": true,
  "execution_count": 25,
  "last_executed": "2024-01-01T12:00:00Z",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Status Codes:**
- `200` - Success
- `201` - Workflow automation created successfully
- `400` - Bad request
- `401` - Unauthorized

### 6. Advanced Communication

#### Communication Sessions
```http
GET /api/v1/advanced-communication/communication-sessions/
POST /api/v1/advanced-communication/communication-sessions/
```

**Authentication:** Required (JWT)

**Request Body (POST):**
```json
{
  "session_type": "video_call",
  "participants": [1, 2, 3],
  "scheduled_time": "2024-01-15T14:00:00Z",
  "duration": 60,
  "meeting_room": "Conference Room A",
  "agenda": "Discuss ticket resolution strategy"
}
```

**Response Schema:**
```json
{
  "id": 1,
  "session_type": "video_call",
  "participants": [
    {
      "id": 1,
      "email": "user1@example.com",
      "full_name": "User One"
    }
  ],
  "scheduled_time": "2024-01-15T14:00:00Z",
  "duration": 60,
  "meeting_room": "Conference Room A",
  "agenda": "Discuss ticket resolution strategy",
  "status": "scheduled",
  "meeting_link": "https://meet.helpdesk.com/abc123",
  "recording_url": null,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Status Codes:**
- `200` - Success
- `201` - Communication session created successfully
- `400` - Bad request
- `401` - Unauthorized

---

## Advanced Enterprise Endpoints

### 1. Integration Platform

#### API Integrations
```http
GET /api/v1/integration-platform/api-integrations/
POST /api/v1/integration-platform/api-integrations/
```

**Authentication:** Required (JWT)

**Request Body (POST):**
```json
{
  "name": "Salesforce Integration",
  "api_type": "rest",
  "base_url": "https://api.salesforce.com",
  "version": "v1",
  "authentication_methods": ["oauth2", "api_key"],
  "rate_limits": {
    "requests_per_minute": 1000,
    "requests_per_day": 100000
  },
  "api_documentation": {
    "swagger_url": "https://api.salesforce.com/docs",
    "version": "1.0.0"
  }
}
```

**Response Schema:**
```json
{
  "id": 1,
  "name": "Salesforce Integration",
  "api_type": "rest",
  "base_url": "https://api.salesforce.com",
  "version": "v1",
  "authentication_methods": ["oauth2", "api_key"],
  "rate_limits": {
    "requests_per_minute": 1000,
    "requests_per_day": 100000
  },
  "api_documentation": {
    "swagger_url": "https://api.salesforce.com/docs",
    "version": "1.0.0"
  },
  "total_requests": 0,
  "successful_requests": 0,
  "failed_requests": 0,
  "average_response_time": 0,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Status Codes:**
- `200` - Success
- `201` - API integration created successfully
- `400` - Bad request
- `401` - Unauthorized

#### Webhooks
```http
GET /api/v1/integration-platform/webhooks/
POST /api/v1/integration-platform/webhooks/
```

**Authentication:** Required (JWT)

**Request Body (POST):**
```json
{
  "name": "Ticket Created Webhook",
  "url": "https://external-system.com/webhook",
  "events": ["ticket.created", "ticket.updated"],
  "secret": "webhook_secret_key",
  "is_active": true
}
```

**Response Schema:**
```json
{
  "id": 1,
  "name": "Ticket Created Webhook",
  "url": "https://external-system.com/webhook",
  "events": ["ticket.created", "ticket.updated"],
  "secret": "webhook_secret_key",
  "is_active": true,
  "delivery_count": 0,
  "success_count": 0,
  "failure_count": 0,
  "last_delivery": null,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Status Codes:**
- `200` - Success
- `201` - Webhook created successfully
- `400` - Bad request
- `401` - Unauthorized

### 2. Customer Experience

#### Customer Feedback
```http
GET /api/v1/customer-experience/feedback/
POST /api/v1/customer-experience/feedback/
```

**Authentication:** Required (JWT)

**Request Body (POST):**
```json
{
  "ticket_id": "123e4567-e89b-12d3-a456-426614174000",
  "rating": 5,
  "feedback": "Excellent service! The issue was resolved quickly.",
  "categories": ["response_time", "solution_quality"],
  "is_public": true
}
```

**Response Schema:**
```json
{
  "id": 1,
  "ticket": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "ticket_number": "TKT-001",
    "subject": "Login Issue"
  },
  "customer": {
    "id": 1,
    "email": "customer@example.com",
    "full_name": "John Customer"
  },
  "rating": 5,
  "feedback": "Excellent service! The issue was resolved quickly.",
  "categories": ["response_time", "solution_quality"],
  "is_public": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Status Codes:**
- `200` - Success
- `201` - Feedback created successfully
- `400` - Bad request
- `401` - Unauthorized

#### Customer Journey
```http
GET /api/v1/customer-experience/journey/{customer_id}/
```

**Authentication:** Required (JWT)

**Response Schema:**
```json
{
  "customer_id": 1,
  "journey_stages": [
    {
      "stage": "awareness",
      "timestamp": "2024-01-01T00:00:00Z",
      "touchpoints": [
        {
          "type": "website_visit",
          "timestamp": "2024-01-01T00:00:00Z",
          "details": "Visited pricing page"
        }
      ]
    },
    {
      "stage": "consideration",
      "timestamp": "2024-01-02T00:00:00Z",
      "touchpoints": [
        {
          "type": "demo_request",
          "timestamp": "2024-01-02T00:00:00Z",
          "details": "Requested product demo"
        }
      ]
    },
    {
      "stage": "purchase",
      "timestamp": "2024-01-03T00:00:00Z",
      "touchpoints": [
        {
          "type": "subscription_created",
          "timestamp": "2024-01-03T00:00:00Z",
          "details": "Created enterprise subscription"
        }
      ]
    }
  ],
  "total_touchpoints": 5,
  "journey_duration": "2 days",
  "conversion_rate": 1.0
}
```

**Status Codes:**
- `200` - Success
- `401` - Unauthorized
- `404` - Customer not found

---

## Response Schemas

### Standard Response Format

#### Success Response
```json
{
  "data": {
    // Response data here
  },
  "meta": {
    "timestamp": "2024-01-01T00:00:00Z",
    "version": "v1",
    "request_id": "req_123456789"
  }
}
```

#### Paginated Response
```json
{
  "count": 100,
  "next": "http://api.helpdesk.com/api/v1/tickets/?page=2",
  "previous": null,
  "results": [
    // Array of items
  ],
  "meta": {
    "timestamp": "2024-01-01T00:00:00Z",
    "version": "v1",
    "request_id": "req_123456789"
  }
}
```

#### Error Response
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": {
      "field": "email",
      "message": "Invalid email format"
    }
  },
  "meta": {
    "timestamp": "2024-01-01T00:00:00Z",
    "version": "v1",
    "request_id": "req_123456789"
  }
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Description | Usage |
|------|-------------|-------|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 405 | Method Not Allowed | HTTP method not supported |
| 409 | Conflict | Resource already exists |
| 422 | Unprocessable Entity | Validation errors |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

### Error Response Format

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "field_name",
      "message": "Specific field error message"
    },
    "timestamp": "2024-01-01T00:00:00Z",
    "request_id": "req_123456789"
  }
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Request validation failed |
| `AUTHENTICATION_REQUIRED` | Authentication required |
| `INSUFFICIENT_PERMISSIONS` | Insufficient permissions |
| `RESOURCE_NOT_FOUND` | Resource not found |
| `RESOURCE_ALREADY_EXISTS` | Resource already exists |
| `RATE_LIMIT_EXCEEDED` | Rate limit exceeded |
| `INTERNAL_SERVER_ERROR` | Internal server error |

---

## Rate Limiting

### Rate Limits

| Endpoint Category | Rate Limit | Window |
|------------------|------------|--------|
| Authentication | 10 requests | 1 minute |
| General API | 1000 requests | 1 hour |
| File Upload | 100 requests | 1 hour |
| Webhooks | 500 requests | 1 hour |

### Rate Limit Headers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

### Rate Limit Exceeded Response

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again later.",
    "details": {
      "limit": 1000,
      "remaining": 0,
      "reset_time": "2024-01-01T01:00:00Z"
    }
  }
}
```

---

## Examples

### Complete API Workflow Example

#### 1. User Registration
```bash
curl -X POST https://api.helpdesk.com/api/v1/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "securepassword123",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890"
  }'
```

#### 2. User Login
```bash
curl -X POST https://api.helpdesk.com/api/v1/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

#### 3. Create Ticket
```bash
curl -X POST https://api.helpdesk.com/api/v1/tickets/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Login Issue",
    "description": "Cannot login to the system",
    "priority": "high",
    "tags": ["login", "authentication"]
  }'
```

#### 4. Get Tickets
```bash
curl -X GET "https://api.helpdesk.com/api/v1/tickets/?status=open&priority=high" \
  -H "Authorization: Bearer <access_token>"
```

#### 5. Add Comment to Ticket
```bash
curl -X POST https://api.helpdesk.com/api/v1/tickets/123e4567-e89b-12d3-a456-426614174000/comments/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Working on this issue. Will update soon.",
    "is_internal": false
  }'
```

### Advanced Feature Examples

#### AI-Powered Ticket Categorization
```bash
curl -X POST https://api.helpdesk.com/api/v1/ai-ml/categorize-ticket/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": "123e4567-e89b-12d3-a456-426614174000",
    "subject": "Password Reset Issue",
    "description": "I cannot reset my password using the forgot password link"
  }'
```

#### Real-time Analytics
```bash
curl -X GET https://api.helpdesk.com/api/v1/advanced-analytics/realtime/ \
  -H "Authorization: Bearer <access_token>"
```

#### Mobile App Configuration
```bash
curl -X POST https://api.helpdesk.com/api/v1/mobile-iot/mobile-apps/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Helpdesk Mobile",
    "platform_type": "react_native",
    "app_configuration": {
      "version": "1.0.0",
      "features": ["tickets", "notifications", "offline_sync"]
    }
  }'
```

---

## API Testing

### Postman Collection
A complete Postman collection is available for testing all API endpoints:
- Import the collection from: `docs/postman/helpdesk-api.json`
- Environment variables for different environments
- Pre-configured authentication headers
- Example requests for all endpoints

### API Documentation
Interactive API documentation is available at:
- Development: `http://localhost:8000/api/docs/`
- Production: `https://api.helpdesk.com/api/docs/`

### SDK Libraries
Official SDK libraries are available for:
- **Python**: `pip install helpdesk-sdk`
- **JavaScript**: `npm install @helpdesk/sdk`
- **PHP**: `composer require helpdesk/sdk`
- **Java**: Available in Maven Central

---

## Support and Resources

### API Support
- **Documentation**: https://docs.helpdesk.com/api/
- **Status Page**: https://status.helpdesk.com/
- **Support Email**: api-support@helpdesk.com
- **Community Forum**: https://community.helpdesk.com/

### Rate Limits and Quotas
- **Free Tier**: 1,000 requests/month
- **Basic Tier**: 10,000 requests/month
- **Professional Tier**: 100,000 requests/month
- **Enterprise Tier**: Unlimited requests

### Changelog
API changes and updates are documented in the changelog:
- **Changelog**: https://docs.helpdesk.com/api/changelog/
- **Deprecation Policy**: 6 months notice for breaking changes
- **Version Support**: Current and previous major versions

---

*This documentation is maintained by the API team and updated with each release.*

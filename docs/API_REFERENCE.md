# 🔌 **API Endpoint Reference**

**Version:** 1.0.0  
**Last Updated:** October 13, 2025

## 📋 **Table of Contents**

- [API Overview](#api-overview)
- [Authentication](#authentication)
- [Base URLs](#base-urls)
- [Common Patterns](#common-patterns)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Endpoints by Category](#endpoints-by-category)
- [Request/Response Examples](#requestresponse-examples)
- [SDK Examples](#sdk-examples)
- [Testing](#testing)

---

## 🎯 **API Overview**

The Helpdesk Platform API is a RESTful API built with Django REST Framework, providing comprehensive endpoints for all platform functionality. The API follows REST principles and provides consistent, predictable interfaces.

### **API Characteristics**
- **RESTful Design**: Follows REST architectural principles
- **JSON Format**: All requests and responses use JSON
- **HTTPS Only**: All API calls must use HTTPS in production
- **Versioned**: API versioning for backward compatibility
- **Documented**: Complete OpenAPI/Swagger documentation
- **Rate Limited**: Built-in rate limiting for API protection

### **API Versions**
- **v1**: Current stable version (recommended)
- **v2**: Next major version (in development)

---

## 🔐 **Authentication**

### **Authentication Methods**

#### **1. JWT Token Authentication**
```http
Authorization: Bearer <jwt_token>
```

#### **2. API Key Authentication**
```http
X-API-Key: <api_key>
```

#### **3. Session Authentication**
```http
Cookie: sessionid=<session_id>
```

### **Token Management**

#### **Login Endpoint**
```http
POST /api/v1/auth/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "remember_me": true
}
```

#### **Token Refresh**
```http
POST /api/v1/auth/refresh/
Content-Type: application/json

{
  "refresh_token": "<refresh_token>"
}
```

#### **Logout**
```http
POST /api/v1/auth/logout/
Authorization: Bearer <jwt_token>
```

---

## 🌐 **Base URLs**

### **Environment-Specific URLs**

| Environment | Base URL | Description |
|-------------|----------|-------------|
| **Development** | `http://localhost:8000/api/v1/` | Local development |
| **Staging** | `https://staging-api.helpdesk.com/api/v1/` | Staging environment |
| **Production** | `https://api.helpdesk.com/api/v1/` | Production environment |

### **API Documentation**
- **Swagger UI**: `{base_url}/docs/`
- **ReDoc**: `{base_url}/redoc/`
- **OpenAPI Schema**: `{base_url}/schema/`

---

## 🔄 **Common Patterns**

### **Pagination**
All list endpoints support pagination with the following parameters:

```http
GET /api/v1/tickets/?page=1&page_size=20&ordering=-created_at
```

**Response Format:**
```json
{
  "count": 150,
  "next": "https://api.helpdesk.com/api/v1/tickets/?page=2",
  "previous": null,
  "results": [...]
}
```

### **Filtering**
Most endpoints support filtering with query parameters:

```http
GET /api/v1/tickets/?status=open&priority=high&assigned_to=123
```

### **Search**
Full-text search across relevant fields:

```http
GET /api/v1/tickets/?search=urgent database issue
```

### **Ordering**
Sort results by one or more fields:

```http
GET /api/v1/tickets/?ordering=-created_at,priority
```

---

## ❌ **Error Handling**

### **HTTP Status Codes**

| Code | Description | Usage |
|------|-------------|-------|
| **200** | OK | Successful GET, PUT, PATCH |
| **201** | Created | Successful POST |
| **204** | No Content | Successful DELETE |
| **400** | Bad Request | Invalid request data |
| **401** | Unauthorized | Authentication required |
| **403** | Forbidden | Insufficient permissions |
| **404** | Not Found | Resource not found |
| **405** | Method Not Allowed | HTTP method not supported |
| **429** | Too Many Requests | Rate limit exceeded |
| **500** | Internal Server Error | Server error |

### **Error Response Format**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field_name": ["This field is required."],
      "email": ["Enter a valid email address."]
    },
    "timestamp": "2025-10-13T10:30:00Z",
    "request_id": "req_123456789"
  }
}
```

### **Common Error Codes**

| Code | Description | Resolution |
|------|-------------|------------|
| `VALIDATION_ERROR` | Invalid input data | Check request format and required fields |
| `AUTHENTICATION_REQUIRED` | Missing or invalid authentication | Provide valid JWT token or API key |
| `PERMISSION_DENIED` | Insufficient permissions | Check user roles and permissions |
| `RESOURCE_NOT_FOUND` | Requested resource doesn't exist | Verify resource ID and organization access |
| `RATE_LIMIT_EXCEEDED` | Too many requests | Wait before making additional requests |

---

## ⚡ **Rate Limiting**

### **Rate Limits by Endpoint Type**

| Endpoint Type | Limit | Window |
|---------------|-------|--------|
| **Authentication** | 5 requests | 1 minute |
| **Read Operations** | 1000 requests | 1 hour |
| **Write Operations** | 100 requests | 1 hour |
| **Search Operations** | 200 requests | 1 hour |
| **File Upload** | 50 requests | 1 hour |

### **Rate Limit Headers**
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

### **Rate Limit Exceeded Response**
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again later.",
    "retry_after": 3600
  }
}
```

---

## 📚 **Endpoints by Category**

### **🔐 Authentication Endpoints**

#### **POST** `/api/v1/auth/login/`
**Description**: Authenticate user and return JWT tokens

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "remember_me": false
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_agent": true,
    "is_customer": false,
    "is_technician": false
  },
  "expires_in": 3600
}
```

#### **POST** `/api/v1/auth/refresh/`
**Description**: Refresh JWT access token

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### **POST** `/api/v1/auth/logout/`
**Description**: Logout user and invalidate tokens

#### **POST** `/api/v1/auth/register/`
**Description**: Register new user account

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "password": "password123",
  "first_name": "Jane",
  "last_name": "Smith",
  "organization_slug": "acme-corp"
}
```

#### **POST** `/api/v1/auth/forgot-password/`
**Description**: Request password reset

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

#### **POST** `/api/v1/auth/reset-password/`
**Description**: Reset password with token

**Request Body:**
```json
{
  "token": "reset_token_here",
  "new_password": "newpassword123"
}
```

### **👥 User Management Endpoints**

#### **GET** `/api/v1/users/`
**Description**: List users in organization

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20)
- `search`: Search by name or email
- `role`: Filter by role (agent, customer, technician)
- `is_active`: Filter by active status

**Response:**
```json
{
  "count": 50,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "is_agent": true,
      "is_customer": false,
      "is_technician": false,
      "last_active_at": "2025-10-13T10:30:00Z",
      "created_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

#### **GET** `/api/v1/users/{id}/`
**Description**: Get specific user details

#### **PUT** `/api/v1/users/{id}/`
**Description**: Update user information

#### **PATCH** `/api/v1/users/{id}/`
**Description**: Partially update user information

#### **DELETE** `/api/v1/users/{id}/`
**Description**: Delete user account

### **🎫 Ticket Management Endpoints**

#### **GET** `/api/v1/tickets/`
**Description**: List tickets with filtering and pagination

**Query Parameters:**
- `status`: Filter by status (open, in_progress, pending, resolved, closed)
- `priority`: Filter by priority (low, medium, high, urgent, critical)
- `category_id`: Filter by category
- `assigned_to_id`: Filter by assigned user
- `created_by_id`: Filter by creator
- `search`: Full-text search
- `created_after`: Filter by creation date
- `created_before`: Filter by creation date

**Response:**
```json
{
  "count": 150,
  "next": "https://api.helpdesk.com/api/v1/tickets/?page=2",
  "previous": null,
  "results": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "Database connection issue",
      "description": "Users are experiencing slow database queries",
      "status": "open",
      "priority": "high",
      "category": {
        "id": "cat_123",
        "name": "Technical Issues",
        "color": "#ff6b6b"
      },
      "assigned_to": {
        "id": "user_123",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com"
      },
      "created_by": {
        "id": "user_456",
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane@example.com"
      },
      "due_date": "2025-10-15T17:00:00Z",
      "sla_status": {
        "status": "on_track",
        "due_date": "2025-10-15T17:00:00Z",
        "time_remaining_minutes": 1440
      },
      "tags": ["database", "performance"],
      "created_at": "2025-10-13T10:30:00Z",
      "updated_at": "2025-10-13T10:30:00Z"
    }
  ]
}
```

#### **POST** `/api/v1/tickets/`
**Description**: Create new ticket

**Request Body:**
```json
{
  "title": "Database connection issue",
  "description": "Users are experiencing slow database queries",
  "priority": "high",
  "category_id": "cat_123",
  "tags": ["database", "performance"],
  "custom_fields": {
    "severity": "critical",
    "environment": "production"
  }
}
```

#### **GET** `/api/v1/tickets/{id}/`
**Description**: Get specific ticket details

#### **PUT** `/api/v1/tickets/{id}/`
**Description**: Update entire ticket

#### **PATCH** `/api/v1/tickets/{id}/`
**Description**: Partially update ticket

#### **DELETE** `/api/v1/tickets/{id}/`
**Description**: Delete ticket

#### **POST** `/api/v1/tickets/{id}/comments/`
**Description**: Add comment to ticket

**Request Body:**
```json
{
  "content": "I've identified the issue. It's related to connection pooling.",
  "is_internal": false,
  "mentions": ["user_123", "user_456"]
}
```

#### **GET** `/api/v1/tickets/{id}/comments/`
**Description**: List ticket comments

#### **POST** `/api/v1/tickets/{id}/attachments/`
**Description**: Upload attachment to ticket

**Request Body:** (multipart/form-data)
```
file: [binary file data]
description: "Screenshot of the error"
```

### **🔧 Field Service Endpoints**

#### **GET** `/api/v1/work-orders/`
**Description**: List work orders

**Query Parameters:**
- `status`: Filter by status (scheduled, in_progress, completed, cancelled, on_hold)
- `priority`: Filter by priority (low, medium, high, urgent)
- `customer_id`: Filter by customer
- `assigned_technician_id`: Filter by technician
- `scheduled_after`: Filter by scheduled date
- `scheduled_before`: Filter by scheduled date

#### **POST** `/api/v1/work-orders/`
**Description**: Create new work order

**Request Body:**
```json
{
  "title": "Server maintenance",
  "description": "Monthly server maintenance and updates",
  "priority": "medium",
  "customer_id": "cust_123",
  "location_id": "loc_456",
  "scheduled_at": "2025-10-15T09:00:00Z",
  "estimated_duration": 120,
  "tasks": [
    {
      "title": "Update software",
      "description": "Install latest security patches",
      "estimated_duration": 60
    },
    {
      "title": "Check hardware",
      "description": "Verify all hardware components",
      "estimated_duration": 60
    }
  ],
  "materials": [
    {
      "name": "Cable ties",
      "quantity": 10,
      "unit": "pieces",
      "cost": 5.99
    }
  ]
}
```

#### **GET** `/api/v1/work-orders/{id}/`
**Description**: Get specific work order details

#### **PUT** `/api/v1/work-orders/{id}/`
**Description**: Update work order

#### **PATCH** `/api/v1/work-orders/{id}/`
**Description**: Partially update work order

#### **DELETE** `/api/v1/work-orders/{id}/`
**Description**: Delete work order

#### **POST** `/api/v1/work-orders/{id}/tasks/`
**Description**: Add task to work order

#### **GET** `/api/v1/work-orders/{id}/tasks/`
**Description**: List work order tasks

#### **POST** `/api/v1/work-orders/{id}/materials/`
**Description**: Add material to work order

#### **GET** `/api/v1/work-orders/{id}/materials/`
**Description**: List work order materials

### **📚 Knowledge Base Endpoints**

#### **GET** `/api/v1/knowledge-base/articles/`
**Description**: List knowledge base articles

**Query Parameters:**
- `category_id`: Filter by category
- `status`: Filter by status (draft, published, archived)
- `search`: Full-text search
- `author_id`: Filter by author
- `tags`: Filter by tags

#### **POST** `/api/v1/knowledge-base/articles/`
**Description**: Create new article

**Request Body:**
```json
{
  "title": "How to reset your password",
  "content": "To reset your password, follow these steps...",
  "summary": "Step-by-step guide for password reset",
  "category_id": "cat_123",
  "tags": ["password", "security", "help"],
  "status": "published",
  "seo_title": "Password Reset Guide",
  "seo_description": "Learn how to reset your password",
  "seo_keywords": "password, reset, security"
}
```

#### **GET** `/api/v1/knowledge-base/articles/{id}/`
**Description**: Get specific article

#### **PUT** `/api/v1/knowledge-base/articles/{id}/`
**Description**: Update article

#### **PATCH** `/api/v1/knowledge-base/articles/{id}/`
**Description**: Partially update article

#### **DELETE** `/api/v1/knowledge-base/articles/{id}/`
**Description**: Delete article

#### **POST** `/api/v1/knowledge-base/articles/{id}/vote/`
**Description**: Vote on article helpfulness

**Request Body:**
```json
{
  "helpful": true
}
```

#### **GET** `/api/v1/knowledge-base/categories/`
**Description**: List knowledge base categories

#### **POST** `/api/v1/knowledge-base/categories/`
**Description**: Create new category

### **📊 Analytics Endpoints**

#### **GET** `/api/v1/analytics/dashboard/`
**Description**: Get analytics dashboard data

**Query Parameters:**
- `date_range`: Date range for analytics (7d, 30d, 90d, 1y)
- `metrics`: Specific metrics to include
- `filters`: Additional filters

#### **GET** `/api/v1/analytics/tickets/`
**Description**: Get ticket analytics

#### **GET** `/api/v1/analytics/work-orders/`
**Description**: Get work order analytics

#### **GET** `/api/v1/analytics/users/`
**Description**: Get user analytics

#### **GET** `/api/v1/analytics/performance/`
**Description**: Get system performance metrics

### **🔔 Notification Endpoints**

#### **GET** `/api/v1/notifications/`
**Description**: List user notifications

**Query Parameters:**
- `type`: Filter by notification type
- `priority`: Filter by priority
- `is_read`: Filter by read status
- `created_after`: Filter by creation date

#### **POST** `/api/v1/notifications/{id}/read/`
**Description**: Mark notification as read

#### **POST** `/api/v1/notifications/mark-all-read/`
**Description**: Mark all notifications as read

#### **DELETE** `/api/v1/notifications/{id}/`
**Description**: Delete notification

### **📁 File Upload Endpoints**

#### **POST** `/api/v1/files/upload/`
**Description**: Upload file

**Request Body:** (multipart/form-data)
```
file: [binary file data]
category: "attachments"
description: "File description"
```

#### **GET** `/api/v1/files/{id}/`
**Description**: Get file details

#### **DELETE** `/api/v1/files/{id}/`
**Description**: Delete file

---

## 💡 **Request/Response Examples**

### **Creating a Ticket**

#### **Request:**
```http
POST /api/v1/tickets/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Content-Type: application/json

{
  "title": "Server is down",
  "description": "The production server is not responding to requests",
  "priority": "urgent",
  "category_id": "cat_123",
  "tags": ["server", "production", "critical"]
}
```

#### **Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Server is down",
  "description": "The production server is not responding to requests",
  "status": "open",
  "priority": "urgent",
  "category": {
    "id": "cat_123",
    "name": "Technical Issues",
    "color": "#ff6b6b"
  },
  "assigned_to": null,
  "created_by": {
    "id": "user_123",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com"
  },
  "due_date": "2025-10-13T16:30:00Z",
  "sla_status": {
    "status": "on_track",
    "due_date": "2025-10-13T16:30:00Z",
    "time_remaining_minutes": 360
  },
  "tags": ["server", "production", "critical"],
  "attachments": [],
  "comments": [],
  "created_at": "2025-10-13T10:30:00Z",
  "updated_at": "2025-10-13T10:30:00Z"
}
```

### **Updating a Ticket**

#### **Request:**
```http
PATCH /api/v1/tickets/123e4567-e89b-12d3-a456-426614174000/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Content-Type: application/json

{
  "status": "in_progress",
  "assigned_to_id": "user_456",
  "priority": "critical"
}
```

#### **Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Server is down",
  "description": "The production server is not responding to requests",
  "status": "in_progress",
  "priority": "critical",
  "category": {
    "id": "cat_123",
    "name": "Technical Issues",
    "color": "#ff6b6b"
  },
  "assigned_to": {
    "id": "user_456",
    "first_name": "Jane",
    "last_name": "Smith",
    "email": "jane@example.com"
  },
  "created_by": {
    "id": "user_123",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com"
  },
  "due_date": "2025-10-13T16:30:00Z",
  "sla_status": {
    "status": "at_risk",
    "due_date": "2025-10-13T16:30:00Z",
    "time_remaining_minutes": 180
  },
  "tags": ["server", "production", "critical"],
  "attachments": [],
  "comments": [],
  "created_at": "2025-10-13T10:30:00Z",
  "updated_at": "2025-10-13T11:00:00Z"
}
```

---

## 🛠️ **SDK Examples**

### **JavaScript/Node.js**

#### **Installation:**
```bash
npm install @helpdesk-platform/sdk
```

#### **Basic Usage:**
```javascript
import { HelpdeskClient } from '@helpdesk-platform/sdk';

const client = new HelpdeskClient({
  baseUrl: 'https://api.helpdesk.com/api/v1',
  apiKey: 'your-api-key'
});

// Create a ticket
const ticket = await client.tickets.create({
  title: 'Server is down',
  description: 'The production server is not responding',
  priority: 'urgent',
  category_id: 'cat_123'
});

// List tickets
const tickets = await client.tickets.list({
  status: 'open',
  priority: 'high'
});

// Update a ticket
await client.tickets.update(ticket.id, {
  status: 'in_progress',
  assigned_to_id: 'user_456'
});
```

### **Python**

#### **Installation:**
```bash
pip install helpdesk-platform-sdk
```

#### **Basic Usage:**
```python
from helpdesk_platform import HelpdeskClient

client = HelpdeskClient(
    base_url='https://api.helpdesk.com/api/v1',
    api_key='your-api-key'
)

# Create a ticket
ticket = client.tickets.create({
    'title': 'Server is down',
    'description': 'The production server is not responding',
    'priority': 'urgent',
    'category_id': 'cat_123'
})

# List tickets
tickets = client.tickets.list(
    status='open',
    priority='high'
)

# Update a ticket
client.tickets.update(ticket.id, {
    'status': 'in_progress',
    'assigned_to_id': 'user_456'
})
```

### **cURL Examples**

#### **Create Ticket:**
```bash
curl -X POST https://api.helpdesk.com/api/v1/tickets/ \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Server is down",
    "description": "The production server is not responding",
    "priority": "urgent",
    "category_id": "cat_123"
  }'
```

#### **List Tickets:**
```bash
curl -X GET "https://api.helpdesk.com/api/v1/tickets/?status=open&priority=high" \
  -H "Authorization: Bearer your-jwt-token"
```

#### **Update Ticket:**
```bash
curl -X PATCH https://api.helpdesk.com/api/v1/tickets/123e4567-e89b-12d3-a456-426614174000/ \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress",
    "assigned_to_id": "user_456"
  }'
```

---

## 🧪 **Testing**

### **API Testing Tools**

#### **1. Postman Collection**
- Import the provided Postman collection
- Set up environment variables
- Run automated tests

#### **2. Insomnia**
- Import the API schema
- Create test requests
- Validate responses

#### **3. curl**
- Use the provided curl examples
- Test individual endpoints
- Validate authentication

### **Test Data**

#### **Sample Users:**
```json
{
  "admin": {
    "email": "admin@example.com",
    "password": "admin123",
    "role": "admin"
  },
  "agent": {
    "email": "agent@example.com",
    "password": "agent123",
    "role": "agent"
  },
  "customer": {
    "email": "customer@example.com",
    "password": "customer123",
    "role": "customer"
  }
}
```

#### **Sample Organizations:**
```json
{
  "acme-corp": {
    "name": "ACME Corporation",
    "slug": "acme-corp",
    "domain": "acme.com"
  },
  "tech-startup": {
    "name": "Tech Startup Inc",
    "slug": "tech-startup",
    "domain": "techstartup.com"
  }
}
```

### **Automated Testing**

#### **Unit Tests:**
```bash
# Run API unit tests
python manage.py test apps.api.tests

# Run with coverage
python manage.py test apps.api.tests --coverage
```

#### **Integration Tests:**
```bash
# Run integration tests
python manage.py test tests.integration

# Run specific test suite
python manage.py test tests.integration.test_tickets
```

#### **Load Tests:**
```bash
# Run load tests
python manage.py test tests.load

# Run with specific load
python manage.py test tests.load --load-level=high
```

---

## 📚 **Additional Resources**

### **Documentation Links**
- **OpenAPI Schema**: `/api/v1/schema/`
- **Swagger UI**: `/api/v1/docs/`
- **ReDoc**: `/api/v1/redoc/`
- **Postman Collection**: `/api/v1/postman/`

### **Support**
- **API Support**: api-support@helpdesk.com
- **Documentation Issues**: docs@helpdesk.com
- **Feature Requests**: features@helpdesk.com

### **Community**
- **GitHub Repository**: https://github.com/helpdesk-platform/api
- **Discord Community**: https://discord.gg/helpdesk-platform
- **Stack Overflow**: Tag: `helpdesk-platform`

---

**Last Updated**: October 13, 2025  
**Next Review**: November 13, 2025  
**Maintained By**: API Team

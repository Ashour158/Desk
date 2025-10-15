# API Documentation

This directory contains all API-related documentation, endpoint inventories, and API specifications.

## Contents

### API Reference
- **COMPREHENSIVE_API_DOCUMENTATION.md** - Complete API documentation
- **COMPREHENSIVE_API_ENDPOINT_INVENTORY.md** - Full endpoint inventory
- **API_ENDPOINT_INVENTORY.md** - API endpoint listing

### API Development
- **API_IMPROVEMENTS_IMPLEMENTATION_REPORT.md** - API improvements
- **API_VALIDATION_REPORT.md** - API validation results

## API Structure

### Authentication
- Token-based authentication
- JWT tokens
- OAuth2 support

### API Endpoints

#### Core APIs
- `/api/v1/tickets/` - Ticket management
- `/api/v1/users/` - User management
- `/api/v1/organizations/` - Organization management

#### Service APIs
- `/api/v1/field-service/` - Field service operations
- `/api/v1/knowledge-base/` - Knowledge base
- `/api/v1/analytics/` - Analytics and reporting

### API Versioning

The API uses URL-based versioning: `/api/v1/`, `/api/v2/`

### Rate Limiting

- Default: 100 requests per hour per user
- Authenticated: 1000 requests per hour
- Admin: Unlimited

## Quick Reference

### Making API Requests

```bash
# Get authentication token
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'

# Use token for requests
curl -X GET http://localhost:8000/api/v1/tickets/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Response Format

```json
{
  "status": "success",
  "data": {},
  "message": "Operation completed successfully"
}
```

## Documentation Tools

- **Swagger/OpenAPI**: Available at `/api/docs/`
- **Redoc**: Available at `/api/redoc/`
- **Postman Collections**: See `/postman_collections/`

## For More Information

1. [API Documentation](COMPREHENSIVE_API_DOCUMENTATION.md)
2. [API Endpoints](COMPREHENSIVE_API_ENDPOINT_INVENTORY.md)
3. Interactive docs at `/api/docs/` when server is running

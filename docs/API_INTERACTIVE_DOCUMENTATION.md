# 🔌 **Interactive API Documentation**

**Version:** 1.0.0  
**Last Updated:** October 13, 2025

---

## 📋 **Table of Contents**

- [Overview](#overview)
- [Accessing Documentation](#accessing-documentation)
- [Swagger UI](#swagger-ui)
- [ReDoc](#redoc)
- [OpenAPI Schema](#openapi-schema)
- [Authentication](#authentication)
- [Testing APIs](#testing-apis)
- [Customization](#customization)
- [Troubleshooting](#troubleshooting)

---

## 🎯 **Overview**

The Helpdesk Platform provides comprehensive interactive API documentation powered by OpenAPI 3.0 and Swagger UI. This documentation is automatically generated from your Django REST Framework code and provides:

- **Interactive API Explorer**: Test APIs directly from the browser
- **Request/Response Examples**: See exactly what to send and expect
- **Authentication Support**: Built-in JWT token authentication
- **Schema Validation**: Automatic request/response validation
- **Code Generation**: Generate client SDKs in multiple languages

---

## 🌐 **Accessing Documentation**

### **Development Environment**
- **Swagger UI**: http://localhost:8000/api/swagger/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

### **Production Environment**
- **Swagger UI**: https://api.helpdesk-platform.com/api/swagger/
- **ReDoc**: https://api.helpdesk-platform.com/api/redoc/
- **OpenAPI Schema**: https://api.helpdesk-platform.com/api/schema/

---

## 🎨 **Swagger UI**

### **Features**
- **Interactive Testing**: Test API endpoints directly
- **Authentication**: Built-in JWT token support
- **Request/Response Examples**: See real examples
- **Schema Validation**: Automatic validation
- **Code Generation**: Generate client code

### **Using Swagger UI**

#### **1. Authentication**
```bash
# Get JWT token
curl -X POST "http://localhost:8000/api/v1/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password"
  }'

# Use token in Swagger UI
# Click "Authorize" button
# Enter: Bearer <your-jwt-token>
```

#### **2. Testing Endpoints**
1. **Select Endpoint**: Click on any endpoint
2. **Try It Out**: Click "Try it out" button
3. **Fill Parameters**: Enter required parameters
4. **Execute**: Click "Execute" button
5. **View Response**: See response data and status

#### **3. Request Examples**
```json
# Create Ticket
{
  "subject": "Login Issue",
  "description": "Cannot login to the system",
  "priority": "high",
  "category": "technical"
}

# Create Work Order
{
  "title": "Equipment Installation",
  "description": "Install new server equipment",
  "customer": "uuid",
  "scheduled_start": "2024-01-01T09:00:00Z",
  "technician": "uuid"
}
```

---

## 📚 **ReDoc**

### **Features**
- **Clean Documentation**: Beautiful, readable documentation
- **Schema Details**: Detailed schema information
- **Examples**: Comprehensive examples
- **Search**: Built-in search functionality

### **Using ReDoc**

#### **1. Navigation**
- **Sidebar**: Navigate through endpoints
- **Search**: Use search box to find endpoints
- **Tags**: Filter by API tags

#### **2. Schema Information**
- **Request Schema**: Detailed request parameters
- **Response Schema**: Response structure
- **Data Types**: Field types and constraints
- **Examples**: Real-world examples

---

## 📄 **OpenAPI Schema**

### **Schema Features**
- **OpenAPI 3.0**: Latest OpenAPI specification
- **Complete Coverage**: All endpoints documented
- **Schema Validation**: Automatic validation
- **Code Generation**: Generate client SDKs

### **Using the Schema**

#### **1. Download Schema**
```bash
# Download OpenAPI schema
curl -o api-schema.json http://localhost:8000/api/schema/
```

#### **2. Generate Client SDKs**
```bash
# Generate Python client
openapi-generator generate -i api-schema.json -g python -o ./clients/python

# Generate JavaScript client
openapi-generator generate -i api-schema.json -g javascript -o ./clients/javascript

# Generate Java client
openapi-generator generate -i api-schema.json -g java -o ./clients/java
```

#### **3. Import into Tools**
- **Postman**: Import schema for API testing
- **Insomnia**: Import for API development
- **VS Code**: Use with REST Client extension

---

## 🔐 **Authentication**

### **JWT Token Authentication**

#### **1. Login to Get Token**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password"
  }'
```

#### **2. Use Token in Requests**
```bash
curl -X GET "http://localhost:8000/api/v1/tickets/" \
  -H "Authorization: Bearer <your-jwt-token>"
```

#### **3. Refresh Token**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/refresh/" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "<your-refresh-token>"
  }'
```

### **API Key Authentication**
```bash
curl -X GET "http://localhost:8000/api/v1/tickets/" \
  -H "X-API-Key: <your-api-key>"
```

---

## 🧪 **Testing APIs**

### **Using Swagger UI**

#### **1. Basic Testing**
1. **Open Swagger UI**: Navigate to `/api/swagger/`
2. **Authenticate**: Click "Authorize" and enter JWT token
3. **Select Endpoint**: Choose an endpoint to test
4. **Try It Out**: Click "Try it out" button
5. **Fill Parameters**: Enter required parameters
6. **Execute**: Click "Execute" button
7. **View Response**: Check response data and status

#### **2. Advanced Testing**
- **Multiple Requests**: Test multiple endpoints
- **Error Scenarios**: Test error conditions
- **Validation**: Test input validation
- **Authentication**: Test with different tokens

### **Using cURL**

#### **1. Authentication**
```bash
# Login
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password"
  }' | jq -r '.access')

# Use token
curl -X GET "http://localhost:8000/api/v1/tickets/" \
  -H "Authorization: Bearer $TOKEN"
```

#### **2. Create Resources**
```bash
# Create ticket
curl -X POST "http://localhost:8000/api/v1/tickets/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Test Ticket",
    "description": "This is a test ticket",
    "priority": "medium"
  }'
```

---

## 🎨 **Customization**

### **Swagger UI Customization**

#### **1. Theme Customization**
```python
# In settings.py
SPECTACULAR_SETTINGS = {
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
        'filter': True,
        'showExtensions': True,
        'showCommonExtensions': True,
        'tryItOutEnabled': True,
        'theme': {
            'colors': {
                'primary': {
                    'main': '#2E86AB'
                }
            }
        }
    }
}
```

#### **2. Logo and Branding**
```python
SPECTACULAR_SETTINGS = {
    'EXTENSIONS_INFO': {
        'x-logo': {
            'url': '/static/images/logo.png',
            'altText': 'Helpdesk Platform'
        }
    }
}
```

### **ReDoc Customization**

#### **1. Theme Customization**
```python
SPECTACULAR_SETTINGS = {
    'REDOC_UI_SETTINGS': {
        'theme': {
            'colors': {
                'primary': {
                    'main': '#2E86AB'
                }
            }
        }
    }
}
```

---

## 🛠️ **Troubleshooting**

### **Common Issues**

#### **1. Documentation Not Loading**
```bash
# Check if drf-spectacular is installed
pip list | grep drf-spectacular

# Install if missing
pip install drf-spectacular
```

#### **2. Authentication Issues**
```bash
# Check JWT token format
echo "Bearer <your-token>"

# Verify token is valid
curl -X GET "http://localhost:8000/api/v1/auth/me/" \
  -H "Authorization: Bearer <your-token>"
```

#### **3. Schema Generation Issues**
```bash
# Regenerate schema
python manage.py spectacular --file schema.yml

# Check for errors
python manage.py spectacular --validate
```

#### **4. CORS Issues**
```python
# In settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
```

### **Debug Mode**

#### **1. Enable Debug Mode**
```python
# In settings.py
SPECTACULAR_SETTINGS = {
    'SERVE_INCLUDE_SCHEMA': True,
    'SERVE_PERMISSIONS': ['rest_framework.permissions.AllowAny'],
}
```

#### **2. View Raw Schema**
```bash
# View raw OpenAPI schema
curl http://localhost:8000/api/schema/ | jq .
```

---

## 📊 **API Documentation Features**

### **Automatic Features**
- **Schema Generation**: Automatic from Django models
- **Request/Response Examples**: Generated from serializers
- **Validation**: Automatic request validation
- **Error Handling**: Standardized error responses

### **Manual Features**
- **Custom Examples**: Add custom examples
- **Documentation**: Add detailed descriptions
- **Tags**: Organize endpoints by functionality
- **Servers**: Configure multiple environments

### **Integration Features**
- **Postman**: Import schema for testing
- **Insomnia**: Import for development
- **VS Code**: Use with REST Client
- **Code Generation**: Generate client SDKs

---

## 🚀 **Best Practices**

### **API Design**
- **Consistent Naming**: Use consistent endpoint naming
- **HTTP Methods**: Use appropriate HTTP methods
- **Status Codes**: Return appropriate status codes
- **Error Handling**: Provide clear error messages

### **Documentation**
- **Descriptions**: Add clear descriptions
- **Examples**: Provide realistic examples
- **Tags**: Organize endpoints logically
- **Versioning**: Document API versions

### **Testing**
- **Test Coverage**: Test all endpoints
- **Error Scenarios**: Test error conditions
- **Authentication**: Test with different tokens
- **Validation**: Test input validation

---

## 📚 **Resources**

### **Documentation**
- [OpenAPI Specification](https://swagger.io/specification/)
- [Swagger UI Documentation](https://swagger.io/tools/swagger-ui/)
- [ReDoc Documentation](https://redoc.ly/)
- [DRF Spectacular Documentation](https://drf-spectacular.readthedocs.io/)

### **Tools**
- **OpenAPI Generator**: Generate client SDKs
- **Postman**: API testing and development
- **Insomnia**: API development
- **VS Code**: REST Client extension

### **Examples**
- **Python Client**: Generated Python SDK
- **JavaScript Client**: Generated JavaScript SDK
- **Java Client**: Generated Java SDK
- **cURL Examples**: Command-line examples

---

**Last Updated**: October 13, 2025  
**Next Review**: November 13, 2025  
**Maintained By**: Development Team

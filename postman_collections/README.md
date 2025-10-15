# 📮 **Postman Collections for Helpdesk Platform**

This directory contains Postman collections for testing the Helpdesk Platform API.

---

## 📋 **Available Collections**

### **1. Helpdesk Platform API**
- **File**: `Helpdesk_Platform_API.postman_collection.json`
- **Description**: Comprehensive API collection for all endpoints
- **Features**: 
  - Authentication with JWT tokens
  - Automatic token management
  - Environment variables
  - Test scripts
  - Response validation

---

## 🚀 **Getting Started**

### **1. Import Collection**

#### **Method 1: Import from File**
1. Open Postman
2. Click "Import" button
3. Select `Helpdesk_Platform_API.postman_collection.json`
4. Click "Import"

#### **Method 2: Import from URL**
1. Open Postman
2. Click "Import" button
3. Select "Link" tab
4. Enter collection URL (if hosted)
5. Click "Import"

### **2. Set Up Environment**

#### **Create Environment**
1. Click "Environments" in Postman
2. Click "Create Environment"
3. Name it "Helpdesk Platform - Development"
4. Add the following variables:

| Variable | Initial Value | Current Value |
|----------|---------------|---------------|
| `base_url` | `http://localhost:8000` | `http://localhost:8000` |
| `api_version` | `v1` | `v1` |
| `jwt_token` | `` | `` |
| `refresh_token` | `` | `` |
| `user_id` | `` | `` |
| `organization_id` | `` | `` |
| `ticket_id` | `` | `` |
| `work_order_id` | `` | `` |

#### **Production Environment**
For production testing, create another environment with:
- `base_url`: `https://api.helpdesk-platform.com`
- Other variables remain the same

### **3. Authentication Setup**

#### **Get JWT Token**
1. Select "Authentication" → "Login" request
2. Update the request body with your credentials:
   ```json
   {
     "email": "your-email@example.com",
     "password": "your-password"
   }
   ```
3. Send the request
4. The collection will automatically store the JWT token

#### **Token Management**
- The collection automatically handles token refresh
- Tokens are stored in collection variables
- All authenticated requests use the stored token

---

## 📚 **Collection Structure**

### **Authentication**
- **Login**: User authentication
- **Register**: User registration
- **Refresh Token**: Token refresh
- **Logout**: User logout
- **Get Current User**: Get user profile

### **Users**
- **List Users**: Get all users
- **Get User**: Get specific user
- **Update User**: Update user profile

### **Organizations**
- **List Organizations**: Get all organizations
- **Get Organization**: Get specific organization
- **Update Organization**: Update organization settings

### **Tickets**
- **List Tickets**: Get all tickets with filtering
- **Create Ticket**: Create new ticket
- **Get Ticket**: Get specific ticket
- **Update Ticket**: Update ticket
- **Assign Ticket**: Assign ticket to agent
- **Add Comment**: Add comment to ticket
- **Close Ticket**: Close ticket

### **Work Orders**
- **List Work Orders**: Get all work orders
- **Create Work Order**: Create new work order
- **Get Work Order**: Get specific work order
- **Update Work Order**: Update work order
- **Complete Work Order**: Complete work order

### **Knowledge Base**
- **List Articles**: Get all articles
- **Create Article**: Create new article
- **Get Article**: Get specific article
- **Rate Article**: Rate article

### **Analytics**
- **Get Dashboard Stats**: Get dashboard statistics
- **Get Ticket Analytics**: Get ticket analytics
- **Get Performance Metrics**: Get performance metrics

### **Notifications**
- **List Notifications**: Get all notifications
- **Mark as Read**: Mark notifications as read
- **Get Notification Settings**: Get notification settings
- **Update Notification Settings**: Update notification settings

### **Files**
- **Upload File**: Upload file
- **List Files**: Get all files
- **Download File**: Download file

### **Search**
- **Global Search**: Search across all content
- **Search Tickets**: Search tickets
- **Search Knowledge Base**: Search knowledge base

### **Health**
- **Health Check**: System health check
- **API Health**: API health check
- **Database Health**: Database health check
- **Redis Health**: Redis health check

---

## 🧪 **Testing Features**

### **Automatic Token Management**
The collection includes scripts that automatically:
- Store JWT tokens from login responses
- Use stored tokens in authenticated requests
- Handle token refresh when needed

### **Response Validation**
Each request includes tests that validate:
- Response time (should be < 5000ms)
- Content-Type header
- Response status codes
- Response structure

### **Environment Variables**
The collection uses environment variables for:
- Base URL configuration
- API version
- Authentication tokens
- Resource IDs (tickets, work orders, etc.)

---

## 🔧 **Customization**

### **Adding New Requests**
1. Right-click on a folder
2. Select "Add Request"
3. Configure the request:
   - Method (GET, POST, PUT, PATCH, DELETE)
   - URL with variables
   - Headers (Authorization, Content-Type)
   - Body (for POST/PUT/PATCH requests)
   - Tests (response validation)

### **Modifying Existing Requests**
1. Select the request
2. Update the configuration
3. Save changes
4. Test the request

### **Adding Tests**
Add JavaScript tests to validate responses:
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has required fields", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('id');
    pm.expect(jsonData).to.have.property('name');
});
```

---

## 📊 **Usage Examples**

### **1. Complete Ticket Workflow**
1. **Login** to get authentication token
2. **Create Ticket** with issue details
3. **Get Ticket** to verify creation
4. **Assign Ticket** to an agent
5. **Add Comment** to ticket
6. **Update Ticket** status
7. **Close Ticket** when resolved

### **2. Work Order Management**
1. **Login** to get authentication token
2. **Create Work Order** for field service
3. **Get Work Order** to verify creation
4. **Update Work Order** with progress
5. **Complete Work Order** with results

### **3. Knowledge Base Management**
1. **Login** to get authentication token
2. **Create Article** with helpful content
3. **Get Article** to verify creation
4. **Rate Article** for feedback
5. **Search Articles** for specific topics

---

## 🐛 **Troubleshooting**

### **Common Issues**

#### **Authentication Errors**
- **Problem**: 401 Unauthorized
- **Solution**: Run the Login request first to get a valid token

#### **Connection Errors**
- **Problem**: Connection refused
- **Solution**: Check if the API server is running on the correct port

#### **Variable Issues**
- **Problem**: Variables not updating
- **Solution**: Check environment selection and variable names

### **Debug Tips**

#### **Check Response**
- Look at the response body for error details
- Check the response headers for additional information
- Verify the request URL and parameters

#### **Check Environment**
- Ensure the correct environment is selected
- Verify environment variables are set correctly
- Check if variables are being used in requests

#### **Check Console**
- Open Postman Console (View → Show Postman Console)
- Look for JavaScript errors in test scripts
- Check network requests and responses

---

## 📚 **Additional Resources**

### **Documentation**
- [API Reference](../docs/API_REFERENCE.md)
- [Interactive API Documentation](../docs/API_INTERACTIVE_DOCUMENTATION.md)
- [Troubleshooting Guide](../docs/TROUBLESHOOTING.md)

### **Postman Resources**
- [Postman Learning Center](https://learning.postman.com/)
- [Postman Documentation](https://documenter.postman.com/)
- [Postman Community](https://community.postman.com/)

### **API Testing Best Practices**
- Test all HTTP methods (GET, POST, PUT, PATCH, DELETE)
- Test error scenarios (invalid data, missing fields)
- Test authentication and authorization
- Test response times and performance
- Test data validation and constraints

---

## 🤝 **Contributing**

### **Adding New Collections**
1. Create new collection file
2. Follow the existing structure
3. Include comprehensive documentation
4. Add test scripts for validation
5. Update this README

### **Improving Existing Collections**
1. Add more test cases
2. Improve error handling
3. Add more request examples
4. Update documentation
5. Optimize performance

---

**Last Updated**: October 13, 2025  
**Next Review**: November 13, 2025  
**Maintained By**: Development Team

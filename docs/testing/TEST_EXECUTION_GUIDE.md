# 🧪 **Comprehensive API Testing Execution Guide**

## Overview
This guide provides step-by-step instructions for testing all 107 API endpoints using Postman/Insomnia, verifying documentation, testing error scenarios, checking versioning, and validating rate limiting.

---

## 📋 **Prerequisites**

### Required Tools
- **Postman** or **Insomnia** (API testing clients)
- **Newman** (Postman CLI for automation)
- **Python 3.7+** (for custom test scripts)
- **Node.js** (for Newman)
- **curl** (for basic HTTP testing)

### Installation Commands
```bash
# Install Newman (Postman CLI)
npm install -g newman

# Install Python dependencies
pip install requests python-dateutil

# Install Node.js (if not already installed)
# Download from https://nodejs.org/
```

---

## 🚀 **Quick Start**

### 1. **Start the API Server**
```bash
# Navigate to the project directory
cd core

# Start Django development server
python manage.py runserver 0.0.0.0:8000

# Or start with specific settings
python manage.py runserver 0.0.0.0:8000 --settings=config.settings.development
```

### 2. **Run All Tests Automatically**
```bash
# Make the script executable (Linux/Mac)
chmod +x test_scripts/run_all_tests.sh

# Run comprehensive test suite
./test_scripts/run_all_tests.sh

# Or run on Windows
bash test_scripts/run_all_tests.sh
```

---

## 📮 **Postman/Insomnia Testing**

### 1. **Import Collections**
1. **Open Postman/Insomnia**
2. **Import Collection**: `postman_collections/API_Testing_Suite.postman_collection.json`
3. **Import Environment**: `postman_collections/API_Testing_Environment.postman_environment.json`

### 2. **Configure Environment Variables**
```json
{
  "base_url": "http://localhost:8000/api/v1",
  "auth_token": "",
  "organization_id": "",
  "user_id": "",
  "ticket_id": "",
  "test_email": "test@example.com",
  "test_password": "TestPassword123!"
}
```

### 3. **Run Collection Tests**
1. **Select the collection** in Postman/Insomnia
2. **Click "Run"** to execute all tests
3. **Review results** in the test runner interface

### 4. **Automated Testing with Newman**
```bash
# Run Postman collection with Newman
newman run postman_collections/API_Testing_Suite.postman_collection.json \
  --environment postman_collections/API_Testing_Environment.postman_environment.json \
  --reporters cli,html \
  --reporter-html-export test-results.html

# Run with specific options
newman run postman_collections/API_Testing_Suite.postman_collection.json \
  --environment postman_collections/API_Testing_Environment.postman_environment.json \
  --delay-request 1000 \
  --timeout-request 30000 \
  --reporters cli,json \
  --reporter-json-export test-results.json
```

---

## 🐍 **Python Test Scripts**

### 1. **Comprehensive API Testing**
```bash
# Run all API endpoint tests
python test_scripts/api_test_runner.py \
  --base-url http://localhost:8000/api/v1 \
  --email test@example.com \
  --password TestPassword123! \
  --output api_test_results.json

# Run with verbose output
python test_scripts/api_test_runner.py \
  --base-url http://localhost:8000/api/v1 \
  --verbose
```

### 2. **Security Testing**
```bash
# Run comprehensive security tests
python test_scripts/security_test.py \
  --base-url http://localhost:8000/api/v1 \
  --email test@example.com \
  --password TestPassword123! \
  --output security_test_results.json
```

### 3. **Rate Limiting Testing**
```bash
# Run rate limiting tests
python test_scripts/rate_limit_test.py \
  --base-url http://localhost:8000/api/v1 \
  --email test@example.com \
  --password TestPassword123! \
  --output rate_limit_test_results.json
```

---

## 🔍 **Manual Testing Procedures**

### 1. **API Documentation Verification**

#### **Check OpenAPI Schema**
```bash
# Test API schema endpoint
curl -X GET "http://localhost:8000/api/schema/" \
  -H "Accept: application/json"

# Expected: 200 OK with OpenAPI schema
```

#### **Check Swagger UI**
```bash
# Test Swagger UI endpoint
curl -X GET "http://localhost:8000/api/docs/" \
  -H "Accept: text/html"

# Expected: 200 OK with HTML content
```

### 2. **Error Scenario Testing**

#### **Invalid Input Testing**
```bash
# Test invalid email format
curl -X POST "http://localhost:8000/api/v1/auth/register/" \
  -H "Content-Type: application/json" \
  -d '{"email": "invalid-email", "password": "TestPassword123!", "first_name": "Test", "last_name": "User"}'

# Expected: 400 Bad Request with validation error
```

#### **Unauthorized Access Testing**
```bash
# Test without authentication token
curl -X GET "http://localhost:8000/api/v1/tickets/"

# Expected: 401 Unauthorized
```

#### **Non-existent Resource Testing**
```bash
# Test non-existent ticket
curl -X GET "http://localhost:8000/api/v1/tickets/999999/" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Expected: 404 Not Found
```

### 3. **API Versioning Testing**

#### **Version Header Testing**
```bash
# Test API version 1
curl -X GET "http://localhost:8000/api/v1/tickets/" \
  -H "Accept: application/vnd.api.v1+json" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Test API version 2
curl -X GET "http://localhost:8000/api/v1/tickets/" \
  -H "Accept: application/vnd.api.v2+json" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### **URL Versioning Testing**
```bash
# Test versioned URL
curl -X GET "http://localhost:8000/api/v2/tickets/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. **Rate Limiting Testing**

#### **General API Rate Limiting**
```bash
# Make multiple requests to test rate limiting
for i in {1..20}; do
  curl -X GET "http://localhost:8000/api/v1/tickets/" \
    -H "Authorization: Bearer YOUR_TOKEN" \
    -w "Request $i: %{http_code} - %{time_total}s\n"
  sleep 0.1
done

# Expected: Some requests should return 429 Too Many Requests
```

#### **Authentication Rate Limiting**
```bash
# Test login rate limiting
for i in {1..15}; do
  curl -X POST "http://localhost:8000/api/v1/auth/login/" \
    -H "Content-Type: application/json" \
    -d '{"email": "test@example.com", "password": "wrong_password"}' \
    -w "Login attempt $i: %{http_code}\n"
  sleep 0.1
done

# Expected: Some attempts should return 429 Too Many Requests
```

---

## 🔒 **Security Testing**

### 1. **SQL Injection Testing**
```bash
# Test SQL injection in search parameter
curl -X GET "http://localhost:8000/api/v1/tickets/?search=' OR 1=1 --" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Expected: 400 Bad Request or 403 Forbidden
```

### 2. **XSS Attack Testing**
```bash
# Test XSS in ticket creation
curl -X POST "http://localhost:8000/api/v1/tickets/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"subject": "<script>alert(\"XSS\")</script>", "description": "Test ticket"}'

# Expected: 400 Bad Request or 403 Forbidden
```

### 3. **File Upload Security Testing**
```bash
# Test malicious file upload
curl -X POST "http://localhost:8000/api/v1/tickets/1/attachments/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@malicious.exe" \
  -F "description=Test file"

# Expected: 400 Bad Request with security error
```

---

## 📊 **Test Results Analysis**

### 1. **View Test Results**
```bash
# View API test results
cat test_results/api_test_results_*.json | jq '.'

# View security test results
cat test_results/security_test_results_*.json | jq '.'

# View rate limiting results
cat test_results/rate_limit_test_results_*.json | jq '.'
```

### 2. **Generate Test Reports**
```bash
# Generate HTML report from Newman
newman run postman_collections/API_Testing_Suite.postman_collection.json \
  --environment postman_collections/API_Testing_Environment.postman_environment.json \
  --reporters html \
  --reporter-html-export test-report.html

# Open the report in browser
open test-report.html
```

### 3. **Performance Analysis**
```bash
# Analyze response times
python -c "
import json
with open('test_results/api_test_results_*.json', 'r') as f:
    data = json.load(f)
    response_times = [r['response_time'] for r in data['test_results'] if r['response_time'] > 0]
    print(f'Average response time: {sum(response_times)/len(response_times):.2f}s')
    print(f'Max response time: {max(response_times):.2f}s')
    print(f'Min response time: {min(response_times):.2f}s')
"
```

---

## 🚨 **Troubleshooting**

### 1. **Common Issues**

#### **Authentication Failures**
```bash
# Check if user exists
curl -X POST "http://localhost:8000/api/v1/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "TestPassword123!"}'

# If user doesn't exist, create one
curl -X POST "http://localhost:8000/api/v1/auth/register/" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "TestPassword123!", "first_name": "Test", "last_name": "User"}'
```

#### **Rate Limiting Issues**
```bash
# Check rate limit headers
curl -X GET "http://localhost:8000/api/v1/tickets/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -v

# Look for headers:
# X-RateLimit-Limit: 1000
# X-RateLimit-Remaining: 999
# X-RateLimit-Reset: 2024-01-01T12:00:00Z
```

#### **CORS Issues**
```bash
# Check CORS headers
curl -X OPTIONS "http://localhost:8000/api/v1/tickets/" \
  -H "Origin: http://localhost:3000" \
  -v

# Expected headers:
# Access-Control-Allow-Origin: http://localhost:3000
# Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
# Access-Control-Allow-Headers: Authorization, Content-Type
```

### 2. **Debug Mode**
```bash
# Run tests with debug output
python test_scripts/api_test_runner.py \
  --base-url http://localhost:8000/api/v1 \
  --verbose \
  --debug

# Check server logs
tail -f core/logs/django.log
```

---

## 📈 **Continuous Integration**

### 1. **GitHub Actions**
```yaml
name: API Testing
on: [push, pull_request]

jobs:
  api-testing:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        npm install -g newman
    - name: Start server
      run: |
        python manage.py runserver &
        sleep 10
    - name: Run API tests
      run: |
        python test_scripts/api_test_runner.py \
          --base-url http://localhost:8000/api/v1 \
          --output test-results.json
    - name: Run security tests
      run: |
        python test_scripts/security_test.py \
          --base-url http://localhost:8000/api/v1 \
          --output security-results.json
    - name: Upload results
      uses: actions/upload-artifact@v2
      with:
        name: test-results
        path: test-results.json
```

### 2. **Jenkins Pipeline**
```groovy
pipeline {
    agent any
    stages {
        stage('Setup') {
            steps {
                sh 'pip install -r requirements.txt'
                sh 'npm install -g newman'
            }
        }
        stage('Start Server') {
            steps {
                sh 'python manage.py runserver &'
                sh 'sleep 10'
            }
        }
        stage('API Testing') {
            steps {
                sh 'python test_scripts/api_test_runner.py --base-url http://localhost:8000/api/v1'
            }
        }
        stage('Security Testing') {
            steps {
                sh 'python test_scripts/security_test.py --base-url http://localhost:8000/api/v1'
            }
        }
        stage('Rate Limiting Testing') {
            steps {
                sh 'python test_scripts/rate_limit_test.py --base-url http://localhost:8000/api/v1'
            }
        }
    }
    post {
        always {
            sh 'pkill -f "python manage.py runserver"'
        }
    }
}
```

---

## 📋 **Test Checklist**

### ✅ **Pre-Testing Checklist**
- [ ] API server is running on `http://localhost:8000`
- [ ] Database is accessible and migrated
- [ ] Test user account exists
- [ ] Required tools are installed (Postman, Newman, Python)
- [ ] Environment variables are configured

### ✅ **Testing Checklist**
- [ ] All 107 endpoints are tested
- [ ] Authentication flows work correctly
- [ ] Error scenarios return proper status codes
- [ ] Rate limiting is enforced
- [ ] Security measures block malicious requests
- [ ] API documentation is accessible
- [ ] Versioning works correctly
- [ ] Performance is within acceptable limits

### ✅ **Post-Testing Checklist**
- [ ] All test results are saved
- [ ] Test reports are generated
- [ ] Failed tests are documented
- [ ] Performance metrics are analyzed
- [ ] Security vulnerabilities are reported
- [ ] Recommendations are provided

---

## 🎯 **Success Criteria**

### **API Testing Success Metrics**
- **Endpoint Coverage**: 100% (107/107 endpoints tested)
- **Success Rate**: ≥ 95%
- **Response Time**: ≤ 500ms average
- **Error Handling**: Proper status codes for all scenarios
- **Security**: No critical vulnerabilities
- **Documentation**: All endpoints documented
- **Versioning**: Multiple API versions supported
- **Rate Limiting**: Properly enforced

### **Test Result Interpretation**
- **✅ PASS**: All tests passed, API is production-ready
- **⚠️ PARTIAL PASS**: Some issues found, review and fix
- **❌ FAIL**: Multiple issues found, significant work needed

---

## 📞 **Support and Resources**

### **Documentation**
- [API Documentation Suite](API_TESTING_SUITE.md)
- [Postman Collection](postman_collections/API_Testing_Suite.postman_collection.json)
- [Test Scripts](test_scripts/)

### **Tools and Resources**
- [Postman Documentation](https://learning.postman.com/)
- [Newman Documentation](https://github.com/postmanlabs/newman)
- [Python Requests Library](https://docs.python-requests.org/)

### **Getting Help**
- Check server logs: `tail -f core/logs/django.log`
- Verify API status: `curl http://localhost:8000/api/v1/health/`
- Test connectivity: `ping localhost`

---

**🎉 Happy Testing! This comprehensive testing suite ensures your API is robust, secure, and production-ready.**

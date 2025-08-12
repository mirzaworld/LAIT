# LAIT API Documentation

## 📋 Overview

This directory contains comprehensive API documentation for the LAIT Legal Intelligence Platform, including:

- **OpenAPI/Swagger Documentation**: Interactive API docs at `/api/docs`
- **Postman Collection**: Ready-to-use API testing collection
- **Authentication Examples**: Complete auth flow demonstrations

## 🔗 Access Documentation

### Interactive Swagger UI
Once the backend is running, access the interactive documentation at:

```
http://localhost:5003/api/docs
```

**Features:**
- 📖 Complete endpoint documentation
- 🧪 Interactive testing interface  
- 🔒 Built-in authentication support
- 📊 Request/response examples
- 📝 Schema definitions

### OpenAPI Specification
Get the raw OpenAPI 3.0 JSON specification:

```
http://localhost:5003/api/openapi.json
```

### Production Documentation
When deployed to production:

```
https://lait-api.onrender.com/api/docs
https://lait-api.onrender.com/api/openapi.json
```

## 📦 Postman Collection

### Import Collection
1. Open Postman
2. Click **Import** → **Upload Files**
3. Select `docs/postman_collection.json`
4. Collection will be imported with all endpoints and examples

### Collection Features
- ✅ **Complete API Coverage**: All endpoints included
- 🔄 **Auto Token Management**: Tokens automatically saved after login
- 📝 **Pre-configured Examples**: Ready-to-use request bodies
- 🔗 **Environment Variables**: Easy switching between dev/prod
- 📋 **Test Scripts**: Automatic response validation

### Quick Start with Postman
1. **Set Base URL**: Update `baseUrl` variable to your API endpoint
   - Development: `http://localhost:5003`
   - Production: `https://lait-api.onrender.com`

2. **Register/Login**: Run authentication requests first
   - Tokens are automatically saved to collection variables
   - No manual token copying required

3. **Test Endpoints**: All subsequent requests will include auth automatically

## 🔐 Authentication Flow

### 1. Register New User
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe",
  "company": "Legal Corp"
}
```

**Response:**
- `access_token`: Short-lived (15 minutes)
- `refresh_token`: Long-lived (7 days)
- `expires_in`: Token expiry in seconds

### 2. Login Existing User
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

### 3. Refresh Access Token
```http
POST /api/auth/refresh
Content-Type: application/json

{
  "refresh_token": "your_refresh_token_here"
}
```

### 4. Access Protected Endpoints
```http
GET /api/invoices
Authorization: Bearer your_access_token_here
```

## 📁 File Upload Examples

### Upload PDF Invoice
```http
POST /api/invoices/upload
Authorization: Bearer your_access_token
Content-Type: multipart/form-data

file: [select PDF file]
vendor: "Acme Legal Services" (optional)
```

### Upload Structured JSON
```http
POST /api/invoices/upload
Authorization: Bearer your_access_token
Content-Type: application/json

{
  "vendor": "Legal Associates LLC",
  "amount": 2500.00,
  "line_items": [
    {
      "description": "Legal research",
      "amount": 1200.00,
      "rate": 350.00,
      "hours": 3.43
    }
  ]
}
```

## 🛡️ Security & Rate Limits

### Rate Limiting
- **General API**: 200 requests/hour
- **Login**: 5 attempts/minute
- **Upload**: 30/minute per user + 5/minute per token
- **Token Refresh**: 10/minute

### File Upload Limits
- **Max Size**: 10MB
- **Supported Types**: PDF, TXT, CSV
- **Magic Number Validation**: File content verified
- **Security**: Extension + content validation

### Authentication Security
- **bcrypt**: Password hashing with salt
- **JWT**: Short-lived access tokens (15 min)
- **Token Pairs**: Access + refresh token system
- **CORS**: Restricted to configured origins
- **Logging**: Security events logged (data masked)

## 🧪 Testing Locally

### 1. Start Backend
```bash
cd backend
source venv_real/bin/activate
python app_real.py
```

### 2. Access Documentation
- Open browser: http://localhost:5003/api/docs
- Interactive testing available immediately

### 3. Test with Postman
- Import collection from `docs/postman_collection.json`
- Set `baseUrl` to `http://localhost:5003`
- Run "Register User" or "Login User" first
- Test any endpoint with auto-authentication

### 4. Verify OpenAPI Spec
```bash
curl http://localhost:5003/api/openapi.json | jq
```

## 📊 API Endpoints Summary

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user profile

### Invoice Management
- `POST /api/invoices/upload` - Upload invoice (file or JSON)
- `GET /api/invoices` - List user invoices
- `GET /api/invoices/{id}` - Get invoice details

### Dashboard
- `GET /api/dashboard/metrics` - Get dashboard analytics

### System
- `GET /api/health` - Health check
- `GET /api/ml/status` - ML service status
- `GET /api/docs` - Swagger UI documentation
- `GET /api/openapi.json` - OpenAPI specification

## 🔧 Customization

### Adding New Endpoints
1. Add route with OpenAPI docstring:
```python
@app.route('/api/new-endpoint', methods=['POST'])
@jwt_required
def new_endpoint():
    \"\"\"New endpoint description
    ---
    post:
      tags:
        - NewFeature
      summary: Brief description
      # ... OpenAPI spec
    \"\"\"
    # Implementation
```

2. Add Marshmallow schema if needed:
```python
class NewSchema(Schema):
    field = fields.Str(description="Field description")

spec.components.schema("NewSchema", schema=NewSchema)
```

3. Update Postman collection with new request

### Production Deployment
- Documentation automatically available at your production URL
- Update Postman collection `baseUrl` variable
- All rate limits and security features active

---

**Documentation Version**: 1.0.0  
**Last Updated**: August 12, 2025  
**Compatible**: LAIT Platform v1.0.0

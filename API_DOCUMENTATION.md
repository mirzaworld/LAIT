# LAIT Legal Intelligence Platform - API Documentation

## Overview

The LAIT (Legal AI Technology) platform provides a comprehensive API for legal intelligence, invoice analysis, vendor management, and analytics. This documentation covers all available endpoints, authentication, and usage examples.

**Base URL:** `http://localhost:5003`  
**API Version:** v1.0  
**Authentication:** JWT Bearer Token

---

## Table of Contents

1. [Authentication](#authentication)
2. [Health & Status](#health--status)
3. [Legal Intelligence API](#legal-intelligence-api)
4. [Analytics API](#analytics-api)
5. [Vendor Management API](#vendor-management-api)
6. [Invoice Management API](#invoice-management-api)
7. [ML Models API](#ml-models-api)
8. [Admin API](#admin-api)
9. [Error Handling](#error-handling)
10. [Rate Limiting](#rate-limiting)

---

## Authentication

### JWT Authentication

All protected endpoints require a valid JWT token in the Authorization header:

```http
Authorization: Bearer <your-jwt-token>
```

### Login

**POST** `/api/auth/login`

Authenticate user and receive JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "user"
  }
}
```

### Register

**POST** `/api/auth/register`

Register a new user account.

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "password": "password123",
  "first_name": "Jane",
  "last_name": "Smith"
}
```

---

## Health & Status

### Health Check

**GET** `/api/health`

Check system health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-06-22T21:30:00Z"
}
```

### ML Models Status

**GET** `/api/ml/status`

Get status of all ML models.

**Response:**
```json
{
  "models": {
    "enhanced_invoice_analyzer": true,
    "invoice_analyzer": true,
    "matter_analyzer": true,
    "risk_predictor": true,
    "vendor_analyzer": true
  },
  "import_errors": {},
  "init_errors": {}
}
```

---

## Legal Intelligence API

### Test Legal Intelligence

**GET** `/api/legal-intelligence/test`

Test legal intelligence service connectivity.

**Response:**
```json
{
  "status": "success",
  "message": "Legal Intelligence API is working",
  "services": {
    "courtlistener": "available",
    "attorney_verification": "active",
    "case_research": "active",
    "precedent_search": "active"
  },
  "timestamp": "2025-06-22T21:30:00Z"
}
```

### Verify Attorney

**POST** `/api/legal-intelligence/verify-attorney`

Verify attorney credentials using multiple sources.

**Request Body:**
```json
{
  "attorney_name": "John Smith",
  "law_firm": "Smith & Associates",
  "bar_number": "12345",
  "state": "CA"
}
```

**Response:**
```json
{
  "verified": true,
  "attorney_name": "John Smith",
  "law_firm": "Smith & Associates",
  "bar_number": "12345",
  "state": "CA",
  "verification_sources": ["CourtListener API", "Bar Database"],
  "confidence": "high",
  "verification_date": "2025-06-22T21:30:00Z"
}
```

### Search Cases

**POST** `/api/legal-intelligence/search-cases`

Search for legal cases and precedents.

**Request Body:**
```json
{
  "query": "contract dispute",
  "court": "federal",
  "limit": 10
}
```

**Response:**
```json
{
  "cases": [
    {
      "id": "case_123",
      "title": "Smith v. Johnson",
      "court": "Federal District Court",
      "date": "2024-01-15",
      "summary": "Contract dispute regarding...",
      "citations": ["123 F.3d 456", "456 U.S. 789"]
    }
  ],
  "total_results": 150,
  "search_time": 0.5
}
```

---

## Analytics API

### Dashboard Metrics

**GET** `/api/analytics/dashboard/metrics`

Get comprehensive dashboard metrics.

**Response:**
```json
{
  "totalSpend": 2500000,
  "invoiceCount": 150,
  "vendorCount": 25,
  "averageRiskScore": 35,
  "spendChange": 12.5,
  "recentInvoices": [
    {
      "id": 1,
      "vendor": "Law Firm A",
      "amount": 50000,
      "date": "2024-01-15",
      "status": "approved",
      "riskScore": 25
    }
  ],
  "topVendors": [
    {
      "name": "Top Law Firm",
      "totalSpend": 500000
    }
  ]
}
```

### Analytics Summary

**GET** `/api/analytics/summary`

Get detailed analytics summary with date range filtering.

**Query Parameters:**
- `date_from` (optional): Start date (YYYY-MM-DD)
- `date_to` (optional): End date (YYYY-MM-DD)

**Response:**
```json
{
  "total_spend": 2500000,
  "invoice_count": 150,
  "spend_change_pct": 12.5,
  "active_matters_count": 47,
  "risk_factors_count": 23,
  "high_risk_invoices_count": 8,
  "avg_processing_time": 3.2,
  "monthly_spend": [
    {
      "period": "2024-01",
      "amount": 250000
    }
  ]
}
```

### Vendor Analytics

**GET** `/api/analytics/vendors`

Get vendor performance analytics.

**Response:**
```json
{
  "vendors": [
    {
      "id": 1,
      "name": "Law Firm A",
      "total_spend": 500000,
      "invoice_count": 25,
      "avg_rate": 450,
      "performance_score": 85,
      "risk_score": 30
    }
  ]
}
```

---

## Vendor Management API

### List Vendors

**GET** `/api/vendors`

Get all vendors with analytics.

**Response:**
```json
{
  "vendors": [
    {
      "id": 1,
      "name": "Law Firm A",
      "category": "AmLaw 100",
      "spend": 500000,
      "matter_count": 15,
      "avg_rate": 450,
      "performance_score": 85,
      "diversity_score": 75,
      "on_time_rate": 95
    }
  ]
}
```

### Search Vendors

**GET** `/api/vendors/search`

Search vendors with filters.

**Query Parameters:**
- `name` (optional): Vendor name
- `practice_area` (optional): Practice area
- `firm_size` (optional): Firm size category
- `location` (optional): Location
- `min_performance_score` (optional): Minimum performance score

**Response:**
```json
{
  "vendors": [...],
  "total": 25,
  "page": 1,
  "per_page": 50
}
```

### Vendor Analytics Summary

**GET** `/api/vendors/analytics/summary`

Get vendor analytics summary.

**Response:**
```json
{
  "total_vendors": 25,
  "total_spend": 2500000,
  "avg_performance_score": 82,
  "top_performers": [...],
  "risk_vendors": [...]
}
```

---

## Invoice Management API

### List Invoices

**GET** `/api/invoices`

Get all invoices.

**Response:**
```json
[
  {
    "id": 1,
    "vendor_name": "Law Firm A",
    "invoice_number": "INV-2024-001",
    "date": "2024-01-15",
    "total_amount": 50000,
    "overspend_risk": 25,
    "processed": true
  }
]
```

### Get Invoice Details

**GET** `/api/invoices/{invoice_id}`

Get detailed invoice information.

**Response:**
```json
{
  "id": 1,
  "vendor_name": "Law Firm A",
  "invoice_number": "INV-2024-001",
  "date": "2024-01-15",
  "total_amount": 50000,
  "overspend_risk": 25,
  "processed": true,
  "pdf_url": "https://...",
  "lines": [
    {
      "id": 1,
      "description": "Legal research",
      "hours": 10,
      "rate": 450,
      "line_total": 4500,
      "is_flagged": false
    }
  ]
}
```

### Upload Invoice

**POST** `/api/upload-invoice`

Upload and analyze a new invoice.

**Request Body:** Multipart form data
- `file`: PDF invoice file
- `vendor` (optional): Vendor name
- `amount` (optional): Invoice amount
- `date` (optional): Invoice date

**Response:**
```json
{
  "success": true,
  "invoice_id": "INV-2024-002",
  "invoice_added": true,
  "invoice_data": {
    "vendor": "Law Firm B",
    "amount": 35000,
    "date": "2024-01-16",
    "invoice_number": "INV-2024-002"
  },
  "analysis": {
    "risk_score": 35,
    "risk_level": "medium",
    "recommendations": [
      "Review billing rates for compliance"
    ]
  }
}
```

---

## ML Models API

### Model Status

**GET** `/api/ml/status`

Get status of all ML models.

### Model Inference

**POST** `/api/ml/analyze-invoice`

Analyze invoice using ML models.

**Request Body:**
```json
{
  "invoice_data": {
    "vendor": "Law Firm A",
    "amount": 50000,
    "line_items": [...]
  }
}
```

**Response:**
```json
{
  "risk_score": 35,
  "anomalies": [],
  "recommendations": [...],
  "confidence": 0.85
}
```

---

## Admin API

### Get Settings

**GET** `/api/admin/settings`

Get application settings (Admin only).

**Response:**
```json
{
  "anomaly_threshold": 0.8,
  "high_risk_threshold": 7,
  "hourly_rate_threshold": 1.2,
  "notifications_enabled": true,
  "auto_retrain_enabled": true
}
```

### Update Settings

**PUT** `/api/admin/settings`

Update application settings (Admin only).

**Request Body:**
```json
{
  "anomaly_threshold": 0.85,
  "high_risk_threshold": 8
}
```

### Audit Logs

**GET** `/api/admin/audit-logs`

Get system audit logs (Admin only).

**Query Parameters:**
- `offset` (optional): Pagination offset
- `limit` (optional): Number of logs to return
- `action` (optional): Filter by action type
- `user_id` (optional): Filter by user ID

**Response:**
```json
{
  "logs": [
    {
      "id": 1,
      "user_id": 1,
      "username": "admin@example.com",
      "action": "LOGIN",
      "details": "User login successful",
      "timestamp": "2025-06-22T21:30:00Z"
    }
  ],
  "pagination": {
    "total": 100,
    "offset": 0,
    "limit": 50
  }
}
```

---

## Error Handling

### Error Response Format

All API errors follow a consistent format:

```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {
    "field": "Additional error details"
  }
}
```

### Common HTTP Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

### Example Error Responses

**Authentication Error (401):**
```json
{
  "error": "Missing Authorization Header",
  "code": "AUTH_REQUIRED"
}
```

**Validation Error (422):**
```json
{
  "error": "Validation failed",
  "code": "VALIDATION_ERROR",
  "details": {
    "email": "Invalid email format",
    "password": "Password must be at least 8 characters"
  }
}
```

---

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **General endpoints:** 100 requests per minute
- **Authentication endpoints:** 10 requests per minute
- **ML model endpoints:** 50 requests per minute

Rate limit headers are included in responses:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642876800
```

When rate limit is exceeded:

```json
{
  "error": "Rate limit exceeded",
  "code": "RATE_LIMIT_EXCEEDED",
  "retry_after": 60
}
```

---

## SDK Examples

### Python SDK Example

```python
import requests

class LAITClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {'Authorization': f'Bearer {token}'}
    
    def get_dashboard_metrics(self):
        response = requests.get(
            f"{self.base_url}/api/analytics/dashboard/metrics",
            headers=self.headers
        )
        return response.json()
    
    def verify_attorney(self, attorney_data):
        response = requests.post(
            f"{self.base_url}/api/legal-intelligence/verify-attorney",
            json=attorney_data,
            headers=self.headers
        )
        return response.json()

# Usage
client = LAITClient("http://localhost:5003", "your-jwt-token")
metrics = client.get_dashboard_metrics()
```

### JavaScript SDK Example

```javascript
class LAITClient {
    constructor(baseUrl, token) {
        this.baseUrl = baseUrl;
        this.headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
    }
    
    async getDashboardMetrics() {
        const response = await fetch(
            `${this.baseUrl}/api/analytics/dashboard/metrics`,
            { headers: this.headers }
        );
        return response.json();
    }
    
    async verifyAttorney(attorneyData) {
        const response = await fetch(
            `${this.baseUrl}/api/legal-intelligence/verify-attorney`,
            {
                method: 'POST',
                headers: this.headers,
                body: JSON.stringify(attorneyData)
            }
        );
        return response.json();
    }
}

// Usage
const client = new LAITClient('http://localhost:5003', 'your-jwt-token');
const metrics = await client.getDashboardMetrics();
```

---

## Support

For API support and questions:

- **Documentation:** This document
- **Issues:** GitHub Issues
- **Email:** support@lait.legal

---

**Last Updated:** June 22, 2025  
**API Version:** v1.0 
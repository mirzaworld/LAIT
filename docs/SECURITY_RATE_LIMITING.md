# 🛡️ LAIT Security Implementation - Rate Limiting

## Overview

Flask-Limiter has been implemented to protect critical endpoints from abuse and ensure fair usage of the LAIT platform.

## Rate Limiting Configuration

### 🔐 Authentication Endpoint Protection

**Login Endpoint**: `/api/auth/login`
- **Limit**: 5 requests per minute per IP address
- **Purpose**: Prevent brute force password attacks
- **Key Function**: IP-based rate limiting
- **Storage**: Redis with memory fallback

```python
@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    # Authentication logic
```

### 📤 Upload Endpoint Protection  

**Upload Endpoint**: `/api/invoices/upload`
- **Limit**: 60 requests per minute per authenticated user
- **Purpose**: Prevent resource exhaustion and abuse
- **Key Function**: JWT token-based rate limiting
- **Storage**: Redis with memory fallback

```python
@app.route('/api/invoices/upload', methods=['POST'])
@jwt_required()
@limiter.limit("60 per minute", key_func=get_user_token_key)
def upload_invoice():
    # Upload logic
```

## Implementation Details

### Rate Limiter Initialization

```python
# Initialize rate limiter with Redis backend (fallback to memory)
redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/1')
try:
    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        storage_uri=redis_url,
        default_limits=["1000 per hour", "100 per minute"]
    )
    logger.info(f"Rate limiter initialized with Redis: {redis_url}")
except Exception as e:
    logger.warning(f"Failed to connect to Redis, using memory storage: {e}")
    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        default_limits=["1000 per hour", "100 per minute"]
    )
```

### Custom Key Functions

**IP-Based Rate Limiting** (Login):
```python
# Uses default get_remote_address function
@limiter.limit("5 per minute")
```

**Token-Based Rate Limiting** (Upload):
```python
def get_user_token_key():
    """Get rate limit key from JWT token for authenticated endpoints"""
    try:
        from flask_jwt_extended import verify_jwt_in_request
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
        if user_id:
            return f"user:{user_id}"
        return get_remote_address(request)
    except:
        return get_remote_address(request)
```

### Error Handling

**Rate Limit Exceeded Response**:
```python
@app.errorhandler(429)
def rate_limit_exceeded(error):
    """Handle rate limit exceeded errors"""
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': 'Too many requests. Please try again later.',
        'retry_after': getattr(error, 'retry_after', 60)
    }), 429
```

## Security Benefits

### 🛡️ Attack Prevention

1. **Brute Force Protection**
   - Login attempts limited to 5 per minute per IP
   - Prevents automated password cracking attempts
   - Forces attackers to slow down significantly

2. **Resource Exhaustion Prevention**
   - Upload limited to 60 per minute per user
   - Prevents single users from overwhelming the system
   - Maintains fair resource allocation

3. **DDoS Mitigation**
   - Global rate limits provide baseline protection
   - Redis storage enables distributed rate limiting
   - Memory fallback ensures availability

### 📊 Fair Usage Enforcement

1. **User-Based Limiting**
   - Upload limits tied to authenticated users
   - Prevents shared account abuse
   - Enables legitimate high-volume users

2. **IP-Based Limiting**
   - Login limits prevent proxy-based attacks
   - Protects against credential stuffing
   - Maintains service availability

## Configuration Options

### Environment Variables

```bash
# Redis configuration for rate limiting storage
REDIS_URL=redis://localhost:6379/1

# Flask-Limiter will use Redis if available, memory otherwise
```

### Customizable Limits

**Default Limits** (applied to all endpoints):
- 1000 requests per hour
- 100 requests per minute

**Endpoint-Specific Limits**:
- Login: 5/minute per IP
- Upload: 60/minute per user

### Rate Limit Headers

Flask-Limiter automatically adds headers to responses:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining in window
- `X-RateLimit-Reset`: When the limit resets
- `Retry-After`: Seconds to wait when rate limited

## Testing Rate Limits

### Automated Testing

Run the rate limiting test script:
```bash
# Test both login and upload rate limits
python tests/test_rate_limiting.py
```

### Manual Testing

**Test Login Rate Limiting**:
```bash
# Make multiple login attempts quickly
for i in {1..8}; do
  curl -X POST http://localhost:5003/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"wrong"}'
  echo " - Request $i"
done
```

**Test Upload Rate Limiting**:
```bash
# Get auth token first
TOKEN=$(curl -X POST http://localhost:5003/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}' \
  | jq -r '.token')

# Make multiple upload attempts
for i in {1..65}; do
  curl -X POST http://localhost:5003/api/invoices/upload \
    -H "Authorization: Bearer $TOKEN" \
    -F "file=@test.txt"
  echo " - Upload $i"
done
```

## Monitoring and Alerts

### Rate Limit Metrics

Monitor these metrics in production:
- Rate limit violations per endpoint
- Top rate-limited IP addresses
- User accounts hitting limits frequently
- Redis storage performance

### Log Analysis

Rate limit events are logged:
```python
# In Flask-Limiter, violations are automatically logged
# Custom logging can be added:
logger.warning(f"Rate limit exceeded for {get_remote_address()} on {request.endpoint}")
```

### Redis Monitoring

Monitor Redis performance:
```bash
# Check Redis connection
redis-cli ping

# Monitor rate limit keys
redis-cli keys "LIMITER*"

# Check memory usage
redis-cli info memory
```

## Production Considerations

### Scaling with Redis

1. **Redis Cluster**
   - Use Redis Cluster for high availability
   - Ensures rate limits work across multiple app instances
   - Provides persistence and backup

2. **Redis Configuration**
   ```redis
   # Recommended Redis settings for rate limiting
   maxmemory-policy allkeys-lru
   save 900 1
   save 300 10
   ```

### Rate Limit Tuning

**Adjust limits based on usage patterns**:
- Monitor legitimate user behavior
- Adjust limits to balance security and usability
- Consider different limits for different user tiers

**Business Logic Considerations**:
- Exempt certain IP addresses (office networks)
- Implement user-specific limit overrides
- Add temporary limit increases for special events

### Error Response Customization

**Client-Friendly Error Messages**:
```python
@app.errorhandler(429)
def rate_limit_exceeded(error):
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': 'You have made too many requests. Please wait before trying again.',
        'retry_after': getattr(error, 'retry_after', 60),
        'limit': getattr(error, 'limit', 'Unknown'),
        'window': getattr(error, 'window', 'Unknown')
    }), 429
```

## Security Best Practices

### 🔒 Additional Security Layers

Rate limiting works best as part of a comprehensive security strategy:

1. **Input Validation**
   - Validate all request data
   - Sanitize file uploads
   - Check file types and sizes

2. **Authentication Security**
   - Use strong password requirements
   - Implement account lockouts
   - Add MFA for sensitive operations

3. **Network Security**
   - Use HTTPS in production
   - Implement proper CORS policies
   - Consider IP whitelisting for admin endpoints

### 📱 Client-Side Handling

Implement proper client-side rate limit handling:
```javascript
// Handle 429 responses gracefully
if (response.status === 429) {
  const retryAfter = response.headers.get('Retry-After');
  // Show user-friendly message with retry time
  showRateLimitMessage(retryAfter);
}
```

---

🛡️ **Rate limiting is now active and protecting your LAIT platform from abuse while ensuring legitimate users have fair access to resources.**

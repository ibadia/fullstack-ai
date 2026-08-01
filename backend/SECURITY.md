# Security & Reliability Guide

## Overview

This document outlines security and reliability practices for the receipt management API.

## Security Principles

### 1. Secrets Management

**NEVER committed to Git:**
- `.env` file (contains API keys, database passwords)
- Private keys or certificates
- User credentials

**Proper Handling:**
- **In Production:**
  - Use managed secret services (AWS Secrets Manager, Google Secret Manager, HashiCorp Vault)
  - Never pass secrets as command-line arguments
  - Never log secrets (handled by sanitizing filter)

### 2. CORS Configuration

CORS (Cross-Origin Resource Sharing) is deliberately configured per environment:

**Development (permissive):**

**Staging:**

**Production (strict):**

**Why This Matters:**
- Prevents unauthorized cross-site requests
- Protects against CSRF attacks
- Controls which domains can access your API

### 3. File Upload Security

**Validation Layers:**

1. **File Size Limit**: 10MB max
   - Prevents disk exhaustion attacks
   - Configurable in `RECEIPT_UPLOAD`

2. **MIME Type Validation**:
   - Checks `Content-Type` header
   - Only allows: JPEG, PNG, WebP
   - Prevents uploading executables as images

3. **Magic Byte Verification**:

4. **File Extension Check**:
- Whitelist of allowed extensions
- Case-insensitive check

**Secure File Storage:**
- Files stored outside web root
- Served via Django, not directly accessible
- Cleanup policies recommended for old files

### 4. Logging & Monitoring

**What Gets Logged:**
- Request method, path, status code
- User ID (not email or phone)
- Processing time
- Error codes (not full error messages for 5xx)
- File metadata (name, size, type - not content)

**What's Sanitized (NOT logged):**
- API keys and tokens
- Passwords and secrets
- Authorization headers
- Email addresses
- File contents (never log binary data)
- Full error messages (might leak system info)

**Access Logs:**

### 5. HTTP Security Headers

Automatically set by Django middleware:

| Header | Purpose | Value |
|--------|---------|-------|
| `X-Content-Type-Options` | Prevent MIME sniffing | `nosniff` |
| `X-Frame-Options` | Prevent clickjacking | `DENY` |
| `Strict-Transport-Security` | Force HTTPS | `max-age=31536000` (production only) |
| `Content-Security-Policy` | Control resource loading | `default-src 'self'` |

### 6. Authentication & Authorization

**JWT Tokens:**
- Access tokens valid for 1 day
- Refresh tokens valid for 7 days
- Tokens rotated automatically
- Blacklist old tokens after rotation

**Request Flow:**

**Secure Storage (Frontend):**

## Reliability Practices

### 1. Error Handling

**Idempotent Operations:**

**Retry Logic:**
- Synchronous mode: No automatic retry (simple, predictable)
- Asynchronous mode: Exponential backoff up to 3 retries
  - Attempt 1: Immediate
  - Attempt 2: 2 seconds later
  - Attempt 3: 4 seconds later

**Error Responses:**

*4xx Errors (Client's Fault):*

*5xx Errors (Server's Fault):*
Note: 5xx doesn't include full exception (prevents leaking system info).

### 2. Request Deduplication

For idempotent operations, use request IDs:

**When to Use:**
- Safe methods (GET, HEAD) with no side effects
- Idempotent methods (PUT, DELETE) that can handle retries

**Avoid Use:** 
- Non-idempotent actions (e.g., POST /payments)
- Operations where side effects occur prior to response (e.g., sending emails)

**Implementation Notes:**
- Generate unique ID per upload (UUIDs recommended)
- Include ID in receipt creation request
- Log ID with receipt metadata for traceability

**Benefits:**
- Prevents duplicate uploads
- Ensures idempotency across retries
- Aids in troubleshooting and support

**Use Cases:**
- Retry same upload on network failure
- Trace request through logs
- Deduplicate if needed

### 3. Rate Limiting

**Anonymous Users**: 100 requests/hour
**Authenticated Users**: 1,000 requests/hour

**Rate Limit Headers:**

**Exceeding Limit (429 Too Many Requests):**

### 4. Timeouts

**Sync Mode Processing:**
- 60 seconds per request
- If analysis takes longer, request times out
- Receipt marked as failed with `timeout` error code

**Celery Async Mode:**
- 30 second timeout per task
- Automatic retry on timeout
- Max 3 retries total

### 5. Graceful Degradation

**Provider Not Available:**

**Celery Not Available:**

## Testing Security

### 1. Test File Upload Security

### 3. Test Logging (No Secrets)

### 4. Test Rate Limiting

## Deployment Checklist

Before going to production:

- [ ] `ENVIRONMENT=production` in .env
- [ ] `DEBUG=False`
- [ ] `SECRET_KEY` minimum 50 characters (generated)
- [ ] `ALLOWED_HOSTS` set to your domain(s)
- [ ] `CORS_ALLOWED_ORIGINS` set to frontend domain(s)
- [ ] `SECURE_SSL_REDIRECT=True`
- [ ] `SESSION_COOKIE_SECURE=True`
- [ ] HTTPS certificate configured
- [ ] Database password changed from default
- [ ] API keys stored in managed secrets service
- [ ] Logging configured (file or remote service)
- [ ] File cleanup policy configured
- [ ] Backup strategy in place
- [ ] Monitoring/alerting configured
- [ ] Security audit completed

## Common Issues

### "CSRF token missing"

### "API key not found in environment"

### "File upload fails with magic byte error"

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Django Security](https://docs.djangoproject.com/en/stable/topics/security/)
- [Django REST Framework Security](https://www.django-rest-framework.org/#security)
- [CORS Explained](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8949)
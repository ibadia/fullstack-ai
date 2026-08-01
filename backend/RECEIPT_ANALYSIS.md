## AI Providers

### 1. Mock Provider (Default)
- **Use When**: Testing, development, demos, no API key
- **Speed**: ~0.5-1.5s per receipt (simulated)
- **Cost**: Free
- **Setup**: No configuration needed

### 2. OpenAI GPT-4 Vision
- **Use When**: High accuracy needed, production
- **Speed**: ~2-5s per receipt
- **Cost**: ~$0.01-0.03 per receipt
- **Model**: `gpt-4-vision`

**Setup**:

**Cost Estimation**:
- Vision request tokens: ~500-1000 tokens ($0.01-0.03)
- 10,000 receipts/month: ~$100-300

### 3. Anthropic Claude 3 Opus
- **Use When**: Excellent reliability, edge cases
- **Speed**: ~2-5s per receipt
- **Cost**: ~$0.015-0.04 per receipt
- **Model**: `claude-3-opus`

**Setup**:

## API Endpoints

### Upload Receipt

````````


# Response
````````

**Response (Sync Mode - 200)**:
````````


# Response
````````

### Get Receipt Details

````````


# Response
````````

Returns receipt with current status and extracted data (if complete).

### List Receipts

````````


# Response
````````

**Query Parameters**:
- `analysis_status`: Filter by status (pending, processing, completed, failed)
- `page`: Page number for pagination

### Get Line Items

````````


# Response
````````markdown
````````

## Error Handling

| Error Code | Status | Description | Resolution |
|-----------|--------|-------------|-----------|
| `validation_error` | 400 | Missing required fields | Check image quality, ensure full receipt visible |
| `invalid_format` | 400 | Unsupported image format | Use JPEG, PNG, or WebP format |
| `timeout` | 400 | Request exceeded timeout | Try again, check image size |
| `api_error` | 400 | API provider error | Check credentials, rate limits |
| `processing_error` | 500 | Server-side error | Check logs, retry |
| `max_retries` | 500 | Exceeded retry attempts (async) | Check provider status, retry later |

**Error Response Example**:
````````


# Response
````````markdown
````````

## Testing

### MVP Quick Test (No Setup Required)

````````


# Response
````````markdown
````````

### Test Error Handling

````````


# Response
````````

### Test with Real API Key

````````


# Response
````````markdown
````````

### Test Async Mode

````````


# Response
````````markdown
````````

## Extracted Data Schema

All providers return this JSON structure:

````````


# Response
````````markdown
````````

## Operational Considerations

### Sync Mode (MVP - Recommended)
| Aspect | Details |
|--------|---------|
| **Setup Time** | ~5 minutes |
| **Infrastructure** | None required |
| **Throughput** | ~720 receipts/hour (at 5s each) |
| **Response Time** | 2-5 seconds per upload |
| **Cost** | $0/month (mock) or $0.01-0.04 per receipt (real API) |
| **Failure Recovery** | Automatic retry in image analysis |
| **Hosting** | Serverless-compatible (Lambda, Cloud Functions) |

### Async Mode (Scaling)
| Aspect | Details |
|--------|---------|
| **Setup Time** | 30+ minutes (Redis/RabbitMQ setup) |
| **Infrastructure** | Redis/RabbitMQ + Worker processes |
| **Throughput** | Unlimited (scales horizontally) |
| **Response Time** | <100ms upload, 2-5s background processing |
| **Cost** | Infrastructure cost + $0.01-0.04 per receipt |
| **Failure Recovery** | Automatic retry with exponential backoff |
| **Hosting** | Dedicated servers or managed Kubernetes |

### File Handling
- **Max file size**: 10MB
- **Supported formats**: JPEG, PNG, WebP
- **Storage location**: `media/receipts/YYYY/MM/DD/`
- **Estimated size**: 50-100KB per receipt (including metadata)
- **Retention**: Indefinite (configure cleanup if needed)

## Migration from Sync to Async

When ready to scale:

1. Set up Redis/RabbitMQ
2. Update `.env`:
````````
3. Start Celery worker: `celery -A core worker -l info`
4. Restart API server

Existing API calls work unchanged. Processing just moves to background.

## Troubleshooting

### "ModuleNotFoundError: No module named 'openai'"
````````


# Response
````````markdown
````````

### "Request timeout" (Sync Mode)
- Increase `RECEIPT_PROCESSING.REQUEST_TIMEOUT` in settings
- Use async mode for better scalability
- Check image size

### "Celery not available" (Async Mode)
````````


# Response
````````markdown
````````

### "Receipt stuck in 'processing'" (Async Mode)
- Check Celery worker is running
- Check Redis connection: `redis-cli ping`
- Check logs: `celery -A core worker -l debug`

## Adding Custom Analyzers

1. Create `backend/apps/receipts/services/analyzers/custom_analyzer.py`
2. Extend `BaseReceiptAnalyzer`
3. Implement `analyze()` method
4. Add to `AnalyzerFactory.AVAILABLE_PROVIDERS`

## Security Notes

- API keys stored in environment variables (never committed)
- File upload validates type and size
- Mock provider recommended for development
- Database stores only structured data
- Original images stored with Django's file storage (can be S3, etc.)
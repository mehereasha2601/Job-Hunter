# Job Hunter API

FastAPI backend for the Job Hunter Web UI.

## Features

- REST API for job browsing and filtering
- Job status updates
- Trigger GitHub Actions tailoring workflow
- Dashboard statistics
- Past outputs viewer
- Password authentication

## Setup

### 1. Install Dependencies

```bash
cd api
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Make sure these are set in your `.env` file:

```bash
# Required (already configured)
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key

# New for API
UI_PASSWORD=your-secure-password
GH_PAT=your-github-personal-access-token
```

### 3. Run the API

```bash
cd api
python main.py
```

Or with uvicorn directly:

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

## API Endpoints

### Authentication
All endpoints require HTTP Basic Auth with the `UI_PASSWORD`.

### Endpoints

#### `GET /`
Root endpoint with API info.

#### `GET /api/health`
Health check - tests database connection.

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2026-03-26T21:00:00"
}
```

#### `GET /api/jobs`
List all jobs with optional filters and sorting.

**Query Parameters:**
- `status` - Filter by status (seen, scored, tailored, applied, etc.)
- `min_score` - Minimum score threshold (0-10)
- `company` - Filter by company name (partial match)
- `source` - Filter by source (greenhouse, linkedin, etc.)
- `sort_by` - Sort field: `score`, `date_posted`, `first_seen_at` (default: score)
- `limit` - Max results (default: 100, max: 500)
- `offset` - Pagination offset (default: 0)

**Examples:**
```bash
# Get highest scored jobs
GET /api/jobs?min_score=7&sort_by=score

# Get newest jobs posted
GET /api/jobs?sort_by=date_posted&limit=50

# Get recent high-scoring jobs
GET /api/jobs?min_score=8&sort_by=date_posted

# Filter by company and status
GET /api/jobs?company=Stripe&status=scored
```

**Response:**
```json
{
  "jobs": [
    {
      "id": "abc123",
      "title": "Software Engineer",
      "company": "Stripe",
      "location": "San Francisco, CA",
      "date_posted": "2026-03-26T18:00:01.107406",
      "score": 9.0,
      "status": "scored",
      "first_seen_at": "2026-03-26T19:00:00",
      ...
    }
  ],
  "count": 50,
  "offset": 0,
  "limit": 100
}
```

#### `GET /api/jobs/{job_id}`
Get single job details.

**Response:**
```json
{
  "id": "job123",
  "title": "Software Engineer",
  "company": "Stripe",
  "score": 9.0,
  ...
}
```

#### `PATCH /api/jobs/{job_id}/status`
Update job status.

**Body:**
```json
{
  "status": "applied"
}
```

**Valid statuses:** seen, scored, tailored, applied, response, interview, offer, rejected

**Response:**
```json
{
  "success": true,
  "job_id": "job123",
  "status": "applied"
}
```

#### `GET /api/stats`
Get dashboard statistics.

**Response:**
```json
{
  "total_scraped": 124,
  "total_scored": 89,
  "total_tailored": 12,
  "total_applied": 5,
  "by_company": {"Stripe": 3, "Google": 5, ...},
  "by_source": {"greenhouse": 40, "linkedin": 30, ...},
  "by_status": {"scored": 50, "applied": 5, ...}
}
```

#### `POST /api/tailor`
Trigger GitHub Actions tailoring workflow for selected jobs.

**Body:**
```json
{
  "job_ids": ["job123", "job456"]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Tailoring triggered for 2 job(s)",
  "job_ids": ["job123", "job456"],
  "workflow": "step2_tailor"
}
```

#### `GET /api/outputs`
List all tailored jobs with output links.

**Response:**
```json
{
  "outputs": [
    {
      "id": "job123",
      "title": "Software Engineer",
      "company": "Stripe",
      "tailored_at": "2026-03-26T20:00:00",
      "resume_pdf_url": "https://...",
      "doc_url": "https://docs.google.com/...",
      "email_doc_url": "https://docs.google.com/...",
      "md_path": "output/2026-03-26/Stripe_Software-Engineer.md",
      "status": "applied"
    }
  ],
  "count": 12
}
```

## Interactive Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## CORS Configuration

The API is configured to allow requests from any origin (`allow_origins=["*"]`).

In production, you should restrict this to your frontend domain:

```python
allow_origins=["https://yourusername.github.io"]
```

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200` - Success
- `400` - Bad request (invalid input)
- `401` - Unauthorized (invalid password)
- `404` - Not found
- `500` - Server error

Error responses include a detail message:

```json
{
  "detail": "Job not found"
}
```

## Testing

### Using curl

```bash
# Health check
curl http://localhost:8000/api/health

# List jobs (with auth)
curl -u "user:your-password" http://localhost:8000/api/jobs?min_score=7

# Get stats
curl -u "user:your-password" http://localhost:8000/api/stats

# Trigger tailoring
curl -u "user:your-password" -X POST http://localhost:8000/api/tailor \
  -H "Content-Type: application/json" \
  -d '{"job_ids": ["job123", "job456"]}'
```

### Using Python

```python
import httpx

# With authentication
auth = ("user", "your-password")

# List jobs
response = httpx.get("http://localhost:8000/api/jobs", auth=auth)
print(response.json())

# Update status
response = httpx.patch(
    "http://localhost:8000/api/jobs/job123/status",
    auth=auth,
    json={"status": "applied"}
)
print(response.json())
```

## Deployment

### Local Development
```bash
python api/main.py
```

### Production (with Gunicorn)
```bash
pip install gunicorn
gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker (Optional)
Create `api/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t job-hunter-api ./api
docker run -p 8000:8000 --env-file .env job-hunter-api
```

## Security Notes

- The API uses HTTP Basic Authentication with a single password
- This is suitable for personal use
- For production with multiple users, implement proper authentication (JWT, OAuth, etc.)
- Always use HTTPS in production
- Keep your `GH_PAT` secure and never commit it to the repo

## Troubleshooting

### Port already in use
```bash
# Find process using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>
```

### Database connection errors
- Verify `SUPABASE_URL` and `SUPABASE_KEY` in `.env`
- Check Supabase dashboard for any issues
- Test connection: `python -c "from src.db import Database; db = Database(); print('OK')"`

### GitHub workflow trigger fails
- Verify `GH_PAT` is set and has correct permissions
- Check token has `workflow` scope
- Verify repo name matches: `mehereasha2601/Job-Hunter`

---

**API Status:** ✅ Ready for use

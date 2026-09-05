# Setup & Deployment Guide
## Cross-Border Deal Intelligence + Property DD Platform

**Timeline: 20 weeks solo build → Launch**

---

## PHASE 1: LOCAL SETUP (Week 0-1)

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Node.js 18+
- Git
- AWS Account (for Lambda/RDS)
- Stripe Account
- Anthropic API Key

### Step 1: Clone & Environment

```bash
# Create project directory
mkdir deal-intelligence && cd deal-intelligence

# Initialize git
git init

# Copy environment template
cp .env.template .env

# Edit .env with your credentials
nano .env
```

### Step 2: Backend Setup

```bash
# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create database
createdb deal_intelligence

# Run migrations
python -m alembic upgrade head
```

### Step 3: Test Local Server

```bash
# Start FastAPI server
python main.py

# Should see: "Uvicorn running on http://127.0.0.1:8000"

# Test health endpoint
curl http://localhost:8000/health
```

### Step 4: Frontend Setup (Optional for MVP)

```bash
# Create React app (Week 2)
npx create-react-app frontend
cd frontend
npm install axios react-router-dom

# Start dev server
npm start
```

---

## PHASE 2: DATABASE SETUP (Week 1-2)

### AWS RDS Setup

```bash
# Create RDS PostgreSQL instance
aws rds create-db-instance \
  --db-instance-identifier deal-intelligence \
  --db-instance-class db.t2.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password YourPassword123 \
  --allocated-storage 20 \
  --backup-retention-period 7

# Wait 5-10 minutes for instance to be available

# Get endpoint
aws rds describe-db-instances --db-instance-identifier deal-intelligence
# Copy the "Endpoint.Address" value

# Update .env with RDS endpoint
DATABASE_URL=postgresql://admin:YourPassword123@[endpoint]:5432/deal_intelligence

# Connect and run migrations
psql -h [endpoint] -U admin -d deal_intelligence -f 001_initial_schema.sql
```

### Create Indexes (for performance)

```sql
-- Connect to database
psql -h [endpoint] -U admin deal_intelligence

-- Run these to ensure indexes exist:
CREATE INDEX idx_deals_score_desc ON deals(score DESC);
CREATE INDEX idx_properties_investment_score_desc ON properties(investment_score DESC);
CREATE INDEX idx_user_alerts_user_enabled ON user_alerts(user_id, enabled);
```

---

## PHASE 3: API DEVELOPMENT (Week 2-5)

### Develop Endpoints Locally

```bash
# Each week, test endpoints with curl/Postman

# Week 2: Auth endpoints
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123",
    "first_name": "John",
    "last_name": "Doe",
    "company_name": "Test Corp"
  }'

# Week 3: Deal endpoints
curl http://localhost:8000/deals?limit=10

# Week 4: Property endpoints
curl http://localhost:8000/properties?country=AE

# Week 5: Alert endpoints
curl -X POST http://localhost:8000/alerts \
  -H "Authorization: Bearer [token]" \
  -H "Content-Type: application/json" \
  -d '{
    "alert_name": "Tech Deals in SG",
    "alert_type": "deal",
    "criteria": {"sectors": ["technology"], "geographies": ["SG"]},
    "frequency": "daily"
  }'
```

### Integrate Claude Scoring

```bash
# Test scoring engine
python scoring_engine.py

# Should output sample deal score: 78/100
```

---

## PHASE 4: DATA PIPELINE (Week 3-5)

### Test Data Collection

```bash
# Run scraping service
python scraping_service.py

# Should collect deals and properties from mock sources
```

### Schedule Scraping Jobs (AWS Lambda)

```bash
# Create Lambda function for scheduled scraping
aws lambda create-function \
  --function-name deal-intelligence-scraper \
  --runtime python3.11 \
  --handler scraping_service.lambda_handler \
  --zip-file fileb://function.zip

# Schedule with EventBridge (every 6 hours)
aws events put-rule \
  --name deal-intelligence-scraper-schedule \
  --schedule-expression "rate(6 hours)"
```

---

## PHASE 5: FRONTEND DEVELOPMENT (Week 6-8)

### React Components (Claude generates these)

```bash
cd frontend

# Create main pages
src/pages/Dashboard.jsx        # Main feed
src/pages/DealDetail.jsx       # Deal details
src/pages/PropertyDetail.jsx   # Property DD report
src/pages/Alerts.jsx           # Alert management
src/pages/Profile.jsx          # User settings
```

### Connect to Backend

```javascript
// src/api/client.js
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default client;
```

---

## PHASE 6: TESTING & STAGING (Week 9)

### Unit Tests

```bash
# Backend tests
pytest tests/ -v

# Frontend tests
npm test
```

### Deploy to Staging

```bash
# Build frontend
cd frontend && npm run build

# Deploy to AWS S3 + CloudFront
aws s3 sync build/ s3://deal-intelligence-staging/

# Backend: Deploy to Fargate
aws ecs create-service \
  --cluster deal-intelligence-staging \
  --service-name api \
  --task-definition deal-intelligence:1 \
  --desired-count 1
```

### Staging Tests

```bash
# Test signup/login
curl -X POST https://staging-api.dealsintell.com/auth/signup ...

# Test deal listing
curl https://staging-api.dealsintell.com/deals

# Check dashboards load
open https://staging.dealsintell.com
```

---

## PHASE 7: MONETIZATION SETUP (Week 8-9)

### Stripe Integration

```bash
# Get API keys from Stripe dashboard
# Add to .env:
STRIPE_API_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...

# Create pricing plans
# Deal Intelligence: $999/month
# Property DD: $799/month
# Bundle: $1,499/month

# Generate Stripe product/price IDs
# Add to database
```

### Invoice & Billing

```python
# In main.py, add Stripe payment endpoint
@app.post("/subscribe")
async def subscribe(plan: str, db: Session = Depends(get_db)):
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price": os.getenv(f"STRIPE_{plan.upper()}_PRICE_ID"),
            "quantity": 1,
        }],
        mode="subscription",
        success_url="https://dealsintell.com/success",
        cancel_url="https://dealsintell.com/cancel",
    )
    return {"checkout_url": session.url}
```

---

## PHASE 8: PRODUCTION LAUNCH (Week 10)

### Pre-Launch Checklist

- [ ] Database backups configured
- [ ] SSL certificate installed (AWS ACM)
- [ ] Monitoring & alerts set up (CloudWatch)
- [ ] Error tracking enabled (Sentry)
- [ ] CDN configured (CloudFront)
- [ ] API rate limiting enabled
- [ ] CORS properly configured
- [ ] Security headers set
- [ ] GDPR/privacy policy drafted
- [ ] Terms of service drafted
- [ ] Payment processing tested
- [ ] Email notifications working
- [ ] Admin dashboard created

### Deploy to Production

```bash
# Frontend
aws s3 sync frontend/build/ s3://deal-intelligence-prod/
aws cloudfront create-invalidation --distribution-id E123ABC --paths "/*"

# Backend
aws ecs update-service \
  --cluster deal-intelligence \
  --service api \
  --force-new-deployment
```

### Domain & DNS

```bash
# Register domain (dealsintell.com)
# Point to CloudFront distribution
# Update .env CORS origins
# Update Stripe webhook URLs
```

---

## PHASE 9: LAUNCH & CUSTOMER ACQUISITION (Week 10-11)

### Beta Access

```bash
# Email your network (PE firms, advisers, family offices)
# Subject: Exclusive Beta Access - Deal Intelligence Platform

"Dear [Name],

You're invited to beta test Deal Intelligence, an AI-powered platform 
for cross-border deal sourcing and property due diligence.

Early-bird pricing: $499/month (50% off)
Sign up: https://dealsintell.com/beta

This is exclusive to our closed beta group.

Best,
[Your Name]"
```

### Feedback Loop

```bash
# Week 10-11: 3-5 beta customers
# Collect feedback via surveys/calls
# Fix bugs + iterate
# Prepare for public launch
```

---

## ONGOING OPERATIONS (Week 12+)

### Monitoring

```bash
# Check CloudWatch logs daily
aws logs tail /aws/lambda/deal-intelligence-scraper --follow

# Monitor Sentry for errors
# Check API response times
# Verify scheduled jobs are running
```

### Updates & Maintenance

```bash
# Weekly: Review new deals/properties
# Bi-weekly: Update scoring models (via Claude)
# Monthly: Customer feedback review
# Monthly: Feature roadmap prioritization
```

### Cost Tracking

```
Monthly costs (production):
├── AWS RDS: $20
├── AWS Fargate: $30
├── AWS Lambda: $5
├── AWS S3 + CloudFront: $10
├── Claude API: $50
├── Gemini API: $20
├── SendGrid: $20
├── Stripe fees: ~2.9% + $0.30 per transaction
└── TOTAL: ~$157 + transaction fees
```

---

## TROUBLESHOOTING

### Database Connection Error
```bash
# Check RDS security group allows your IP
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxx \
  --protocol tcp \
  --port 5432 \
  --cidr 0.0.0.0/0
```

### Claude API Rate Limit
```python
# Add retry logic
from anthropic import RateLimitError
import time

def call_claude_with_retry(prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.messages.create(...)
        except RateLimitError:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise
```

### Email Not Sending
```bash
# Verify SendGrid API key
curl --request POST \
  --url https://api.sendgrid.com/v3/mail/send \
  -H "Authorization: Bearer $SENDGRID_API_KEY"
```

---

## NEXT STEPS AFTER LAUNCH

1. **Week 12+: Property DD Module**
   - Launch as add-on to Deal Intelligence
   - Upsell existing customers
   - Expand property data sources

2. **Month 3+: Advanced Features**
   - Custom scoring rules
   - Portfolio tracking
   - Advanced analytics

3. **Month 6+: Partnerships**
   - Integrate with banking platforms
   - Partner with law firms (due diligence)
   - White-label options

---

## SUPPORT

For questions:
- Check architecture docs: `/ARCHITECTURE.md`
- Review code comments in each file
- Ask Claude for specific implementation help
- Debug using FastAPI interactive docs: `http://localhost:8000/docs`

---

**Good luck! You've got this. 🚀**

Remember: Ship fast, iterate based on customer feedback, and scale what works.

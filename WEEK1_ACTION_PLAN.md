# Week 1 Action Plan
## Getting Your Deal Intelligence Platform Running

**Goal: Working backend API + database ready for development**

---

## Day 1: Local Setup (4-5 hours)

### Morning (9am - 12pm)
- [ ] Create project directory
- [ ] Clone/download all code files from this session
- [ ] Set up git repository
- [ ] Copy `.env.template` to `.env`
- [ ] Add your API keys to `.env`:
  - `ANTHROPIC_API_KEY` (get from Anthropic)
  - `NEWSAPI_KEY` (get from newsapi.org - free)
  - `SECRET_KEY` (generate random string)

### Afternoon (1pm - 5pm)
- [ ] Install Python 3.11+ (if not already installed)
- [ ] Create Python virtual environment
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Download/install PostgreSQL locally
- [ ] Create database: `createdb deal_intelligence`

### Evening (5pm - 6pm)
- [ ] Run migrations: `python -m alembic upgrade head`
  - Or manually run: `psql deal_intelligence < 001_initial_schema.sql`
- [ ] Start backend: `python main.py`
- [ ] Test health endpoint: `curl http://localhost:8000/health`
- [ ] Bookmark FastAPI interactive docs: `http://localhost:8000/docs`

---

## Day 2: Test Core Endpoints (4-5 hours)

### Morning (9am - 12pm)

**Test Authentication:**
```bash
# Signup
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123",
    "first_name": "John",
    "last_name": "Doe"
  }'

# You should get back access_token
# Save this token for testing other endpoints
```

**Test Deal Endpoints:**
```bash
# List deals (should be empty initially)
curl http://localhost:8000/deals

# Get trending deals
curl http://localhost:8000/deals/trending
```

**Test Property Endpoints:**
```bash
# List properties
curl http://localhost:8000/properties?country=AE
```

### Afternoon (1pm - 5pm)

**Test Scoring Engine:**
```bash
# Run the scoring service test
python scoring_engine.py

# Should output:
# Deal Score: 78/100
# Breakdown: {sector: 25, geography: 30, ...}
# Reasoning: "..."
```

**Test Data Scraping:**
```bash
# Run scraping service
python scraping_service.py

# Should collect mock deals and properties
# Check that data appears correctly
```

### Evening (5pm - 6pm)
- [ ] All endpoints returning data successfully
- [ ] Claude scoring working
- [ ] No error logs
- [ ] Document any issues found

---

## Day 3: AWS Setup (3-4 hours)

### Morning (9am - 12pm)

**Set up AWS Account:**
- [ ] Create AWS account (if not existing)
- [ ] Create IAM user with RDS/Lambda/S3 permissions
- [ ] Get AWS access keys
- [ ] Install AWS CLI: `pip install awscli`
- [ ] Configure credentials: `aws configure`

**Create RDS Database:**
```bash
# Create PostgreSQL instance
aws rds create-db-instance \
  --db-instance-identifier deal-intelligence-dev \
  --db-instance-class db.t2.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password YourPassword123! \
  --allocated-storage 20 \
  --publicly-accessible

# Wait 5-10 minutes for instance to be ready
# (Grab coffee ☕)

# Get the endpoint
aws rds describe-db-instances --db-instance-identifier deal-intelligence-dev
```

### Afternoon (1pm - 4pm)

**Connect to RDS and Initialize:**
```bash
# Update .env with RDS endpoint
DATABASE_URL=postgresql://admin:YourPassword123!@deal-intelligence-dev.xxxxx.us-east-1.rds.amazonaws.com:5432/deal_intelligence

# Run migrations on RDS
psql -h deal-intelligence-dev.xxxxx.us-east-1.rds.amazonaws.com \
  -U admin \
  -d deal_intelligence < 001_initial_schema.sql
```

### Evening (4pm - 5pm)
- [ ] RDS instance running
- [ ] Database tables created
- [ ] Can connect remotely

---

## Day 4: Stripe & SendGrid Setup (3-4 hours)

### Morning (9am - 12pm)

**Stripe Setup:**
- [ ] Go to stripe.com/register
- [ ] Create account
- [ ] Get Test API Key from Dashboard
- [ ] Add to .env:
  ```
  STRIPE_API_KEY=sk_test_...
  STRIPE_PUBLISHABLE_KEY=pk_test_...
  ```

**SendGrid Setup:**
- [ ] Go to sendgrid.com
- [ ] Create account
- [ ] Verify sender email
- [ ] Create API key
- [ ] Add to .env:
  ```
  SENDGRID_API_KEY=SG...
  SENDGRID_FROM_EMAIL=noreply@yourdomain.com
  ```

### Afternoon (1pm - 4pm)

**Test Payments:**
```bash
# Test Stripe integration in API
# (This will be implemented in main.py Week 8)

curl -X POST http://localhost:8000/subscribe \
  -H "Content-Type: application/json" \
  -d '{"plan": "deal_intel"}'
```

### Evening (4pm - 5pm)
- [ ] Stripe test account working
- [ ] SendGrid email sending
- [ ] No errors in logs

---

## Day 5: Documentation & Review (2-3 hours)

### Morning (9am - 11am)

**Code Review:**
- [ ] Review all generated files
- [ ] Understand database schema
- [ ] Understand API endpoints
- [ ] Understand scoring logic

**Create Deployment Checklist:**
- [ ] Copy SETUP.md checklist
- [ ] Print or save to reference during build
- [ ] Mark Week 1 items as complete

### Late Morning (11am - 12pm)

**Plan Week 2:**
- [ ] Deal Intelligence MVP (Weeks 2-5)
- [ ] Start with enhanced API endpoints
- [ ] Add more data sources
- [ ] Improve scoring algorithms

### Afternoon (1pm - 2pm)

**Quick Test Suite:**
```bash
# Create simple test file
pytest tests/test_api.py -v

# Should show all endpoints working
```

### Final (2pm - 3pm)
- [ ] All Week 1 items complete
- [ ] Ready for Week 2 development
- [ ] Have backup of local database

---

## FILES YOU HAVE

```
scratchpad/
├── ARCHITECTURE.md          ← System design (for reference)
├── SETUP.md                 ← Full setup guide
├── WEEK1_ACTION_PLAN.md    ← This file
├── requirements.txt         ← Python dependencies
├── .env.template           ← Environment variables template
├── 001_initial_schema.sql  ← Database schema
├── main.py                 ← FastAPI application
├── models.py               ← SQLAlchemy ORM models
├── scoring_engine.py       ← Claude AI scoring
└── scraping_service.py     ← Data collection
```

---

## ISSUES? HERE'S HOW TO DEBUG

### "ModuleNotFoundError: No module named 'anthropic'"
```bash
pip install anthropic
```

### "Could not connect to database"
```bash
# Check PostgreSQL is running
psql -l

# Create database if missing
createdb deal_intelligence
```

### "Stripe API key error"
```bash
# Verify .env has correct key
cat .env | grep STRIPE

# Get key from Stripe Dashboard
# https://dashboard.stripe.com/apikeys
```

### "Claude API rate limit"
- Normal - occurs after ~60 requests/min
- Will be handled automatically in production

---

## SUCCESS CRITERIA FOR WEEK 1

✅ **Backend running locally**
```bash
python main.py
# "Uvicorn running on http://127.0.0.1:8000"
```

✅ **Database connected**
```bash
curl http://localhost:8000/health
# {"status": "healthy"}
```

✅ **Authentication working**
```bash
# Can signup and login
# Get JWT token back
```

✅ **Scoring engine functional**
```bash
python scoring_engine.py
# Outputs: Deal Score: 78/100
```

✅ **AWS RDS ready**
```bash
# Can connect remotely
# Database tables created
```

✅ **Stripe & SendGrid configured**
```bash
# API keys in .env
# Test endpoints responding
```

---

## TIME ESTIMATE

- **Day 1**: 5 hours
- **Day 2**: 5 hours
- **Day 3**: 4 hours
- **Day 4**: 4 hours
- **Day 5**: 3 hours
- **TOTAL**: ~21 hours (split across the week)

**Average: 4-5 hours per day**

---

## NEXT WEEK (Week 2) PREVIEW

Once Week 1 is complete, Week 2 focuses on:
1. Expanding API endpoints (more deal/property filters)
2. Integrating more news sources
3. Enhancing Claude scoring logic
4. Building alert matching system

You'll be building towards the first beta customer by Week 11.

---

## MOMENTUM CHECKPOINT

**At the end of Week 1, you should feel:**
- ✅ Confident the architecture works
- ✅ Able to add new features independently
- ✅ Ready to iterate quickly
- ✅ Excited about the potential

If you get stuck on any step, Claude (me) can help debug or generate additional code.

**You've got this! 🚀**

---

## QUICK REFERENCE

**Start backend:**
```bash
source venv/bin/activate
python main.py
```

**Run tests:**
```bash
pytest tests/ -v
```

**Test scoring:**
```bash
python scoring_engine.py
```

**Check database:**
```bash
psql deal_intelligence
\dt  -- List tables
\q   -- Quit
```

**View API docs:**
```
http://localhost:8000/docs
```

---

Good luck with Week 1! Message me anytime you need help. 💪

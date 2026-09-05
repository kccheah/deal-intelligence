# Quick Start Guide
## Get Deal Intelligence Running in 30 Minutes

---

## OPTION 1: Local Development (No Docker)

### Step 1: Clone & Setup (5 min)
```bash
# Download all files from this session
# Organize in a folder called deal-intelligence/

cd deal-intelligence
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Database Setup (5 min)
```bash
# Create PostgreSQL database
createdb deal_intelligence

# Run migrations
psql deal_intelligence < 001_initial_schema.sql

# Verify tables created
psql deal_intelligence -c "\dt"
```

### Step 3: Environment Config (2 min)
```bash
# Copy template
cp .env.template .env

# Edit .env and add your API keys:
# - ANTHROPIC_API_KEY (from Claude console)
# - NEWSAPI_KEY (from newsapi.org)
# - SECRET_KEY (just generate a random string)

nano .env  # or use your favorite editor
```

### Step 4: Start Backend (3 min)
```bash
# Terminal 1: Start API
python main.py

# Should see:
# Uvicorn running on http://127.0.0.1:8000
```

### Step 5: Test It Works (10 min)
```bash
# Terminal 2: Test endpoints

# Health check
curl http://localhost:8000/health

# Interactive docs
open http://localhost:8000/docs

# Try signup
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123",
    "first_name": "John",
    "last_name": "Doe"
  }'

# List deals
curl http://localhost:8000/deals
```

**✅ Done!** API is running.

---

## OPTION 2: Docker (Recommended for Staging)

### Step 1: Setup (2 min)
```bash
cd deal-intelligence

# Copy environment template
cp .env.template .env
nano .env  # Add your API keys
```

### Step 2: Launch with Docker Compose (5 min)
```bash
# Start all services (PostgreSQL + API)
docker-compose up -d

# Wait 10 seconds for services to start
sleep 10

# Check logs
docker-compose logs -f api
```

### Step 3: Test (10 min)
```bash
# Health check
curl http://localhost:8000/health

# Try signup
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123",
    "first_name": "John",
    "last_name": "Doe"
  }'

# Open interactive docs
open http://localhost:8000/docs
```

### Stop Services
```bash
docker-compose down

# Clean up volumes
docker-compose down -v
```

---

## OPTION 3: AWS Deployment (For Production)

### Prerequisites
- AWS Account
- AWS CLI configured
- Docker & Docker Compose installed

### Step 1: Create RDS Database (5 min)
```bash
aws rds create-db-instance \
  --db-instance-identifier deal-intelligence \
  --db-instance-class db.t2.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password YourPassword123! \
  --allocated-storage 20

# Wait for instance to be ready (5-10 min)
aws rds describe-db-instances --db-instance-identifier deal-intelligence
```

### Step 2: Update Environment
```bash
# Get RDS endpoint from AWS console
# Update .env:

DATABASE_URL=postgresql://admin:YourPassword123!@[endpoint]:5432/deal_intelligence
```

### Step 3: Deploy to Fargate
```bash
# Build Docker image
docker build -t deal-intelligence .

# Push to ECR
aws ecr create-repository --repository-name deal-intelligence
docker tag deal-intelligence [account-id].dkr.ecr.us-east-1.amazonaws.com/deal-intelligence
docker push [account-id].dkr.ecr.us-east-1.amazonaws.com/deal-intelligence

# Create ECS cluster
aws ecs create-cluster --cluster-name deal-intelligence

# Create task definition (see deployment docs for full config)
# Deploy to Fargate
```

---

## Common Commands

### Start Development Server
```bash
source venv/bin/activate
python main.py
```

### Run Tests
```bash
pytest tests/ -v
```

### Generate Test Data
```bash
python scraping_service.py
```

### Test Scoring Engine
```bash
python scoring_engine.py
```

### Check Database
```bash
psql deal_intelligence
\dt          # List tables
\d deals     # Show deals table structure
SELECT * FROM deals LIMIT 5;  # View deals
\q           # Quit
```

### View API Documentation
```
http://localhost:8000/docs
```

---

## Environment Variables

Required for running:
```
DATABASE_URL=postgresql://user:password@localhost/deal_intelligence
SECRET_KEY=your-secret-key
ANTHROPIC_API_KEY=your-anthropic-key
NEWSAPI_KEY=your-newsapi-key
```

Optional:
```
CORS_ORIGINS=http://localhost:3000
DEBUG=true
STRIPE_API_KEY=your-stripe-key
SENDGRID_API_KEY=your-sendgrid-key
```

---

## Troubleshooting

### "Connection refused" error
```bash
# Make sure PostgreSQL is running
psql -l

# If not installed:
# macOS: brew install postgresql
# Ubuntu: sudo apt-get install postgresql
# Windows: Download from postgresql.org
```

### "ModuleNotFoundError"
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### "ANTHROPIC_API_KEY not set"
```bash
# Add to .env file
ANTHROPIC_API_KEY=sk-ant-... (your actual key)

# Or export in terminal
export ANTHROPIC_API_KEY=sk-ant-...
```

### Database migration errors
```bash
# Recreate database
dropdb deal_intelligence
createdb deal_intelligence
psql deal_intelligence < 001_initial_schema.sql
```

---

## Next Steps

1. ✅ API running locally
2. ⏭️ Generate React frontend: Ask Claude to create React components
3. ⏭️ Add more data sources: Expand scraping service
4. ⏭️ Connect Stripe: Set up payments
5. ⏭️ Deploy to AWS: Follow deployment guide

---

## Architecture Overview

```
┌─────────────────────────────────────────┐
│         React Frontend (3000)           │
└────────────────────┬────────────────────┘
                     │
┌────────────────────▼────────────────────┐
│      FastAPI Backend (8000)             │
│  ├── Auth (signup/login)                │
│  ├── Deal endpoints                     │
│  ├── Property endpoints                 │
│  └── Alert endpoints                    │
└────────────────────┬────────────────────┘
                     │
┌────────────────────▼────────────────────┐
│      PostgreSQL Database                │
│  ├── Users                              │
│  ├── Deals                              │
│  ├── Properties                         │
│  └── Alerts                             │
└─────────────────────────────────────────┘
```

---

## File Structure

```
deal-intelligence/
├── QUICKSTART.md              ← This file
├── SETUP.md                   ← Full setup guide
├── ARCHITECTURE.md            ← Technical details
├── WEEK1_ACTION_PLAN.md       ← Daily checklist
├── requirements.txt           ← Python dependencies
├── .env.template              ← Environment variables
├── .gitignore                 ← Git ignore rules
├── main.py                    ← FastAPI app
├── models.py                  ← Database models
├── scoring_engine.py          ← Claude AI scoring
├── scraping_service.py        ← Data collection
├── test_api.py                ← Unit tests
├── Dockerfile                 ← Container definition
├── docker-compose.yml         ← Local dev stack
├── 001_initial_schema.sql     ← Database schema
└── ci_cd.yml                  ← GitHub Actions workflow
```

---

## Support

- **Documentation**: See SETUP.md for full guide
- **Code**: All files have inline comments
- **Issues**: Check TROUBLESHOOTING section above
- **Help**: Ask Claude (me) to debug or generate additional code

---

## What to Do Now

**Choose one:**

**Option A: Get running locally (5 min)**
```bash
# Follow OPTION 1 above
```

**Option B: Use Docker (5 min)**
```bash
# Follow OPTION 2 above
```

**Option C: Deploy to AWS (20 min)**
```bash
# Follow OPTION 3 above
```

---

🚀 **Ready? Let's go!**

Run `python main.py` and open http://localhost:8000/docs

---

For detailed documentation, see:
- Full setup guide: `SETUP.md`
- Daily action plan: `WEEK1_ACTION_PLAN.md`
- Technical architecture: `ARCHITECTURE.md`

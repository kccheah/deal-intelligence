# Cross-Border Deal Intelligence + Property DD Platform
## Technical Architecture (Solo Founder Build)

---

## 1. SYSTEM OVERVIEW

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                            │
│  (React Dashboard: Deal Intel + Property DD Modules)             │
└──────────────────────┬──────────────────────────────────────────┘
                       │
        ┌──────────────┴───────────────┐
        │                              │
   ┌────▼─────────┐          ┌────────▼──────┐
   │  Deal Intel  │          │  Property DD  │
   │   Module     │          │    Module     │
   └────┬─────────┘          └────────┬──────┘
        │                              │
        └──────────────┬───────────────┘
                       │
        ┌──────────────▼───────────────────┐
        │      API Layer (FastAPI)         │
        │  - Authentication                │
        │  - Data endpoints                │
        │  - Scoring engine                │
        │  - Alert management              │
        └──────────────┬───────────────────┘
                       │
   ┌───────────────────┼───────────────────┐
   │                   │                   │
┌──▼──────────┐  ┌─────▼─────┐  ┌────────▼──┐
│   Database  │  │ Scraping   │  │ Scoring   │
│ (PostgreSQL)│  │ Pipeline   │  │ Engine    │
└─────────────┘  │ (Scheduled)│  │(Claude AI)│
                 └────────────┘  └───────────┘
                       │
        ┌──────────────▼───────────────┐
        │  Data Sources                 │
        │  - M&A databases (API)        │
        │  - News feeds (RSS/API)       │
        │  - Regulatory filings         │
        │  - Property records           │
        └───────────────────────────────┘
```

---

## 2. DATABASE SCHEMA

### Core Tables (Unified)

```sql
-- Users & Subscriptions
users
├── id (PK)
├── email (unique)
├── password_hash
├── company_name
├── subscription_tier (deal_intel | property_dd | bundle)
├── status (active | trial | paused | cancelled)
├── stripe_customer_id
├── created_at
├── updated_at

-- Deal Intelligence Data
deals
├── id (PK)
├── external_source_id (unique per source)
├── source (crunchbase | preqin | pitchbook | news)
├── deal_type (ma | pe | jv | fdi)
├── company_name
├── industry
├── deal_value_usd
├── announced_date
├── target_geography (country_code)
├── acquiring_company
├── deal_description
├── raw_data (JSON - original source data)
├── score (1-100)
├── score_breakdown (JSON - {sector: 20, geo: 30, ...})
├── created_at

-- Property Data
properties
├── id (PK)
├── external_source_id (unique per source)
├── source (dubai_land_dept | thailand_condo | sg_ura | etc)
├── property_type (residential | commercial | industrial)
├── location
├── country_code
├── price_usd
├── size_sqm
├── year_built
├── ownership_legal_status (freehold | leasehold | restricted)
├── dd_status (pending | completed | flagged)
├── dd_data (JSON - legal, tax, regulatory, risk scores)
├── investment_score (1-100)
├── created_at

-- User Alerts & Subscriptions
user_alerts
├── id (PK)
├── user_id (FK)
├── alert_type (deal | property)
├── criteria (JSON - {sector: [...], geo: [...], value_min: ...})
├── frequency (realtime | daily | weekly)
├── enabled
├── created_at

-- Scoring History (for A/B testing)
scoring_history
├── id (PK)
├── deal_id or property_id
├── version
├── score
├── methodology (JSON)
├── created_at
```

### Indexes
- `deals(source, external_source_id)` - prevent duplicates
- `deals(announced_date DESC)` - recency
- `deals(score DESC)` - sorting
- `properties(country_code, property_type)` - filtering
- `user_alerts(user_id, enabled)` - alert queries

---

## 3. API STRUCTURE

### Authentication
```
POST   /auth/signup         - Register
POST   /auth/login          - Login (JWT)
POST   /auth/refresh        - Refresh token
POST   /auth/logout         - Logout
```

### Deal Intelligence
```
GET    /deals               - List deals (paginated, filtered)
GET    /deals/{id}          - Deal details + reasoning
GET    /deals/search        - Search by criteria (sector, geo, value)
POST   /deals/filter        - Advanced filtering
GET    /deals/trending      - Top deals this week
```

### Property DD
```
GET    /properties          - List properties (filtered)
GET    /properties/{id}     - Property + full DD report
POST   /properties/upload   - Upload property for analysis
GET    /properties/{id}/dd  - Detailed due diligence report
```

### User Alerts
```
POST   /alerts              - Create alert
GET    /alerts              - List user's alerts
PUT    /alerts/{id}         - Update alert criteria
DELETE /alerts/{id}         - Delete alert
GET    /alerts/{id}/history - Alert triggers history
```

### User & Subscription
```
GET    /user/profile        - User info
PUT    /user/profile        - Update profile
GET    /user/subscription   - Current plan + usage
POST   /user/upgrade        - Upgrade plan
```

---

## 4. DATA PIPELINE ARCHITECTURE

### Deal Intelligence Flow

```
SOURCES:
├── CrunchBase API (monthly refresh)
├── News APIs (daily, RSS feeds)
├── Preqin data (if budget allows, else free tiers)
├── LinkedIn Jobs API (signals of activity)
└── Regulatory filings (quarterly)

         ↓
    EXTRACTION LAYER (Python + Claude)
├── Download raw data
├── Parse & normalize
├── Deduplication (by external_source_id + date)
└── Store raw data in DB
    
         ↓
    ENRICHMENT LAYER (Claude AI)
├── Extract key entities (companies, geographies, sectors)
├── Classify deal type (M&A vs PE vs JV vs FDI)
├── Identify strategic fit (based on user criteria)
└── Generate summary + reasoning

         ↓
    SCORING LAYER (Rules + Claude)
├── Risk assessment (political, regulatory, market)
├── Sector attractiveness (1-100)
├── Geography fit (1-100)
├── Deal size scoring (1-100)
├── Strategic alignment (1-100)
├── FINAL SCORE = Weighted average
└── Store score + breakdown

         ↓
    ALERT LAYER
├── Check against user alert criteria
├── Match user's sector/geo/value preferences
├── Generate alert message (Claude)
└── Send via email + dashboard notification
```

### Property DD Flow

```
INPUT: Property listing or address

         ↓
    DATA GATHERING LAYER
├── Public records lookup
├── Regulatory status check (ownership restrictions)
├── Tax & depreciation info
├── Title/lien search
├── Building permits & compliance
└── Store all findings

         ↓
    ANALYSIS LAYER (Claude)
├── Legal review (restrictive clauses, covenants)
├── Regulatory risk (capital restrictions, FDI rules)
├── Tax implications (withholding, treaty benefits)
├── Structural assessment (if available)
├── Market comparables (if available)

         ↓
    SCORING LAYER
├── Investment viability (1-100)
├── Risk level (high/medium/low)
├── Timeline to acquisition (est. months)
├── Regulatory compliance (flags vs green)
└── ROI estimate (if data available)

         ↓
    REPORTING LAYER
├── Generate DD report (PDF + JSON)
├── Highlight red flags
├── Provide acquisition timeline
└── Store for user dashboard
```

### Scheduling
```
Scheduled Tasks (AWS Lambda):
├── 2x daily: News/RSS scraping (6am, 6pm Dubai time)
├── Weekly: CrunchBase refresh (Sunday 2am)
├── Hourly: Check alerts, send notifications
├── Daily: Scoring re-runs (1am Dubai time)
└── Monthly: Data quality audit + duplicate cleanup
```

---

## 5. TECH STACK SPECIFICATION

| Component | Technology | Why |
|---|---|---|
| **Backend** | Python 3.11 + FastAPI | Claude generates FastAPI code quickly; fast, modern |
| **Database** | PostgreSQL 15 (AWS RDS) | Managed, scalable, JSON support for scoring/data |
| **Frontend** | React 18 + TypeScript | Claude generates components; strong ecosystem |
| **Hosting** | AWS (RDS + Lambda + EC2/Fargate) | Managed services, minimal DevOps |
| **AI Integration** | Claude API + Gemini API | Claude for reasoning/scoring, Gemini for bulk analysis |
| **Data Scraping** | Selenium + BeautifulSoup (Python) | Fast, Claude can generate scrapers |
| **Authentication** | Auth0 or JWT + PostgreSQL | Managed auth, can add OAuth later |
| **Payments** | Stripe API | Easiest to integrate, Claude knows Stripe well |
| **Notifications** | SendGrid (email) + WebSocket (real-time) | Reliable, scalable |
| **Deployment** | Docker + GitHub Actions | CI/CD automation, easy to redeploy |
| **Monitoring** | Sentry + CloudWatch | Error tracking, performance monitoring |

---

## 6. DEPLOYMENT ARCHITECTURE

### Development Environment
```
Local:
├── Python venv
├── PostgreSQL (Docker)
├── React dev server
└── .env with API keys
```

### Staging Environment
```
AWS:
├── RDS PostgreSQL (small instance)
├── Lambda (scheduled scraping jobs)
├── EC2 t2.micro or Fargate (API server)
├── CloudFront (CDN for frontend)
└── S3 (static assets + generated reports)
```

### Production Environment
```
AWS:
├── RDS PostgreSQL (multi-AZ, automated backups)
├── Lambda (scheduled jobs, autoscaling)
├── Fargate (containerized API, autoscaling)
├── CloudFront (global CDN)
├── S3 (static assets + reports)
├── SQS (queue for long-running tasks)
├── CloudWatch (monitoring + alarms)
└── Route53 (DNS)
```

### Deployment Pipeline
```
1. Commit to GitHub
2. GitHub Actions triggers:
   ├── Run tests
   ├── Build Docker image
   ├── Push to AWS ECR
   ├── Deploy to staging
   ├── Smoke tests
   └── (On approval) Deploy to production
```

---

## 7. AUTHENTICATION & SECURITY

### User Authentication
- JWT tokens (15 min expiry)
- Refresh tokens (7 days)
- Password hashing (bcrypt)
- Rate limiting (100 requests/min per user)

### API Security
- TLS/SSL encryption
- CORS (frontend domain only)
- Input validation (FastAPI pydantic)
- SQL injection prevention (parameterized queries)
- XSS prevention (React/TypeScript)

### Data Security
- Password hashing (bcrypt)
- Encrypted API keys in environment variables
- Database encryption at rest (AWS RDS)
- Backups encrypted (S3)
- No storing sensitive data (SSN, ID numbers, etc.)

---

## 8. SCALABILITY CONSIDERATIONS

### Current (MVP)
- 1 backend instance (Fargate)
- 1 RDS instance (small)
- Handles ~100 concurrent users
- ~10K deals + properties in DB

### Year 1 (10K users)
- Auto-scaling Fargate (2-5 instances)
- RDS read replicas for heavy queries
- Separate queue (SQS) for scraping jobs
- Redis cache for frequent queries
- Handles ~10K concurrent users

### Year 2+ (100K users)
- Global CDN (CloudFront)
- Database sharding by geography
- Separate microservices (scraping, scoring, alerts)
- Kafka for event streaming
- Machine learning pipeline for scoring

---

## 9. EXTERNAL API INTEGRATIONS

### Data Sources (MVP)
| Source | API/Method | Cost | Frequency |
|---|---|---|---|
| **CrunchBase** | API (free tier) | Free (limited) | Monthly |
| **News** | Google News API + RSS | Free | Daily |
| **Preqin** | API (free tier) or web scrape | Free-$500/mo | Monthly |
| **LinkedIn** | RSS feeds (job postings) | Free | Daily |
| **Property Data** | Public APIs (country-specific) | Free-$200/mo | Monthly |

### Service Integrations
| Service | Purpose | Cost |
|---|---|---|
| **Stripe** | Payments | 2.9% + $0.30 per transaction |
| **SendGrid** | Email | Free tier (100/day), $20/mo for more |
| **Auth0** | Authentication | Free tier, $13/mo for MFA |
| **Sentry** | Error tracking | Free tier, $29/mo for more |
| **Gemini API** | Data analysis | $10-50/mo (pay-per-use) |
| **Claude API** | Scoring/reasoning | $10-100/mo (pay-per-use) |

**Total external costs (MVP): ~$500-800/month**

---

## 10. MVPS FEATURE SET

### Deal Intelligence MVP
- ✅ Scrape 3 deal sources (News API, CrunchBase free, RSS)
- ✅ Basic deal scoring (sector, geography, size)
- ✅ Dashboard (list view, filter by score)
- ✅ User alerts (sector + geo matching)
- ✅ Email notifications
- ✅ Basic auth (signup/login)
- ✅ Stripe integration (Pay-per-deal or subscription)
- ❌ Advanced analytics
- ❌ Custom scoring rules
- ❌ API for customers
- ❌ Mobile app

### Property DD MVP
- ✅ Property data input (address or listing)
- ✅ Regulatory status check (basic API lookup)
- ✅ DD checklist (legal, tax, regulatory)
- ✅ Risk scoring (high/medium/low)
- ✅ PDF report generation
- ✅ Store DD reports in user dashboard
- ❌ Automated title searches
- ❌ Architectural assessment
- ❌ Valuation estimates
- ❌ Market comparable analysis

---

## 11. CLAUDE AI INTEGRATION POINTS

| Task | How Claude Helps | Integration |
|---|---|---|
| **Deal Analysis** | Read deal description → Extract strategic insights → Score fit | Claude API (text input) |
| **Deal Summarization** | Generate 3-sentence summary of each deal | Claude API (batch) |
| **Property Legal Review** | Analyze contract/terms → Flag legal risks | Claude API (document input) |
| **Scoring Reasoning** | Explain why deal scored 75/100 | Claude API (reasoning output) |
| **Alert Message Generation** | Write personalized alert emails | Claude API (templating) |
| **DD Report Generation** | Structure findings into professional report | Claude API (formatting) |
| **Regulatory Analysis** | Assess FDI/capital restrictions by country | Claude API (knowledge base) |
| **Competitor Analysis** | Compare this deal to market benchmarks | Claude API (data synthesis) |

**Usage estimate:** ~$40-80/month (small volume, MVP)

---

## 12. DATA FLOW EXAMPLE

### Scenario: New M&A Deal Announced in Thailand

```
1. News API returns headline:
   "Thai tech startup XYZ acquired by Vietnamese PE firm"

2. Scraping service extracts:
   - Company: XYZ
   - Geography: Thailand
   - Deal type: M&A (inferred)
   - Sector: Tech
   - Deal value: $15M (extracted)

3. Enrichment (Claude):
   "XYZ is a Series B fintech focused on BNPL in SE Asia.
    This M&A signals strong exit opportunity in regional fintech.
    Vietnamese PE firm entering Thai market (geographic expansion signal)."

4. Scoring:
   - Sector attractiveness (Tech in ASEAN): 80/100
   - Geography (Thailand emerging market): 75/100
   - Deal size ($10M-50M sweet spot): 85/100
   - Strategic insight (PE entry signal): 70/100
   - FINAL SCORE: 78/100

5. Alert matching:
   - User A (interested in Thailand tech): ✅ Match
   - User B (interested in Vietnam only): ❌ No match

6. Alert sent to User A:
   Email: "🎯 High-confidence deal match: Thai tech M&A (78/100)"
   Dashboard: Deal appears in their feed with reasoning

7. User can:
   - Save deal for later
   - View full analysis + Claude's reasoning
   - Export to PDF
```

---

## 13. DEPLOYMENT CHECKLIST

**Week 0 (Setup):**
- [ ] AWS account + RDS + Fargate setup
- [ ] GitHub repo created
- [ ] GitHub Actions workflow configured
- [ ] Environment variables configured (.env)
- [ ] Stripe account + API keys
- [ ] SendGrid account + email templates

**Week 1 (Backend Infrastructure):**
- [ ] FastAPI scaffold generated by Claude
- [ ] Database migrations created
- [ ] Auth endpoints (signup/login)
- [ ] Stripe integration
- [ ] SendGrid integration
- [ ] Deployed to staging

**Week 2 (Frontend):**
- [ ] React components generated
- [ ] Dashboard pages (deals, properties, alerts, user)
- [ ] Styling + responsive design
- [ ] API integration
- [ ] Deployed to staging

**Week 3 (Scraping + Scoring):**
- [ ] Scraping service (Python)
- [ ] Claude scoring integration
- [ ] Alert matching logic
- [ ] Email sending
- [ ] Scheduled jobs (Lambda)

**Week 4 (Testing + Launch):**
- [ ] End-to-end testing
- [ ] Load testing
- [ ] Security audit
- [ ] Deploy to production
- [ ] Invite beta customers

---

## 14. COST BREAKDOWN (Monthly, MVP)

| Item | Cost | Notes |
|---|---|---|
| AWS RDS (small) | $20 | Managed PostgreSQL |
| AWS Fargate | $30 | Container orchestration |
| AWS Lambda | $5 | Scheduled scraping |
| AWS S3 + CloudFront | $10 | Static assets + reports |
| Stripe | Variable | 2.9% + $0.30 per transaction |
| SendGrid | $20 | Email service |
| Claude API | $50 | Scoring + analysis |
| Gemini API | $20 | Bulk data processing |
| Domain + SSL | $2 | Annual, monthly estimate |
| **TOTAL** | **$157 + transaction fees** | Scales with customer growth |

**Gross margin on $999 subscription: ~77%**

---

## REVIEW CHECKLIST

- [ ] Database schema makes sense?
- [ ] API endpoints sufficient for MVP?
- [ ] Data flow clear?
- [ ] Tech stack appropriate for solo build?
- [ ] Deployment strategy realistic?
- [ ] Scalability path clear?
- [ ] Security considerations covered?
- [ ] Cost reasonable?

**Changes needed?** Reply with specifics and I'll revise before code generation.

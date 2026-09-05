"""
Main FastAPI Application
Deal Intelligence + Property DD Platform
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# DATABASE SETUP
# ============================================================================

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set in .env")

engine = create_engine(
    DATABASE_URL,
    echo=os.getenv("DEBUG", "false").lower() == "true",
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================================
# APP INITIALIZATION
# ============================================================================

app = FastAPI(
    title="Deal Intelligence API",
    description="Cross-border deal intelligence + property due diligence platform",
    version="0.1.0",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "deal-intelligence-api",
        "version": "0.1.0"
    }

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"

class UserSignUp(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    company_name: str = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

@app.post("/auth/signup", response_model=Token)
async def signup(user_data: UserSignUp, db: Session = Depends(get_db)):
    """Register new user"""
    # Import here to avoid circular imports
    from models import User

    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    hashed_password = pwd_context.hash(user_data.password)

    # Create user
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        company_name=user_data.company_name,
        subscription_tier="trial",
        subscription_status="active",
        trial_ends_at=datetime.utcnow() + timedelta(days=14)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate token
    access_token = create_access_token(data={"sub": str(new_user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 900  # 15 minutes
    }

@app.post("/auth/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login user"""
    from models import User

    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not pwd_context.verify(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Update last login
    user.last_login_at = datetime.utcnow()
    db.commit()

    # Generate token
    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 900
    }

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ============================================================================
# DEAL INTELLIGENCE ENDPOINTS
# ============================================================================

from typing import List, Optional

class DealResponse(BaseModel):
    id: str
    company_name: str
    deal_type: str
    deal_value_usd: int
    announced_date: str
    target_geography: str
    score: int
    score_breakdown: dict
    deal_description: str

    class Config:
        from_attributes = True

@app.get("/deals", response_model=List[DealResponse])
async def list_deals(
    skip: int = 0,
    limit: int = 20,
    sector: Optional[str] = None,
    geography: Optional[str] = None,
    min_score: Optional[int] = None,
    sort_by: str = "score",
    db: Session = Depends(get_db),
    token: str = Depends(lambda: "")
):
    """List deals with filtering"""
    from models import Deal

    query = db.query(Deal)

    if sector:
        query = query.filter(Deal.industry == sector)
    if geography:
        query = query.filter(Deal.target_geography == geography)
    if min_score:
        query = query.filter(Deal.score >= min_score)

    if sort_by == "score":
        query = query.order_by(Deal.score.desc())
    elif sort_by == "date":
        query = query.order_by(Deal.announced_date.desc())

    deals = query.offset(skip).limit(limit).all()
    return deals

@app.get("/deals/{deal_id}", response_model=DealResponse)
async def get_deal(deal_id: str, db: Session = Depends(get_db)):
    """Get deal details"""
    from models import Deal

    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    return deal

@app.get("/deals/trending")
async def trending_deals(
    days: int = 7,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get trending deals"""
    from models import Deal
    from datetime import datetime, timedelta

    start_date = datetime.utcnow() - timedelta(days=days)

    deals = db.query(Deal)\
        .filter(Deal.announced_date >= start_date)\
        .order_by(Deal.score.desc())\
        .limit(limit)\
        .all()

    return deals

# ============================================================================
# PROPERTY DD ENDPOINTS
# ============================================================================

class PropertyDDResponse(BaseModel):
    id: str
    address: str
    city: str
    country_code: str
    property_type: str
    price_usd: int
    investment_score: int
    risk_level: str
    dd_status: str
    dd_data: dict

    class Config:
        from_attributes = True

@app.get("/properties", response_model=List[PropertyDDResponse])
async def list_properties(
    skip: int = 0,
    limit: int = 20,
    country: Optional[str] = None,
    property_type: Optional[str] = None,
    min_score: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """List properties with filtering"""
    from models import Property

    query = db.query(Property)

    if country:
        query = query.filter(Property.country_code == country)
    if property_type:
        query = query.filter(Property.property_type == property_type)
    if min_score:
        query = query.filter(Property.investment_score >= min_score)

    properties = query.offset(skip).limit(limit).all()
    return properties

@app.get("/properties/{property_id}", response_model=PropertyDDResponse)
async def get_property(property_id: str, db: Session = Depends(get_db)):
    """Get property DD report"""
    from models import Property

    prop = db.query(Property).filter(Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    return prop

# ============================================================================
# ALERTS ENDPOINTS
# ============================================================================

class CreateAlertRequest(BaseModel):
    alert_name: str
    alert_type: str  # deal | property | both
    criteria: dict
    frequency: str = "realtime"

class AlertResponse(BaseModel):
    id: str
    alert_name: str
    alert_type: str
    criteria: dict
    frequency: str
    enabled: bool

    class Config:
        from_attributes = True

@app.post("/alerts", response_model=AlertResponse)
async def create_alert(
    alert_data: CreateAlertRequest,
    db: Session = Depends(get_db),
    token: str = Depends(lambda: "")
):
    """Create alert for user"""
    from models import UserAlert

    user_id = verify_token(token) if token else None
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    new_alert = UserAlert(
        user_id=user_id,
        alert_name=alert_data.alert_name,
        alert_type=alert_data.alert_type,
        criteria=alert_data.criteria,
        frequency=alert_data.frequency,
        enabled=True
    )
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)

    return new_alert

@app.get("/alerts", response_model=List[AlertResponse])
async def list_alerts(
    db: Session = Depends(get_db),
    token: str = Depends(lambda: "")
):
    """List user's alerts"""
    from models import UserAlert

    user_id = verify_token(token) if token else None
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    alerts = db.query(UserAlert).filter(UserAlert.user_id == user_id).all()
    return alerts

# ============================================================================
# USER ENDPOINTS
# ============================================================================

@app.get("/user/profile")
async def get_user_profile(
    db: Session = Depends(get_db),
    token: str = Depends(lambda: "")
):
    """Get user profile"""
    from models import User

    user_id = verify_token(token) if token else None
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": str(user.id),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "company_name": user.company_name,
        "subscription_tier": user.subscription_tier,
        "subscription_status": user.subscription_status
    }

# ============================================================================
# ERROR HANDLING
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "error": exc.detail,
        "status_code": exc.status_code
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

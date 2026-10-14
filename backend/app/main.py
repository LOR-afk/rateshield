from datetime import timedelta
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from .config import settings
from .database import SessionLocal
from .limiter import SlidingWindowLimiter
from .models import Policy, SecurityEvent, utcnow
from .schemas import DemoLogin, EventOut, PolicyOut, PolicyUpdate

app = FastAPI(title="RateShield", version="0.1.0", openapi_version="3.1.0")
app.add_middleware(CORSMiddleware, allow_origins=[x.strip() for x in settings.cors_origins.split(",")], allow_methods=["GET", "POST", "PUT"], allow_headers=["Content-Type"])
limiter = SlidingWindowLimiter()


def db_session():
    with SessionLocal() as session:
        yield session


def policy_for(db: Session):
    policy = db.get(Policy, 1)
    if policy is None:
        policy = Policy(id=1, max_requests=10, window_seconds=60, failed_login_threshold=4)
        db.add(policy)
        db.commit()
        db.refresh(policy)
    return policy


def client_ip(request: Request):
    return request.client.host if request.client else "unknown"


def record(db: Session, ip: str, kind: str, endpoint: str, code: int, detail: str):
    event = SecurityEvent(client_ip=ip, kind=kind, endpoint=endpoint, status_code=code, detail=detail)
    db.add(event)
    db.commit()
    return event


def local_demo_only(request: Request):
    if not settings.demo_mode or client_ip(request) not in ("127.0.0.1", "::1", "testclient"):
        raise HTTPException(403, "Demo mode is restricted to local requests")


@app.get("/api/health")
def health():
    return {"status": "ok", "demo_mode": settings.demo_mode}


@app.get("/api/policy", response_model=PolicyOut)
def get_policy(db: Session = Depends(db_session)):
    return policy_for(db)


@app.put("/api/policy", response_model=PolicyOut)
def update_policy(data: PolicyUpdate, request: Request, db: Session = Depends(db_session)):
    local_demo_only(request)
    p = policy_for(db)
    for k, v in data.model_dump().items():
        setattr(p, k, v)
    db.commit()
    db.refresh(p)
    limiter.reset()
    return p


@app.get("/api/events", response_model=list[EventOut])
def events(request: Request, db: Session = Depends(db_session)):
    local_demo_only(request)
    return db.scalars(select(SecurityEvent).order_by(SecurityEvent.id.desc()).limit(100)).all()


@app.get("/api/summary")
def summary(request: Request, db: Session = Depends(db_session)):
    local_demo_only(request)
    rows = db.scalars(select(SecurityEvent).order_by(SecurityEvent.id.desc()).limit(1000)).all()
    ips = sorted(set(x.client_ip for x in rows))
    clients = []
    for ip in ips:
        matches = [x for x in rows if x.client_ip == ip]
        blocked = sum(x.kind == "rate_limited" for x in matches)
        failures = sum(x.kind == "login_failure" for x in matches)
        score = min(100, blocked * 25 + failures * 15)
        clients.append({"client_ip": ip, "risk_score": score, "blocked": blocked, "login_failures": failures, "events": len(matches)})
    clients.sort(key=lambda x: x["risk_score"], reverse=True)
    return {"total_events": len(rows), "blocked_requests": sum(x.kind == "rate_limited" for x in rows), "login_failures": sum(x.kind == "login_failure" for x in rows), "clients": clients}


@app.get("/api/protected/ping")
def protected_ping(request: Request, db: Session = Depends(db_session)):
    p = policy_for(db)
    ip = client_ip(request)
    allowed, remaining, retry_after = limiter.check(ip, p.max_requests, p.window_seconds)
    if not allowed:
        record(db, ip, "rate_limited", "/api/protected/ping", 429, "Request limit exceeded")
        return JSONResponse(status_code=429, headers={"Retry-After": str(retry_after), "X-RateLimit-Remaining": "0"}, content={"detail": "Too many requests", "retry_after": retry_after})
    record(db, ip, "request", "/api/protected/ping", 200, "Request allowed")
    return JSONResponse(content={"message": "Request allowed", "remaining": remaining}, headers={"X-RateLimit-Remaining": str(remaining)})


@app.post("/api/demo/login")
def demo_login(data: DemoLogin, request: Request, db: Session = Depends(db_session)):
    local_demo_only(request)
    ip = client_ip(request)
    p = policy_for(db)
    if data.success:
        record(db, ip, "login_success", "/api/demo/login", 200, "Simulated login successful")
        return {"message": "Simulated login successful"}
    since = utcnow() - timedelta(minutes=15)
    failures = db.scalar(select(func.count(SecurityEvent.id)).where(SecurityEvent.client_ip == ip, SecurityEvent.kind == "login_failure", SecurityEvent.created_at >= since)) or 0
    record(db, ip, "login_failure", "/api/demo/login", 401, "Simulated invalid credentials")
    if failures + 1 >= p.failed_login_threshold:
        record(db, ip, "suspicious_login", "/api/demo/login", 200, "Failed login threshold reached")
    return JSONResponse(status_code=401, content={"detail": "Simulated invalid credentials", "suspicious": failures + 1 >= p.failed_login_threshold})

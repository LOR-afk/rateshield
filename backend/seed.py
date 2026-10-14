from app.database import SessionLocal
from app.main import policy_for

with SessionLocal() as db:
    policy_for(db)
print("Default policy initialized")

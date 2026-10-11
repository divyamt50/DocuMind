import os
from dotenv import load_dotenv
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY not present in the .env")

ALGORITHM = "HSA256"
TOKEN_ACTIVE_TIME = 30


password_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password:str)->str:
    return password_context.hash(password)

def check_password(input_password:str, hashed_password:str)->bool:
    return password_context.verify(input_password, hashed_password)

def generate_jwt(*,tenant_id:str, user_id:str)->str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub":user_id,
        "tenant_id":tenant_id,
        "iat":now,
        "exp":now+timedelta(minutes=TOKEN_ACTIVE_TIME)
    }

    return jwt.encode(payload, JWT_SECRET_KEY,algorithm=ALGORITHM)

def verify_jwt(jwt_token:str)->bool:
    return jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
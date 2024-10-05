from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import os
import aiosqlite

SECRET_KEY = os.environ.get("SECRET_KEY", "fallback-secret-key")
if SECRET_KEY == "fallback-secret-key": print("Using fallback secret key.")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

DATABASE = 'users.db'

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Correct the table creation to `users`
async def init_db():
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                uid INTEGER NOT NULL
            )
        ''')
        await db.commit()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

async def authenticate_user(username: str, password: str):
    async with aiosqlite.connect(DATABASE) as db:
        async with db.execute("SELECT * FROM users WHERE username = ?", (username,)) as cursor:
            user = await cursor.fetchone()
            if user is None:
                return False
            stored_hashed_password = user[2]
            if not verify_password(password, stored_hashed_password):
                return False
            return {"username": user[1], "uid": user[3]} 

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    async with aiosqlite.connect(DATABASE) as db:
        async with db.execute("SELECT * FROM users WHERE username = ?", (username,)) as cursor:
            user = await cursor.fetchone()
            if user is None:
                raise credentials_exception
            return {"username": user[1], "uid": user[3]}

# -*- coding: utf-8 -*-
"""
Created on Thu Nov 23 15:18:13 2023

@author: aikan
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
import uvicorn
import bcrypt
from typing import Literal
from pydantic import BaseModel

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class User(BaseModel):
    nom: str
    prenom: str
    pseudo: str
    email: str
    password: str
    disabled: bool = False
    licence: Literal["étudiant", "premium", "entreprise"]

class UserInDB(User):
    hashed_password: str
    
# Secret key should be kept secret!
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

indicators = {
    "RSI": [{
        "value": 42.7,
        "date": "2023-11-23",
        "crypto": "BTC"
    },
        {"value": 35.6,
        "date": "2023-12-23",
        "crypto": "BTC"},
        {"value": 37.9,
        "date": "2023-11-23",
        "crypto": "ETH"}],
    "MACD": [{
        "value": 0.0045,
        "date": "2023-12-23",
        "crypto": "ETH"
    },
        {
            "value": 0.0035,
            "date": "2023-10-23",
            "crypto": "BTC"
        },
        {
            "value": 0.0026,
            "date": "2023-11-23",
            "crypto": "ETH"
        }]
}

def create_access_token(data: dict):
    encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        return email
    except jwt.PyJWTError:
        raise credentials_exception

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    email = verify_token(token, credentials_exception)
    user = next((u for u in users if u['email'] == email), None)
    if user is None:
        raise credentials_exception
    return UserInDB(**user)


def hash_password(password: str) -> str:
    """Hash a password for storing."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a stored password against one provided by user"""
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = next((u for u in users if u['pseudo'] == form_data.username), None)
    if user and verify_password(form_data.password, user['hashed_password']) and not user['disabled']:
        access_token = create_access_token(data={"sub": user["email"]})
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(status_code=400, detail="Informations d'identification incorrectes ou compte désactivé")

@app.post("/signup")
async def signup(user: User):
    # Ajoutez l'utilisateur à la base de données ici
    return {"message": "User created successfully"}

@app.get("/indicators/rsi")
async def read_rsi(current_user: User = Depends(get_current_user), data = indicators):
    # Vérifiez ici les droits d'accès de l'utilisateur
    # puis retournez les données RSI
    return {f"data : {data['RSI']}"}

@app.get("/indicators/macd")
async def read_macd(current_user: User = Depends(get_current_user), data = indicators):
    user = next((u for u in users if u['email'] == current_user.email), None)
    if user and user['licence'] != "étudiant":
        return {"data": "MACD data"}
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès interdit pour les utilisateurs avec licence 'étudiant'")


users = [
    {
        "nom": "Dupont",
        "prenom": "Jean",
        "pseudo": "jdupont",
        "email": "jean.dupont@example.com",
        "password" : "password_1",
        "disabled": False,
        "licence": "entreprise"
    },
    {
        "nom": "Martin",
        "prenom": "Alice",
        "pseudo": "amartin",
        "email": "alice.martin@example.com",
        "password" : "password_2",
        "disabled": False,
        "licence": "étudiant"
    },
    {
        "nom": "Leroy",
        "prenom": "Émile",
        "pseudo": "eleroy",
        "email": "emile.leroy@example.com",
        "password" : "password_3",
        "disabled": True,
        "licence": "premium"
    }
]


for user in users:
    user['hashed_password'] = hash_password(user["password"])



# Pour lancer le serveur, aller dans cmd :
# cd C:\Users\morel\PycharmProjects\api_tp4\
# uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Puis aller sur http://127.0.0.1:8000/docs#/ pour avoir le swagger
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt

# Configuration
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

# OAuth2PasswordBearer est utilisé pour gérer les tokens JWT dans les en-têtes
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Simuler une base de données d'utilisateurs
fake_users_db = {
    "john": {
        "username": "john",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "password": "hello",
        "disabled": False,
    }
}


# Pydantic model pour les utilisateurs
class User(BaseModel):
    username: str
    email: str = None
    full_name: str = None
    disabled: bool = None


# Pydantic model pour les utilisateurs stockés en base de données
class UserInDB(User):
    password: str


# Fonction pour obtenir un utilisateur à partir de la base de données
def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


# Fonction pour créer un token JWT
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
        token_data = username
    except jwt.PyJWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data)
    if user is None:
        raise credentials_exception
    return user

# Route pour la création d'un token JWT lors de la connexion
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(fake_users_db, form_data.username)
    if not user or form_data.password != user.password:  # Notez le changement ici
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


# Route protégée nécessitant un token JWT pour accéder
@app.get("/test", response_model=dict)
async def user_can_access_or_not(current_user: User = Depends(get_current_user)):
    return {"message": f"L'utilisateur {current_user.username} est bien connecté"}

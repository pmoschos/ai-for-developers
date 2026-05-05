from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

# The APIRouter is used to group related endpoints together.
# prefix='/auth' means every route here will start with /auth
router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

# Configuration for JWT (JSON Web Token) creation
SECRET_KEY = '197b2c37c391bed93fe80344fe73b806947a65e36206e05a1a23c2fa12702fe3'
ALGORITHM = 'HS256'

# CryptContext is used to hash passwords so we don't store them in plain text
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# OAuth2PasswordBearer extracts the token from the "Authorization: Bearer <token>" header
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

# Pydantic model for receiving user creation data
class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number: str

# Pydantic model for the token response structure
class Token(BaseModel):
    access_token: str
    token_type: str

# Dependency to open and close a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Annotated makes our dependency injection cleaner to read in endpoint signatures
db_dependency = Annotated[Session, Depends(get_db)]

# Helper function to verify a user's credentials against the database mapped user
def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    # Verify checks the provided plain password against the hashed password in the DB
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

# Helper function to generate a secure JWT string
def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id, 'role': role} # This data is embedded inside the token
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires}) # 'exp' tells the token exactly when to expire automatically
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

# Dependency to validate the JWT from the header and extract the current user
async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        # Decode the token using our secret key
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user.')
        return {'username': username, 'id': user_id, 'user_role': user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    # Check if a user with the same username already exists
    existing_user = db.query(Users).filter(Users.username == create_user_request.username).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

    # Check if a user with the same email already exists
    existing_email = db.query(Users).filter(Users.email == create_user_request.email).first()
    if existing_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    # Map the incoming request into our SQLAlchemy User model
    create_user_model = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        hashed_password=bcrypt_context.hash(create_user_request.password), # Hash immediately!
        is_active=True
    )

    db.add(create_user_model)
    db.commit()
    return {'message': 'User created successfully'}

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')
    
    # Issue a 20-minute access token
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))
    return {'access_token': token, 'token_type': 'bearer'}







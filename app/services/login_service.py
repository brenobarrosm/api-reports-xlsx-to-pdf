from jose import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

from app.entities.user import LoginRequest, Token
from app.exceptions.invalid_user_credentials_exception import InvalidUserCredentialsException
from app.utils.database import db
from app.utils.settings import settings


class LoginService:
    def __init__(self):
        self.SECRET_KEY = settings.SECRET_KEY
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 60
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.db = db

    def execute(self, login_request: LoginRequest):
        user = self.get_user_by_email(login_request.email)
        if not user or not self.verify_password(login_request.password, user["hashed_password"]):
            raise InvalidUserCredentialsException

        token_data = {
            "sub": str(user["id"]),
            "email": user["email"]
        }

        access_token = self.create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        return Token(access_token=access_token, token_type="bearer")

    def get_user_by_email(self, email: str):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, email, hashed_password FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()
            if row:
                return {"id": row[0], "email": row[1], "hashed_password": row[2]}
        return None

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()
        expire = datetime.now() + (expires_delta or timedelta(minutes=15))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

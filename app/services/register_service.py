from app.entities.user import RegisterRequest
from app.utils.database import db
from passlib.context import CryptContext
from fastapi import HTTPException, status


class RegisterService:
    def __init__(self):
        self.db = db
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def execute(self, register_request: RegisterRequest):
        try:
            with self.db.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM users WHERE email = ?", (register_request.email,))
                if cursor.fetchone():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="E-mail já está em uso."
                    )
                hashed_password = self.pwd_context.hash(register_request.password)
                cursor.execute(
                    "INSERT INTO users (nome, email, hashed_password) VALUES (?, ?, ?)",
                    (register_request.nome, register_request.email, hashed_password)
                )

            return {"message": "Usuário registrado com sucesso."}

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao registrar o usuário."
            )

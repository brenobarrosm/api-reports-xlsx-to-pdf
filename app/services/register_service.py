from app.entities.user import RegisterRequest
from app.utils.database import db
from passlib.context import CryptContext
from fastapi import HTTPException

class RegisterService:

    def __init__(self):
        self.db = db
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def execute(self, register_request: RegisterRequest):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        print("Tabelas existentes:", cursor.fetchall())
        cursor.execute("SELECT id FROM main.users WHERE email = ?", (register_request.email,))
        if cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=400, detail="E-mail já está em uso.")

        hashed_password = self.pwd_context.hash(register_request.password)

        try:
            cursor.execute(
                "INSERT INTO main.users (nome, email, hashed_password) VALUES (?, ?, ?)",
                (register_request.nome, register_request.email, hashed_password)
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=500, detail="Erro ao registrar o usuário.")
        finally:
            conn.close()

        return {"message": "Usuário registrado com sucesso."}

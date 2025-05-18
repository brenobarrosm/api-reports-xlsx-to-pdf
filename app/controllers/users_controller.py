from fastapi import APIRouter

from app.entities.user import LoginRequest, RegisterRequest
from app.services.login_service import LoginService
from app.services.register_service import RegisterService

router = APIRouter(prefix='/users')

login_service = LoginService()
register_service = RegisterService()


@router.post("/login")
def login(login_request: LoginRequest):
    return login_service.execute(login_request)

@router.post("/register")
def register(register_request: RegisterRequest):
    return register_service.execute(register_request)


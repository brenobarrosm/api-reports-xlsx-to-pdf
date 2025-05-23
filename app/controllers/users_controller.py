from fastapi import APIRouter, Header, HTTPException, Depends
from starlette import status

from app.entities.user import LoginRequest, RegisterRequest
from app.services.login_service import LoginService
from app.services.register_service import RegisterService
from app.utils.settings import settings

router = APIRouter(prefix='/users')

login_service = LoginService()
register_service = RegisterService()

def validate_api_key(api_key: str = Header(..., alias="X-API-Key")):
    expected_key = settings.SECRET_KEY
    if api_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )

@router.post("/login")
def login(login_request: LoginRequest):
    return login_service.execute(login_request)

@router.post("/register", dependencies=[Depends(validate_api_key)])
def register(register_request: RegisterRequest):
    return register_service.execute(register_request)

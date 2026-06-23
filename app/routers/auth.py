from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.user import RegisterRequest, LoginRequest, TokenResponse
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository
from app.core.dependencies import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


def _service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(UserRepository(db))


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, service: AuthService = Depends(_service)):
    result = service.register(body.username, body.password)
    if not result.is_success:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=result.error)


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, service: AuthService = Depends(_service)):
    result = service.login(body.username, body.password)
    if not result.is_success:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=result.error)
    return result.value

from app.core.result import Result
from app.core.security import hash_password, verify_password, create_access_token
from app.repositories.user_repository import UserRepository
from app.schemas.user import TokenResponse


class AuthService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def register(self, username: str, password: str) -> Result[None]:
        if self.repo.find_by_username(username):
            return Result.fail("Username already taken")
        self.repo.create(username=username, password_hash=hash_password(password))
        return Result.ok()

    def login(self, username: str, password: str) -> Result[TokenResponse]:
        user = self.repo.find_by_username(username)
        if not user or not verify_password(password, user.password_hash):
            return Result.fail("Invalid credentials")
        token = create_access_token({"sub": str(user.id)})
        return Result.ok(TokenResponse(access_token=token))

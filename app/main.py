from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.session import Base, engine, SessionLocal
from app.routers import auth, users
from app.routers import ava_acompanhamento, ava_format_generator
from app.models.user import User
from app.core.security import hash_password
from app.config import settings

Base.metadata.create_all(bind=engine)

# Cria um usuário padrão caso o banco de dados acabe de ser criado (ou se ele não existir)
with SessionLocal() as db:
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        new_admin = User(username="admin", password_hash=hash_password("admin123"))
        db.add(new_admin)
        db.commit()

app = FastAPI(
    title="SigmaEdu API",
    description="API para a plataforma SigmaEdu.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(ava_acompanhamento.router)
app.include_router(ava_format_generator.router)

from fastapi import FastAPI
from app.database.session import Base, engine
from app.routers import auth, users

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SigmaEdu API",
    description="API para a plataforma SigmaEdu.",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(users.router)

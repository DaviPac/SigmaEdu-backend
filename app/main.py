import json
import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.security import hash_password
from app.database.session import Base, SessionLocal, engine
from app.models.questao import Questao, QuestaoAlternativa, QuestaoArquivo
from app.models.user import User
from app.routers import auth, ava_acompanhamento, ava_format_generator, questoes, users

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("startup")

# ── Cria tabelas ────────────────────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ── Seed: usuário admin ─────────────────────────────────────────────────────────
with SessionLocal() as db:
    if not db.query(User).filter(User.username == "admin").first():
        db.add(User(username="admin", password_hash=hash_password("admin123")))
        db.commit()

# ── Seed: banco de questões ENEM ────────────────────────────────────────────────
_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

with SessionLocal() as db:
    if db.query(Questao).count() == 0:
        log.info("Seed: importando questoes do ENEM...")
        total = 0
        for ano in [2020, 2021]:
            json_path = os.path.join(_DATA_DIR, f"enem_{ano}.json")
            if not os.path.exists(json_path):
                log.warning("Arquivo nao encontrado: %s", json_path)
                continue
            log.info("Lendo %s...", json_path)
            with open(json_path, encoding="utf-8") as f:
                questoes_json = json.load(f)
            for q_data in questoes_json:
                if not q_data.get("area") or not q_data.get("pergunta"):
                    continue
                q = Questao(
                    ano=ano,
                    titulo=q_data.get("titulo", ""),
                    area=q_data.get("area"),
                    contexto=q_data.get("contexto"),
                    pergunta=q_data.get("pergunta"),
                    alternativa_correta=q_data.get("alternativa_correta", ""),
                    codigo_competencia=q_data.get("codigo_competencia"),
                    descricao_competencia=q_data.get("descricao_competencia"),
                    subarea=q_data.get("subarea"),
                    arquivos=[
                        QuestaoArquivo(arquivo_base64=b64)
                        for b64 in (q_data.get("arquivos") or [])
                        if b64
                    ],
                    alternativas=[
                        QuestaoAlternativa(
                            letra=a["letra"],
                            texto=a.get("texto"),
                            arquivo_base64=a.get("arquivo_base64"),
                        )
                        for a in (q_data.get("alternativas") or [])
                    ],
                )
                db.add(q)
                total += 1
            db.commit()
            log.info("Ano %d: %d questoes inseridas.", ano, len(questoes_json))
        log.info("Seed concluido: %d questoes no total.", total)

# ── App ─────────────────────────────────────────────────────────────────────────
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
app.include_router(questoes.router)

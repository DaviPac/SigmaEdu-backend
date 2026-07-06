import random
import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.dependencies import get_db
from app.models.questao import Questao, QuestaoAlternativa, QuestaoArquivo
from app.schemas.questao import QuestaoResponse, GrupoInfo, AlternativaResponse

log = logging.getLogger("ava.questoes")
router = APIRouter(prefix="/ava", tags=["questoes"])


def _serialize(q: Questao) -> QuestaoResponse:
    return QuestaoResponse(
        id=q.id,
        ano=q.ano,
        titulo=q.titulo,
        area=q.area,
        contexto=q.contexto,
        pergunta=q.pergunta,
        arquivos=[a.arquivo_base64 for a in q.arquivos],
        alternativas=[
            AlternativaResponse(letra=a.letra, texto=a.texto, arquivo_base64=a.arquivo_base64)
            for a in sorted(q.alternativas, key=lambda x: x.letra)
        ],
        alternativa_correta=q.alternativa_correta,
        codigo_competencia=q.codigo_competencia,
        descricao_competencia=q.descricao_competencia,
        subarea=q.subarea,
    )


# Rota literal antes da parametrizada para evitar colisão de rota
@router.get("/questoes/grupos", response_model=List[GrupoInfo])
def listar_grupos(db: Session = Depends(get_db)):
    rows = (
        db.query(Questao.area, Questao.subarea, func.count(Questao.id))
        .group_by(Questao.area, Questao.subarea)
        .order_by(Questao.area, Questao.subarea)
        .all()
    )
    return [GrupoInfo(area=r[0] or "", subarea=r[1], count=r[2]) for r in rows]


@router.get("/questoes/simulado", response_model=List[QuestaoResponse])
def simulado(
    n: int = Query(10, ge=5, le=15),
    ano: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Retorna N questões aleatórias de todas as áreas para compor um simulado."""
    query = db.query(Questao.id)
    if ano:
        query = query.filter(Questao.ano == ano)
    all_ids = [r[0] for r in query.all()]
    if not all_ids:
        return []
    sampled = random.sample(all_ids, min(n, len(all_ids)))
    questoes = db.query(Questao).filter(Questao.id.in_(sampled)).all()
    return [_serialize(q) for q in questoes]


@router.get("/questoes", response_model=List[QuestaoResponse])
def listar_questoes(
    area: Optional[str] = None,
    subarea: Optional[str] = None,
    ano: Optional[int] = None,
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
):
    """Retorna uma amostra aleatória de questões, opcionalmente filtradas por área/subárea/ano."""
    query = db.query(Questao.id)
    if area:
        query = query.filter(Questao.area == area)
    if subarea:
        query = query.filter(Questao.subarea == subarea)
    if ano:
        query = query.filter(Questao.ano == ano)
    all_ids = [r[0] for r in query.all()]
    if not all_ids:
        return []
    sampled = random.sample(all_ids, min(limit, len(all_ids)))
    questoes = db.query(Questao).filter(Questao.id.in_(sampled)).all()
    return [_serialize(q) for q in questoes]


@router.get("/questoes/{questao_id}", response_model=QuestaoResponse)
def get_questao(questao_id: int, db: Session = Depends(get_db)):
    q = db.query(Questao).filter(Questao.id == questao_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Questão não encontrada")
    return _serialize(q)

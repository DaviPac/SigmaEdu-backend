import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.desempenho import Desempenho
from app.models.user import User
from app.schemas.desempenho import AreaStats, DesempenhoCreate, DesempenhoStats, SubareaStats

log = logging.getLogger("ava.desempenho")
router = APIRouter(prefix="/ava", tags=["desempenho"])

_AREA_LABELS = {
    "LC": "Linguagens e Códigos",
    "CN": "Ciências da Natureza",
    "CH": "Ciências Humanas",
    "MT": "Matemática",
}
_AREA_ORDER = ["LC", "CN", "CH", "MT"]


@router.post("/desempenho")
def salvar_desempenho(
    body: DesempenhoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    for r in body.resultados:
        db.add(
            Desempenho(
                user_id=current_user.id,
                questao_id=r.questao_id,
                acertou=r.acertou,
                area=r.area,
                subarea=r.subarea,
            )
        )
    db.commit()
    log.info("Desempenho salvo: %d itens para user_id=%d", len(body.resultados), current_user.id)
    return {"saved": len(body.resultados)}


@router.get("/desempenho/stats", response_model=DesempenhoStats)
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = db.query(Desempenho).filter(Desempenho.user_id == current_user.id).all()

    area_map: dict[str, dict] = {}
    for row in rows:
        area = row.area or "XX"
        if area not in area_map:
            area_map[area] = {"total": 0, "corretas": 0, "subareas": {}}
        area_map[area]["total"] += 1
        if row.acertou:
            area_map[area]["corretas"] += 1
        if row.subarea:
            sm = area_map[area]["subareas"]
            if row.subarea not in sm:
                sm[row.subarea] = {"total": 0, "corretas": 0}
            sm[row.subarea]["total"] += 1
            if row.acertou:
                sm[row.subarea]["corretas"] += 1

    areas_out: list[AreaStats] = []
    total_geral = corretas_geral = 0

    for area in _AREA_ORDER:
        if area not in area_map:
            continue
        d = area_map[area]
        total_geral += d["total"]
        corretas_geral += d["corretas"]
        pct = round(d["corretas"] / d["total"] * 100, 1) if d["total"] else 0.0

        subareas = sorted(
            [
                SubareaStats(
                    subarea=sub,
                    total=sd["total"],
                    corretas=sd["corretas"],
                    percentual=round(sd["corretas"] / sd["total"] * 100, 1) if sd["total"] else 0.0,
                )
                for sub, sd in d["subareas"].items()
            ],
            key=lambda s: -s.total,
        )

        areas_out.append(
            AreaStats(
                area=area,
                label=_AREA_LABELS.get(area, area),
                total=d["total"],
                corretas=d["corretas"],
                percentual=pct,
                subareas=subareas,
            )
        )

    pct_geral = round(corretas_geral / total_geral * 100, 1) if total_geral else 0.0
    return DesempenhoStats(
        areas=areas_out,
        total_geral=total_geral,
        corretas_geral=corretas_geral,
        percentual_geral=pct_geral,
    )

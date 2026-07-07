from typing import List, Optional
from pydantic import BaseModel


class ResultadoItem(BaseModel):
    questao_id: int
    acertou: bool
    area: Optional[str] = None
    subarea: Optional[str] = None


class DesempenhoCreate(BaseModel):
    resultados: List[ResultadoItem]


class SubareaStats(BaseModel):
    subarea: str
    total: int
    corretas: int
    percentual: float


class AreaStats(BaseModel):
    area: str
    label: str
    total: int
    corretas: int
    percentual: float
    subareas: List[SubareaStats]


class DesempenhoStats(BaseModel):
    areas: List[AreaStats]
    total_geral: int
    corretas_geral: int
    percentual_geral: float

from pydantic import BaseModel
from typing import Optional, List


class AlternativaResponse(BaseModel):
    letra: str
    texto: Optional[str]
    arquivo_base64: Optional[str]

    model_config = {"from_attributes": True}


class QuestaoResponse(BaseModel):
    id: int
    ano: int
    titulo: str
    area: Optional[str]
    contexto: Optional[str]
    pergunta: str
    arquivos: List[str]
    alternativas: List[AlternativaResponse]
    alternativa_correta: str
    codigo_competencia: Optional[int]
    descricao_competencia: Optional[str]
    subarea: Optional[str]


class GrupoInfo(BaseModel):
    area: str
    subarea: Optional[str]
    count: int

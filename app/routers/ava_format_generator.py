import logging
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.format_generator_service import generate_format_template

log = logging.getLogger("ava.format_generator")
router = APIRouter(prefix="/ava", tags=["ava"])


class FormatGeneratorRequest(BaseModel):
    """Payload de entrada para geração de template HTML."""

    personality: str


class FormatGeneratorResponse(BaseModel):
    """Payload de saída contendo o template HTML gerado."""

    format: str


@router.post("/format-generator", response_model=FormatGeneratorResponse)
async def format_generator(body: FormatGeneratorRequest) -> FormatGeneratorResponse:
    """Gera e retorna um template HTML visual baseado na personalidade solicitada."""
    log.info("Format Generator: gerando template para personalidade '%s'", body.personality)
    html = await generate_format_template(body.personality)
    return FormatGeneratorResponse(format=html)

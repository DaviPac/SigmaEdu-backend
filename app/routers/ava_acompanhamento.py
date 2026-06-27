import logging
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.acompanhamento_service import (
    run_validator_agent,
    run_formulator_agent,
    run_professor_agent,
)

log = logging.getLogger("ava.acompanhamento")
router = APIRouter(prefix="/ava", tags=["ava"])


class AcompanhamentoMessage(BaseModel):
    """Representa uma mensagem do histórico de conversa."""

    role: str
    text: str


class AcompanhamentoRequest(BaseModel):
    """Payload de entrada para o endpoint de acompanhamento."""

    history: list[AcompanhamentoMessage] = []
    userMessage: str
    personality: str = "Normal"
    formatTemplate: str | None = None


class AcompanhamentoResponse(BaseModel):
    """Payload de saída com o texto gerado pelo Agente Professor."""

    text: str


@router.post("/acompanhamento", response_model=AcompanhamentoResponse)
async def acompanhamento(body: AcompanhamentoRequest) -> AcompanhamentoResponse:
    """Orquestra o fluxo multi-agentes (Validador → Formulador → Professor) e retorna a resposta ao aluno."""
    log.info("Acompanhamento [%s]: iniciando crew para '%s...'", body.personality, body.userMessage[:60])

    try:
        validation = await run_validator_agent(body.userMessage)

        formulator_context = ""
        if validation.get("isEnemSubject"):
            log.info("Assunto ENEM detectado: %s (%s). Acionando Formulador...", validation.get("subjectName"), validation.get("difficulty"))
            formulator_context = await run_formulator_agent(body.userMessage, validation)
        elif validation.get("subjectName") is None and validation.get("reasoning") and "genéric" not in str(validation.get("reasoning", "")):
            formulator_context = "[NOTA DO SUPERVISOR]: O aluno está perguntando sobre algo que NÃO CAI no ENEM. Dê uma bronca amigável e lembre-o de focar nos assuntos da prova."

        history_dicts = [m.model_dump() for m in body.history]
        text = await run_professor_agent(
            history=history_dicts,
            user_message=body.userMessage,
            personality=body.personality,
            format_template=body.formatTemplate,
            formulator_context=formulator_context,
        )

        return AcompanhamentoResponse(text=text)
    except Exception as e:
        log.error("Erro no fluxo principal do Acompanhamento: %s", e, exc_info=True)
        return AcompanhamentoResponse(text="Desculpe, ocorreu um erro interno e não consegui gerar sua resposta. Por favor, tente novamente em alguns instantes!")


import json
from pathlib import Path
from openai import AsyncOpenAI
from app.config import settings


def _load_enem_taxonomy() -> str:
    """Carrega e retorna a taxonomia ENEM como string JSON."""
    data_path = Path(__file__).parent.parent / "data" / "enem_banco_questoes.json"
    if data_path.exists():
        return data_path.read_text(encoding="utf-8")
    return "{}"


def _build_openai_client() -> AsyncOpenAI:
    """Instancia o cliente OpenAI com as configurações do ambiente."""
    return AsyncOpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.llm_base_url,
    )


def _extract_json(text: str) -> dict:
    """Extrai e parseia o primeiro objeto JSON encontrado no texto."""
    import re
    match = re.search(r"\{[\s\S]*\}", text)
    try:
        return json.loads(match.group(0) if match else text)
    except (json.JSONDecodeError, AttributeError):
        return {"isEnemSubject": False, "subjectName": None, "difficulty": None, "reasoning": "parse error"}


async def run_validator_agent(user_message: str) -> dict:
    """Aciona o Agente Validador para verificar se a mensagem é sobre conteúdo do ENEM."""
    client = _build_openai_client()
    taxonomy = _load_enem_taxonomy()

    system_prompt = f"""Você é o Agente Validador de Currículo do ENEM.
Sua missão exclusiva é ler a mensagem do aluno e verificar se o que ele pede está dentro dos assuntos do ENEM.

Banco de Assuntos (Taxonomia JSON):
{taxonomy}

INSTRUÇÃO CRÍTICA: Responda ESTRITAMENTE em formato JSON puro, sem nenhum texto extra. Use este schema exato:
{{
  "isEnemSubject": boolean,
  "subjectName": string | null,
  "difficulty": "Fácil" | "Médio" | "Difícil" | null,
  "reasoning": string
}}

Regras:
1. Se a mensagem for sobre um assunto escolar que consta na taxonomia, retorne isEnemSubject = true.
2. Identifique o "subjectName" e a "difficulty" usando OS MESMOS DADOS presentes na taxonomia.
3. Se a mensagem for genérica (ex: "oi", "tudo bem"), retorne isEnemSubject = false.
4. "reasoning" é para uso interno."""

    response = await client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f'Mensagem do aluno: "{user_message}"'},
        ],
    )

    return _extract_json(response.choices[0].message.content or "")


async def run_formulator_agent(user_message: str, validation: dict) -> str:
    """Aciona o Agente Formulador para gerar conteúdo didático baseado na validação do ENEM."""
    client = _build_openai_client()

    system_prompt = f"""Você é o Agente Formulador Pedagógico e conteudista de um cursinho para o ENEM.
O Agente Validador determinou que o aluno deseja aprender sobre:
- Assunto: {validation.get("subjectName")}
- Nível de Dificuldade Estimado no ENEM: {validation.get("difficulty")}

Sua missão:
Crie um roteiro bruto e super detalhado contendo a explicação da matéria para que o Professor repasse ao aluno.
1. Escreva um resumo claro e direto da teoria.
2. Elabore uma "Questão Exemplo" fictícia, no estilo do ENEM, no nível especificado.
3. Forneça a resolução detalhada, passo a passo.

Formate em Markdown."""

    response = await client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f'Dúvida original do aluno: "{user_message}"'},
        ],
    )

    return response.choices[0].message.content or ""


def _build_professor_system_prompt(personality: str, format_template: str | None, formulator_context: str) -> str:
    """Monta o system prompt do Agente Professor com personalidade e contexto pedagógico."""
    style_map = {
        "Mais lúdico": "- Use uma linguagem divertida, lúdica e encorajadora. Pode usar emojis à vontade.",
        "Mais direto": "- Seja extremamente direto e conciso. Foque apenas nos fatos.",
    }
    style_guideline = style_map.get(personality) or (
        f"- Adote a seguinte personalidade: {personality}"
        if personality and personality != "Normal"
        else "- Seja didático e objetivo"
    )

    template_guideline = ""
    if format_template:
        template_guideline = f"""
REQUISITO CRÍTICO DE FORMATO DE SAÍDA:
Você DEVE OBRIGATORIAMENTE estruturar sua resposta inteira preenchendo o template HTML abaixo.
Não adicione NENHUM texto fora deste HTML. Seu retorno deve ser PURAMENTE o código HTML.

Template HTML:
{format_template}"""

    pedagogical_context = (
        f"""
[INSTRUÇÃO CRÍTICA DO SETOR PEDAGÓGICO]
Sua equipe de tutores (O Formulador) já rascunhou a teoria e resolução perfeita para essa dúvida.
Seu dever é APENAS pegar esse conteúdo técnico e falar com a SUA personalidade.
Conteúdo técnico a ser repassado:
\"\"\"
{formulator_context}
\"\"\"
"""
        if formulator_context
        else ""
    )

    return f"""Você é o Agente Professor (Acompanhamento) da SigmaEdu — focado em monitorar o progresso do aluno no ENEM.

Diretrizes:
- Analise dúvidas sobre o desempenho e direcione o aluno.
{style_guideline}
- Responda em português brasileiro.
- Contextualize as orientações pensando no ENEM.
- Respostas concisas: 2 a 5 parágrafos no máximo.
{pedagogical_context}
{template_guideline}"""


async def run_professor_agent(
    history: list[dict],
    user_message: str,
    personality: str,
    format_template: str | None,
    formulator_context: str,
) -> str:
    """Aciona o Agente Professor para gerar a resposta final ao aluno."""
    client = _build_openai_client()

    system_prompt = _build_professor_system_prompt(personality, format_template, formulator_context)

    history_context = ""
    if history:
        lines = [
            f'{"Aluno" if m["role"] == "user" else "Agente"}: {m["text"]}'
            for m in history[-8:]
        ]
        history_context = "\n\n## Histórico da conversa\n" + "\n".join(lines)

    prompt = f"{history_context}\n\nAluno: {user_message}"

    response = await client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
    )

    return response.choices[0].message.content or ""

import os

file_path = "app/services/acompanhamento_service.py"

content = """import json
from pathlib import Path
from openai import AsyncOpenAI
from app.config import settings


def _load_enem_taxonomy(simplified: bool = False) -> str:
    \"\"\"Carrega e retorna a taxonomia ENEM como string JSON.
    Se simplified=True, remove o nó de questões para economizar tokens do Validador.\"\"\"
    data_path = Path(__file__).parent.parent / "data" / "enem_banco_questoes.json"
    if not data_path.exists():
        return "{}"
        
    content = data_path.read_text(encoding="utf-8")
    if not simplified:
        return content
        
    try:
        data = json.loads(content)
        for disc in data.get("disciplinas", []):
            for ass in disc.get("assuntos", []):
                for sub in ass.get("subtemas", []):
                    if "questoes" in sub:
                        del sub["questoes"]
        return json.dumps(data, ensure_ascii=False)
    except Exception:
        return content

def _find_subject_data(subject_name: str, difficulty: str) -> str:
    \"\"\"Busca os dados reais da questão no banco de dados baseando-se no assunto e dificuldade.\"\"\"
    data_path = Path(__file__).parent.parent / "data" / "enem_banco_questoes.json"
    if not data_path.exists():
        return ""
    
    try:
        data = json.loads(data_path.read_text(encoding="utf-8"))
        for disc in data.get("disciplinas", []):
            for ass in disc.get("assuntos", []):
                for sub in ass.get("subtemas", []):
                    if sub.get("nome") == subject_name:
                        questoes = sub.get("questoes", [])
                        if difficulty:
                            q_diff = [q for q in questoes if q.get("dificuldade_estimada") == difficulty]
                            if q_diff:
                                return json.dumps(q_diff, ensure_ascii=False, indent=2)
                        return json.dumps(questoes, ensure_ascii=False, indent=2)
    except Exception:
        pass
    return ""


def _build_openai_client() -> AsyncOpenAI:
    \"\"\"Instancia o cliente OpenAI com as configurações do ambiente.\"\"\"
    return AsyncOpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.llm_base_url,
    )


def _extract_json(text: str) -> dict:
    \"\"\"Extrai e parseia o primeiro objeto JSON encontrado no texto.\"\"\"
    import re
    match = re.search(r"\\{[\\s\\S]*\\}", text)
    try:
        result = json.loads(match.group(0) if match else text)
        if not isinstance(result, dict):
            raise ValueError("Parsed JSON is not a dictionary")
        return result
    except Exception:
        return {"isEnemSubject": False, "subjectName": None, "difficulty": None, "reasoning": "parse error"}


async def run_validator_agent(user_message: str) -> dict:
    \"\"\"Aciona o Agente Validador para verificar se a mensagem é sobre conteúdo do ENEM.\"\"\"
    client = _build_openai_client()
    taxonomy = _load_enem_taxonomy(simplified=True)

    system_prompt = f\"\"\"Você é o Agente Validador de Currículo do ENEM.
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
4. "reasoning" é para uso interno.\"\"\"

    import logging
    log = logging.getLogger("ava.acompanhamento_service")

    try:
        response = await client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f'Mensagem do aluno: "{user_message}"'},
            ],
            temperature=0.0,
            response_format={"type": "json_object"},
        )
        return _extract_json(response.choices[0].message.content or "")
    except Exception as e:
        log.error("Erro na API do Validador: %s", e)
        return {"isEnemSubject": False, "subjectName": None, "difficulty": None, "reasoning": "api error"}


async def run_professor_agent(
    history: list[dict],
    user_message: str,
    personality: str,
    format_template: str | None,
    validation: dict,
) -> str:
    \"\"\"Aciona o Agente Professor para gerar a resposta final ao aluno, integrando a busca de material (RAG).\"\"\"
    client = _build_openai_client()

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
        template_guideline = f\"\"\"
REQUISITO CRÍTICO DE FORMATO DE SAÍDA:
Você DEVE OBRIGATORIAMENTE estruturar sua resposta inteira preenchendo o template HTML abaixo.
Não adicione NENHUM texto fora deste HTML. Seu retorno deve ser PURAMENTE o código HTML.

Template HTML:
{format_template}\"\"\"

    pedagogical_context = ""
    if validation.get("supervisor_note"):
        pedagogical_context = validation["supervisor_note"]
    elif validation.get("isEnemSubject"):
        subject_name = validation.get("subjectName")
        difficulty = validation.get("difficulty")
        rag_context = ""
        if subject_name:
            subject_data = _find_subject_data(subject_name, difficulty)
            if subject_data:
                rag_context = f"\\n\\n[BANCO DE QUESTÕES REAIS ENCONTRADAS PARA O ASSUNTO]:\\n{subject_data}"
                
        rag_instruction = "Utilize AS QUESTÕES REAIS mapeadas abaixo para o aluno resolver. Se houver um arquivo PDF referenciado, indique-o como material de estudo adicional." if rag_context else "Elabore uma 'Questão Exemplo' fictícia, no estilo do ENEM, no nível especificado."
        
        pedagogical_context = f\"\"\"
[INSTRUÇÕES PEDAGÓGICAS]
O aluno deseja aprender sobre:
- Assunto: {subject_name}
- Nível de Dificuldade: {difficulty}

Seu dever como Professor:
1. Escreva um resumo claro e direto da teoria.
2. {rag_instruction}
3. Forneça a resolução detalhada, passo a passo.{rag_context}
\"\"\"

    system_prompt = f\"\"\"Você é o Agente Professor (Acompanhamento) da SigmaEdu — focado em monitorar o progresso do aluno no ENEM.

Diretrizes de Comportamento:
- Analise dúvidas sobre o desempenho e direcione o aluno.
{style_guideline}
- Responda em português brasileiro.
- Contextualize as orientações pensando no ENEM.
- Respostas concisas: 2 a 5 parágrafos no máximo.

{pedagogical_context}
{template_guideline}\"\"\"

    history_context = ""
    if history:
        lines = [
            f'{"Aluno" if m["role"] == "user" else "Agente"}: {m["text"]}'
            for m in history[-8:]
        ]
        history_context = "\\n\\n## Histórico da conversa\\n" + "\\n".join(lines)

    prompt = f"{history_context}\\n\\nAluno: {user_message}"

    import logging
    log = logging.getLogger("ava.acompanhamento_service")

    try:
        response = await client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        log.error("Erro na API do Professor: %s", e)
        return "Desculpe, estou com instabilidade no momento e não pude gerar sua resposta. Por favor, tente novamente em alguns instantes!"
"""

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

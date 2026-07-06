import json
from pathlib import Path
from openai import AsyncOpenAI
from app.config import settings


def _load_enem_taxonomy(simplified: bool = False) -> str:
    """Carrega e retorna a taxonomia ENEM como string JSON.
    Se simplified=True, remove o nó de questões para economizar tokens do Validador."""
    data_path = Path(__file__).parent.parent / "data" / "banco_questoes" / "enem_banco_questoes.json"
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
    """Busca os dados reais da questão no banco de dados baseando-se no assunto e dificuldade."""
    data_path = Path(__file__).parent.parent / "data" / "banco_questoes" / "enem_banco_questoes.json"
    if not data_path.exists():
        return ""
    
    try:
        data = json.loads(data_path.read_text(encoding="utf-8"))
        for disc in data.get("disciplinas", []):
            for ass in disc.get("assuntos", []):
                for sub in ass.get("subtemas", []):
                    if sub.get("nome") == subject_name:
                        questoes = sub.get("questoes", [])
                        
                        # Função auxiliar para ordenar por dificuldade (Fácil -> Médio -> Difícil)
                        def sort_key(q):
                            diff = q.get("dificuldade_estimada", "")
                            if diff == "Fácil": return 1
                            if diff == "Médio": return 2
                            if diff == "Difícil": return 3
                            return 4
                        
                        questoes.sort(key=sort_key)
                        
                        if difficulty:
                            q_diff = [q for q in questoes if q.get("dificuldade_estimada") == difficulty]
                            if q_diff:
                                return json.dumps(q_diff, ensure_ascii=False, indent=2)
                        return json.dumps(questoes, ensure_ascii=False, indent=2)
    except Exception:
        pass
    return ""


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
        result = json.loads(match.group(0) if match else text)
        if not isinstance(result, dict):
            raise ValueError("Parsed JSON is not a dictionary")
        return result
    except Exception:
        return {"isEnemSubject": False, "subjectName": None, "difficulty": None, "reasoning": "parse error"}


async def run_validator_agent(user_message: str) -> dict:
    """Aciona o Agente Validador para verificar se a mensagem é sobre conteúdo do ENEM."""
    client = _build_openai_client()
    taxonomy = _load_enem_taxonomy(simplified=True)

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

    import logging
    log = logging.getLogger("ava.acompanhamento_service")

    try:
        response = await client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "user", "content": f"{system_prompt}\n\nMensagem do aluno: \"{user_message}\""}
            ],
            temperature=0.0,
            response_format={"type": "json_object"},
        )
        return _extract_json(response.choices[0].message.content or "")
    except Exception as e:
        log.error("Erro na API do Validador: %s", e)
        return {"isEnemSubject": False, "subjectName": None, "difficulty": None, "reasoning": "api error"}


async def run_formulator_agent(user_message: str, validation: dict) -> str:
    """Aciona o Agente Formulador para gerar conteúdo didático baseado na validação do ENEM."""
    client = _build_openai_client()

    subject_name = validation.get("subjectName")
    difficulty = validation.get("difficulty")
    
    rag_context = ""
    if subject_name:
        subject_data = _find_subject_data(subject_name, difficulty)
        if subject_data:
            rag_context = f"\n\nBase de Questões Encontradas para o assunto:\n{subject_data}"
            
    rag_instruction = "Utilize UMA DAS QUESTÕES REAIS mapeadas abaixo. Não invente a primeira questão. Escolha SEMPRE a questão classificada como MAIS FÁCIL no banco fornecido." if rag_context else "Crie uma 'Questão Base' fictícia no nível especificado."

    system_prompt = f"""Você é o Agente Formulador Pedagógico e conteudista de um cursinho para o ENEM.
O Agente Validador determinou que o aluno deseja aprender sobre:
- Assunto: {subject_name}
- Nível de Dificuldade Estimado no ENEM: {difficulty}

[ESTRUTURA DIDÁTICA OBRIGATÓRIA]
Você DEVE estruturar o roteiro EXATAMENTE com as seguintes 4 seções, usando Markdown e espaçamento:

### 1. Teoria Direcionada
Breve explicação teórica e fórmulas focadas ESTRITAMENTE no que é necessário para resolver a questão base.

### 2. A Questão Base
Apresente a questão escolhida.
{rag_instruction}
⚠️ FORMATAÇÃO OBRIGATÓRIA: Coloque O TEXTO INTEIRO desta questão dentro de um bloco de citação Markdown (linhas iniciando com `> `), para destacá-la visualmente.

### 3. Resolução Passo a Passo
Resolva a questão apresentada de forma detalhada, explicando a lógica de forma clara.

### 4. Desafio de Fixação
Crie INEDITAMENTE uma NOVA questão no mesmo estilo e mesmo nível da anterior para testar o aluno. Se for matemática, mude apenas os valores ou contexto. Se for outra matéria, mantenha a essência lógica. 
⚠️ FORMATAÇÃO OBRIGATÓRIA: Destaque também esse Desafio usando blocos de citação (`> `). NÃO resolva o desafio, apenas deixe a pergunta para o aluno.
{rag_context}"""

    import logging
    log = logging.getLogger("ava.acompanhamento_service")

    try:
        response = await client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "user", "content": f"{system_prompt}\n\nDúvida original do aluno: \"{user_message}\""},
            ],
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        log.error("Erro na API do Formulador: %s", e)
        return ""


async def run_professor_agent(
    history: list[dict],
    user_message: str,
    personality: str,
    format_template: str | None,
    formulator_context: str | None = None,
    validation: dict | None = None,
) -> str:
    """
    Aciona o Agente Professor para gerar a resposta final ao aluno.
    Se validation for fornecido em vez de formulator_context, usa a versão otimizada (2 agentes).
    """
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
        template_guideline = f"""
REQUISITO CRÍTICO DE FORMATO DE SAÍDA:
Você DEVE OBRIGATORIAMENTE estruturar sua resposta inteira preenchendo o template HTML abaixo.
Não adicione NENHUM texto fora deste HTML. Seu retorno deve ser PURAMENTE o código HTML.

Template HTML:
{format_template}"""

    pedagogical_context = ""
    
    # FLUXO OTIMIZADO (Sem Formulador Separado)
    if validation is not None:
        if validation.get("supervisor_note"):
            pedagogical_context = validation["supervisor_note"]
        elif validation.get("isEnemSubject"):
            subject_name = validation.get("subjectName")
            difficulty = validation.get("difficulty")
            rag_context = ""
            if subject_name:
                subject_data = _find_subject_data(subject_name, difficulty)
                if subject_data:
                    rag_context = f"\n\n[BANCO DE QUESTÕES REAIS ENCONTRADAS PARA O ASSUNTO]:\n{subject_data}"
                    
            rag_instruction = "Utilize UMA DAS QUESTÕES REAIS mapeadas abaixo. Escolha SEMPRE a questão classificada como MAIS FÁCIL no banco fornecido." if rag_context else "Crie uma 'Questão Base' fictícia no nível especificado."
            
            pedagogical_context = f"""
[INSTRUÇÕES PEDAGÓGICAS E ESTRUTURA OBRIGATÓRIA]
O aluno deseja aprender sobre:
- Assunto: {subject_name}
- Nível de Dificuldade: {difficulty}

Você DEVE conversar com o aluno e estruturar a resposta EXATAMENTE com as seguintes 4 seções:

### 1. Teoria Direcionada
Forneça a teoria estritamente necessária para a questão base.

### 2. A Questão Base
Apresente a questão escolhida.
{rag_instruction}
⚠️ FORMATAÇÃO: O texto da questão DEVE estar envolto em um bloco de citação Markdown (use `> ` no início das linhas) para se destacar visualmente.

### 3. Resolução Passo a Passo
Resolva a questão base explicando a lógica.

### 4. Desafio de Fixação
Crie INEDITAMENTE uma NOVA questão no mesmo estilo (mesmo nível, mesmos conceitos, mudando apenas valores ou contexto) para testar o aluno AGORA. 
⚠️ FORMATAÇÃO: O texto do Desafio também DEVE estar em bloco de citação (`> `). NÃO dê a resposta do desafio, instigue o aluno a tentar resolver!
{rag_context}
"""
    # FLUXO CLÁSSICO (Com Formulador Separado)
    else:
        if formulator_context:
            pedagogical_context = f"""
[INSTRUÇÃO CRÍTICA DO SETOR PEDAGÓGICO]
Sua equipe de tutores (O Formulador) já rascunhou a teoria e resolução perfeita para essa dúvida.
Seu dever é APENAS pegar esse conteúdo técnico e falar com a SUA personalidade.
Conteúdo técnico a ser repassado:
{formulator_context}
"""

    system_prompt = f"""Você é o Agente Professor (Acompanhamento) da SigmaEdu — focado em monitorar o progresso do aluno no ENEM.

Diretrizes de Comportamento:
- Analise dúvidas sobre o desempenho e direcione o aluno.
{style_guideline}
- Responda em português brasileiro.
- Contextualize as orientações pensando no ENEM.

[MANUTENÇÃO DE ESTRUTURA OBRIGATÓRIA]
Independentemente da sua personalidade, você DEVE MANTER INTACTA a estrutura de 4 seções (Teoria, Questão Base, Resolução Passo a Passo, Desafio de Fixação) presente no conteúdo técnico.
⚠️ É ESTRITAMENTE PROIBIDO remover os blocos de citação (`> `) que envolvem as questões e o desafio! Você deve preservar essa formatação visual.

{pedagogical_context}
{template_guideline}"""

    history_context = ""
    if history:
        lines = [
            f'{"Aluno" if m["role"] == "user" else "Agente"}: {m["text"]}'
            for m in history[-8:]
        ]
        history_context = "\n\n## Histórico da conversa\n" + "\n".join(lines)

    prompt = f"{history_context}\n\nAluno: {user_message}"

    import logging
    log = logging.getLogger("ava.acompanhamento_service")

    try:
        response = await client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "user", "content": f"{system_prompt}\n\n{prompt}"},
            ],
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        log.error("Erro na API do Professor: %s", e)
        return "Desculpe, estou com instabilidade no momento e não pude gerar sua resposta. Por favor, tente novamente em alguns instantes!"

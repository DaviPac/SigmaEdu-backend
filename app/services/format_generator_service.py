from openai import AsyncOpenAI
from app.config import settings


def _build_openai_client() -> AsyncOpenAI:
    """Instancia o cliente OpenAI com as configurações do ambiente."""
    return AsyncOpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.llm_base_url,
    )


def _clean_html(raw: str) -> str:
    """Remove delimitadores de bloco de código caso o modelo os inclua na resposta."""
    text = raw.strip()
    if text.startswith("```html"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


async def generate_format_template(personality: str) -> str:
    """Gera e retorna um template HTML de resposta baseado na personalidade fornecida."""
    client = _build_openai_client()

    system_prompt = f"""Você é um Web Designer e Estrategista Didático trabalhando para um chatbot educacional.
Seu objetivo é criar ESTRITAMENTE o código HTML de um template visual que combine com a personalidade: "{personality}".

Diretrizes HTML:
- Retorne APENAS o HTML, sem blocos ```html ou explicações.
- Use UMA <div> contêiner principal para envelopar tudo.
- Use classes Tailwind para estilização (backgrounds suaves, borders, padding p-4, rounded-lg, text-sm, space-y-3, dark:bg-gray-800).
- O template DEVE ter EXATAMENTE as seguintes 4 divisões temáticas com títulos (<h3>):
  1. Teoria Direcionada
  2. A Questão Base
  3. Resolução Passo a Passo
  4. Desafio de Fixação
- Dentro de cada divisão, coloque um placeholder em colchetes como "[Insira o conteúdo aqui]".
- ATENÇÃO: Nas seções "A Questão Base" e "Desafio de Fixação", envolva o placeholder em um contêiner destacado (ex: um blockquote ou div com border-l-4 e background diferente) para que a questão salte aos olhos e não fique parecendo um texto blocado.
- Adicione emojis condizentes no título de cada seção.
- Não use <html>, <body> ou <script>."""

    response = await client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "user", "content": f"{system_prompt}\n\nGere o template de resposta HTML (Tailwind) para a personalidade: {personality}"},
        ],
    )

    return _clean_html(response.choices[0].message.content or "")

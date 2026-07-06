import asyncio
from app.routers.ava_acompanhamento import acompanhamento, AcompanhamentoRequest
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
load_dotenv()

async def main():
    request = AcompanhamentoRequest(
        history=[],
        userMessage="Geografia do Brasil: Humana",
        personality="Mais direto",
        formatTemplate=None
    )
    
    print("\n[TESTE] Iniciando teste da rota...")
    response = await acompanhamento(request)
    print("\n=== RESPOSTA FINAL DO AGENTE PROFESSOR ===\n")
    with open("test_output_geo.md", "w", encoding="utf-8") as f:
        f.write(response.text)
    print("\n[TESTE CONCLUÍDO] A resposta foi salva no arquivo test_output_geo.md!")

if __name__ == "__main__":
    asyncio.run(main())

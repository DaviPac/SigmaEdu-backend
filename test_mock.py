import asyncio
from unittest.mock import AsyncMock, patch
from app.routers.ava_acompanhamento import acompanhamento, AcompanhamentoRequest

async def main():
    req = AcompanhamentoRequest(userMessage='trigonometri')
    with patch('app.routers.ava_acompanhamento.run_validator_agent', new_callable=AsyncMock) as mock_val:
        # Simulate LLM output when it thinks it's a generic word or doesn't know
        mock_val.return_value = {'isEnemSubject': False, 'subjectName': None, 'difficulty': None, 'reasoning': None}
        try:
            res = await acompanhamento(req)
            print('Result:', res)
        except Exception as e:
            import traceback; traceback.print_exc()

asyncio.run(main())

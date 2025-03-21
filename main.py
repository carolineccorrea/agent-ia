import asyncio
from agente import Agente

async def main():
    agente_instancia = Agente()
    pergunta = "Meu nome é Ana Silva e meu CPF é 12345678901. Preciso do meu boleto, por favor."
    resultado = await agente_instancia.executor.ainvoke({"input": pergunta})
    print(resultado)

if __name__ == "__main__":
    asyncio.run(main())

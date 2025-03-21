import os
import re
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage

from models.Boleto import Boleto
from api_client import buscar_boleto_por_cpf

load_dotenv()

# Prompt Template para extração de CPF
cpf_prompt_template = PromptTemplate(
    input_variables=["pergunta"],
    template=(
        "A partir da pergunta abaixo, extraia apenas o CPF do usuário.\n"
        "O CPF deve conter exatamente 11 dígitos, apenas números, sem pontos ou traços.\n"
        "Pergunta: {pergunta}\n"
        "CPF extraído (apenas números):"
    )
)

# Memória da conversa
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

def extrair_cpf(texto: str) -> str:
    """Extrai a primeira sequência de 11 dígitos encontrada no texto."""
    match = re.search(r'(\d{11})', texto)
    return match.group(1) if match else ""

async def consulta_boleto_com_cpf(pergunta: str):
    # Extrai o CPF da pergunta
    cpf = extrair_cpf(pergunta)
    if not re.fullmatch(r"\d{11}", cpf):
        return "CPF não fornecido ou inválido."

    memory.chat_memory.add_message(HumanMessage(content=f"CPF extraído: {cpf}"))

    try:
        resultado = await buscar_boleto_por_cpf(cpf)
    except Exception as e:
        return str(e)

    if isinstance(resultado, Boleto):
        return {"cpf": cpf, "boleto": resultado}

    return resultado

class ConsultaBoleto:
    name = "consulta_boleto"
    description = "Realiza consulta de boleto usando apenas o CPF extraído da pergunta."

    async def run(self, input: str):
        return await consulta_boleto_com_cpf(input)

__all__ = ["ConsultaBoleto"]
import os
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage
from langchain_core.pydantic_v1 import BaseModel, Field

from models.Boleto import Boleto
from api_client import buscar_boleto_por_cpf
from llm_client import llm  # Instância centralizada do LLM

load_dotenv()

# Memória da conversa
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Modelo para extração de nome e CPF
class DadosExtraidos(BaseModel):
    nome: str = Field(..., description="Nome completo do usuário")
    cpf: str = Field(..., description="CPF do usuário com 11 dígitos")

parser_dados = JsonOutputParser(pydantic_object=DadosExtraidos)

prompt_extracao = PromptTemplate(
    template=(
        "A partir da pergunta abaixo, extraia o nome completo e o CPF da pessoa.\n"
        "Pergunta: {pergunta}\n\n"
        "Retorne em JSON com os campos:\n"
        "- nome (string)\n"
        "- cpf (string com 11 dígitos)\n\n"
        "{formatacao}"
    ),
    input_variables=["pergunta"],
    partial_variables={"formatacao": parser_dados.get_format_instructions()}
)

chain_extracao_dados = prompt_extracao | llm | parser_dados

# Prompt + Parser para validação de nome
class ValidacaoNomeOutput(BaseModel):
    valido: bool = Field(..., description="Se os nomes são considerados iguais")
    motivo: str = Field(..., description="Justificativa da validação")

validador_parser = JsonOutputParser(pydantic_object=ValidacaoNomeOutput)

validador_prompt = PromptTemplate(
    template=(
        "Compare o nome informado pelo usuário com o nome do boleto.\n"
        "Nome informado: {nome_usuario}\n"
        "Nome do boleto: {nome_boleto}\n"
        "Responda com JSON se os nomes representam a mesma pessoa.\n"
        "Retorne os campos 'valido' (true ou false) e 'motivo'.\n"
        "{formato_saida}"
    ),
    input_variables=["nome_usuario", "nome_boleto"],
    partial_variables={"formato_saida": validador_parser.get_format_instructions()}
)

validar_nome_chain = validador_prompt | llm | validador_parser

async def consulta_boleto_com_cpf(pergunta: str):
    try:
        dados = chain_extracao_dados.invoke({"pergunta": pergunta})
    except Exception as e:
        return f"Erro ao extrair dados: {str(e)}"

    cpf = dados.get("cpf")
    nome_usuario = dados.get("nome")

    if not cpf or len(cpf) != 11:
        return "CPF não fornecido ou inválido."

    memory.chat_memory.add_message(HumanMessage(content=f"CPF extraído: {cpf}"))
    print("Nome extraído do usuário:", nome_usuario)

    try:
        boleto = await buscar_boleto_por_cpf(cpf)
    except Exception as e:
        return str(e)

    if nome_usuario:
        resultado = validar_nome_chain.invoke({
            "nome_usuario": nome_usuario,
            "nome_boleto": boleto.nome_pagador
        })

        print("Resultado da validação de nome:", resultado)

        if not resultado.get("valido"):
            return f"Ops! Não foi possível validar o nome informado. {resultado.get('motivo')}"

    return {
        "cpf": cpf,
        "boleto": boleto
    }

class ConsultaBoleto:
    name = "consulta_boleto"
    description = "Realiza consulta de boleto usando apenas o CPF extraído da pergunta."

    async def run(self, input: str):
        return await consulta_boleto_com_cpf(input)

__all__ = ["ConsultaBoleto"]

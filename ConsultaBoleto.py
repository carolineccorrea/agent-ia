import os
from dotenv import load_dotenv
from langchain_core.output_parsers import JsonOutputParser
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.prompts import PromptTemplate

from models.Boleto import Boleto
from api_client import buscar_boleto_por_cpf
from llm_client import llm

load_dotenv()

# Memória da conversa
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# === MODELOS ===
class DadosUsuario(BaseModel):
    nome: str = Field(..., description="Nome completo do usuário")
    cpf: str = Field(..., description="CPF do usuário com 11 dígitos")

class ValidacaoNomeOutput(BaseModel):
    valido: bool = Field(..., description="Se os nomes são considerados iguais")
    motivo: str = Field(..., description="Justificativa da validação")

# === CHAINS COM ICEL ===
def criar_chain_extracao_dados():
    parser_dados = JsonOutputParser(pydantic_object=DadosUsuario)
    prompt_extracao = PromptTemplate(
        template=(
            "A partir da pergunta a seguir, extraia o nome completo e o CPF do usuário.\n\n"
            "Pergunta: {pergunta}\n\n"
            "Responda com o JSON:\n"
            "{formato_saida}"
        ),
        input_variables=["pergunta"],
        partial_variables={"formato_saida": parser_dados.get_format_instructions()}
    )
    return prompt_extracao | llm | parser_dados

chain_extracao_dados = criar_chain_extracao_dados()

validador_parser = JsonOutputParser(pydantic_object=ValidacaoNomeOutput)
validador_prompt = PromptTemplate(
    template=(
        "Compare o nome informado com o nome do boleto e diga se representam a mesma pessoa.\n"
        "Nome informado: {nome_usuario}\n"
        "Nome do boleto: {nome_boleto}\n\n"
        "Retorne JSON com:\n"
        "- valido (true ou false)\n"
        "- motivo (texto explicando a decisão)\n"
        "{formato_saida}"
    ),
    input_variables=["nome_usuario", "nome_boleto"],
    partial_variables={"formato_saida": validador_parser.get_format_instructions()}
)

validar_nome_chain = validador_prompt | llm | validador_parser

# === MAIN FUNÇÃO ===
async def consulta_boleto_com_cpf(pergunta: str):
    print("Pergunta recebida:", pergunta)

    try:
        dados_usuario = chain_extracao_dados.invoke({"pergunta": pergunta})
        dados = DadosUsuario(**dados_usuario)
        print(f"Nome extraído: {dados.nome}, CPF extraído: {dados.cpf}")
    except Exception as e:
        return f"Erro ao extrair dados: {e}"

    nome_usuario = dados.nome.strip()
    cpf = dados.cpf.strip()

    if not cpf or len(cpf) != 11 or not cpf.isdigit():
        return "CPF não fornecido ou inválido."

    memory.chat_memory.add_message(HumanMessage(content=f"CPF extraído: {cpf}"))
    print("Nome final considerado:", nome_usuario)

    try:
        boleto = await buscar_boleto_por_cpf(cpf)
    except Exception as e:
        return str(e)

    if nome_usuario:
        resultado_dict = validar_nome_chain.invoke({
            "nome_usuario": nome_usuario,
            "nome_boleto": boleto.nome_pagador
        })
        resultado = ValidacaoNomeOutput(**resultado_dict)

        print("Resultado da validação de nome:", resultado)

        if not resultado.valido:
            return f"Ops! O nome informado não corresponde ao do boleto. {resultado.motivo}"

    return {
        "cpf": cpf,
        "boleto": boleto
    }

# === FERRAMENTA ===
class ConsultaBoleto:
    name = "consulta_boleto"
    description = "Realiza consulta de boleto a partir da pergunta completa do usuário, extraindo e validando nome e CPF."

    async def run(self, input: str):
        return await consulta_boleto_com_cpf(input)


__all__ = ["ConsultaBoleto"]

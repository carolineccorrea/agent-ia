# agente.py
import os
from langchain.agents import Tool, AgentExecutor, create_openai_tools_agent
from langchain import hub
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv

from ConsultaBoleto import ConsultaBoleto
from llm_client import llm
import asyncio

load_dotenv()

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

class Agente:
    def __init__(self):
        consulta_boleto_instance = ConsultaBoleto()

        tools = [
            Tool(
                name=consulta_boleto_instance.name,
                func=lambda x: asyncio.run(consulta_boleto_instance.run(x)),  # wrap async to sync
                description=consulta_boleto_instance.description
            )
        ]

        prompt = hub.pull("hwchase17/openai-functions-agent")
        agente = create_openai_tools_agent(llm, tools, prompt)

        self.executor = AgentExecutor(
            agent=agente,
            tools=tools,
            memory=memory,
            verbose=True,
            handle_parsing_errors=True
        )
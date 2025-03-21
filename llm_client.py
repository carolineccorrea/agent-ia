import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.6,
    api_key=os.getenv("OPENAI_API_KEY")
)

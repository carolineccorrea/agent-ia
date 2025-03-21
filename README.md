# 🔍 Consulta de Boletos com LLM (LangChain + OpenAI)

Este projeto demonstra o uso de **Large Language Models (LLMs)** com **LangChain**, integrando uma API externa para consultar boletos a partir de uma entrada em linguagem natural.

---

## 💡 Visão Geral

O usuário fornece uma pergunta como:

> "Meu nome é Ana Silva e meu CPF é 12345678901. Gostaria de consultar meu boleto, por favor."

O sistema:

1. **Extrai o CPF e o nome** da frase com a LLM;
2. **Consulta uma API externa** de boletos com base no CPF;
3. **Valida se o nome informado bate com o nome do pagador** retornado pela API usando uma segunda chain LLM;
4. Retorna uma resposta contextualizada e amigável.

---

## 🔧 Tecnologias Utilizadas

- [LangChain](https://www.langchain.com/)
- [OpenAI](https://openai.com/)
- [FastAPI](https://fastapi.tiangolo.com/) (Mock da API de boletos)
- [httpx](https://www.python-httpx.org/) (requisições assíncronas)
- [Pydantic](https://docs.pydantic.dev/)
- Python 3.12+

---

## 📁 Estrutura do Projeto


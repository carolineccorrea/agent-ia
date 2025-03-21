import os
import httpx
from dotenv import load_dotenv
from models.Boleto import Boleto

load_dotenv()

async def buscar_boleto_por_cpf(cpf: str) -> Boleto:
    """
    Consulta assíncrona à API de boletos.
    
    Raises:
        ValueError: Se a variável de ambiente estiver ausente ou boleto não encontrado.
        RuntimeError: Para falhas de conexão ou erros inesperados da API.
    """
    print("Comeco da consulta de boletos com a string...")
    print(str)
    url_api = os.getenv("URL_API_BOLETOS")
    if not url_api:
        raise ValueError("A variável de ambiente URL_API_BOLETOS não está definida.")
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{url_api}/boletos/{cpf}")
            print(response)
    except httpx.RequestError as e:
        raise RuntimeError(f"Erro ao conectar com a API de boletos: {str(e)}")

    if response.status_code == 200:
        return Boleto(**response.json())
    elif response.status_code == 404:
        print(cpf)
        raise ValueError(f"Nenhum boleto encontrado para o CPF {cpf}.")
    else:
        print(cpf)
        raise RuntimeError(f"Erro inesperado da API: {response.status_code} - {response.text}")

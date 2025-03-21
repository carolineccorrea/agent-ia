from pydantic import BaseModel


class Boleto(BaseModel):
    cpf: str
    valor: float
    data_vencimento: str
    nome_pagador: str
    status: str
    
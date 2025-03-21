from pydantic import BaseModel

class UserInfo(BaseModel):
    nome_completo: str
    cpf: str
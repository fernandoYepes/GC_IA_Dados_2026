from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI(title="Casa de Sucos API")

# Banco de dados em memória
db_sucos = []
suco_id_counter = 1

# Modelo de dados de entrada para o Suco
class SucoInput(BaseModel):
    nome: str
    frutas: list[str]
    tem_gosto_de: str

# Função auxiliar para buscar dados na Fruityvice
def buscar_dados_fruta(nome_fruta: str):
    url = f"https://www.fruityvice.com/api/fruit/{nome_fruta}"
    response = requests.get(url)
    
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail=f"Fruta '{nome_fruta}' não encontrada na base de dados.")
    
    return response.json()

@app.get("/frutas/{nome}")
def consultar_fruta(nome: str):
    """Consulta uma fruta na API Fruityvice e retorna os dados em português."""
    dados = buscar_dados_fruta(nome)
    
    return {
        "nome": dados["name"],
        "calorias": dados["nutritions"]["calories"],
        "acucar": dados["nutritions"]["sugar"]
    }

@app.post("/sucos")
def criar_suco(suco: SucoInput):
    """Cadastra um novo suco e calcula suas informações nutricionais."""
    global suco_id_counter
    
    total_calorias = 0.0
    total_acucar = 0.0
    
    # Consulta cada fruta e soma os valores
    for fruta in suco.frutas:
        dados = buscar_dados_fruta(fruta)
        total_calorias += dados["nutritions"]["calories"]
        total_acucar += dados["nutritions"]["sugar"]
        
    novo_suco = {
        "id": suco_id_counter,
        "nome": suco.nome,
        "frutas": suco.frutas,
        "tem_gosto_de": suco.tem_gosto_de,
        "total_calorias": round(total_calorias, 2),
        "total_acucar": round(total_acucar, 2)
    }
    
    db_sucos.append(novo_suco)
    suco_id_counter += 1
    
    return novo_suco

@app.get("/sucos")
def listar_sucos():
    """Retorna todos os sucos cadastrados."""
    return db_sucos

@app.put("/sucos/{suco_id}")
def atualizar_suco(suco_id: int, suco_atualizado: SucoInput):
    """Desafio Bônus: Atualiza as frutas de um suco e recalcula os valores."""
    for index, suco_existente in enumerate(db_sucos):
        if suco_existente["id"] == suco_id:
            total_calorias = 0.0
            total_acucar = 0.0
            
            for fruta in suco_atualizado.frutas:
                dados = buscar_dados_fruta(fruta)
                total_calorias += dados["nutritions"]["calories"]
                total_acucar += dados["nutritions"]["sugar"]
                
            suco_modificado = {
                "id": suco_id,
                "nome": suco_atualizado.nome,
                "frutas": suco_atualizado.frutas,
                "tem_gosto_de": suco_atualizado.tem_gosto_de,
                "total_calorias": round(total_calorias, 2),
                "total_acucar": round(total_acucar, 2)
            }
            
            db_sucos[index] = suco_modificado
            return suco_modificado
            
    raise HTTPException(status_code=404, detail="Suco não encontrado para atualização.")
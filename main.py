import math
from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
from typing import List

app = FastAPI()

PROXY_SECRET_REAL = "fcefb110-c656-11f1-8f79-811c4988dbe1"

class Coordenada(BaseModel):
    id: str
    lat: float 
    lon: float  

class RequisicaoRota(BaseModel):
    pontos: List[Coordenada]

def calcular_geodesica_christoffel(p1: Coordenada, p2: Coordenada) -> float:
    theta1 = math.radians(90 - p1.lat)
    phi1 = math.radians(p1.lon)
    theta2 = math.radians(90 - p2.lat)
    phi2 = math.radians(p2.lon)
    
    R = 6371.0 
    
    if theta1 == theta2 and phi1 == phi2:
        return 0.0

    d_theta = theta2 - theta1
    d_phi = phi2 - phi1
    
    v_theta = d_theta
    v_phi = d_phi
    
    dt = 0.001  
    passos = int(1.0 / dt)
    
    theta = theta1
    phi = phi1
    distancia_acumulada = 0.0
    
    for _ in range(passos):
        sin_theta = math.sin(theta)
        if abs(sin_theta) < 1e-5:
            sin_theta = 1e-5

        gamma_theta_phi_phi = -sin_theta * math.cos(theta)
        gamma_phi_theta_phi = math.cos(theta) / sin_theta
        
        acel_theta = - (gamma_theta_phi_phi * (v_phi ** 2))
        acel_phi = - (2 * gamma_phi_theta_phi * v_theta * v_phi)
        
        v_theta += acel_theta * dt
        v_phi += acel_phi * dt
        
        ds = R * math.sqrt((v_theta * dt)**2 + (sin_theta * v_phi * dt)**2)
        distancia_acumulada += ds
        
        theta += v_theta * dt
        phi += v_phi * dt

    return distancia_acumulada

@app.post("/calcular-rota")
def api_otimizar_rota(
    dados: RequisicaoRota, 
    request: Request,
    x_rapidapi_proxy_secret: str = Header(None)
):
    cliente_host = request.client.host
    eh_local = cliente_host in ["127.0.0.1", "localhost"]
    
    if not eh_local:
        if x_rapidapi_proxy_secret != PROXY_SECRET_REAL:
            raise HTTPException(status_code=403, detail="Acesso negado. Utilize o marketplace oficial.")
    
    pontos_recebidos = dados.pontos
    if len(pontos_recebidos) < 2:
        return {"erro": "Envie pelo menos 2 pontos."}
    
    distancia_total = 0.0
    for i in range(len(pontos_recebidos) - 1):
        distancia_total += calcular_geodesica_christoffel(pontos_recebidos[i], pontos_recebidos[i+1])
    
return {
    "status": "success",
    "total_distance_km": distancia_total_km,
    "algorithm_used": "Einstein-Christoffel Geodesic Solver V1"
}

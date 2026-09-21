from fastapi import FastAPI, Request, Response

app = FastAPI()

VERIFY_TOKEN = "como2hogar_secreto_2026"

@app.get("/")
def home():
    return {"status": "Servidor de Como2hogar activo y esperando mensajes"}

@app.get("/webhook")
def verificar_conexion(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return Response(content=challenge, media_type="text/plain")
    
    return Response(content="Acceso denegado", status_code=403)
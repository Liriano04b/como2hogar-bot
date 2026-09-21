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

@app.post("/webhook")
async def recibir_mensajes(request: Request):
    # Meta nos enviará los mensajes de los clientes en formato JSON
    body = await request.json()
    
    # Imprimimos el mensaje en la consola de Render para poder leerlo
    print("Nuevo mensaje recibido de Meta:", body)
    
    # Siempre debemos responderle a Meta con un 200 OK para que sepa que lo recibimos
    return Response(content="EVENT_RECEIVED", status_code=200)
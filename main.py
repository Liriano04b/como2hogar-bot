import requests
from fastapi import FastAPI, Request, Response

app = FastAPI()

VERIFY_TOKEN = "como2hogar_secreto_2026"
ACCESS_TOKEN = "EAGWlZBLVo92sBSn5Dxzv5iQgdudTN1UmnRI9oZA4vJ4aRylrCZAuZA3ORZAXk8ru4L4LDtO3pEXWWVwOCmNGyvrhwOtzflMaY8qPEo6I5Ew6ZBZCXWEtVXbX7WBBIqVuHA3HCriy95gJIPB8Txvz2V7uvT4uRT2IgqvqlFHIIEgKCqX4gtpia1C0lLRZClhZBNR0Hg707fQZDZD"

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
    body = await request.json()
    
    try:
        # Extraemos el mensaje y quién lo envía
        evento = body["entry"][0]["messaging"][0]
        sender_id = evento["sender"]["id"]
        
        if "message" in evento and "text" in evento["message"]:
            mensaje_cliente = evento["message"]["text"]
            print(f"Mensaje recibido de {sender_id}: {mensaje_cliente}")
            
            # Preparamos la respuesta
            url = f"https://graph.facebook.com/v19.0/me/messages?access_token={ACCESS_TOKEN}"
            headers = {"Content-Type": "application/json"}
            respuesta = {
                "recipient": {"id": sender_id},
                "message": {"text": "¡Hola! Soy el asistente virtual de Como2hogar. He recibido tu mensaje."}
            }
            
            # Enviamos la respuesta a Meta
            requests.post(url, headers=headers, json=respuesta)
            
    except Exception as e:
        print("Error al procesar el mensaje:", e)

    return Response(content="EVENT_RECEIVED", status_code=200)
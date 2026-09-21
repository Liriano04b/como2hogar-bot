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
        for entry in body.get("entry", []):
            
            # 1. DETECTAR SI ES UN COMENTARIO
            if "changes" in entry:
                for change in entry["changes"]:
                    if change.get("field") == "comments":
                        comentario = change["value"]
                        comment_id = comentario["id"]
                        
                        if comentario.get("from", {}).get("id") == comentario.get("media", {}).get("owner", {}).get("id"):
                            continue

                        # Convertimos el texto a minúsculas para facilitar la búsqueda
                        texto = comentario.get("text", "").lower()
                        print(f"Nuevo comentario en IG: {texto}")

                        # 🟢 NUEVO: Lista de palabras clave que activan el bot
                        palabras_clave = ["precio", "precios", "y el precio", "Cuanto cuesta", "cual es el precio", "info", "información", "informacion", "cuanto", "costo", "detalles"]

                        # Verificamos si el cliente usó alguna de esas palabras
                        if any(palabra in texto for palabra in palabras_clave):
                            url_base = "https://graph.facebook.com/v19.0"

                            # Responder públicamente
                            url_publica = f"{url_base}/{comment_id}/replies?access_token={ACCESS_TOKEN}"
                            requests.post(url_publica, json={
                                "message": "¡Hola! Te acabo de enviar toda la información por mensaje directo (DM). 🚀"
                            })

                            # Enviar DM
                            url_privada = f"{url_base}/me/messages?access_token={ACCESS_TOKEN}"
                            requests.post(url_privada, json={
                                "recipient": {"comment_id": comment_id},
                                "message": {"text": "¡Hola! Vimos tu comentario. Aquí tienes la información sobre nuestras aspiradoras inteligentes. ¿Qué modelo te interesa?"}
                            })
                        else:
                            print("Comentario ignorado (no contiene palabras de venta).")

            # 2. DETECTAR SI ES UN MENSAJE DIRECTO (DM) NORMAL
            elif "messaging" in entry:
                for event in entry["messaging"]:
                    if "message" in event and "text" in event["message"]:
                        sender_id = event["sender"]["id"]
                        mensaje = event["message"]["text"]
                        print(f"Mensaje directo recibido: {mensaje}")
                        
                        url = f"https://graph.facebook.com/v19.0/me/messages?access_token={ACCESS_TOKEN}"
                        requests.post(url, json={
                            "recipient": {"id": sender_id},
                            "message": {"text": "¡Hola de nuevo! Soy el asistente de Como2hogar. ¿En qué te puedo ayudar hoy?"}
                        })

    except Exception as e:
        print("Error al procesar el mensaje:", e)

    return Response(content="EVENT_RECEIVED", status_code=200)
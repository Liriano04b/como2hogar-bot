from fastapi import FastAPI, Request, Response, BackgroundTasks
import requests

app = FastAPI()

VERIFY_TOKEN = "como2hogar_secreto_2026"
ACCESS_TOKEN = "IGAAPt9ZCmuVkZABZAGI1NzctbG9fZAk9OQnctMVpHNUlpT3B4NkltVXZAZAX0RnRmR1elRXT01HVm1wNnRic3JWc3p4eDlpT1pNc1pIcGpnSFdjbjV5ZAUM2VWlxOThkNjN5NF9jdUhETW1Ca0V6bGFJRkVUZAHNZAcHRsYnlJZATBoVi13TQZDZD"

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

def procesar_mensajes_en_segundo_plano(body):
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

                        texto = comentario.get("text", "").lower()
                        print(f"Nuevo comentario en IG: {texto}")

                        palabras_clave = ["precio", "precios", "y el precio", "cuanto cuesta", "cual es el precio", "info", "información", "informacion", "cuanto", "costo", "detalles"]

                        if any(palabra in texto for palabra in palabras_clave):
                            url_base = "https://graph.facebook.com/v19.0"

                            url_publica = f"{url_base}/{comment_id}/replies?access_token={ACCESS_TOKEN}"
                            requests.post(url_publica, json={
                                "message": "¡Hola! Te acabo de enviar toda la información por mensaje directo (DM). 🚀"
                            }, timeout=5)

                            url_privada = f"{url_base}/me/messages?access_token={ACCESS_TOKEN}"
                            requests.post(url_privada, json={
                                "recipient": {"comment_id": comment_id},
                                "message": {"text": "¡Hola! Vimos tu comentario. Aquí tienes la información sobre nuestras aspiradoras inteligentes. ¿Qué modelo te interesa?"}
                            }, timeout=5)

            # 2. DETECTAR SI ES UN MENSAJE DIRECTO (DM) NORMAL
            elif "messaging" in entry:
                for event in entry["messaging"]:
                    if event.get("message", {}).get("is_echo"):
                        continue
                        
                    if "message" in event and "text" in event["message"]:
                        sender_id = event["sender"]["id"]
                        mensaje = event["message"]["text"].lower()
                        print(f"Mensaje directo recibido: {mensaje}")
                        
                        if "dreame" in mensaje:
                            respuesta = "¡Excelente elección! Las aspiradoras robot Dreame cuentan con mapeo inteligente y base de autovaciado. ¿Buscas algún modelo en específico como la L10s Ultra?"
                        elif "mova" in mensaje:
                            respuesta = "¡Las aspiradoras Mova son increíbles para el hogar! Tenemos disponibles modelos en formato robot y wet/dry. ¿Para qué tipo de piso la necesitas?"
                        elif "precio" in mensaje or "costo" in mensaje:
                            respuesta = "Nuestros precios varían según el modelo. Las opciones básicas inician en [Precio] y los modelos premium en [Precio]. ¡Cuéntame cuál te llama la atención!"
                        else:
                            respuesta = "¡Hola! Soy el asistente de Como2hogar. 🤖 Tenemos los mejores equipos inteligentes para limpiar tu casa. Escribe 'Dreame', 'Mova' o 'Precio' para darte más detalles."

                        url = f"https://graph.facebook.com/v19.0/me/messages?access_token={ACCESS_TOKEN}"
                        requests.post(url, json={
                            "recipient": {"id": sender_id},
                            "message": {"text": respuesta}
                        }, timeout=5)

    except Exception as e:
        print("Error al procesar el mensaje:", e)

# ESTA ES LA FUNCIÓN QUE RECIBE EL GOLPE INICIAL DE META
@app.post("/webhook")
async def recibir_mensajes(request: Request, background_tasks: BackgroundTasks):
    body = await request.json()
    
    print("====== PAYLOAD RECIBIDO ======")
    print(body)
    print("==============================")
    
    # 🟢 Delegar el trabajo al fondo y responder a Meta en 1 milisegundo
    background_tasks.add_task(procesar_mensajes_en_segundo_plano, body)
    
    return Response(content="EVENT_RECEIVED", status_code=200)
import os
import requests
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
META_APP_ID = os.getenv("META_APP_ID")
META_APP_SECRET = os.getenv("META_APP_SECRET")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://whatsapp-dashboard-zeta.vercel.app",
        "https://whatsapp-dashboard-mz60.vercel.app",
        "https://whatsapp-dashboard-f90h.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

messages_store = []

@app.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return PlainTextResponse(content=challenge)

    return PlainTextResponse(content="Verification failed", status_code=400)

@app.post("/webhook")
async def receive_message(request: Request):
    data = await request.json()

    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        messages = value.get("messages")

        if messages:
            msg_text = messages[0]["text"]["body"]
            sender = messages[0]["from"]

            messages_store.append({
                "from": sender,
                "message": msg_text
            })

    except Exception as e:
        print("Error:", e)

    return {"status": "received"}

@app.get("/messages")
async def get_messages():
    return messages_store

@app.post("/signup-data")
async def signup_data(data: dict):
    code = data.get("code")

    token_url = "https://graph.facebook.com/v18.0/oauth/access_token"

    params = {
        "client_id": META_APP_ID,
        "client_secret": META_APP_SECRET,
        "code": code,
        "redirect_uri": "https://whatsapp-dashboard-f90h.vercel.app/"
    }

    response = requests.get(token_url, params=params)
    token_data = response.json()

    print("TOKEN DATA 🔥", token_data)

    return token_data

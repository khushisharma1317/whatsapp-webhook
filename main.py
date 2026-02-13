from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
import os

app = FastAPI()

VERIFY_TOKEN = "khushi_token_123"

META_APP_ID = "1677000596794817"
META_APP_SECRET = "YOUR_APP_SECRET"   # 🔴 yaha apna secret daalo

# ⭐ Allow BOTH your Vercel domains (zeta + f90h)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://whatsapp-dashboard-zeta.vercel.app",
        "https://whatsapp-dashboard-f90h.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

messages_store = []

# 🔵 Webhook verification
@app.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return PlainTextResponse(content=challenge)

    return PlainTextResponse(content="Verification failed", status_code=400)

# 🟢 Receive WhatsApp messages
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

# 🔵 Dashboard fetch messages
@app.get("/messages")
async def get_messages():
    return messages_store

# 🔥 Embedded Signup → CODE → ACCESS TOKEN
@app.post("/signup-data")
async def signup_data(data: dict):
    code = data.get("code")

    token_url = "https://graph.facebook.com/v18.0/oauth/access_token"

    params = {
        "client_id": META_APP_ID,
        "client_secret": META_APP_SECRET,
        "code": code,
        "redirect_uri": "https://whatsapp-dashboard-f90h.vercel.app/"  # ⚠️ SAME AS FRONTEND
    }

    response = requests.get(token_url, params=params)
    token_data = response.json()

    print("TOKEN DATA 🔥", token_data)

    return token_data

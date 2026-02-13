import os
import requests
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
META_APP_ID = os.getenv("META_APP_ID")
META_APP_SECRET = os.getenv("META_APP_SECRET")

FRONTEND_URL = os.getenv("FRONTEND_URL")

# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
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
    print("📩 Incoming:", data)

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
        print("❌ Parsing error:", e)

    return {"status": "received"}


# 🔵 Dashboard fetch
@app.get("/messages")
async def get_messages():
    return messages_store


@app.get("/")
async def root():
    return {"status": "Backend running"}



# 🔥 Embedded Signup → CODE → ACCESS TOKEN
@app.post("/signup-data")
async def signup_data(data: dict):
    code = data.get("code")

    if not code:
        return JSONResponse(
            status_code=400,
            content={"error": "No code received"}
        )

    print("🔑 CODE RECEIVED:", code)

    token_url = "https://graph.facebook.com/v18.0/oauth/access_token"

    params = {
        "client_id": META_APP_ID,
        "client_secret": META_APP_SECRET,
        "code": code,
        "redirect_uri": FRONTEND_URL,  # ⚠️ must match Meta + frontend
    }

    response = requests.get(token_url, params=params)
    token_data = response.json()

    print("🎯 TOKEN RESPONSE:", token_data)

    return token_data

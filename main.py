from fastapi import FastAPI, Request
import requests
import os

app = FastAPI()

CLIENT_ID = os.getenv("ROBLOX_CLIENT_ID")
CLIENT_SECRET = os.getenv("ROBLOX_CLIENT_SECRET")
REDIRECT_URI = os.getenv("ROBLOX_REDIRECT_URI")

@app.get("/auth")
async def roblox_auth(request: Request):
    code = request.query_params.get("code")
    state = request.query_params.get("state")  # Discord user ID

    if not code:
        return {"error": "No code provided"}

    # Exchange code for token
    token_res = requests.post(
        "https://apis.roblox.com/oauth/v1/token",
        auth=(CLIENT_ID, CLIENT_SECRET),
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    token_data = token_res.json()
    access_token = token_data.get("access_token")

    if not access_token:
        return {"error": "Failed to get access token", "details": token_data}

    # Get user info
    user_res = requests.get(
        "https://apis.roblox.com/oauth/v1/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    roblox_user = user_res.json()

    # TODO: save roblox_user["sub"] ↔ state (Discord ID) in MongoDB

    return {
        "success": True,
        "roblox_id": roblox_user["sub"],
        "discord_id": state,
    }

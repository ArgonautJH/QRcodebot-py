# oauth_handler.py
from flask import Flask, request, redirect
import os
import config
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from config import bot_token, app_token

app = Flask(__name__)

@app.route("/slack/oauth/callback", methods=["GET"])
def oauth_callback():
    # Handle the OAuth callback
    code = request.args.get("code")
    if code:
        client = WebClient(token=bot_token)
        try:
            response = client.oauth_v2_access(
                client_id=app_token["client_id"],
                client_secret=app_token["client_secret"],
                code=code,
            )
            # Handle the response, e.g., store the access token
            print(response)
        except SlackApiError as e:
            print(f"Error getting OAuth tokens: {e}")
    
    return "OAuth process completed. You can close this window."

if __name__ == "__main__":
    command = "gunicorn -c gunicorn_config.py oauth_handler:app"
    os.system(command)

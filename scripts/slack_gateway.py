import os
import json
import boto3
import hmac
import hashlib
from flask import Flask, request, jsonify, abort
from launch_agent_runtime import query_agent  # reuse your existing logic

# Load config
with open("config/agent_config.json") as f:
    config = json.load(f)

KB_ID = config["knowledge_base_id"]
REGION = config.get("region", "us-east-1")

# Slack secrets
SLACK_SIGNING_SECRET = "16a6ddb75bc1bba5ae3f69f67d9fd12b" # os.environ.get("SLACK_SIGNING_SECRET")
SLACK_BOT_TOKEN ="xoxb-9678753858163-9756293886532-b0gWqbh9vWaAWXFNIJCMqIQF" # os.environ.get("SLACK_BOT_TOKEN")

#print("signing secret", SLACK_SIGNING_SECRET)

# AWS client
bedrock = boto3.client("bedrock-agent-runtime", region_name=REGION)

app = Flask(__name__)

def verify_slack_signature(req):
    timestamp = req.headers.get("X-Slack-Request-Timestamp")
    signature = req.headers.get("X-Slack-Signature")
    if not timestamp or not signature:
        return False

    body = req.get_data().decode("utf-8")
    basestring = f"v0:{timestamp}:{body}"
    my_signature = "v0=" + hmac.new(
        SLACK_SIGNING_SECRET.encode(), basestring.encode(), hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(my_signature, signature)

def send_slack_message(channel, text):
    import requests
    headers = {
        "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "channel": channel,
        "text": text
    }
    response = requests.post("https://slack.com/api/chat.postMessage", headers=headers, json=payload)
    return response.ok

@app.route("/slack/events", methods=["POST"])
def slack_events():
    if not verify_slack_signature(request):
        abort(403)

    data = request.json

    # Handle Slack URL verification
    if data.get("type") == "url_verification":
        return jsonify({"challenge": data["challenge"]})

    # Handle message events
    if data.get("type") == "event_callback":
        event = data.get("event", {})
        if event.get("type") == "message" and "bot_id" not in event:
            user_text = event.get("text", "")
            channel = event.get("channel")

            results = query_agent(KB_ID, user_text, region=REGION)
            if results:
                top_answer = results[0]["content"]["text"]
                send_slack_message(channel, top_answer)
            else:
                send_slack_message(channel, "🤖 Sorry, I couldn't find an answer.")

    return "", 200

if __name__ == "__main__":
    app.run(port=5000, debug=True)
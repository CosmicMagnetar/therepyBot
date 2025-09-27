from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from openai import OpenAI
import os
from dotenv import load_dotenv
import traceback

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Enable CORS for all origins (safe for development)
CORS(app)

# OpenRouter client
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    print("Warning: OPENROUTER_API_KEY not set!")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY
)

# System prompt for therapy bot
system_message = {
    "role": "system",
    "content": (
        "You are a friendly and empathetic virtual therapist. "
        "Your goal is to listen, provide emotional support, and give helpful suggestions. "
        "Only answer questions related to therapy, emotions, mental health, coping strategies, or personal well-being. "
        "If the user asks about anything else, politely refuse and say: "
        "'I'm here to provide therapy and emotional support, so I can't answer that.' "
        "Avoid giving medical diagnoses."
    )
}

# Serve frontend (make sure index.html exists)
@app.route("/")
def index():
    try:
        return send_from_directory(os.path.dirname(__file__), "index.html")
    except Exception as e:
        traceback.print_exc()
        return "index.html not found", 500

# Chat endpoint
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON payload provided"}), 400

        user_input = data.get("message", "").strip()
        if not user_input:
            return jsonify({"error": "No message provided"}), 400

        if user_input.lower() in ["bye", "exit", "quit"]:
            return jsonify({"response": "It was nice talking to you. Take care! 💛"})

        messages = [
            system_message,
            {"role": "user", "content": user_input}
        ]

        # Call OpenRouter
        completion = client.chat.completions.create(
            model="x-ai/grok-4-fast:free",
            messages=messages
        )

        # DEBUG: Print full completion to see structure
        print("OpenRouter response:", completion)

        # Adjust based on actual response structure
        bot_response = completion.choices[0].message.content
        return jsonify({"response": bot_response})

    except Exception as e:
        # Print full traceback for debugging
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Server running on http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)

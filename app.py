from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Enable CORS for all routes and origins
CORS(app, resources={r"/*": {"origins": "*"}})  # <-- Make sure this is applied globally

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY")
)

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

@app.route("/")
def index():
    return send_from_directory(os.path.dirname(__file__), "index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_input = request.json.get("message", "").strip()
        if not user_input:
            return jsonify({"error": "No message provided"}), 400

        if user_input.lower() in ["bye", "exit", "quit"]:
            return jsonify({"response": "It was nice talking to you. Take care! 💛"})

        messages = [
            system_message,
            {"role": "user", "content": user_input}
        ]

        completion = client.chat.completions.create(
            model="x-ai/grok-4-fast:free",
            messages=messages
        )

        bot_response = completion.choices[0].message.content
        return jsonify({"response": bot_response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=True)

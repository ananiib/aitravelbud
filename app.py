from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/ai", methods=["POST"])
def ai_response():
    data = request.json
    user_input = data.get("question") or f"Plan a trip to {data.get('destination')} on {data.get('dates')} with preferences: {data.get('preferences')}"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": user_input}],
        max_tokens=500
    )
    answer = response.choices[0].message.content
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

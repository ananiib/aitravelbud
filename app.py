from flask import Flask, request, jsonify, send_from_directory
import openai
import os

app = Flask(__name__, static_folder='.', static_url_path='')
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route("/ai", methods=["POST"])
def ai_response():
    data = request.json
    user_input = data.get("question") or f"Plan a trip to {data.get('destination')} from {data.get('dateFrom')} to {data.get('dateTo')} with preferences: {data.get('preferences')}"
    
    try:
        # Updated to use the new OpenAI API format
        client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": user_input}],
            max_tokens=500
        )
        answer = response.choices[0].message.content
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=True)

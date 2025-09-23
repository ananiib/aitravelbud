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
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return jsonify({
                "answer": "⚠️ OpenAI API key is not configured on the server. Please set OPENAI_API_KEY and try again.",
                "error": "missing_api_key"
            }), 200

        # Use the official OpenAI python client correctly
        org_id = os.environ.get("OPENAI_ORG")
        if org_id:
            client = openai.OpenAI(api_key=api_key, organization=org_id)
        else:
            client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are a helpful travel planner. Provide concise, actionable itineraries."},
                      {"role": "user", "content": user_input}],
            max_tokens=600
        )

        answer = (response.choices[0].message.content if getattr(response.choices[0], "message", None) else None) or \
                 getattr(response.choices[0], "text", None) or "Sorry, I couldn't generate a response."
        return jsonify({"answer": answer})
    except Exception as e:
        error_text = str(e) if e else "Unknown error"
        if "invalid_api_key" in error_text or "Incorrect API key provided" in error_text:
            friendly = (
                "❌ The API key is invalid. Double-check you pasted the FULL key (no spaces/newlines), "
                "updated it in Render Settings → Environment as OPENAI_API_KEY, and restarted the service. "
                "If your account uses an organization, also set OPENAI_ORG to your org ID."
            )
            return jsonify({"answer": friendly, "error": "invalid_api_key"}), 200
        if "insufficient_quota" in error_text or "You exceeded your current quota" in error_text:
            friendly = (
                "⚠️ The AI provider reported insufficient quota on this API key. "
                "Please check your OpenAI plan/billing or use the local test server (python test_local.py)."
            )
            return jsonify({"answer": friendly, "error": "insufficient_quota"}), 200
        return jsonify({"answer": "", "error": error_text}), 500

@app.route("/suggest-destinations", methods=["POST"])
def suggest_destinations():
    """
    Returns a small list of destination strings suggested by AI.
    Response: { destinations: ["Paris", "Rome", "Barcelona"] }
    """
    try:
        api_key = os.environ.get("OPENAI_API_KEY")
        # Fallback if no API key: return a static example
        if not api_key:
            return jsonify({"destinations": ["Paris", "Rome", "Barcelona"]})

        org_id = os.environ.get("OPENAI_ORG")
        if org_id:
            client = openai.OpenAI(api_key=api_key, organization=org_id)
        else:
            client = openai.OpenAI(api_key=api_key)

        prompt = (
            "Suggest exactly 3 highly recommended travel destinations as a JSON array of strings. "
            "Only output the JSON array, no extra text."
        )
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a concise travel assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=60,
            temperature=0.5,
        )
        raw = (response.choices[0].message.content if getattr(response.choices[0], "message", None) else None) or \
              getattr(response.choices[0], "text", None) or "[]"

        # Best-effort parse JSON array
        import json
        try:
            arr = json.loads(raw)
            if not isinstance(arr, list):
                arr = []
        except Exception:
            arr = []

        # Fallback if model didn't return parsable array
        if not arr:
            arr = ["Paris", "Rome", "Barcelona"]

        # Clean to strings only
        arr = [str(x) for x in arr][:3]
        return jsonify({"destinations": arr})
    except Exception as e:
        # On any error, provide a friendly fallback
        return jsonify({"destinations": ["Paris", "Rome", "Barcelona"], "error": str(e)}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=True)

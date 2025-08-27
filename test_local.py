#!/usr/bin/env python3
"""
Simple test script to test your Flask app locally without OpenAI API calls
"""

from flask import Flask, request, jsonify, send_from_directory
import os

app = Flask(__name__, static_folder='.', static_url_path='')

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route("/ai", methods=["POST"])
def ai_response():
    data = request.json
    user_input = data.get("question") or f"Plan a trip to {data.get('destination')} from {data.get('dateFrom')} to {data.get('dateTo')} with preferences: {data.get('preferences')}"
    
    # Mock response for testing (no OpenAI API needed)
    mock_response = f"🎉 Mock AI Response: I'd be happy to help plan your trip! You asked: '{user_input}'. This is a test response - your app is working locally! 🚀"
    
    return jsonify({"answer": mock_response})

if __name__ == "__main__":
    print("🚀 Starting local test server...")
    print("📱 Open your browser and go to: http://localhost:8000")
    print("🔧 This is a test version - no OpenAI API calls will be made")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    app.run(host="0.0.0.0", port=8000, debug=True)

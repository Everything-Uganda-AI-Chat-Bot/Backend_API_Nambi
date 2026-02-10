from flask import Blueprint, request, jsonify
from functools import lru_cache
from gemini import get_gemini_model
from services.content_fetcher import fetch_multiple_pages

chat_bp = Blueprint("chat", __name__)

SITE_URLS = [
    "https://everything-ug.netlify.app/",
    "https://everything-ug.netlify.app/facts",
    # "https://everything-ug.netlify.app/culture",
    # "https://everything-ug.netlify.app/top-cities/kampala",
    # "https://everything-ug.netlify.app/religion",
    # "https://everything-ug.netlify.app/travel-tips",
    # "https://everything-ug.netlify.app/destinations",
    # "https://everything-ug.netlify.app/activities",
    # "https://everything-ug.netlify.app/about",
    # "https://everything-ug.netlify.app/where-to-stay",
    # "https://everything-ug.netlify.app/insights",
    # "https://everything-ug.netlify.app/impact",
    "https://everything-ug.netlify.app/holiday-booking"
]

# Lazy-load site content once, cache with LRU
@lru_cache(maxsize=1)
def get_site_content():
    try:
        print("Fetching site content...")
        content = fetch_multiple_pages(SITE_URLS)
        print("Site content loaded.")
        return content
    except Exception as e:
        print("Warning: Failed to fetch site content:", e)
        return ""

@chat_bp.route("/chat", methods=["POST"])
def chat():
    """
    Chat with Nambi (Everything Uganda chatbot)
    ---
    tags:
      - Chatbot
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - question
          properties:
            question:
              type: string
              example: "Tell me about Kampala"
    responses:
      200:
        description: Bot response
        schema:
          type: object
          properties:
            answer:
              type: string
      400:
        description: Missing question
      500:
        description: Server error
    """
    data = request.get_json()
    if not data or "question" not in data:
        return jsonify({"error": "Question is required"}), 400

    question = data["question"]

    try:
        model = get_gemini_model()
        site_content = get_site_content() 

        prompt = f"""
You are a chatbot assistant for Everything Uganda.
Your name is Nambi.

COMPANY SITE CONTENT:
{site_content}

USER QUESTION:
{question}
"""

        response = model.generate_content(prompt)
        return jsonify({"answer": response.text})

    except Exception as e:
        return jsonify({
            "error": "Failed to generate response, try again later",
            "details": str(e)
        }), 500


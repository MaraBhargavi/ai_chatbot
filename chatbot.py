import sqlite3
import nltk
from nltk.tokenize import word_tokenize
from textblob import TextBlob

nltk.download("punkt", quiet=True)


# -------- SENTIMENT --------
def detect_sentiment(text):
    polarity = TextBlob(text).sentiment.polarity

    if polarity > 0.2:
        return "positive"
    elif polarity < -0.2:
        return "negative"
    else:
        return "neutral"


# -------- FAQ SEARCH --------
def search_faq(user_message):
    conn = sqlite3.connect("chat_logs.db")
    cursor = conn.cursor()

    cursor.execute("SELECT question, answer FROM faq")
    faq_data = cursor.fetchall()

    conn.close()

    user_words = set(word_tokenize(user_message.lower()))

    best_match = None
    best_score = 0

    for question, answer in faq_data:
        faq_words = set(word_tokenize(question.lower()))
        score = len(user_words.intersection(faq_words))

        if score > best_score:
            best_score = score
            best_match = answer

    if best_score >= 1:
        return best_match

    return None


# -------- MAIN CHATBOT --------
def get_bot_response(user_message, context=None):
    if context is None:
        context = {}

    text = user_message.lower().strip()
    words = word_tokenize(text)

    # -------- THANK YOU --------
    if text in ["thank you", "thanks", "thankyou"]:
        return {
            "reply": "You're welcome! I'm happy I could help.",
            "context": {"last_topic": "positive"}
        }

    # -------- SENTIMENT --------
    sentiment = detect_sentiment(user_message)

    if sentiment == "negative":
        return {
            "reply": "I'm sorry you're facing this issue. I understand your frustration, and I'll do my best to help.",
            "context": {"last_topic": "negative"}
        }

    if sentiment == "positive":
        return {
            "reply": "Glad to hear that. Let me know if you need anything else.",
            "context": {"last_topic": "positive"}
        }

    # -------- FAQ --------
    faq_answer = search_faq(user_message)
    if faq_answer:
        return {
            "reply": faq_answer,
            "context": {"last_topic": "faq"}
        }

    # -------- GREETING --------
    if any(word in words for word in ["hi", "hello", "hey"]):
        return {
            "reply": "Hello! How can I help you today?",
            "context": {"last_topic": "greeting"}
        }

    # -------- CANCEL --------
    if "cancel" in words or "cancellation" in words:
        return {
            "reply": "Do you want to cancel an order, subscription, or something else?",
            "context": {"last_topic": "cancel"}
        }

    # -------- ORDER --------
    if "order" in words:
        return {
            "reply": "I can help with your order. Please share your order issue.",
            "context": {"last_topic": "order"}
        }

    # -------- PAYMENT --------
    if "payment" in words or "pay" in words:
        return {
            "reply": "Please describe your payment issue.",
            "context": {"last_topic": "payment"}
        }

    # -------- SHIPPING --------
    if "shipping" in words or "delivery" in words:
        return {
            "reply": "I can help with shipping or delivery questions. What's the issue?",
            "context": {"last_topic": "shipping"}
        }

    # -------- REFUND --------
    if "refund" in words:
        return {
            "reply": "I can help with refunds. Please share your refund request details.",
            "context": {"last_topic": "refund"}
        }

    # -------- RETURN --------
    if "return" in words:
        return {
            "reply": "I can help with returns. Please mention the product and reason for return.",
            "context": {"last_topic": "return"}
        }

    # -------- ACCOUNT --------
    if any(word in words for word in ["account", "login", "password"]):
        return {
            "reply": "Are you facing a login, password, or account access issue?",
            "context": {"last_topic": "account"}
        }

    # -------- SUPPORT --------
    if any(word in words for word in ["support", "problem", "issue"]):
        return {
            "reply": "Please describe the issue in detail so I can help.",
            "context": {"last_topic": "support"}
        }

    # -------- PRICING --------
    if any(word in words for word in ["price", "pricing", "plan"]):
        return {
            "reply": "Are you asking about pricing, subscription plans, or product cost?",
            "context": {"last_topic": "pricing"}
        }

    # -------- COMPLAINT --------
    if "complaint" in words:
        return {
            "reply": "I'm sorry you're having trouble. Please explain your complaint so I can assist.",
            "context": {"last_topic": "complaint"}
        }

    # -------- HELP --------
    if "help" in words:
        last_topic = context.get("last_topic")

        mapping = {
            "order": "You were asking about your order. Please share your order details.",
            "payment": "You mentioned a payment issue. Please describe what happened.",
            "shipping": "You were asking about shipping. Tell me the delivery issue.",
            "refund": "You mentioned a refund. Please share order details.",
            "faq": "Can you tell me which FAQ topic you need help with?"
        }

        return {
            "reply": mapping.get(last_topic, "Sure. Tell me what problem you're facing."),
            "context": context
        }

    # -------- SMART FALLBACK --------
    return {
        "reply": "Could you clarify your question? I can help with orders, refunds, shipping, pricing, account login, and support issues.",
        "context": context
    }
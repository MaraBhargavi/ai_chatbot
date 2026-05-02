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

    best_score = 0
    best_match = None

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

    # -------- THANK YOU FIX --------
    if text in ["thank you", "thanks", "thankyou"]:
        return {
            "reply": "You're welcome! I'm happy I could help 😊",
            "context": {"last_topic": "positive"}
        }

    # -------- SENTIMENT --------
    sentiment = detect_sentiment(user_message)

    if sentiment == "negative":
        return {
            "reply": "I'm sorry you're facing this issue. I'll do my best to help you.",
            "context": {"last_topic": "negative"}
        }

    if sentiment == "positive":
        return {
            "reply": "Glad to hear that 😊 Let me know if you need anything else.",
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
    if "cancel" in words:
        return {
            "reply": "Do you want to cancel an order, subscription, or something else?",
            "context": {"last_topic": "cancel"}
        }

    # -------- ORDER --------
    if "order" in words:
        return {
            "reply": "I can help with your order. Please share the details.",
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
            "reply": "I can help with shipping or delivery. What is the issue?",
            "context": {"last_topic": "shipping"}
        }

    # -------- REFUND --------
    if "refund" in words:
        return {
            "reply": "I can help with refunds. Please share details.",
            "context": {"last_topic": "refund"}
        }

    # -------- RETURN --------
    if "return" in words:
        return {
            "reply": "I can help with returns. Please explain the reason.",
            "context": {"last_topic": "return"}
        }

    # -------- ACCOUNT --------
    if any(word in words for word in ["account", "login", "password"]):
        return {
            "reply": "Are you facing login or account issues?",
            "context": {"last_topic": "account"}
        }

    # -------- SUPPORT --------
    if any(word in words for word in ["support", "issue", "problem"]):
        return {
            "reply": "Please describe your issue so I can help.",
            "context": {"last_topic": "support"}
        }

    # -------- PRICING --------
    if any(word in words for word in ["price", "pricing", "plan"]):
        return {
            "reply": "Are you asking about pricing or subscription plans?",
            "context": {"last_topic": "pricing"}
        }

    # -------- COMPLAINT --------
    if "complaint" in words:
        return {
            "reply": "I'm sorry about that. Please explain your complaint.",
            "context": {"last_topic": "complaint"}
        }

    # -------- HELP (FIXED SAFE VERSION) --------
    if "help" in words:
        last_topic = context.get("last_topic")

        mapping = {
            "order": "You were asking about orders. Please share details.",
            "payment": "You mentioned payment issue. Please explain.",
            "shipping": "You were asking about shipping. Tell me more.",
            "refund": "You mentioned refund. Please share details.",
            "faq": "Tell me which FAQ topic you need help with."
        }

        return {
            "reply": mapping.get(last_topic, "Sure, please tell me your issue."),
            "context": context
        }

    # -------- FINAL FALLBACK (SAFE) --------
    return {
        "reply": "I can help with orders, refunds, shipping, payments, accounts, and support. Please tell me your issue.",
        "context": context
    }
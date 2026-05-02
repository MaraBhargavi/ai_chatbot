import streamlit as st
from chatbot import get_bot_response
from database import init_db, save_chat, seed_faq

# initialize DB + FAQ
init_db()
seed_faq()

st.set_page_config(page_title="AI Chatbot", layout="centered")

st.title("🤖 AI Customer Support Chatbot")

# session memory
if "context" not in st.session_state:
    st.session_state.context = {}

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# -------- CHAT INPUT --------
user_message = st.text_input("Type your message here:")

if st.button("Send") and user_message:

    bot_response = get_bot_response(
        user_message,
        st.session_state.context
    )

    reply = bot_response["reply"]
    st.session_state.context = bot_response["context"]

    # save to DB
    save_chat(user_message, reply)

    # store in UI history
    st.session_state.chat_history.append(("You", user_message))
    st.session_state.chat_history.append(("Bot", reply))


# -------- DISPLAY CHAT --------
for sender, msg in st.session_state.chat_history:
    if sender == "You":
        st.markdown(f"🧑 **You:** {msg}")
    else:
        st.markdown(f"🤖 **Bot:** {msg}")
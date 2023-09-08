import json
import uuid

import requests
import streamlit as st

st.title("Discover Nolan!")


# Initialization
if "key" not in st.session_state:
    st.session_state["key"] = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

st.subheader(st.session_state["key"])

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["message"])

# Accept user input
if user_message := st.chat_input():
    # Add user message to chat history

    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(user_message)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        response = requests.get(
            "http://localhost:8000/query",
            params={
                "query": user_message,
                "session_id": st.session_state["key"],
                "message_history": json.dumps(st.session_state.messages),
            },
        ).json()

        assistant_response = response["content"]

        message_placeholder.markdown(assistant_response)
        # Add assistant response to chat history

    st.session_state.messages.append({"role": "user", "message": user_message})
    st.session_state.messages.append(
        {
            "role": "assistant",
            "message": assistant_response,
            "metadata": response["metadata"],
        }
    )

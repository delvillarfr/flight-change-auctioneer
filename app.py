import streamlit as st
from openai import OpenAI

from config import INSTRUCTIONS

client = OpenAI(api_key = st.secrets["OPENAI_API_KEY"])

# Load the system message
system_messages = [
        {"role": "developer", "content": INSTRUCTIONS},
        {"role": "user", "content": "Begin now."}
        ]

# Start the conversation.
if "messages" not in st.session_state:

    # Complete the system messages.
    stream = client.chat.completions.create(
        model = "gpt-5.6-luna",
        messages = system_messages,
        stream = False
    )

    # The completion begins the message history.
    st.session_state["messages"] = [
            {"role": "assistant", "content": stream.choices[0].message.content}
            ]

# Display the message history.
for m in st.session_state["messages"]:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Add the prompt input box.
prompt = st.chat_input("Ask me anything...")

# Respond to the prompt.
if prompt is not None:

    # Display the prompt before completing it.
    # If the LLM call fails, the user knows his prompt was delivered.
    with st.chat_message("user"):
        st.markdown(prompt)

    # Save the prompt before completing it.
    # If the LLM call fails, the prompt isn't lost.
    st.session_state["messages"].append(
            {"role": "user", "content": prompt}
            )


    # Complete the prompt.
    stream = client.chat.completions.create(
        model = "gpt-5.6-luna",
        messages = system_messages + st.session_state["messages"],
        stream = True
    )

    # Display and save the response.
    with st.chat_message("assistant"):
        response = st.write_stream(stream)
    st.session_state["messages"].append(
            {"role": "assistant", "content": response}
            )

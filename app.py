import streamlit as st
from openai import OpenAI

from config import load_system_prompt, TOOLS, register_latest_offer

def complete_messages(client, messages, stream):
    """Complete the list of messages using the OpenAI Chat Completions API.
    """
    # Gather all messages and select their API-admitted fields.
    api_messages = []
    for m in messages:
        api_messages.append({"role": m["role"], "content": m["content"]})

    return client.chat.completions.create(
        model = "gpt-5.6-luna",
        messages = api_messages,
        stream = stream
    )

# Start a client.
client = OpenAI(api_key = st.secrets["OPENAI_API_KEY"])

# Start the conversation.
if "messages" not in st.session_state:

    # Initialize the message history.
    st.session_state["messages"] = [
        {
            "role": "developer",
            "content": load_system_prompt(),
            "visibility": "internal"
        },
        {
            "role": "user",
            "content": "Begin now.",
            "visibility": "internal"
        }
    ]

    # Complete the system messages and add to history.
    system_completion = complete_messages(
        client,
        st.session_state["messages"],
        stream = False
    )
    st.session_state["messages"].append(
        {
            "role": "assistant",
            "content": system_completion.choices[0].message.content,
            "visibility": "user-facing"
        }
    )

# Display the message history.
for m in st.session_state["messages"]:
    if m["visibility"] == "user-facing":
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
        {"role": "user", "content": prompt, "visibility": "user-facing"}
    )

    # Complete the prompt.
    stream = complete_messages(
        client,
        st.session_state["messages"],
        stream = True
    )

    # Display and save the response.
    with st.chat_message("assistant"):
        response = st.write_stream(stream)
    st.session_state["messages"].append(
        {"role": "assistant", "content": response, "visibility": "user-facing"}
    )

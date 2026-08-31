import json
import time

import streamlit as st
from openai import OpenAI

from config import load_system_prompt, TOOLS, register_latest_offer


def complete_messages(client, messages):
    """Complete the message history using the OpenAI Chat Completions API.
    """
    completion = []
    while True:

        # Gather all messages and select their API-admitted fields.
        api_messages = []
        for m in messages + completion:
            api_message = {"role": m["role"], "content": m["content"]}
            if "tool_calls" in m:
                api_message["tool_calls"] = m["tool_calls"]
            if "tool_call_id" in m:
                api_message["tool_call_id"] = m["tool_call_id"]
            api_messages.append(api_message)

        response = client.chat.completions.create(
            model = "gpt-5.6-luna",
            messages = api_messages,
            tools = TOOLS,
            reasoning_effort = "none",
        )
        response_message = response.choices[0].message

        if response_message.tool_calls is not None:
            # Record the tool-call turn, then run each tool.
            completion.append({
                "role": "assistant",
                "content": response_message.content,
                "tool_calls": [c.model_dump() for c in response_message.tool_calls],
                "visibility": "internal",
            })
            for call in response_message.tool_calls:
                result = register_latest_offer(**json.loads(call.function.arguments))
                completion.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": result,
                    "visibility": "internal",
                })

        else:
            completion.append({
                "role": "assistant",
                "content": response_message.content,
                "visibility": "user-facing",
            })
            return completion

@st.fragment(run_every = 1)
def show_countdown():
    """Display the per-session offering window countdown, ticking every second."""
    remaining = int(st.session_state["deadline"] - time.time())
    if remaining > 0:
        minutes, seconds = divmod(remaining, 60)
        st.info(f"Offering window closes in {minutes}:{seconds:02d}")
    else:
        st.warning("The offering window has closed.")


# Start a client.
client = OpenAI(api_key = st.secrets["OPENAI_API_KEY"])

session_is_new = "messages" not in st.session_state

# Sessions have a fixed time window to accept offers.
if session_is_new:
    st.session_state["deadline"] = time.time() + 60

# Show the countdown to the end of the offering window.
show_countdown()

# Load the system prompt and complete it.
if session_is_new:
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

    st.session_state["messages"] += complete_messages(
        client,
        st.session_state["messages"]
    )

# Display the user-facing messages.
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
    completion = complete_messages(client, st.session_state["messages"])
    st.session_state["messages"] += completion

    # Display the response.
    with st.chat_message("assistant"):
        st.markdown(completion[-1]["content"])

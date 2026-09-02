from datetime import datetime, timedelta, timezone
import json
import time

from openai import OpenAI
import pandas as pd
import streamlit as st

import config

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
            tools = config.TOOLS,
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
            # We specify the first function's argument, customer_id, not the LLM.
            for call in response_message.tool_calls:
                fn = config.TOOL_FUNCTIONS[call.function.name]
                result = fn(
                        st.session_state["customer_id"],
                        **json.loads(call.function.arguments)
                        )
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
    with st.container(key = "countdown-bar"):
        remaining = st.session_state["deadline"] - time.time()
        if remaining > 0:
            minutes, seconds = divmod(int(remaining), 60)
            st.info(f"Offering window closes in {minutes}:{seconds:02d}")
        else:
            st.warning("The offering window has closed.")
            if not st.session_state["results_initiated"]:
                st.session_state["results_initiated"] = True
                st.rerun()

def main():
    # Start a client.
    client = OpenAI(api_key = st.secrets["OPENAI_API_KEY"])

    session_is_new = "messages" not in st.session_state

    if session_is_new:

        # Get the auction's deadline and initialize it if there isn't one underway.
        end_datetime = config.initialize_auction()
        st.session_state["deadline"] = int(end_datetime.timestamp())

        # Get the customer's id and load her to the main database
        st.session_state["customer_id"] = config.load_customer_info()

        st.session_state["results_initiated"] = False
        st.session_state["results_delivered"] = False
        st.session_state["results_df"] = None


        # Load the system prompt and complete it.
        st.session_state["messages"] = [
            {
                "role": "developer",
                "content": config.load_system_prompt(),
                "visibility": "internal"
            },
            {
                "role": "developer",
                "content": "The customer's name is " + st.session_state["customer_id"],
                "visibility": "internal"
            },
            {
                "role": "assistant",
                "content": config.FIRST_MESSAGE,
                "visibility": "user-facing"
            }
        ]

    # Pin the countdown bar to the viewport.
    st.markdown(config.COUNTDOWN_CSS, unsafe_allow_html = True)

    # Show the countdown to the end of the offering window.
    show_countdown()

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

    if (
            st.session_state["results_initiated"]
            and not st.session_state["results_delivered"]
            and (time.time() >= st.session_state["deadline"])
    ):
        results = config.get_auction_results()
        customer_results = results.loc[
            results["name"] == st.session_state["customer_id"],
            ["offer", "winner", "compensation"]
        ]

        st.session_state["messages"].append({
            "role": "developer",
            "content": """
                The results are in.
                Please communicate them.
                Also ask the passenger to go to their Northwest Airlines portal to choose their seat.
                Add in mock url https://northwestairlines.mock/seat-selection
                """ + customer_results.to_string(),
            "visibility": "internal"
        })

        # Complete the prompt.
        completion = complete_messages(client, st.session_state["messages"])
        st.session_state["messages"] += completion

        # Display the response.
        with st.chat_message("assistant"):
            st.markdown(completion[-1]["content"])

        st.session_state["results_df"] = results
        st.session_state["results_delivered"] = True

    # Unveil the simulation and show the database.
    if st.session_state["results_df"] is not None:
        with st.chat_message("assistant"):
            st.markdown("You just played the role of **" + st.session_state["customer_id"] + "**.")
            st.dataframe(st.session_state["results_df"].sort_values("offer"))

if __name__ == "__main__":
    main()

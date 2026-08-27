import streamlit as st
from openai import OpenAI

client = OpenAI(api_key = st.secrets["OPENAI_API_KEY"])

# Initialize the message history.
# It is the list of user and assistant messages in this session.
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display the message history.
for m in st.session_state["messages"]:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Add the prompt input box.
prompt = st.chat_input("Ask me anything...")

# Respond to the prompt.
if prompt is not None:

    # Save the prompt before completing it.
    # If the LLM call fails, the prompt isn't lost.
    st.session_state["messages"].append(
            {"role": "user", "content": prompt}
            )

    # Display the prompt before completing it.
    # If the LLM call fails, the user knows his prompt was delivered.
    with st.chat_message("user"):
        st.markdown(prompt)

    # Complete the prompt.
    stream = client.chat.completions.create(
        model = "gpt-5.6-luna",
        messages = st.session_state["messages"],
        stream = True
    )

    # Save and display the response.
    st.session_state["messages"].append(
            {"role": "assistant", "content": response}
            )
    with st.chat_message("assistant"):
        response = st.write_stream(stream)

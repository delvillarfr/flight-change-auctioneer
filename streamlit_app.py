import streamlit as st
from openai import OpenAI

client = OpenAI(api_key = st.secrets["OPENAI_API_KEY"])

# Session state's messages is a list of {"role": , "content": } dicts
if "messages" not in st.session_state:
    st.session_state["messages"] = []

for m in st.session_state["messages"]:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

prompt = st.chat_input("Ask me anything...")
if prompt is not None:

    st.session_state["messages"].append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model = "gpt-5.6-luna",
            messages = st.session_state["messages"],
            stream = True
        )
        response = st.write_stream(stream)

    st.session_state["messages"].append({"role": "assistant", "content": response})

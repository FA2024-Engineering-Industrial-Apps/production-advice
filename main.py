import streamlit as st
import ChatOptimization as chat
from streamlit_utils import *

if "started" not in st.session_state:
    st.session_state["started"] = True
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]
    st.session_state["id"] = get_session()

st.title(f"Hello Production! {st.session_state['id']}")

def write_message(message):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

for message in st.session_state.messages:
    write_message(message)

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    write_message(st.session_state.messages[-1])

    response_stream = chat.get_llm_answer(prompt, st.session_state['id'])
    with st.chat_message("assistant"):
        response = st.write_stream(response_stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
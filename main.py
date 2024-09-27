import streamlit as st
import llm.setup as llmchat
from utils.streamlit_utils import *
import pandas as pd
if __name__ == "__main__":
    @st.cache_resource
    def get_llm():
        return llmchat.agent_executor

    if "started" not in st.session_state:
        st.session_state["started"] = True
        st.session_state["messages"] = [llmchat.AIMessage("Hello, how can I help you?")]
        st.session_state["id"] = get_session()

    def write_message(message):
        with st.chat_message(message.type):
            st.markdown(message.content)
            print("message")
            print(message)

    for message in st.session_state["messages"]:
        write_message(message)

    if prompt := st.chat_input():
        human_message = llmchat.HumanMessage(prompt)
        st.session_state.messages.append(human_message)
        write_message(human_message)
        response = get_llm().invoke(
            {
                "input": prompt,
                "chat_history": st.session_state.messages,
            }
        )
        output = response["output"]
        with st.chat_message("ai"):
            st.markdown(output)
        st.session_state.messages.append(llmchat.AIMessage(output))
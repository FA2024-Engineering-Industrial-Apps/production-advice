import streamlit as st
import ChatOptimization as llmchat
from streamlit_utils import *

@st.cache_resource
def get_llm_runnable():
    return llmchat.RunnableWithMessageHistory(
        llmchat.llm,
        lambda history: history
    )

if "started" not in st.session_state:
    st.session_state["started"] = True
    st.session_state["messages_lang"] = llmchat.ChatMessageHistory(
        messages=[llmchat.AIMessage("Hello, how can I help you?")]
    )
    st.session_state["messages_lang"] = 
    st.session_state["id"] = get_session()

st.title(f"Hello Production! {st.session_state['id']}")

def write_message(message):
    with st.chat_message(message.type):
        st.markdown(message.content)

for message in get_messages()[:-3]:
    write_message(message)

if prompt := st.chat_input():
    human_message = llmchat.HumanMessage(prompt)
    st.session_state.messages.add_message(human_message)
    write_message(get_messages()[-1])

    response_stream = get_llm_runnable().stream(
        [human_message],
        config={"configurable": {"session_id": st.session_state.messages}}
    )
    with st.chat_message("ai"):
        response = st.write_stream(response_stream)
    st.session_state.messages.add_message(llmchat.AIMessage(response))
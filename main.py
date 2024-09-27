import streamlit as st
import llm.setup as llmchat
from utils.streamlit_utils import *

from typing import Union
from dataclasses import dataclass

@dataclass
class DataExport:
    path: str

    @classmethod
    def isinstance(cls, obj) -> bool:
        return type(obj).__name__ == cls.__name__

EXPORTING_FUNCTIONS = [func.func.__name__ for func in [
    llmchat.CallOptimizer,
    llmchat.CallHybridOptimizer,
    llmchat.CallParallelOptimizer,
]]

if __name__ == "__main__":
    @st.cache_resource
    def get_llm():
        return llmchat.agent_executor

    if "started" not in st.session_state:
        st.session_state["started"] = True
        st.session_state["messages"] = [llmchat.AIMessage("Hello, how can I help you?")]
        st.session_state["id"] = get_session()

    st.title("Hello Production!")

    def write_message(message):
        if DataExport.isinstance(message):
            _, c1 = st.columns([3, 1])
            with c1:
                with c1.popover("Export", use_container_width=True):
                    st.markdown(message.path)
            return
        
        with st.chat_message(message.type):
            st.markdown(message.content)

    for message in st.session_state["messages"]:
        write_message(message)

    if prompt := st.chat_input():
        human_message = llmchat.HumanMessage(prompt)
        st.session_state.messages.append(human_message)
        write_message(human_message)
        response = get_llm().invoke(
            {
                "input": prompt,
                "chat_history": [
                    msg for msg in st.session_state.messages
                        if not DataExport.isinstance(msg)
                ],
            }
        )

        # Displaying LLM responce
        output = response["output"]
        with st.chat_message("ai"):
            st.markdown(output)
        st.session_state.messages.append(llmchat.AIMessage(output))

        # Displaying download button if needed
        if "intermediate_steps" in response and len(response["intermediate_steps"]) > 0:
            last_step = response["intermediate_steps"][-1]
            tool_name = last_step[0].tool
            if tool_name in EXPORTING_FUNCTIONS:
                export = DataExport(
                    path=st.session_state["last_function_run"]
                )
                st.session_state.messages.append(export)
                write_message(export)
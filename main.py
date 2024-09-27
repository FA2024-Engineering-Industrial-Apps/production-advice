import streamlit as st
import llm.setup as llmchat
from utils.streamlit_utils import *

import os
from dataclasses import dataclass

@dataclass
class DataExport:
    path: str

    def __post_init__(self):
        self.id = int(os.path.basename(self.path)[:-len(".json")])

    @classmethod
    def isinstance(cls, obj) -> bool:
        return type(obj).__name__ == cls.__name__

EXPORTING_FUNCTIONS = [func.func.__name__ for func in [
    llmchat.CallOptimizer,
    llmchat.CallHybridOptimizer,
    llmchat.CallParallelOptimizer,
]]

def display_export_button(export: DataExport):
    id = export.id
    _, c1 = st.columns([3, 1])
    with c1:
        with c1.popover("Export", use_container_width=True):
            # TODO: implement buttons functionality
            st.download_button(
                label="Download CSV export",
                data="to be implemented",
                file_name=f"export_{export.id}.csv",
                key=f"csv_button_{id}"
            )
            st.download_button(
                label="Download PDF export",
                data="to be implemented",
                file_name=f"export_{export.id}.pdf",
                key=f"pdf_button_{id}"
            )
            st.button(
                label="Deploy to workstation",
                on_click=lambda: print("Deployment was requested"),
                key=f"deploy_button_{id}"
            )

if __name__ == "__main__":
    @st.cache_resource
    def get_llm():
        return llmchat.agent_executor

    if "started" not in st.session_state:
        st.session_state["started"] = True
        st.session_state["messages"] = [
            llmchat.AIMessage("Hello, how can I help you?"),
            # DataExport("./output/1.json") # For testing purposes
        ]
        st.session_state["id"] = get_session()

    st.title("Hello Production!")

    def write_message(message):
        if DataExport.isinstance(message):
            display_export_button(message)
            return
        
        with st.chat_message(message.type):
            st.markdown(message.content)

    for message in st.session_state["messages"]:
        write_message(message)

    if prompt := st.chat_input():
        human_message = llmchat.HumanMessage(prompt)
        st.session_state.messages.append(human_message)
        write_message(human_message)
        response = {}
        with st.status("Thinking..."):
            number_of_tries = 1
            while "output" not in response or "<call_tool>" in response["output"] or "</call_tool>" in response["output"]:
                if number_of_tries == 1:
                    st.write(f"Running the model...")
                else:
                    st.write(f"Rerunning for {number_of_tries}th time...")
                number_of_tries += 1

                response = get_llm().invoke(
                    {
                        "input": prompt,
                        "chat_history": [
                            msg for msg in st.session_state.messages
                                if not DataExport.isinstance(msg)
                        ],
                    },
                    
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
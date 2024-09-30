import streamlit as st
import llm.setup as llmchat
from llm.algorithm_calls import solutions_memory
from utils.streamlit_utils import *
import utils.create_csv as csv_utils
import pandas as pd
import os
import re
import json
from dataclasses import dataclass
from typing import TextIO

import streamlit as st
import pandas as pd
import json
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

    @st.cache_data
    def get_tabular_data(self) -> pd.DataFrame:
        """Loads JSON data and returns it as a Pandas DataFrame."""
        with open(self.path) as file:
            json_data = json.load(file)
        
        csv_file_path = csv_utils.json_solution_to_tabular_csv(self.id, json_data)
        df = pd.read_csv(csv_file_path)

        df.columns = ['combination', 'group', 'product']

        return df

    def export_to_excel(self, excel_file_path: str):
        """Exports the DataFrame to an Excel file."""
        df = self.get_tabular_data()
        df.to_excel(excel_file_path, index=False)

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
            # CSV
            tabular_csv_name = export.get_tabular_data().to_csv(index=False)
            st.download_button(
                label="Download CSV export",
                data=tabular_csv_name,
                file_name=f"export_{export.id}.csv",
                mime="text/csv",
                key=f"csv_button_{id}"
            )

            # Excel
            excel_file_name = f"export_{export.id}.xlsx"
            export.export_to_excel(excel_file_name)
            with open(excel_file_name, "rb") as excel_file:
                st.download_button(
                    label="Download Excel export",
                    data=excel_file,
                    file_name=excel_file_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"excel_button_{id}"
                )

            # Deployment 
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
        with st.status("Thinking...") as status:
            solutions_memory.clear()

            number_of_tries = 1
            while "output" not in response or re.search(r"<(tool|call|ing|_)+(|\/)>", response["output"]):
                if number_of_tries == 1:
                    st.write(f"Running the model...")
                else:
                    st.write(f"Rerunning for {number_of_tries}th time...")
                    st.session_state.messages.append(llmchat.AIMessage("Function execution failed. Remember, that functions accept only JSON input. Please format the user request accordingly."))
                number_of_tries += 1

                def on_tool_call(function_name: str, function_arguments: str) -> None:
                    st.write(f"Using {function_name}...")
                    st.markdown(f"\t`{function_arguments}`")

                response = get_llm().invoke(
                    {
                        "input": prompt,
                        "chat_history": [
                            msg for msg in st.session_state.messages
                                if not DataExport.isinstance(msg)
                        ],
                    },
                    config={
                        "callbacks": [llmchat.OnToolCall(on_tool_call)]
                    }
                )
            status.update(label="Done")

        # Displaying LLM responce
        output = response["output"]
        with st.chat_message("ai"):
            st.markdown(output)
        st.session_state.messages.append(llmchat.AIMessage(output))

        # Displaying download button if needed
        if "intermediate_steps" in response and len(response["intermediate_steps"]) > 0 and \
                "last_function_run" in st.session_state and st.session_state["last_function_run"] is not None:
            last_step = response["intermediate_steps"][-1]
            tool_name = last_step[0].tool
            if tool_name in EXPORTING_FUNCTIONS:
                export = DataExport(
                    path=st.session_state["last_function_run"]
                )
                st.session_state["last_function_run"] = None
                st.session_state.messages.append(export)
                write_message(export)
import streamlit as st
import llm.setup as llmchat
from llm.algorithm_calls import solutions_memory
from utils.streamlit_utils import *
from utils.csv_utils import get_default_vbap_data
from ui.buttons import EXPORTING_FUNCTIONS, DEPLOYING_FUNCTIONS, MessageButton, DataExport, OrderDeployment

import re
import datetime as dt

import pandas as pd


if __name__ == "__main__":
    @st.cache_resource
    def get_llm():
        return llmchat.agent_executor

    @st.cache_resource
    def get_pcb_list():
        return [f"PCB{i:03d}" for i in range(1, 51)]

    if "started" not in st.session_state:
        st.session_state["started"] = True
        st.session_state["messages"] = [
            llmchat.AIMessage("Hello, how can I help you?"),
            # DataExport("./output/1.json") # For testing purposes
        ]
        st.session_state["id"] = get_session()
        st.session_state["vbap_data"] = get_default_vbap_data()

    st.title("Hello Production!")

    def write_message(message):
        if MessageButton.isinstance(message):
            message.display()
            return

        with st.chat_message(message.type):
            st.markdown(message.content)

    # Displaying messages
    for message in st.session_state["messages"]:
        write_message(message)

    
    @st.dialog("Edit SAP data", width="large")
    def edit_sap_data():
        c1, c2, c3, c4 = st.columns(4)
        pcb = c1.selectbox(
            "PCB",
            get_pcb_list(),
            placeholder="Select PCB"
        )
        quantity = c2.number_input(
            "Quantity",
            min_value=1,
            step=1,
            value=1,
            placeholder="Enter quantity"
        )
        delivery_date = c3.date_input(
            "Delivery date",
            value=dt.datetime.strptime("2024-10-03", "%Y-%m-%d"),
            format="YYYY-MM-DD",
        )
        if c4.button("Add"):
            df = st.session_state["vbap_data"]
            df.loc[len(df)] = {
                "MATNR": pcb,
                "KWMENG": quantity,
                "EDATU": pd.to_datetime(delivery_date),

                "VBELN": 1000001001 + len(df.index),
                "POSNR": 200
            }
            df = df.sort_values(by="EDATU", ignore_index=True)
            st.session_state["vbap_data"] = df

        st.write("Current SAP data:")
        st.session_state["vbap_data"] = st.data_editor(
            st.session_state["vbap_data"],
            num_rows="dynamic",
            column_config={
                "EDATU": st.column_config.DateColumn(
                    "EDATU",
                    format="YYYY-MM-DD",
                    step=1
                ),
            },
            hide_index=True
        )

    # Displaying side bar
    st.sidebar.title("Options")
    st.sidebar.button("✏️ Edit SAP data", on_click=edit_sap_data)

    if prompt := st.chat_input():
        human_message = llmchat.HumanMessage(prompt)
        st.session_state.messages.append(human_message)
        write_message(human_message)
        response = {}
        with st.status("Thinking...") as status:
            # In this way the model would have to run algorithm again if the prioritization is requested
            solutions_memory.clear()

            number_of_tries = 1
            while "output" not in response or re.search(r"<(tool|call|ing|_)+(|\/)>", response["output"]):
                if number_of_tries == 1:
                    st.write(f"Running the model...")
                else:
                    st.write(f"Rerunning for {number_of_tries}th time...")
                    # TODO: this should have been a system message
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
                                if not MessageButton.isinstance(msg)
                        ],
                    },
                    config={"callbacks": [
                        llmchat.OnToolCall(on_tool_call),
                        llmchat.OnGetData({"vbap_data": st.session_state["vbap_data"]}),
                    ]}
                )
            status.update(label="Done")

        # Displaying LLM responce
        output = response["output"]
        with st.chat_message("ai"):
            st.markdown(output)
        st.session_state.messages.append(llmchat.AIMessage(output))

        # Displaying download button if needed
        if "intermediate_steps" in response and len(response["intermediate_steps"]) > 0:
            export = None
            order = None
            num_steps = len(response["intermediate_steps"])
            for i, step in enumerate(response["intermediate_steps"]):
                if isinstance(step, tuple) and len(step) == 2 and hasattr(step[0], "tool"):
                    tool_name = step[0].tool
                else:
                    continue

                if tool_name in EXPORTING_FUNCTIONS:
                    export = DataExport(
                        path=st.session_state["last_function_run"]
                    )
                    st.session_state["last_function_run"] = None
                elif i == (num_steps - 1) and tool_name in DEPLOYING_FUNCTIONS:
                    order = OrderDeployment(
                        order=st.session_state["last_order"]
                    )
                    st.session_state["last_order"] = None
            
            message_button = MessageButton(
                export_button=export,
                deploy_button=order
            )
            st.session_state.messages.append(message_button)
            write_message(message_button)
            
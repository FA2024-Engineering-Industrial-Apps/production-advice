import os
import json

import streamlit as st

def sanitize_input(input):
    if isinstance(input, str):
        return json.loads(input)
    return input


current_id = 0
def save_output(json_output: dict):
    global current_id
    id = current_id
    current_id += 1
    
    path = os.path.abspath(os.path.join(
        __file__,
        os.path.pardir,
        os.path.pardir,
        f"output/{id}.json"
    ))
    os.makedirs(
        os.path.dirname(path),
        exist_ok=True
    )
    with open(path, "w") as file:
        file.write(json.dumps(json_output))

    st.session_state["last_function_run"] = path
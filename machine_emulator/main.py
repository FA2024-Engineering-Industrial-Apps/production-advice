import sys, os.path as path
sys.path.append(path.abspath(path.join(__file__, path.pardir, path.pardir)))

import threading
import streamlit as st
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx
import paho.mqtt.subscribe as mqtt_sub

from mqtt.connection import get_params

def write_message(message):
    placeholder = st.empty()
    placeholder.text(f"Received message: {message.payload.decode()}")
    print(f"Received message: {message.payload.decode()}")

if __name__ == "__main__":
    st.title("Machine Emulator 🪛")

    if "status" not in st.session_state:
        st.session_state["start"] = True
        params = get_params()

        MQTT_USER = params['MQTT_USER']
        MQTT_PASSWORD = params['MQTT_PASSWORD']
        MQTT_IP = params['MQTT_IP']
        TOPIC = params['TOPIC']

        # https://discuss.streamlit.io/t/concurrency-with-streamlit/29500/4
        t = threading.Thread(
            target=mqtt_sub.callback,
            args=(
                lambda client, userdata, message: write_message(message),
            ),
            kwargs={
                "topics": TOPIC,
                "hostname": MQTT_IP,
            },
            daemon=True
        )
        add_script_run_ctx(t)
        t.start()
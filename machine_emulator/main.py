import sys, os.path as path
sys.path.append(path.abspath(path.join(__file__, path.pardir, path.pardir)))

import json
import datetime

import streamlit as st
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx
import paho.mqtt.subscribe as mqtt_sub

from mqtt.connection import get_params

if __name__ == "__main__":
    params = get_params()
    MQTT_IP = params['MQTT_IP']
    TOPIC = params['TOPIC']

    st.title("⚙️ Machine Emulator ⚙️")

    def on_message(client, userdata, message):
        data = json.loads(message.payload)
        with st.expander(f"Received data at {datetime.datetime.now().strftime('%H:%M:%S')}"):
            if "production_plan" not in data:
                st.write(data)
                return
            
            markdown = ""
            for day in data["production_plan"]:
                date = day["date"]
                markdown += f"##### {date}\n"

                line = ""
                for entry in day["order"][1:]:
                    if entry == "SETUP_CHANGE":
                        markdown += f"* 🔄️ *setup change*\n\t* {line[:-2]}\n"
                        line = ""
                    elif isinstance(entry, list):
                        line += f"`{entry[1]}` {entry[0]}, "
                if line:
                    markdown += f"* 🔄️ *setup change*\n\t* {line[:-2]}\n"
            
            st.markdown(markdown)

    mqtt_sub.callback(
        on_message,
        TOPIC,
        hostname=MQTT_IP
    )
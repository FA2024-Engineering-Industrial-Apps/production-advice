import os
import re
import time
import json
import csv
from typing import TextIO
import paho.mqtt.client as mqtt

def read_parameter(jsonfile):
    with open(jsonfile) as params:
        data = json.load(params)
        return data
# Function to generate CSV from given input and save with timestamped filename
def create_csv_from_input(input_data):
    # Split the input data by lines and process each line
    data = []
    for line in input_data.strip().split('\n'):
        # Split each line by the first comma only, to keep PCBs grouped together after the first item
        group, pcbs = line.split(',', 1)
        data.append([group, pcbs])

    # Generate timestamp for the file name
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    file_path = f'./output/user_selected_pcbs_{timestamp}.csv'

    # Write to CSV file
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_ALL)
        writer.writerows(data)

    return file_path


def _combination_to_csv(json_data: dict, combination_id: int, writer) -> None:
    for group in json_data["groups"]:
        group_id = group["group_id"]
        for pcb in group["PCBs"]:
            # TODO: also write materials
            writer.writerow([combination_id, group_id, pcb])

def json_solution_to_tabular_csv(file_id: int, json_data: dict) -> str:
    path = os.path.abspath(os.path.join(
        __file__,
        os.path.pardir,
        os.path.pardir,
        f"output/{file_id}_tabular.csv"
    ))

    with open(path, "w") as file:
        writer = csv.writer(file, lineterminator="\n")
        if "groups" in json_data:
            _combination_to_csv(json_data, 1, writer)
            return path
        
        for combination in json_data["combinations"]:
            combination_name, groups = next(iter(combination.items()))
            m = re.match(r"combination(\d+)", combination_name)
            assert m
            _combination_to_csv(
                {"groups": groups},
                int(m.group(1)),
                writer
            )
    
    return path



def publish_user_data(json_data):
    #Use this incase we decide to seperate container for the LLM setup
    # def on_connect(client, userdata, flags, rc):
    #     """Callback function when connected to the broker."""
    #     if rc == 0:
    #         print("Connected to broker successfully")
    #     else:
    #         print(f"Failed to connect, return code {rc}")
# Attach the on_connect callback function
    # client.on_connect = on_connect
    try:
       params = read_parameter('/cfg-data/mqtt-config.json')
       MQTT_USER = params['MQTT_USER']
       MQTT_PASSWORD = params['MQTT_PASSWORD']
       MQTT_IP = params['MQTT_IP']
       TOPIC = params['TOPIC']

# If no config file exists e.g in standalone application, configure with environment variables
    except:
       print("Warning, using default environment values because reading config json file failed")
       MQTT_USER = os.environ['MQTT_USER']
       MQTT_PASSWORD = os.environ['MQTT_PASSWORD']
       MQTT_IP = os.environ['MQTT_IP']
       TOPIC = params['TOPIC']

    json_message = json.dumps(json_data)
    # Create the MQTT client instance
    client = mqtt.Client()
    #set username and password, must be created it databus configurator
    client.username_pw_set(MQTT_USER,MQTT_PASSWORD)
    # Connect to the MQTT broker
    client.connect(MQTT_IP)
    # Start the MQTT loop in a background thread
    client.loop_start()
    # Publish message to the MQTT broker under the specified topic
    client.publish(TOPIC, json_message)
    print(f"Published data: {json_data}")
    # Stop the MQTT loop after publishing the message
    client.loop_stop()
    # Disconnect from the broker
    client.disconnect()
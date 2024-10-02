import sys, os.path as path
sys.path.append(path.abspath(path.join(__file__, path.pardir, path.pardir)))

import json
from utils.docker_utils import is_run_in_docker
import paho.mqtt.client as mqtt


def get_params() -> dict:
    config_path = path.abspath(path.join(
       __file__, path.pardir, "mqtt-config.json"
    ))
    with open(config_path) as config_file:
       params = json.load(config_file)

    if not is_run_in_docker():
        params['MQTT_IP'] = "127.0.0.1"
    
    return params


def publish_user_data(json_data) -> str:
    """
        Returns the result message
    """

    params = get_params()

    MQTT_USER = params['MQTT_USER']
    MQTT_PASSWORD = params['MQTT_PASSWORD']
    MQTT_IP = params['MQTT_IP']
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

    return "Production plan is successfully sent to the edge."


if __name__ == "__main__":
    print(publish_user_data({"test": "test"}))
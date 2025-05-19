
from io import BytesIO
import json
import os
from dotenv import load_dotenv
import requests
import paho.mqtt.client as paho
from paho import mqtt

# This class is used to communicate with the WebServer.
#
class SmartParkAPI:
    camera_url = "camera.php"
    require_new_frame_url =  "require_image.php"
    is_image_request_pending_path = "is_there_camera_image_pending.php"
    update_cv_prediction_path = "update_cv_prediction.php"

    password = ""
    base_url = ""
    mqtt_username = ""
    mqtt_name = ""
    mqtt_server = ""
    mqtt_ai_park_topic = ""
    mqtt_port = 0

    client = None
    

    ########################################
    # MQTT CALLBACKS
    ########################################
    # setting callbacks for different events to see if it works, print the message etc.
    def on_connect(client, userdata, flags, rc, properties=None):
        print("CONNACK received with code %s." % rc)

    # with this callback you can see if your publish was successful
    def on_publish(client, userdata, mid, properties=None):
        print("mid: " + str(mid))

    # print which topic was subscribed to
    def on_subscribe(client, userdata, mid, granted_qos, properties=None):
        print("Subscribed: " + str(mid) + " " + str(granted_qos))

    # used to send the command to the specified callback function
    def on_message(client, userdata, msg):
        SmartParkAPI.on_command(msg.payload.decode())
    ########################################


    # This method is used to open a mqtt connection
    # and creates and return the relative client
    @staticmethod
    def connect_mqtt() -> paho.Client:            
        client = paho.Client(client_id=SmartParkAPI.mqtt_name, userdata=None, protocol=paho.MQTTv5)
        client.on_connect = SmartParkAPI.on_connect

        # enable TLS for secure connection
        client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        # set username and password
        client.username_pw_set(SmartParkAPI.mqtt_username, SmartParkAPI.password)
        # connect to HiveMQ Cloud
        client.connect(SmartParkAPI.mqtt_server, SmartParkAPI.mqtt_port)

        client.on_subscribe = SmartParkAPI.on_subscribe
        client.on_message = SmartParkAPI.on_message
        client.on_publish = SmartParkAPI.on_publish

        SmartParkAPI.client = client

    # Loading base url and password
    # from a .env file
    @staticmethod
    def init():
        load_dotenv()
        SmartParkAPI.base_url = os.getenv("BACKEND")
        SmartParkAPI.base_url = SmartParkAPI.base_url.encode('utf-8').decode('unicode_escape')
        SmartParkAPI.password = os.getenv("PASSWORD")
        SmartParkAPI.mqtt_username = os.getenv("MQTT_USER")
        SmartParkAPI.mqtt_name = os.getenv("MQTT_NAME")
        SmartParkAPI.mqtt_server = os.getenv("MQTT_SERVER")
        SmartParkAPI.mqtt_ai_park_topic = os.getenv("MQTT_AI_PARK_TOPIC")
        SmartParkAPI.mqtt_port = int(os.getenv("MQTT_PORT"))
  
        SmartParkAPI.camera_url = SmartParkAPI.base_url + SmartParkAPI.camera_url
        SmartParkAPI.require_new_frame_url = SmartParkAPI.base_url + SmartParkAPI.require_new_frame_url
        SmartParkAPI.is_image_request_pending_path = SmartParkAPI.base_url + SmartParkAPI.is_image_request_pending_path
        SmartParkAPI.update_cv_prediction_path = SmartParkAPI.base_url + SmartParkAPI.update_cv_prediction_path
        SmartParkAPI.connect_mqtt()

    # def update_cv_prediction(prediction):
    #     SmartParkAPI.get_request(SmartParkAPI.update_cv_prediction_path, params={"info":json.dumps(prediction)})

    def publish_prediction(prediction):
        print(f"sending {prediction} to {SmartParkAPI.mqtt_ai_park_topic}")
        if(SmartParkAPI.client is not None):
            SmartParkAPI.client.publish(SmartParkAPI.mqtt_ai_park_topic, payload=str(prediction), qos=2, retain=True)
        else:
            raise ValueError("mqtt client is None. Please make sure you call SmartParkAPI.init() to initialize the mqtt server.")

    def require_new_frame():
        SmartParkAPI.get_request(SmartParkAPI.require_new_frame_url, params={}, stream=True)

    def is_image_request_pending():
        response = SmartParkAPI.get_request(SmartParkAPI.is_image_request_pending_path, params={}, stream=True)
        return response.content == b'True'

    def fetch_image():
        try:
            response = SmartParkAPI.get_request(SmartParkAPI.camera_url, params={}, stream=True)
            response.raise_for_status() 

            if 'image' in response.headers['content-type']:
                return BytesIO(response.content)
            else:
                return None

        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
        except Exception as e:
            print(f"Some error occurred: {e}")

        return None


    # This method is used to make a 
    # get request. It automatically uses
    # the specified password in the .env
    @staticmethod
    def get_request(url, params, stream = None) -> requests.Response:
        params["password"] = SmartParkAPI.password
        print(params)
        return requests.get(url, params, stream = stream)
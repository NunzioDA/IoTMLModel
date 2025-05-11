
from io import BytesIO
import json
import os
from dotenv import load_dotenv
import requests

# This class is used to communicate with the WebServer.
#
class WebServer:
    camera_url = "camera.php"
    require_new_frame_url =  "require_image.php"
    is_image_request_pending_path = "is_there_camera_image_pending.php"
    update_cv_prediction_path = "update_cv_prediction.php"

    password = ""
    base_url = ""

    # Loading base url and password
    # from a .env file
    @staticmethod
    def init():
        load_dotenv()
        WebServer.base_url = "https://www.coinquilinipercaso.altervista.org/IoTProject/"
        WebServer.base_url = WebServer.base_url.encode('utf-8').decode('unicode_escape')
        WebServer.password = os.getenv("PASSWORD")
  
        WebServer.camera_url = WebServer.base_url + WebServer.camera_url
        WebServer.require_new_frame_url = WebServer.base_url + WebServer.require_new_frame_url
        WebServer.is_image_request_pending_path = WebServer.base_url + WebServer.is_image_request_pending_path
        WebServer.update_cv_prediction_path = WebServer.base_url + WebServer.update_cv_prediction_path

    def update_cv_prediction(prediction):
        WebServer.get_request(WebServer.update_cv_prediction_path, params={"info":json.dumps(prediction)})

    def require_new_frame():
        WebServer.get_request(WebServer.require_new_frame_url, params={}, stream=True)

    def is_image_request_pending():
        response = WebServer.get_request(WebServer.is_image_request_pending_path, params={}, stream=True)
        return response.content == b'True'

    def fetch_image():
        try:
            response = WebServer.get_request(WebServer.camera_url, params={}, stream=True)
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
        params["password"] = WebServer.password
        print(params)
        return requests.get(url, params, stream = stream)
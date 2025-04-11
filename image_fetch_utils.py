import requests
from io import BytesIO

base_path = "https://coinquilinipercaso.altervista.org/IoTProject/"
camera_url = base_path + "camera.php"
require_new_frame_url = base_path + "require_image.php"
is_image_request_pending_path = base_path + "is_there_camera_image_pending.php"
password = ""

def require_new_frame():
    requests.get(require_new_frame_url, params={"password":password}, stream=True)

def is_image_request_pending():
    response = requests.get(is_image_request_pending_path, params={"password":password}, stream=True)
    return response.content == b'True'

def fetch_image():
    try:
        response = requests.get(camera_url, params={"password":password}, stream=True)
        response.raise_for_status()  # Verifica se la risposta è OK

        if 'image' in response.headers['content-type']:
            return BytesIO(response.content)
        else:
            return None

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
    except Exception as e:
        print(f"Some error occurred: {e}")

    return None
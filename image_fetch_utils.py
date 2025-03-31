import requests
from io import BytesIO

base_path = "https://coinquilinipercaso.altervista.org/IoTProject/"
camera_url = base_path + "camera.php"
require_new_frame_url = base_path + "require_image.php"
password = ""

def require_new_frame():
    requests.get(require_new_frame_url, params={"password":password}, stream=True)

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
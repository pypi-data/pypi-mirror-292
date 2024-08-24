import time
import requests
from io import BytesIO
from PIL import Image
from base64 import b64decode, b64encode

from .types import AppiumSessionConfig


def delay(milliseconds: int) -> None:
    """Delays execution for a given number of milliseconds."""
    time.sleep(milliseconds / 1000)


def get_screenshot(appium_session_config: AppiumSessionConfig) -> str:
    """Fetches a screenshot from the Appium server and optionally resizes it if the platform is iOS."""
    screenshot_response = requests.get(
        f"http://{appium_session_config.appium_server_config.host}:"
        f"{appium_session_config.appium_server_config.port}/session/"
        f"{appium_session_config.id}/screenshot"
    )

    screenshot = screenshot_response.json()['value']

    image_data = b64decode(screenshot)
    image = Image.open(BytesIO(image_data))
    image = image.resize((image.size[0], image.size[1]))
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    screenshot = b64encode(buffered.getvalue()).decode('utf-8')

    return screenshot

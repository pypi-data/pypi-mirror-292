import os
from datetime import datetime


def take_screenshot(driver, directory):
    current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    file_name = f'screenshot_{current_time}.png'
    file_path = os.path.join(directory, file_name)

    try:
        driver.save_screenshot(file_path)
        return file_path
    except Exception as e:
        print(f"Failed to capture screenshot: {e}")
        return None

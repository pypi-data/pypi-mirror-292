import cv2
import pyautogui
import numpy as np
import time
import keyboard
from PIL import ImageGrab
from config import IMAGE_PATHS

class ImageClicker:
    def __init__(self):
        self.images = [cv2.imread(img_path, cv2.IMREAD_GRAYSCALE) for img_path in IMAGE_PATHS]
        self.running = False

    def find_and_click(self):
        screen = np.array(ImageGrab.grab())
        screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)

        for img in self.images:
            result = cv2.matchTemplate(screen_gray, img, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            if max_val > 0.8:  # Threshold for image matching
                x, y = max_loc
                h, w = img.shape
                pyautogui.click(x + w // 2, y + h // 2)
                print(f"Clicked at {(x + w // 2, y + h // 2)}")

    def run(self):
        while self.running:
            self.find_and_click()
            time.sleep(0.1)  # Adjust this for performance

    def start(self):
        self.running = True
        self.run()

    def stop(self):
        self.running = False

if __name__ == "__main__":
    clicker = ImageClicker()

    def on_press_f6(e):
        if not clicker.running:
            clicker.start()
        else:
            clicker.stop()

    keyboard.on_press_key("f6", on_press_f6)
    print("Press F6 to start/stop the clicker.")

    keyboard.wait("esc")  # Wait for the user to press the escape key to exit

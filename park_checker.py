import sys
import os

from tools import WebServer
os.environ["QT_QPA_PLATFORM"] = "xcb"
from datetime import datetime
import io

import torch
from PIL import Image, ImageDraw

from PyQt6.QtWidgets import QApplication, QLabel, QHBoxLayout, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QTimer, Qt

from image_management import split_image
from model.classes.veichle_detection_cnn import *


class ParkChecker(QWidget):
    def __init__(self, interval=300):
        super().__init__()
        WebServer.init()
        self.setWindowTitle("Park Checker - Split View")
        self.setGeometry(100, 100, 200*3, 480) 

        self.labels = [QLabel("Loading...") for _ in range(3)]
        for label in self.labels:
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.save_buttons = [QPushButton(f"Save Part {i+1}") for i in range(3)]
        for button in self.save_buttons:
            button.setEnabled(False)
        self.save_buttons[0].clicked.connect(lambda: self.save_image(0))
        self.save_buttons[1].clicked.connect(lambda: self.save_image(1))
        self.save_buttons[2].clicked.connect(lambda: self.save_image(2))

        hbox = QHBoxLayout()
        for label in self.labels:
            hbox.addWidget(label)

        button_layout = QHBoxLayout()
        for button in self.save_buttons:
            button_layout.addWidget(button)

        layout = QVBoxLayout()
        layout.addLayout(hbox)
        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_image)
        self.timer.start(interval)

        self.current_image_parts_with_boxes = [None] * 3  
        self.original_image_parts = [None] * 3  
        self.load_model()

    def load_model(self):
        self.model = VehicleDetectionCNN()
        self.model.load_state_dict(torch.load('./model/saved/park_model.pth', map_location=torch.device('cpu')))
        self.model.eval()

    def update_image(self):
        if not WebServer.is_image_request_pending():
            print("Requiring Image")
            WebServer.require_new_frame()
            image_data = WebServer.fetch_image()
            if image_data:
                image = Image.open(image_data).convert('RGB')
                print("Got image")
                images_split = split_image(image)
                self.current_image_parts_with_boxes = [io.BytesIO() for _ in range(3)]
                self.original_image_parts = list(images_split) # Saving images without borders
                predictions = []

                for i, img_part in enumerate(images_split):
                    input_tensor = transform(img_part).unsqueeze(0)
                    with torch.no_grad():
                        output = self.model(input_tensor)
                        pred = int(output > 0.5)
                        predictions.append(pred)

                    # Copy to draw borders
                    img_with_boxes = img_part.copy()
                    draw = ImageDraw.Draw(img_with_boxes)
                    color = (0, 255, 0) if pred == 1 else (255, 0, 0)
                    draw.rectangle([0, 0, img_with_boxes.width - 1, img_with_boxes.height - 1], outline=color, width=1)

                
                    img_with_boxes.save(self.current_image_parts_with_boxes[i], format="PNG")

                    # Visializing image with borders
                    qt_image = self.pil_to_qt(img_with_boxes)
                    self.labels[i].setPixmap(qt_image)
                    self.labels[i].setScaledContents(True)
                    self.save_buttons[i].setEnabled(True)
                WebServer.update_cv_prediction(predictions)
            else:
                for label in self.labels:
                    label.setText("Failed to load image")
                for button in self.save_buttons:
                    button.setEnabled(False)

        

    def pil_to_qt(self, pil_image):
        """Convert PIL Image to QPixmap"""
        buffer = io.BytesIO()
        pil_image.save(buffer, format="PNG")
        qt_image = QPixmap()
        qt_image.loadFromData(buffer.getvalue())
        return qt_image

    def save_image(self, index):
        """Saving image without borders"""
        if self.original_image_parts[index]:
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            buffer = io.BytesIO()
            self.original_image_parts[index].save(buffer, format="PNG")
            with open(f"saved_original_part_{index + 1}_{now}.png", "wb") as f:
                f.write(buffer.getvalue())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = ParkChecker()
    viewer.show()
    sys.exit(app.exec())
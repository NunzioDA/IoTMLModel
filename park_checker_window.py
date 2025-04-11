import sys

from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QTimer, Qt

from image_fetch_utils import *



class ImageViewer(QWidget):
    def __init__(self, interval=300):  # Aggiornamento ogni 5 secondi
        super().__init__()
        self.setWindowTitle("Image Viewer")
        self.setGeometry(100, 100, 640, 480)

        self.label = QLabel("Loading image...")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_image)
        self.timer.start(interval)

        self.update_image()

    def update_image(self):
        if not is_image_request_pending():
            require_new_frame()
            image_data = fetch_image()
            if image_data:
                pixmap = QPixmap()
                pixmap.loadFromData(image_data.getvalue())
                self.label.setPixmap(pixmap)
                self.label.setScaledContents(True)
            else:
                self.label.setText("Failed to load image")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = ImageViewer()
    viewer.show()
    sys.exit(app.exec())
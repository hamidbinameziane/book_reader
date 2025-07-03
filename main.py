import sys
import fitz
import json
import os
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QTimer


class PDFViewer(QWidget):
    def __init__(self, pdf_path):
        super().__init__()
        self.doc = fitz.open(pdf_path)
        self.save_file = "position.json"
        self.page_index = self.load_last_position()
        self.code_buffer = ""

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowState(Qt.WindowFullScreen)

        # Fix: delay hiding cursor until window is shown
        QTimer.singleShot(500, lambda: self.setCursor(Qt.BlankCursor))

        self.labels = [QLabel() for _ in range(2)]
        for label in self.labels:
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("background-color: black;")

        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        for label in reversed(self.labels):  # RTL
            layout.addWidget(label)
        self.setLayout(layout)

        self.load_pages()

    def load_last_position(self):
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, "r") as f:
                    data = json.load(f)
                    value = int(data.get("page_index", 0))
                    if 0 <= value < len(self.doc):
                        return value
            except:
                pass
        return 0

    def save_position(self):
        with open(self.save_file, "w") as f:
            json.dump({"page_index": self.page_index}, f)

    def keyPressEvent(self, event):
        key = event.key()

        if key == Qt.Key_Down:
            if self.page_index + 2 < len(self.doc):
                self.page_index += 2
                self.load_pages()
                self.save_position()

        elif key == Qt.Key_Up:
            if self.page_index - 2 >= 0:
                self.page_index -= 2
                self.load_pages()
                self.save_position()

        elif key == Qt.Key_Escape:
            self.save_position()
            self.close()

        elif Qt.Key_0 <= key <= Qt.Key_9:
            digit = chr(key)
            self.code_buffer += digit

            if len(self.code_buffer) == 4:
                try:
                    target_page = int(self.code_buffer)
                    if 1 <= target_page <= len(self.doc):
                        self.page_index = target_page - 1
                        self.load_pages()
                        self.save_position()
                except ValueError:
                    pass  # Should not happen
                finally:
                    # Always reset the buffer after a 4-digit attempt
                    self.code_buffer = ""

    def load_pages(self):
        zoom = 2.0
        mat = fitz.Matrix(zoom, zoom)
        page_numbers = [self.page_index + i for i in range(2)]

        for i, label in enumerate(self.labels):
            page_num = page_numbers[i]
            if 0 <= page_num < len(self.doc):
                page = self.doc[page_num]
                pix = page.get_pixmap(matrix=mat, alpha=False)
                img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
                img.invertPixels()
                pixmap = QPixmap.fromImage(img)
                label.setPixmap(pixmap.scaled(
                    label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                label.clear()

    def resizeEvent(self, event):
        self.load_pages()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = PDFViewer("sample.pdf")  # Replace with your file
    viewer.show()
    sys.exit(app.exec_())


import sys
import os
import json
import re
import rasterio
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTextEdit, QFileDialog, QMessageBox, QScrollArea, QInputDialog, QStyleFactory
)
from PyQt5.QtGui import QFont, QFontDatabase, QTextCursor, QTextCharFormat, QClipboard, QIcon, QColor, QPalette
from PyQt5.QtCore import Qt, QTimer

class OrthophotoTool(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Orthophoto Tool")
        self.setMinimumSize(800, 600)

        # Set platform-specific style
        if sys.platform == 'win32':
            # Use Fusion style on Windows for a more modern look
            QApplication.setStyle(QStyleFactory.create('Fusion'))
            # Set a modern color palette
            palette = QApplication.palette()
            palette.setColor(QPalette.Window, QColor(240, 240, 240))
            palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
            palette.setColor(QPalette.Base, QColor(255, 255, 255))
            palette.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
            palette.setColor(QPalette.Button, QColor(240, 240, 240))
            palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))
            QApplication.setPalette(palette)

        # Load custom font
        regular_font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'fonts', 'fccTYPO-Regular.ttf')
        bold_font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'fonts', 'fccTYPO-Bold.ttf')
        self.regular_font_id = QFontDatabase.addApplicationFont(regular_font_path)
        self.bold_font_id = QFontDatabase.addApplicationFont(bold_font_path)
        regular_families = QFontDatabase.applicationFontFamilies(self.regular_font_id)
        bold_families = QFontDatabase.applicationFontFamilies(self.bold_font_id)
        print("Regular font families:", regular_families)
        print("Bold font families:", bold_families)
        self.custom_font = QFont(regular_families[0], 11) if regular_families else QFont("Arial", 11)
        self.bold_font = QFont(bold_families[0], 11) if bold_families else QFont("Arial", 11)
        self.bold_font.setWeight(QFont.Bold)
        QApplication.setFont(self.custom_font)

        # State
        self.tiff_path = None
        self.json_path = None
        self.last_drone = None
        self.last_gsd = None
        self.last_crs = None
        self.last_output = None

        # Layouts
        main_layout = QVBoxLayout(self)
        button_layout = QHBoxLayout()
        main_layout.addLayout(button_layout)

        # Status label
        self.status_label = QLabel("No files loaded")
        self.status_label.setFont(self.custom_font)
        button_layout.addWidget(self.status_label, stretch=1)

        # Buttons
        self.tiff_button = QPushButton("Load TIFF")
        self.tiff_button.setFont(self.custom_font)
        self.tiff_button.clicked.connect(self.load_tiff)
        button_layout.addWidget(self.tiff_button)

        self.json_button = QPushButton("Load JSON")
        self.json_button.setFont(self.custom_font)
        self.json_button.clicked.connect(self.load_json)
        button_layout.addWidget(self.json_button)

        self.process_button = QPushButton("Process Files")
        self.process_button.setFont(self.custom_font)
        self.process_button.clicked.connect(self.process_files)
        button_layout.addWidget(self.process_button)

        self.reset_button = QPushButton("🔄")
        self.reset_button.setFont(self.custom_font)
        self.reset_button.setToolTip("Reset and select new files")
        self.reset_button.setStyleSheet("QPushButton { border: none; background: transparent; }")
        self.reset_button.clicked.connect(self.reset_app)
        button_layout.addWidget(self.reset_button)

        # Text area for metadata
        self.text_edit = QTextEdit()
        self.text_edit.setFont(self.custom_font)
        self.text_edit.setReadOnly(True)
        main_layout.addWidget(self.text_edit, stretch=1)

        # Compile Output and output label
        compile_layout = QHBoxLayout()
        self.compile_button = QPushButton("Compile Output")
        self.compile_button.setFont(self.custom_font)
        self.compile_button.clicked.connect(self.compile_output)
        compile_layout.addWidget(self.compile_button)

        self.output_label = QLabel("Output:")
        self.output_label.setFont(self.custom_font)
        self.output_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.output_label.setToolTip("Click to copy")
        self.output_label.mousePressEvent = self.copy_output_to_clipboard
        compile_layout.addWidget(self.output_label)
        main_layout.addLayout(compile_layout)

        # Load camera modules
        self.camera_modules = self.load_camera_modules()

        self.update_status()

    def reset_app(self):
        self.tiff_path = None
        self.json_path = None
        self.last_drone = None
        self.last_gsd = None
        self.last_crs = None
        self.last_output = None
        self.text_edit.clear()
        self.output_label.setText("Output:")
        self.update_status()

    def update_status(self):
        status = []
        if self.tiff_path:
            status.append(f"TIFF: {os.path.basename(self.tiff_path)}")
        if self.json_path:
            status.append(f"JSON: {os.path.basename(self.json_path)}")
        self.status_label.setText(" | ".join(status) if status else "No files loaded")

        # Step logic
        self.tiff_button.setEnabled(not self.tiff_path)
        self.json_button.setEnabled(bool(self.tiff_path) and not self.json_path)
        self.process_button.setEnabled(bool(self.tiff_path) and bool(self.json_path))

    def load_tiff(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select TIFF file", "", "TIFF files (*.tif);;All files (*)")
        if path:
            self.tiff_path = path
            self.update_status()

    def load_json(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select camera metadata JSON file", "", "JSON files (*.json);;All files (*)")
        if path:
            self.json_path = path
            self.update_status()

    def load_camera_modules(self):
        try:
            json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'drone-camera-modules.json')
            with open(json_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.log(f"Error loading camera modules: {e}", heading=True)
            return []

    def log(self, message, heading=False, attribute=False, end="\n"):
        cursor = self.text_edit.textCursor()
        fmt = QTextCharFormat()
        if heading:
            heading_font = QFont(self.bold_font)
            heading_font.setPointSize(self.custom_font.pointSize() + 3)
            fmt.setFont(heading_font)
        elif attribute:
            fmt.setFont(self.bold_font)
        else:
            fmt.setFont(self.custom_font)
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(message + ("" if end == "" else end), fmt)
        self.text_edit.setTextCursor(cursor)
        self.text_edit.ensureCursorVisible()

    def process_files(self):
        self.text_edit.clear()
        self.last_drone = None
        self.last_gsd = None
        self.last_crs = None
        self.last_output = None

        if not self.tiff_path or not self.json_path:
            self.log("Please load both TIFF and JSON files first", heading=True)
            return

        # TIFF
        try:
            with rasterio.open(self.tiff_path) as src:
                self.log("=== Basic Information ===", heading=True)
                self.log("Size: ", attribute=True, end="")
                self.log(f"{src.width} x {src.height}")
                self.log("Resolution: ", attribute=True, end="")
                self.log(f"{src.res} meters per pixel")
                self.log("Coordinate Reference System (CRS): ", attribute=True, end="")
                self.log(f"{src.crs}")
                self.log("Number of bands: ", attribute=True, end="")
                self.log(f"{src.count}")
                self.log("Data type: ", attribute=True, end="")
                self.log(f"{src.dtypes[0]}")
                self.log("")
                self.log("=== Transform Information ===", heading=True)
                self.log("Transform: ", attribute=True, end="")
                self.log(f"| {src.transform[0]:.2f}, {src.transform[1]:.2f}, {src.transform[2]:.2f} | | {src.transform[3]:.2f}, {src.transform[4]:.2f}, {src.transform[5]:.2f} | | {src.transform[6]:.2f}, {src.transform[7]:.2f}, {src.transform[8]:.2f} |")
                self.log("")
                self.log("=== Bounds ===", heading=True)
                self.log("Bounds: ", attribute=True, end="")
                self.log(f"{src.bounds}")
                self.log("")
                self.log("=== Tags ===", heading=True)
                for key, value in src.tags().items():
                    self.log(f"{key}: ", attribute=True, end="")
                    self.log(f"{value}")
                self.log("")
                self.log("=== Band Information ===", heading=True)
                for i in range(src.count):
                    if i > 0:
                        self.log("")
                    self.log(f"Band {i+1}:", attribute=True)
                    self.log("  Data type: ", attribute=True, end="")
                    self.log(f"{src.dtypes[i]}")
                    self.log("  No data value: ", attribute=True, end="")
                    self.log(f"{src.nodatavals[i]}")
                    if src.descriptions[i]:
                        self.log("  Description: ", attribute=True, end="")
                        self.log(f"{src.descriptions[i]}")
                self.log("")
                # GSD and CRS
                if hasattr(src, 'res') and src.res:
                    gsd_cm = (src.res[0] + src.res[1]) / 2 * 100
                    self.last_gsd = round(gsd_cm, 2)
                else:
                    self.last_gsd = None
                self.last_crs = str(src.crs) if src.crs else None
        except Exception as e:
            self.log(f"Error reading TIFF file: {e}", heading=True)

        # JSON
        try:
            with open(self.json_path, 'r') as f:
                data = json.load(f)
                camera_model_str = next(iter(data))
                camera_data = data[camera_model_str]
                self.log("=== Camera Metadata ===", heading=True)
                # Attribute bold, value normal (same line)
                self.log("Camera Model: ", attribute=True, end="")
                self.log(f"{camera_model_str}")
                # Parse camera code from the camera model string (not the key)
                camera_code = self.parse_camera_model(camera_model_str)
                drone_model = None
                if camera_code:
                    drone_model = self.select_camera_model(camera_code)
                    if drone_model:
                        self.log("Drone: ", attribute=True, end="")
                        self.log(f"{drone_model}")
                self.last_drone = drone_model
        except Exception as e:
            self.log(f"Error reading JSON file: {e}", heading=True)

    def parse_camera_model(self, camera_model_str):
        # Extract camera code from the string (e.g., "fc6310" from "dji fc6310 5472 3648 brown 0.6666")
        match = re.search(r'fc\d+', camera_model_str.lower())
        if match:
            return match.group(0).upper()
        return None

    def select_camera_model(self, camera_code):
        matching_models = [module for module in self.camera_modules if module['camera_code'] == camera_code]
        if len(matching_models) == 1:
            return matching_models[0]['drone_model']
        elif len(matching_models) > 1:
            items = [m['drone_model'] for m in matching_models]
            item, ok = QInputDialog.getItem(self, "Select Camera Model",
                                            f"Decoded camera code '{camera_code}' is assigned to multiple drone models.\nPlease select the correct one:",
                                            items, 0, False)
            if ok:
                return item
        return None

    def compile_output(self):
        if self.last_drone and self.last_gsd is not None and self.last_crs:
            output = f"DJI {self.last_drone} | GSD: {self.last_gsd} cm/px | CRS: {self.last_crs}"
        else:
            output = "(missing data, please process files first)"
        self.last_output = output
        self.output_label.setText(f"Output: {output}")

    def copy_output_to_clipboard(self, event):
        if self.last_output and "missing data" not in self.last_output:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.last_output)
            old_text = self.output_label.text()
            self.output_label.setText("Output copied!")
            QTimer.singleShot(1500, lambda: self.output_label.setText(old_text))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'icons', 'icon.icns' if sys.platform == 'darwin' else 'icon.ico' if sys.platform == 'win32' else 'icon.png')
    app.setWindowIcon(QIcon(icon_path))
    window = OrthophotoTool()
    window.show()
    sys.exit(app.exec_())
<p align="center">
  <a href="https://i.ibb.co/G4YRzK8J/GSD.png">
    <img src="https://i.ibb.co/G4YRzK8J/GSD.png" alt="Orthophoto Tool Logo" width="250"/>
  </a>
</p>

<h1 align="center">Orthophoto Tool</h1>
<p align="center"><em>(Born4Flight | FlyCamCzech | Jakub Ešpandr)</em></p>

## Overview
The Orthophoto Tool is designed to help users analyze and visualize metadata from TIFF and JSON files, particularly for drone imagery. It provides a user-friendly interface for loading, processing, and compiling metadata, making it easier to manage and interpret large datasets. One of its key features is the ability to calculate the Ground Sample Distance (GSD) resolution, which is crucial for understanding the spatial resolution of aerial imagery.

---

## ✨ Features

- Load and display TIFF metadata.
- Load and display camera metadata from a JSON file.
- Match camera codes to drone models using a predefined JSON file.
- Compile and copy output summary to clipboard.
- Customizable UI with support for custom fonts and icons.

---

## 📦 Requirements

- Python 3.6+  
- [PyQt5](https://doc.qt.io/qtforpython/) – Qt bindings for Python  
- [rasterio](https://rasterio.readthedocs.io/) – Geospatial raster I/O library

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/Jakub-Espandr/OrthophotoTool.git
cd OrthophotoTool

# (Optional) Create and activate a virtual environment
python -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate

# Install required dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

---

## 🛠️ Usage

1. **Load TIFF File**: Click the "Load TIFF" button to select a TIFF file.
2. **Load JSON File**: Click the "Load JSON" button to select a JSON file containing camera metadata.
3. **Process Files**: Click the "Process Files" button to display the metadata.
4. **Compile Output**: Click the "Compile Output" button to generate a summary and copy it to the clipboard.
5. **Reset**: Click the reset button (🔄) to clear the current state and start over.

---

## 📁 Project Structure

```
OrthophotoTool/
├── main.py                  # Entry point
├── assets/
│   ├── icons/               # Application icons
│   └── fonts/               # Custom fonts
├── drone-camera-modules.json # JSON file for camera modules
└── requirements.txt         # Dependencies
```

---

## 🔐 License

This project is licensed under the **Non-Commercial Public License (NCPL v1.0)**  
© 2025 Jakub Ešpandr - Born4Flight, FlyCamCzech

See the [LICENSE](https://github.com/Jakub-Espandr/OrthophotoTool/raw/main/LICENSE) file for full terms.
---

## 🙏 Acknowledgments

- Built with ❤️ using PyQt5 and open-source libraries

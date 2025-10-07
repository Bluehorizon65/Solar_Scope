# 🔋 Google Hackathon - Solar-Based Web Application

## 🏠 Rooftop Detection & Solar Panel Placement System

An advanced computer vision system for detecting rooftops in satellite images and optimally placing solar panels using targeted color detection and intelligent placement algorithms.

## 🚀 Features

### 🎯 Advanced Rooftop Detection
- **32 Color Target System**: Precisely detects rooftops using specific RGB color values
- **Configurable Tolerance**: Easy-to-adjust tolerance levels for optimal detection
- **Morphological Filtering**: Advanced shape and area filtering for building-like structures
- **Multi-region Support**: Handles complex rooftop layouts with multiple areas

### ⚡ Smart Solar Panel Placement
- **Custom Panel Mode**: Place exact number of panels (40x25 pixels, numbered)
- **Interactive Input**: User-friendly prompt for panel count selection
- **Optimal Positioning**: Intelligent placement algorithm with coverage requirements
- **Visual Results**: Clean 3-panel output (Original → Detected → Result)

## 🛠️ Quick Start

### Prerequisites
```bash
pip install opencv-python matplotlib numpy
```

### Basic Usage
1. **Configure your image** (edit line 11):
   ```python
   INPUT_IMAGE_PATH = "testcases/your_image.png"
   ```

2. **Adjust tolerance if needed** (edit line 16):
   ```python
   TOLERANCE_VALUES = [3, 2]  # Default values
   ```

3. **Run the script**:
   ```bash
   python rooftop_detection_gk.py
   ```

4. **Enter number of panels** when prompted

## 📁 Project Structure
```
├── rooftop_detection_gk.py    # Main detection script
├── requirements.txt           # Dependencies
├── TOLERANCE_GUIDE.md        # Configuration guide
├── testcases/               # Sample images
│   ├── image.png
│   ├── image copy 2.png
│   └── image copy 3.png
└── README.md               # This file
```

## 🎯 Configuration Options

### Tolerance Settings
- `[3, 2]` - Default balanced detection
- `[5, 4, 3]` - More inclusive (varied colors)
- `[2, 1]` - Very precise (consistent colors)
- `[4]` - Single tolerance (faster)

### Example Outputs
- `final_rooftops_[image].jpg` - Detected rooftop mask
- `final_solar_custom_[image].jpg` - Final result with panels

## 🏆 GK Hacks Competition

This project was developed for the Google Hackathon focusing on solar-based web applications. The system demonstrates:
- ✅ Real-time rooftop detection
- ✅ Intelligent solar panel placement
- ✅ User-friendly interface
- ✅ Configurable parameters
- ✅ Professional visualization

---
**Team**: GK Hacks | **Focus**: Solar Energy Solutions | **Tech**: Computer Vision + AI

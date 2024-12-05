# Speed Camera

This Python package detects vehicle speed using a Raspberry Pi, YOLO, and OpenCV.

## Features
- Detects motion in a specified area.
- Calculates speed in miles per hour (MPH).
- Easy-to-setup monitoring region with mouse clicks.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/speed_camera.git
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
   
1. Run the speed_camera script to start monitoring:
   ```bash
   python -m speed_camera.speed_camera
   ```

## Dependencies

1. OpenCV
2. NumPy
3. picamera2
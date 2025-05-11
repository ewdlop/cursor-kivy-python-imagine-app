# 2D Image Editor

A simple 2D image editor developed using Python and Kivy.

## Features

- Load images from file system
- Basic image operations:
  - Rotate images
  - Convert to grayscale
- Advanced image adjustments:
  - Brightness adjustment (0.0 - 2.0)
  - Contrast adjustment (0.0 - 2.0)
- Image manipulation:
  - Crop with precise coordinates
  - Resize with aspect ratio preservation
- Preview functionality:
  - Real-time preview for all adjustments
  - Image preview in file selection
- Save edited images

## Requirements

- Python 3.7 or higher
- Kivy 2.2.1
- Pillow 10.2.0

## Installation

1. Clone or download this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

```bash
python image_editor.py
```

## Usage Instructions

### Basic Operations
1. Click "Load Image" to select an image to edit
2. Use "Rotate" to rotate the image 90 degrees clockwise
3. Use "Grayscale" to convert the image to grayscale

### Image Adjustments
1. Brightness:
   - Click "Brightness" button
   - Use slider to adjust brightness (0.0 - 2.0)
   - Preview changes in real-time
   - Click "Apply" to confirm or "Reset" to revert

2. Contrast:
   - Click "Contrast" button
   - Use slider to adjust contrast (0.0 - 2.0)
   - Preview changes in real-time
   - Click "Apply" to confirm or "Reset" to revert

### Image Manipulation
1. Crop:
   - Click "Crop" button
   - Enter precise coordinates for crop area
   - Preview the crop area
   - Click "Apply" to confirm

2. Resize:
   - Click "Resize" button
   - Enter desired width and height
   - Toggle "Maintain aspect ratio" if needed
   - Click "Apply" to confirm

### Saving
1. Click "Save Image" button
2. Choose save location
3. Enter filename (default includes timestamp)
4. Click "Save" to save the edited image

## Notes

- Supports common image formats (PNG, JPEG, BMP, etc.)
- Recommended to use smaller image files for better performance
- All adjustments can be previewed before applying
- Original image is preserved until changes are applied
- Temporary files are automatically cleaned up

## Troubleshooting

- If image adjustments don't work, ensure the image is in a compatible format
- For large images, some operations might be slower
- Make sure you have sufficient disk space for temporary files 
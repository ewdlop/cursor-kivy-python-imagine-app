# 图像编辑器 / Image Editor

一个功能丰富的图像编辑应用程序，使用 Python 和 Kivy 构建。
A feature-rich image editing application built with Python and Kivy.

## 功能特点 / Features

### 基本操作 / Basic Operations
- 加载图片 / Load images
- 旋转图片 / Rotate images
- 水平/垂直翻转 / Flip horizontally/vertically
- 转换为灰度图 / Convert to grayscale
- 调整亮度 / Adjust brightness
- 调整对比度 / Adjust contrast

### 滤镜效果 / Filter Effects
- 模糊效果 / Blur effect
- 锐化效果 / Sharpen effect
- 边缘检测 / Edge detection
- 浮雕效果 / Emboss effect
- 支持多个滤镜叠加 / Support multiple filter stacking

### 特效处理 / Special Effects
- 卡通效果 / Cartoon effect
- 素描效果 / Sketch effect
- 边缘检测 / Edge detection
- 降噪处理 / Noise reduction
- 棕褐色效果 / Sepia effect
- 反色效果 / Invert effect
- 轮廓效果 / Contour effect

### 颜色调整 / Color Adjustments
- RGB 通道独立调整 / RGB channel adjustment
- 饱和度调整 / Saturation adjustment
- 锐化调整 / Sharpness adjustment
- 模糊效果（高斯、盒式、中值）/ Blur effects (Gaussian, Box, Median)
- 噪点效果（高斯、椒盐、斑点）/ Noise effects (Gaussian, Salt & Pepper, Speckle)
- 晕影效果 / Vignette effect

### 图像调整 / Image Adjustments
- 裁剪 / Crop
- 调整大小（支持保持宽高比）/ Resize (with aspect ratio preservation)
- 撤销/重做（最多10步）/ Undo/Redo (up to 10 steps)

## 系统要求 / System Requirements

- Python 3.9 或更高版本 / Python 3.9 or higher
- Kivy 2.2.1
- Pillow 10.2.0
- OpenCV 4.9.0
- NumPy 1.26.4

## 安装 / Installation

1. 克隆仓库 / Clone the repository:
```bash
git clone [repository-url]
cd [repository-name]
```

2. 创建虚拟环境（推荐）/ Create virtual environment (recommended):
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或 / or
.venv\Scripts\activate  # Windows
```

3. 安装依赖 / Install dependencies:
```bash
pip install -r requirements.txt
```

## 使用方法 / Usage

1. 运行应用程序 / Run the application:
```bash
python image_editor.py
```

2. 基本操作 / Basic operations:
   - 点击"Load Image"加载图片 / Click "Load Image" to load an image
   - 使用"Rotate"按钮旋转图片 / Use "Rotate" button to rotate the image
   - 使用"Flip H"和"Flip V"按钮水平/垂直翻转图片 / Use "Flip H" and "Flip V" buttons to flip horizontally/vertically
   - 使用"Grayscale"按钮转换为灰度图 / Use "Grayscale" button to convert to grayscale

3. 调整图片 / Adjust image:
   - 使用"Brightness"和"Contrast"按钮调整亮度和对比度 / Use "Brightness" and "Contrast" buttons to adjust brightness and contrast
   - 使用"Color"按钮调整RGB通道 / Use "Color" button to adjust RGB channels
   - 使用"Saturation"按钮调整饱和度 / Use "Saturation" button to adjust saturation
   - 使用"Sharpness"按钮调整锐化度 / Use "Sharpness" button to adjust sharpness

4. 应用滤镜 / Apply filters:
   - 点击"Filters"按钮打开滤镜对话框 / Click "Filters" button to open filter dialog
   - 选择需要的滤镜效果 / Select desired filter effects
   - 可以叠加多个滤镜 / Can stack multiple filters
   - 使用"Clear Filters"清除所有滤镜 / Use "Clear Filters" to remove all filters

5. 应用特效 / Apply effects:
   - 点击"Effects"按钮打开特效对话框 / Click "Effects" button to open effects dialog
   - 选择需要的特效 / Select desired effects
   - 可以预览效果 / Can preview effects
   - 使用"Reset"恢复原始图片 / Use "Reset" to restore original image

6. 模糊效果 / Blur effects:
   - 点击"Blur"按钮打开模糊对话框 / Click "Blur" button to open blur dialog
   - 选择模糊类型（高斯、盒式、中值）/ Select blur type (Gaussian, Box, Median)
   - 调整模糊强度 / Adjust blur intensity
   - 实时预览效果 / Real-time preview

7. 噪点效果 / Noise effects:
   - 点击"Noise"按钮打开噪点对话框 / Click "Noise" button to open noise dialog
   - 选择噪点类型（高斯、椒盐、斑点）/ Select noise type (Gaussian, Salt & Pepper, Speckle)
   - 调整噪点强度 / Adjust noise intensity
   - 实时预览效果 / Real-time preview

8. 其他效果 / Other effects:
   - 使用"Cartoon"按钮应用卡通效果 / Use "Cartoon" button for cartoon effect
   - 使用"Sketch"按钮应用素描效果 / Use "Sketch" button for sketch effect
   - 使用"Edge"按钮应用边缘检测 / Use "Edge" button for edge detection
   - 使用"Denoise"按钮应用降噪 / Use "Denoise" button for noise reduction
   - 使用"Vignette"按钮应用晕影效果 / Use "Vignette" button for vignette effect

9. 保存图片 / Save image:
   - 点击"Save Image"按钮 / Click "Save Image" button
   - 选择保存位置 / Choose save location
   - 输入文件名 / Enter filename
   - 点击"Save"保存 / Click "Save" to save

## 注意事项 / Notes

- 所有调整都支持实时预览 / All adjustments support real-time preview
- 可以使用"Undo"和"Redo"按钮撤销/重做操作 / Use "Undo" and "Redo" buttons to undo/redo operations
- 最多支持10步撤销/重做 / Supports up to 10 undo/redo steps
- 所有效果都可以通过"Reset"按钮恢复原始状态 / All effects can be reset to original state using "Reset" button

## 故障排除 / Troubleshooting

如果遇到问题 / If you encounter issues:

1. 确保已安装所有依赖 / Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

2. 检查 Python 版本是否兼容 / Check Python version compatibility:
```bash
python --version
```

3. 如果出现 OpenCV 相关错误，尝试重新安装 / If OpenCV errors occur, try reinstalling:
```bash
pip uninstall opencv-python
pip install opencv-python
```

4. 如果出现 Kivy 相关错误，尝试重新安装 / If Kivy errors occur, try reinstalling:
```bash
pip uninstall kivy
pip install kivy==2.2.1
```

## 许可证 / License

MIT License 
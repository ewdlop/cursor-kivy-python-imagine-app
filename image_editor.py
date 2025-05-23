from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from PIL import Image as PILImage, ImageEnhance, ImageFilter, ImageOps, ImageChops
import cv2
import numpy as np
import io
import tempfile
import os
from datetime import datetime
from collections import deque

class ImageEditor(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        
        # 创建顶部按钮区域（四行）
        self.button_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=200)
        
        # 第一行按钮 - 基本操作
        self.button_row1 = BoxLayout(size_hint_y=None, height=50)
        self.load_button = Button(text='Load Image', on_press=self.show_file_chooser)
        self.rotate_button = Button(text='Rotate', on_press=self.rotate_image)
        self.flip_h_button = Button(text='Flip H', on_press=self.flip_horizontal)
        self.flip_v_button = Button(text='Flip V', on_press=self.flip_vertical)
        self.grayscale_button = Button(text='Grayscale', on_press=self.grayscale_image)
        self.brightness_button = Button(text='Brightness', on_press=self.show_brightness_dialog)
        self.contrast_button = Button(text='Contrast', on_press=self.show_contrast_dialog)
        
        # 第二行按钮 - 滤镜和效果
        self.button_row2 = BoxLayout(size_hint_y=None, height=50)
        self.filter_button = Button(text='Filters', on_press=self.show_filter_dialog)
        self.effects_button = Button(text='Effects', on_press=self.show_effects_dialog)
        self.cartoon_button = Button(text='Cartoon', on_press=self.apply_cartoon)
        self.sketch_button = Button(text='Sketch', on_press=self.apply_sketch)
        self.edge_button = Button(text='Edge', on_press=self.apply_edge)
        self.denoise_button = Button(text='Denoise', on_press=self.apply_denoise)
        
        # 第三行按钮 - 颜色和调整
        self.button_row3 = BoxLayout(size_hint_y=None, height=50)
        self.color_button = Button(text='Color', on_press=self.show_color_dialog)
        self.saturation_button = Button(text='Saturation', on_press=self.show_saturation_dialog)
        self.sharpness_button = Button(text='Sharpness', on_press=self.show_sharpness_dialog)
        self.blur_button = Button(text='Blur', on_press=self.show_blur_dialog)
        self.noise_button = Button(text='Noise', on_press=self.show_noise_dialog)
        self.vignette_button = Button(text='Vignette', on_press=self.apply_vignette)
        
        # 第四行按钮 - 调整和保存
        self.button_row4 = BoxLayout(size_hint_y=None, height=50)
        self.crop_button = Button(text='Crop', on_press=self.show_crop_dialog)
        self.resize_button = Button(text='Resize', on_press=self.show_resize_dialog)
        self.undo_button = Button(text='Undo', on_press=self.undo)
        self.redo_button = Button(text='Redo', on_press=self.redo)
        self.save_button = Button(text='Save Image', on_press=self.show_save_dialog)
        
        # 添加按钮到第一行
        for button in [self.load_button, self.rotate_button, self.flip_h_button, 
                      self.flip_v_button, self.grayscale_button, self.brightness_button,
                      self.contrast_button]:
            self.button_row1.add_widget(button)
        
        # 添加按钮到第二行
        for button in [self.filter_button, self.effects_button, self.cartoon_button,
                      self.sketch_button, self.edge_button, self.denoise_button]:
            self.button_row2.add_widget(button)
        
        # 添加按钮到第三行
        for button in [self.color_button, self.saturation_button, self.sharpness_button,
                      self.blur_button, self.noise_button, self.vignette_button]:
            self.button_row3.add_widget(button)
        
        # 添加按钮到第四行
        for button in [self.crop_button, self.resize_button, self.undo_button,
                      self.redo_button, self.save_button]:
            self.button_row4.add_widget(button)
        
        # 将四行按钮添加到按钮布局
        self.button_layout.add_widget(self.button_row1)
        self.button_layout.add_widget(self.button_row2)
        self.button_layout.add_widget(self.button_row3)
        self.button_layout.add_widget(self.button_row4)
        
        # 创建图片显示区域
        self.image_widget = Image()
        
        # 添加组件到主布局
        self.add_widget(self.button_layout)
        self.add_widget(self.image_widget)
        
        self.current_image = None
        self.pil_image = None
        self.temp_file = None
        self.preview_temp_file = None
        self.original_image = None  # 保存原始图片用于重置
        
        # 初始化撤销/重做栈
        self.undo_stack = deque(maxlen=10)  # 最多保存10步操作
        self.redo_stack = deque(maxlen=10)
        self.update_undo_redo_buttons()

    def update_undo_redo_buttons(self):
        """更新撤销/重做按钮状态"""
        self.undo_button.disabled = len(self.undo_stack) == 0
        self.redo_button.disabled = len(self.redo_stack) == 0

    def save_state(self):
        """保存当前状态到撤销栈"""
        if self.pil_image:
            self.undo_stack.append(self.pil_image.copy())
            self.redo_stack.clear()  # 清空重做栈
            self.update_undo_redo_buttons()

    def undo(self, instance):
        """撤销上一步操作"""
        if self.undo_stack:
            if self.pil_image:
                self.redo_stack.append(self.pil_image.copy())
            self.pil_image = self.undo_stack.pop()
            self.update_image_display()
            self.update_undo_redo_buttons()

    def redo(self, instance):
        """重做上一步操作"""
        if self.redo_stack:
            if self.pil_image:
                self.undo_stack.append(self.pil_image.copy())
            self.pil_image = self.redo_stack.pop()
            self.update_image_display()
            self.update_undo_redo_buttons()

    def flip_horizontal(self, instance):
        """水平翻转图像"""
        if self.pil_image:
            self.save_state()
            self.pil_image = self.pil_image.transpose(PILImage.FLIP_LEFT_RIGHT)
            self.update_image_display()

    def flip_vertical(self, instance):
        """垂直翻转图像"""
        if self.pil_image:
            self.save_state()
            self.pil_image = self.pil_image.transpose(PILImage.FLIP_TOP_BOTTOM)
            self.update_image_display()

    def show_filter_dialog(self, instance):
        """显示滤镜对话框"""
        if not self.pil_image:
            return
            
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 预览区域
        preview = Image(source=self.temp_file)
        content.add_widget(preview)
        
        # 滤镜按钮区域
        filters_layout = BoxLayout(size_hint_y=None, height=50)
        blur_button = Button(text='Blur')
        sharpen_button = Button(text='Sharpen')
        edge_button = Button(text='Edge')
        emboss_button = Button(text='Emboss')
        
        filters_layout.add_widget(blur_button)
        filters_layout.add_widget(sharpen_button)
        filters_layout.add_widget(edge_button)
        filters_layout.add_widget(emboss_button)
        content.add_widget(filters_layout)
        
        # 已应用滤镜列表
        applied_filters_label = Label(text='Applied Filters: None', size_hint_y=None, height=30)
        content.add_widget(applied_filters_label)
        
        # 按钮区域
        buttons = BoxLayout(size_hint_y=None, height=50)
        cancel_button = Button(text='Cancel')
        apply_button = Button(text='Apply')
        reset_button = Button(text='Reset')
        clear_filters_button = Button(text='Clear Filters')
        
        buttons.add_widget(cancel_button)
        buttons.add_widget(clear_filters_button)
        buttons.add_widget(reset_button)
        buttons.add_widget(apply_button)
        content.add_widget(buttons)
        
        popup = Popup(title='Apply Filter', content=content, size_hint=(0.8, 0.8))
        
        # 保存当前滤镜状态
        applied_filters = []
        filtered_image = None
        
        def update_filter_label():
            """更新已应用滤镜的标签"""
            if applied_filters:
                applied_filters_label.text = 'Applied Filters: ' + ', '.join(applied_filters)
            else:
                applied_filters_label.text = 'Applied Filters: None'
        
        def apply_filter(filter_type):
            nonlocal filtered_image
            if not self.original_image:
                self.original_image = self.pil_image.copy()
            
            # 确保图像是RGB模式
            temp_img = self.ensure_rgb_mode(self.original_image.copy())
            
            try:
                # 应用所有已保存的滤镜
                for f in applied_filters:
                    if f == 'blur':
                        temp_img = temp_img.filter(ImageFilter.BLUR)
                    elif f == 'sharpen':
                        temp_img = temp_img.filter(ImageFilter.SHARPEN)
                    elif f == 'edge':
                        temp_img = temp_img.filter(ImageFilter.FIND_EDGES)
                    elif f == 'emboss':
                        temp_img = temp_img.filter(ImageFilter.EMBOSS)
                
                # 应用新滤镜
                if filter_type == 'blur':
                    temp_img = temp_img.filter(ImageFilter.BLUR)
                elif filter_type == 'sharpen':
                    temp_img = temp_img.filter(ImageFilter.SHARPEN)
                elif filter_type == 'edge':
                    temp_img = temp_img.filter(ImageFilter.FIND_EDGES)
                elif filter_type == 'emboss':
                    temp_img = temp_img.filter(ImageFilter.EMBOSS)
                
                # 保存新滤镜
                applied_filters.append(filter_type)
                filtered_image = temp_img
                
                # 更新预览
                fd, temp_path = tempfile.mkstemp(suffix='.png')
                os.close(fd)
                filtered_image.save(temp_path, format='PNG')
                preview.source = temp_path
                preview.reload()
                os.unlink(temp_path)
                
                # 更新滤镜标签
                update_filter_label()
                
            except Exception as e:
                print(f"Error applying filter: {e}")
        
        def clear_filters(instance):
            nonlocal filtered_image, applied_filters
            applied_filters.clear()
            filtered_image = None
            update_filter_label()
            # 重置预览
            preview.source = self.temp_file
            preview.reload()
        
        def apply_changes(instance):
            nonlocal filtered_image
            if filtered_image:
                self.save_state()
                self.pil_image = filtered_image
                self.update_image_display()
            popup.dismiss()
        
        def reset_changes(instance):
            if self.original_image:
                self.pil_image = self.original_image.copy()
                self.update_image_display()
                # 重置预览
                preview.source = self.temp_file
                preview.reload()
        
        # 绑定滤镜按钮事件
        blur_button.bind(on_press=lambda x: apply_filter('blur'))
        sharpen_button.bind(on_press=lambda x: apply_filter('sharpen'))
        edge_button.bind(on_press=lambda x: apply_filter('edge'))
        emboss_button.bind(on_press=lambda x: apply_filter('emboss'))
        
        apply_button.bind(on_press=apply_changes)
        reset_button.bind(on_press=reset_changes)
        clear_filters_button.bind(on_press=clear_filters)
        cancel_button.bind(on_press=popup.dismiss)
        popup.open()

    def ensure_rgb_mode(self, image):
        """确保图片是RGB模式"""
        if image.mode not in ('RGB', 'RGBA'):
            return image.convert('RGB')
        return image

    def show_file_chooser(self, instance):
        content = BoxLayout(orientation='vertical')
        
        # 创建水平布局来放置文件选择器和预览
        main_layout = BoxLayout(orientation='horizontal', spacing=10)
        
        # 文件选择器
        file_chooser = FileChooserListView(path='.')
        file_chooser.bind(selection=self.on_file_selected)
        
        # 预览区域
        preview_layout = BoxLayout(orientation='vertical', size_hint_x=0.4)
        preview_label = Button(text='Preview', size_hint_y=None, height=30)
        self.preview_image = Image()
        preview_layout.add_widget(preview_label)
        preview_layout.add_widget(self.preview_image)
        
        main_layout.add_widget(file_chooser)
        main_layout.add_widget(preview_layout)
        content.add_widget(main_layout)
        
        # 按钮区域
        buttons = BoxLayout(size_hint_y=None, height=50)
        cancel_button = Button(text='Cancel')
        select_button = Button(text='Select')
        
        buttons.add_widget(cancel_button)
        buttons.add_widget(select_button)
        content.add_widget(buttons)
        
        popup = Popup(title='Select Image', content=content, size_hint=(0.9, 0.9))
        
        def select_file(instance):
            if file_chooser.selection:
                self.load_image(file_chooser.selection[0])
                popup.dismiss()
        
        select_button.bind(on_press=select_file)
        cancel_button.bind(on_press=popup.dismiss)
        popup.open()

    def show_save_dialog(self, instance):
        if not self.pil_image:
            return
            
        content = BoxLayout(orientation='vertical')
        
        # 创建水平布局来放置文件选择器和预览
        main_layout = BoxLayout(orientation='horizontal', spacing=10)
        
        # 文件选择器
        file_chooser = FileChooserListView(path='.')
        file_chooser.path = os.path.expanduser('~')  # 默认打开用户主目录
        
        # 预览区域
        preview_layout = BoxLayout(orientation='vertical', size_hint_x=0.4)
        preview_label = Button(text='Preview', size_hint_y=None, height=30)
        save_preview = Image()
        preview_layout.add_widget(preview_label)
        preview_layout.add_widget(save_preview)
        
        # 显示当前编辑后的图片预览
        if self.temp_file:
            save_preview.source = self.temp_file
            save_preview.reload()
        
        main_layout.add_widget(file_chooser)
        main_layout.add_widget(preview_layout)
        content.add_widget(main_layout)
        
        # 文件名输入区域
        filename_layout = BoxLayout(size_hint_y=None, height=50)
        filename_label = Button(text='Filename:', size_hint_x=0.3)
        filename_input = Button(text=f'edited_image_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png', 
                              size_hint_x=0.7)
        filename_layout.add_widget(filename_label)
        filename_layout.add_widget(filename_input)
        content.add_widget(filename_layout)
        
        # 按钮区域
        buttons = BoxLayout(size_hint_y=None, height=50)
        cancel_button = Button(text='Cancel')
        save_button = Button(text='Save')
        
        buttons.add_widget(cancel_button)
        buttons.add_widget(save_button)
        content.add_widget(buttons)
        
        popup = Popup(title='Save Image', content=content, size_hint=(0.9, 0.9))
        
        def save_file(instance):
            save_path = os.path.join(file_chooser.path, filename_input.text)
            try:
                self.pil_image.save(save_path)
                popup.dismiss()
            except Exception as e:
                print(f"Error saving image: {e}")
        
        save_button.bind(on_press=save_file)
        cancel_button.bind(on_press=popup.dismiss)
        popup.open()

    def on_file_selected(self, instance, value):
        if value:
            try:
                # 清理旧的预览文件
                if self.preview_temp_file and os.path.exists(self.preview_temp_file):
                    os.unlink(self.preview_temp_file)
                
                # 创建新的预览
                preview_img = PILImage.open(value[0])
                # 调整预览图片大小
                max_size = (200, 200)
                preview_img.thumbnail(max_size, PILImage.Resampling.LANCZOS)
                
                # 保存预览图片
                fd, self.preview_temp_file = tempfile.mkstemp(suffix='.png')
                os.close(fd)
                preview_img.save(self.preview_temp_file, format='PNG')
                
                # 显示预览
                self.preview_image.source = self.preview_temp_file
                self.preview_image.reload()
            except Exception as e:
                print(f"Error creating preview: {e}")

    def load_image(self, filename):
        try:
            self.pil_image = PILImage.open(filename)
            self.current_image = filename
            self.update_image_display()
        except Exception as e:
            print(f"Error loading image: {e}")

    def update_image_display(self):
        if self.pil_image:
            # 将PIL图像转换为临时文件
            if self.temp_file:
                try:
                    os.unlink(self.temp_file)
                except:
                    pass
            
            # 创建临时文件
            fd, self.temp_file = tempfile.mkstemp(suffix='.png')
            os.close(fd)
            
            # 保存图像到临时文件
            self.pil_image.save(self.temp_file, format='PNG')
            
            # 更新图像显示
            self.image_widget.source = self.temp_file
            self.image_widget.reload()

    def rotate_image(self, instance):
        if self.pil_image:
            self.save_state()
            self.pil_image = self.pil_image.rotate(90, expand=True)
            self.update_image_display()

    def grayscale_image(self, instance):
        if self.pil_image:
            self.save_state()
            self.pil_image = self.pil_image.convert('L')
            self.update_image_display()

    def show_brightness_dialog(self, instance):
        if not self.pil_image:
            return
            
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 预览区域
        preview = Image(source=self.temp_file)
        content.add_widget(preview)
        
        # 亮度滑块
        slider_layout = BoxLayout(size_hint_y=None, height=50)
        slider_label = Label(text='Brightness:', size_hint_x=0.3)
        brightness_slider = Slider(min=0.0, max=2.0, value=1.0, size_hint_x=0.7)
        slider_layout.add_widget(slider_label)
        slider_layout.add_widget(brightness_slider)
        content.add_widget(slider_layout)
        
        # 按钮区域
        buttons = BoxLayout(size_hint_y=None, height=50)
        cancel_button = Button(text='Cancel')
        apply_button = Button(text='Apply')
        reset_button = Button(text='Reset')
        
        buttons.add_widget(cancel_button)
        buttons.add_widget(reset_button)
        buttons.add_widget(apply_button)
        content.add_widget(buttons)
        
        popup = Popup(title='Adjust Brightness', content=content, size_hint=(0.8, 0.8))
        
        def update_preview(instance, value):
            if not self.original_image:
                self.original_image = self.pil_image.copy()
            # 确保图片是RGB模式
            rgb_image = self.ensure_rgb_mode(self.original_image)
            enhancer = ImageEnhance.Brightness(rgb_image)
            temp_img = enhancer.enhance(value)
            
            # 更新预览
            fd, temp_path = tempfile.mkstemp(suffix='.png')
            os.close(fd)
            temp_img.save(temp_path, format='PNG')
            preview.source = temp_path
            preview.reload()
            os.unlink(temp_path)
        
        def apply_changes(instance):
            if not self.original_image:
                self.original_image = self.pil_image.copy()
            # 确保图片是RGB模式
            rgb_image = self.ensure_rgb_mode(self.original_image)
            enhancer = ImageEnhance.Brightness(rgb_image)
            self.pil_image = enhancer.enhance(brightness_slider.value)
            self.update_image_display()
            popup.dismiss()
        
        def reset_changes(instance):
            if self.original_image:
                self.pil_image = self.original_image.copy()
                brightness_slider.value = 1.0
                self.update_image_display()
        
        brightness_slider.bind(value=update_preview)
        apply_button.bind(on_press=apply_changes)
        reset_button.bind(on_press=reset_changes)
        cancel_button.bind(on_press=popup.dismiss)
        popup.open()

    def show_contrast_dialog(self, instance):
        if not self.pil_image:
            return
            
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 预览区域
        preview = Image(source=self.temp_file)
        content.add_widget(preview)
        
        # 对比度滑块
        slider_layout = BoxLayout(size_hint_y=None, height=50)
        slider_label = Label(text='Contrast:', size_hint_x=0.3)
        contrast_slider = Slider(min=0.0, max=2.0, value=1.0, size_hint_x=0.7)
        slider_layout.add_widget(slider_label)
        slider_layout.add_widget(contrast_slider)
        content.add_widget(slider_layout)
        
        # 按钮区域
        buttons = BoxLayout(size_hint_y=None, height=50)
        cancel_button = Button(text='Cancel')
        apply_button = Button(text='Apply')
        reset_button = Button(text='Reset')
        
        buttons.add_widget(cancel_button)
        buttons.add_widget(reset_button)
        buttons.add_widget(apply_button)
        content.add_widget(buttons)
        
        popup = Popup(title='Adjust Contrast', content=content, size_hint=(0.8, 0.8))
        
        def update_preview(instance, value):
            if not self.original_image:
                self.original_image = self.pil_image.copy()
            # 确保图片是RGB模式
            rgb_image = self.ensure_rgb_mode(self.original_image)
            enhancer = ImageEnhance.Contrast(rgb_image)
            temp_img = enhancer.enhance(value)
            
            # 更新预览
            fd, temp_path = tempfile.mkstemp(suffix='.png')
            os.close(fd)
            temp_img.save(temp_path, format='PNG')
            preview.source = temp_path
            preview.reload()
            os.unlink(temp_path)
        
        def apply_changes(instance):
            if not self.original_image:
                self.original_image = self.pil_image.copy()
            # 确保图片是RGB模式
            rgb_image = self.ensure_rgb_mode(self.original_image)
            enhancer = ImageEnhance.Contrast(rgb_image)
            self.pil_image = enhancer.enhance(contrast_slider.value)
            self.update_image_display()
            popup.dismiss()
        
        def reset_changes(instance):
            if self.original_image:
                self.pil_image = self.original_image.copy()
                contrast_slider.value = 1.0
                self.update_image_display()
        
        contrast_slider.bind(value=update_preview)
        apply_button.bind(on_press=apply_changes)
        reset_button.bind(on_press=reset_changes)
        cancel_button.bind(on_press=popup.dismiss)
        popup.open()

    def show_crop_dialog(self, instance):
        if not self.pil_image:
            return
            
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 预览区域
        preview = Image(source=self.temp_file)
        content.add_widget(preview)
        
        # 裁剪尺寸输入区域
        crop_layout = BoxLayout(size_hint_y=None, height=50)
        
        # 起始点
        start_layout = BoxLayout(size_hint_x=0.5)
        start_x_label = Label(text='Start X:', size_hint_x=0.3)
        start_x_input = TextInput(text='0', multiline=False, size_hint_x=0.7)
        start_y_label = Label(text='Start Y:', size_hint_x=0.3)
        start_y_input = TextInput(text='0', multiline=False, size_hint_x=0.7)
        start_layout.add_widget(start_x_label)
        start_layout.add_widget(start_x_input)
        start_layout.add_widget(start_y_label)
        start_layout.add_widget(start_y_input)
        
        # 结束点
        end_layout = BoxLayout(size_hint_x=0.5)
        end_x_label = Label(text='End X:', size_hint_x=0.3)
        end_x_input = TextInput(text=str(self.pil_image.width), multiline=False, size_hint_x=0.7)
        end_y_label = Label(text='End Y:', size_hint_x=0.3)
        end_y_input = TextInput(text=str(self.pil_image.height), multiline=False, size_hint_x=0.7)
        end_layout.add_widget(end_x_label)
        end_layout.add_widget(end_x_input)
        end_layout.add_widget(end_y_label)
        end_layout.add_widget(end_y_input)
        
        crop_layout.add_widget(start_layout)
        crop_layout.add_widget(end_layout)
        content.add_widget(crop_layout)
        
        # 按钮区域
        buttons = BoxLayout(size_hint_y=None, height=50)
        cancel_button = Button(text='Cancel')
        apply_button = Button(text='Apply')
        
        buttons.add_widget(cancel_button)
        buttons.add_widget(apply_button)
        content.add_widget(buttons)
        
        popup = Popup(title='Crop Image', content=content, size_hint=(0.8, 0.8))
        
        def apply_crop(instance):
            try:
                start_x = int(start_x_input.text)
                start_y = int(start_y_input.text)
                end_x = int(end_x_input.text)
                end_y = int(end_y_input.text)
                
                # 确保坐标在有效范围内
                start_x = max(0, min(start_x, self.pil_image.width))
                start_y = max(0, min(start_y, self.pil_image.height))
                end_x = max(0, min(end_x, self.pil_image.width))
                end_y = max(0, min(end_y, self.pil_image.height))
                
                # 确保结束坐标大于开始坐标
                if end_x <= start_x or end_y <= start_y:
                    print("Invalid crop coordinates")
                    return
                
                self.pil_image = self.pil_image.crop((start_x, start_y, end_x, end_y))
                self.update_image_display()
                popup.dismiss()
            except ValueError:
                print("Invalid coordinates")
        
        apply_button.bind(on_press=apply_crop)
        cancel_button.bind(on_press=popup.dismiss)
        popup.open()

    def show_resize_dialog(self, instance):
        if not self.pil_image:
            return
            
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 预览区域
        preview = Image(source=self.temp_file)
        content.add_widget(preview)
        
        # 尺寸输入区域
        size_layout = BoxLayout(size_hint_y=None, height=50)
        width_label = Label(text='Width:', size_hint_x=0.2)
        width_input = TextInput(text=str(self.pil_image.width), multiline=False, size_hint_x=0.3)
        height_label = Label(text='Height:', size_hint_x=0.2)
        height_input = TextInput(text=str(self.pil_image.height), multiline=False, size_hint_x=0.3)
        
        size_layout.add_widget(width_label)
        size_layout.add_widget(width_input)
        size_layout.add_widget(height_label)
        size_layout.add_widget(height_input)
        content.add_widget(size_layout)
        
        # 保持比例选项
        ratio_layout = BoxLayout(size_hint_y=None, height=50)
        ratio_label = Label(text='Maintain aspect ratio:', size_hint_x=0.6)
        ratio_button = Button(text='Yes', size_hint_x=0.4)
        ratio_layout.add_widget(ratio_label)
        ratio_layout.add_widget(ratio_button)
        content.add_widget(ratio_layout)
        
        # 按钮区域
        buttons = BoxLayout(size_hint_y=None, height=50)
        cancel_button = Button(text='Cancel')
        apply_button = Button(text='Apply')
        
        buttons.add_widget(cancel_button)
        buttons.add_widget(apply_button)
        content.add_widget(buttons)
        
        popup = Popup(title='Resize Image', content=content, size_hint=(0.8, 0.8))
        
        def update_height(instance, value):
            if ratio_button.text == 'Yes':
                try:
                    width = int(value)
                    ratio = self.pil_image.width / self.pil_image.height
                    height = int(width / ratio)
                    height_input.text = str(height)
                except ValueError:
                    pass
        
        def update_width(instance, value):
            if ratio_button.text == 'Yes':
                try:
                    height = int(value)
                    ratio = self.pil_image.width / self.pil_image.height
                    width = int(height * ratio)
                    width_input.text = str(width)
                except ValueError:
                    pass
        
        def apply_resize(instance):
            try:
                width = int(width_input.text)
                height = int(height_input.text)
                if width <= 0 or height <= 0:
                    print("Invalid dimensions")
                    return
                
                self.pil_image = self.pil_image.resize((width, height), PILImage.Resampling.LANCZOS)
                self.update_image_display()
                popup.dismiss()
            except ValueError:
                print("Invalid dimensions")
        
        def toggle_ratio(instance):
            ratio_button.text = 'No' if ratio_button.text == 'Yes' else 'Yes'
        
        width_input.bind(text=update_height)
        height_input.bind(text=update_width)
        ratio_button.bind(on_press=toggle_ratio)
        apply_button.bind(on_press=apply_resize)
        cancel_button.bind(on_press=popup.dismiss)
        popup.open()

    def apply_cartoon(self, instance):
        """应用卡通效果"""
        if not self.pil_image:
            return
            
        self.save_state()
        # 转换为OpenCV格式
        img = self.pil_to_cv2(self.pil_image)
        
        # 应用卡通效果
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                    cv2.THRESH_BINARY, 9, 9)
        color = cv2.bilateralFilter(img, 9, 300, 300)
        cartoon = cv2.bitwise_and(color, color, mask=edges)
        
        # 转回PIL格式
        self.pil_image = self.cv2_to_pil(cartoon)
        self.update_image_display()

    def apply_sketch(self, instance):
        """应用素描效果"""
        if not self.pil_image:
            return
            
        self.save_state()
        # 转换为OpenCV格式
        img = self.pil_to_cv2(self.pil_image)
        
        # 应用素描效果
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        inv = 255 - gray
        blur = cv2.GaussianBlur(inv, (21, 21), 0)
        sketch = cv2.divide(gray, 255 - blur, scale=256)
        
        # 转回PIL格式
        self.pil_image = self.cv2_to_pil(cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR))
        self.update_image_display()

    def apply_edge(self, instance):
        """应用边缘检测"""
        if not self.pil_image:
            return
            
        self.save_state()
        # 转换为OpenCV格式
        img = self.pil_to_cv2(self.pil_image)
        
        # 应用边缘检测
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        
        # 转回PIL格式
        self.pil_image = self.cv2_to_pil(cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR))
        self.update_image_display()

    def apply_denoise(self, instance):
        """应用降噪"""
        if not self.pil_image:
            return
            
        self.save_state()
        # 转换为OpenCV格式
        img = self.pil_to_cv2(self.pil_image)
        
        # 应用降噪
        denoised = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
        
        # 转回PIL格式
        self.pil_image = self.cv2_to_pil(denoised)
        self.update_image_display()

    def show_effects_dialog(self, instance):
        """显示特效对话框"""
        if not self.pil_image:
            return
            
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 预览区域
        preview = Image(source=self.temp_file)
        content.add_widget(preview)
        
        # 特效按钮区域
        effects_layout = BoxLayout(size_hint_y=None, height=50)
        sepia_button = Button(text='Sepia')
        invert_button = Button(text='Invert')
        emboss_button = Button(text='Emboss')
        contour_button = Button(text='Contour')
        
        effects_layout.add_widget(sepia_button)
        effects_layout.add_widget(invert_button)
        effects_layout.add_widget(emboss_button)
        effects_layout.add_widget(contour_button)
        content.add_widget(effects_layout)
        
        # 按钮区域
        buttons = BoxLayout(size_hint_y=None, height=50)
        cancel_button = Button(text='Cancel')
        apply_button = Button(text='Apply')
        reset_button = Button(text='Reset')
        
        buttons.add_widget(cancel_button)
        buttons.add_widget(reset_button)
        buttons.add_widget(apply_button)
        content.add_widget(buttons)
        
        popup = Popup(title='Apply Effects', content=content, size_hint=(0.8, 0.8))
        
        # 保存当前效果状态
        current_effect = None
        current_effect_image = None
        
        def apply_effect(effect_type):
            nonlocal current_effect, current_effect_image
            if not self.original_image:
                self.original_image = self.pil_image.copy()
            
            temp_img = self.original_image.copy()
            
            try:
                if effect_type == 'sepia':
                    # 应用棕褐色效果
                    temp_img = ImageOps.colorize(temp_img.convert('L'), '#704214', '#C0A080')
                elif effect_type == 'invert':
                    # 应用反色效果
                    temp_img = ImageOps.invert(temp_img)
                elif effect_type == 'emboss':
                    # 应用浮雕效果
                    temp_img = temp_img.filter(ImageFilter.EMBOSS)
                elif effect_type == 'contour':
                    # 应用轮廓效果
                    temp_img = temp_img.filter(ImageFilter.CONTOUR)
                
                # 保存当前效果
                current_effect = effect_type
                current_effect_image = temp_img
                
                # 更新预览
                fd, temp_path = tempfile.mkstemp(suffix='.png')
                os.close(fd)
                temp_img.save(temp_path, format='PNG')
                preview.source = temp_path
                preview.reload()
                os.unlink(temp_path)
                
            except Exception as e:
                print(f"Error applying effect: {e}")
        
        def apply_changes(instance):
            nonlocal current_effect_image
            if current_effect_image:
                self.save_state()
                self.pil_image = current_effect_image
                self.update_image_display()
            popup.dismiss()
        
        def reset_changes(instance):
            if self.original_image:
                self.pil_image = self.original_image.copy()
                self.update_image_display()
                # 重置预览
                preview.source = self.temp_file
                preview.reload()
        
        # 绑定特效按钮事件
        sepia_button.bind(on_press=lambda x: apply_effect('sepia'))
        invert_button.bind(on_press=lambda x: apply_effect('invert'))
        emboss_button.bind(on_press=lambda x: apply_effect('emboss'))
        contour_button.bind(on_press=lambda x: apply_effect('contour'))
        
        apply_button.bind(on_press=apply_changes)
        reset_button.bind(on_press=reset_changes)
        cancel_button.bind(on_press=popup.dismiss)
        popup.open()

    def pil_to_cv2(self, pil_image):
        """将PIL图像转换为OpenCV格式"""
        return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    def cv2_to_pil(self, cv2_image):
        """将OpenCV图像转换为PIL格式"""
        return PILImage.fromarray(cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB))

    def show_color_dialog(self, instance):
        """显示颜色调整对话框"""
        if not self.pil_image:
            return
            
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 预览区域
        preview = Image(source=self.temp_file)
        content.add_widget(preview)
        
        # 颜色调整滑块
        sliders_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=150)
        
        # 红色通道
        red_layout = BoxLayout(size_hint_y=None, height=50)
        red_label = Label(text='Red:', size_hint_x=0.3)
        red_slider = Slider(min=0.0, max=2.0, value=1.0, size_hint_x=0.7)
        red_layout.add_widget(red_label)
        red_layout.add_widget(red_slider)
        
        # 绿色通道
        green_layout = BoxLayout(size_hint_y=None, height=50)
        green_label = Label(text='Green:', size_hint_x=0.3)
        green_slider = Slider(min=0.0, max=2.0, value=1.0, size_hint_x=0.7)
        green_layout.add_widget(green_label)
        green_layout.add_widget(green_slider)
        
        # 蓝色通道
        blue_layout = BoxLayout(size_hint_y=None, height=50)
        blue_label = Label(text='Blue:', size_hint_x=0.3)
        blue_slider = Slider(min=0.0, max=2.0, value=1.0, size_hint_x=0.7)
        blue_layout.add_widget(blue_label)
        blue_layout.add_widget(blue_slider)
        
        sliders_layout.add_widget(red_layout)
        sliders_layout.add_widget(green_layout)
        sliders_layout.add_widget(blue_layout)
        content.add_widget(sliders_layout)
        
        # 按钮区域
        buttons = BoxLayout(size_hint_y=None, height=50)
        cancel_button = Button(text='Cancel')
        apply_button = Button(text='Apply')
        reset_button = Button(text='Reset')
        
        buttons.add_widget(cancel_button)
        buttons.add_widget(reset_button)
        buttons.add_widget(apply_button)
        content.add_widget(buttons)
        
        popup = Popup(title='Adjust Colors', content=content, size_hint=(0.8, 0.8))
        
        def update_preview(instance, value):
            if not self.original_image:
                self.original_image = self.pil_image.copy()
            
            # 确保图片是RGB模式
            rgb_image = self.ensure_rgb_mode(self.original_image)
            
            # 分离通道
            r, g, b = rgb_image.split()
            
            # 调整各个通道
            r = ImageEnhance.Brightness(r).enhance(red_slider.value)
            g = ImageEnhance.Brightness(g).enhance(green_slider.value)
            b = ImageEnhance.Brightness(b).enhance(blue_slider.value)
            
            # 合并通道
            temp_img = PILImage.merge('RGB', (r, g, b))
            
            # 更新预览
            fd, temp_path = tempfile.mkstemp(suffix='.png')
            os.close(fd)
            temp_img.save(temp_path, format='PNG')
            preview.source = temp_path
            preview.reload()
            os.unlink(temp_path)
        
        def apply_changes(instance):
            if not self.original_image:
                self.original_image = self.pil_image.copy()
            
            # 确保图片是RGB模式
            rgb_image = self.ensure_rgb_mode(self.original_image)
            
            # 分离通道
            r, g, b = rgb_image.split()
            
            # 调整各个通道
            r = ImageEnhance.Brightness(r).enhance(red_slider.value)
            g = ImageEnhance.Brightness(g).enhance(green_slider.value)
            b = ImageEnhance.Brightness(b).enhance(blue_slider.value)
            
            # 合并通道
            self.pil_image = PILImage.merge('RGB', (r, g, b))
            self.update_image_display()
            popup.dismiss()
        
        def reset_changes(instance):
            if self.original_image:
                self.pil_image = self.original_image.copy()
                red_slider.value = 1.0
                green_slider.value = 1.0
                blue_slider.value = 1.0
                self.update_image_display()
        
        red_slider.bind(value=update_preview)
        green_slider.bind(value=update_preview)
        blue_slider.bind(value=update_preview)
        apply_button.bind(on_press=apply_changes)
        reset_button.bind(on_press=reset_changes)
        cancel_button.bind(on_press=popup.dismiss)
        popup.open()

    def show_saturation_dialog(self, instance):
        """显示饱和度调整对话框"""
        if not self.pil_image:
            return
            
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 预览区域
        preview = Image(source=self.temp_file)
        content.add_widget(preview)
        
        # 饱和度滑块
        slider_layout = BoxLayout(size_hint_y=None, height=50)
        slider_label = Label(text='Saturation:', size_hint_x=0.3)
        saturation_slider = Slider(min=0.0, max=2.0, value=1.0, size_hint_x=0.7)
        slider_layout.add_widget(slider_label)
        slider_layout.add_widget(saturation_slider)
        content.add_widget(slider_layout)
        
        # 按钮区域
        buttons = BoxLayout(size_hint_y=None, height=50)
        cancel_button = Button(text='Cancel')
        apply_button = Button(text='Apply')
        reset_button = Button(text='Reset')
        
        buttons.add_widget(cancel_button)
        buttons.add_widget(reset_button)
        buttons.add_widget(apply_button)
        content.add_widget(buttons)
        
        popup = Popup(title='Adjust Saturation', content=content, size_hint=(0.8, 0.8))
        
        def update_preview(instance, value):
            if not self.original_image:
                self.original_image = self.pil_image.copy()
            
            # 确保图片是RGB模式
            rgb_image = self.ensure_rgb_mode(self.original_image)
            enhancer = ImageEnhance.Color(rgb_image)
            temp_img = enhancer.enhance(value)
            
            # 更新预览
            fd, temp_path = tempfile.mkstemp(suffix='.png')
            os.close(fd)
            temp_img.save(temp_path, format='PNG')
            preview.source = temp_path
            preview.reload()
            os.unlink(temp_path)
        
        def apply_changes(instance):
            if not self.original_image:
                self.original_image = self.pil_image.copy()
            
            # 确保图片是RGB模式
            rgb_image = self.ensure_rgb_mode(self.original_image)
            enhancer = ImageEnhance.Color(rgb_image)
            self.pil_image = enhancer.enhance(saturation_slider.value)
            self.update_image_display()
            popup.dismiss()
        
        def reset_changes(instance):
            if self.original_image:
                self.pil_image = self.original_image.copy()
                saturation_slider.value = 1.0
                self.update_image_display()
        
        saturation_slider.bind(value=update_preview)
        apply_button.bind(on_press=apply_changes)
        reset_button.bind(on_press=reset_changes)
        cancel_button.bind(on_press=popup.dismiss)
        popup.open()

    def show_sharpness_dialog(self, instance):
        """显示锐化调整对话框"""
        if not self.pil_image:
            return
            
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 预览区域
        preview = Image(source=self.temp_file)
        content.add_widget(preview)
        
        # 锐化滑块
        slider_layout = BoxLayout(size_hint_y=None, height=50)
        slider_label = Label(text='Sharpness:', size_hint_x=0.3)
        sharpness_slider = Slider(min=0.0, max=2.0, value=1.0, size_hint_x=0.7)
        slider_layout.add_widget(slider_label)
        slider_layout.add_widget(sharpness_slider)
        content.add_widget(slider_layout)
        
        # 按钮区域
        buttons = BoxLayout(size_hint_y=None, height=50)
        cancel_button = Button(text='Cancel')
        apply_button = Button(text='Apply')
        reset_button = Button(text='Reset')
        
        buttons.add_widget(cancel_button)
        buttons.add_widget(reset_button)
        buttons.add_widget(apply_button)
        content.add_widget(buttons)
        
        popup = Popup(title='Adjust Sharpness', content=content, size_hint=(0.8, 0.8))
        
        def update_preview(instance, value):
            if not self.original_image:
                self.original_image = self.pil_image.copy()
            
            # 确保图片是RGB模式
            rgb_image = self.ensure_rgb_mode(self.original_image)
            enhancer = ImageEnhance.Sharpness(rgb_image)
            temp_img = enhancer.enhance(value)
            
            # 更新预览
            fd, temp_path = tempfile.mkstemp(suffix='.png')
            os.close(fd)
            temp_img.save(temp_path, format='PNG')
            preview.source = temp_path
            preview.reload()
            os.unlink(temp_path)
        
        def apply_changes(instance):
            if not self.original_image:
                self.original_image = self.pil_image.copy()
            
            # 确保图片是RGB模式
            rgb_image = self.ensure_rgb_mode(self.original_image)
            enhancer = ImageEnhance.Sharpness(rgb_image)
            self.pil_image = enhancer.enhance(sharpness_slider.value)
            self.update_image_display()
            popup.dismiss()
        
        def reset_changes(instance):
            if self.original_image:
                self.pil_image = self.original_image.copy()
                sharpness_slider.value = 1.0
                self.update_image_display()
        
        sharpness_slider.bind(value=update_preview)
        apply_button.bind(on_press=apply_changes)
        reset_button.bind(on_press=reset_changes)
        cancel_button.bind(on_press=popup.dismiss)
        popup.open()

    def show_blur_dialog(self, instance):
        """显示模糊调整对话框"""
        if not self.pil_image:
            return
            
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 预览区域
        preview = Image(source=self.temp_file)
        content.add_widget(preview)
        
        # 模糊类型选择
        blur_type_layout = BoxLayout(size_hint_y=None, height=50)
        blur_type_label = Label(text='Blur Type:', size_hint_x=0.3)
        blur_type_spinner = Spinner(
            text='Gaussian',
            values=('Gaussian', 'Box', 'Median'),
            size_hint_x=0.7
        )
        blur_type_layout.add_widget(blur_type_label)
        blur_type_layout.add_widget(blur_type_spinner)
        content.add_widget(blur_type_layout)
        
        # 模糊强度滑块
        slider_layout = BoxLayout(size_hint_y=None, height=50)
        slider_label = Label(text='Intensity:', size_hint_x=0.3)
        blur_slider = Slider(min=1, max=20, value=1, size_hint_x=0.7)
        slider_layout.add_widget(slider_label)
        slider_layout.add_widget(blur_slider)
        content.add_widget(slider_layout)
        
        # 按钮区域
        buttons = BoxLayout(size_hint_y=None, height=50)
        cancel_button = Button(text='Cancel')
        apply_button = Button(text='Apply')
        reset_button = Button(text='Reset')
        
        buttons.add_widget(cancel_button)
        buttons.add_widget(reset_button)
        buttons.add_widget(apply_button)
        content.add_widget(buttons)
        
        popup = Popup(title='Apply Blur', content=content, size_hint=(0.8, 0.8))
        
        def update_preview(instance, value):
            if not self.original_image:
                self.original_image = self.pil_image.copy()
            
            # 转换为OpenCV格式
            img = self.pil_to_cv2(self.original_image)
            
            try:
                # 应用模糊
                if blur_type_spinner.text == 'Gaussian':
                    blurred = cv2.GaussianBlur(img, (0, 0), blur_slider.value)
                elif blur_type_spinner.text == 'Box':
                    ksize = int(blur_slider.value * 2 + 1)
                    blurred = cv2.boxFilter(img, -1, (ksize, ksize))
                else:  # Median
                    ksize = int(blur_slider.value * 2 + 1)
                    # 确保ksize是奇数
                    ksize = max(3, ksize if ksize % 2 == 1 else ksize + 1)
                    blurred = cv2.medianBlur(img, ksize)
                
                # 转回PIL格式
                temp_img = self.cv2_to_pil(blurred)
                
                # 更新预览
                fd, temp_path = tempfile.mkstemp(suffix='.png')
                os.close(fd)
                temp_img.save(temp_path, format='PNG')
                preview.source = temp_path
                preview.reload()
                os.unlink(temp_path)
            except Exception as e:
                print(f"Error applying blur: {e}")
        
        def apply_changes(instance):
            if not self.original_image:
                self.original_image = self.pil_image.copy()
            
            # 转换为OpenCV格式
            img = self.pil_to_cv2(self.original_image)
            
            try:
                # 应用模糊
                if blur_type_spinner.text == 'Gaussian':
                    blurred = cv2.GaussianBlur(img, (0, 0), blur_slider.value)
                elif blur_type_spinner.text == 'Box':
                    ksize = int(blur_slider.value * 2 + 1)
                    blurred = cv2.boxFilter(img, -1, (ksize, ksize))
                else:  # Median
                    ksize = int(blur_slider.value * 2 + 1)
                    # 确保ksize是奇数
                    ksize = max(3, ksize if ksize % 2 == 1 else ksize + 1)
                    blurred = cv2.medianBlur(img, ksize)
                
                # 转回PIL格式
                self.pil_image = self.cv2_to_pil(blurred)
                self.update_image_display()
                popup.dismiss()
            except Exception as e:
                print(f"Error applying blur: {e}")
        
        def reset_changes(instance):
            if self.original_image:
                self.pil_image = self.original_image.copy()
                blur_slider.value = 1
                self.update_image_display()
        
        blur_slider.bind(value=update_preview)
        blur_type_spinner.bind(text=update_preview)
        apply_button.bind(on_press=apply_changes)
        reset_button.bind(on_press=reset_changes)
        cancel_button.bind(on_press=popup.dismiss)
        popup.open()

    def show_noise_dialog(self, instance):
        """显示噪点调整对话框"""
        if not self.pil_image:
            return
            
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 预览区域
        preview = Image(source=self.temp_file)
        content.add_widget(preview)
        
        # 噪点类型选择
        noise_type_layout = BoxLayout(size_hint_y=None, height=50)
        noise_type_label = Label(text='Noise Type:', size_hint_x=0.3)
        noise_type_spinner = Spinner(
            text='Gaussian',
            values=('Gaussian', 'Salt & Pepper', 'Speckle'),
            size_hint_x=0.7
        )
        noise_type_layout.add_widget(noise_type_label)
        noise_type_layout.add_widget(noise_type_spinner)
        content.add_widget(noise_type_layout)
        
        # 噪点强度滑块
        slider_layout = BoxLayout(size_hint_y=None, height=50)
        slider_label = Label(text='Intensity:', size_hint_x=0.3)
        noise_slider = Slider(min=0.0, max=1.0, value=0.1, size_hint_x=0.7)
        slider_layout.add_widget(slider_label)
        slider_layout.add_widget(noise_slider)
        content.add_widget(slider_layout)
        
        # 按钮区域
        buttons = BoxLayout(size_hint_y=None, height=50)
        cancel_button = Button(text='Cancel')
        apply_button = Button(text='Apply')
        reset_button = Button(text='Reset')
        
        buttons.add_widget(cancel_button)
        buttons.add_widget(reset_button)
        buttons.add_widget(apply_button)
        content.add_widget(buttons)
        
        popup = Popup(title='Add Noise', content=content, size_hint=(0.8, 0.8))
        
        def update_preview(instance, value):
            if not self.original_image:
                self.original_image = self.pil_image.copy()
            
            # 转换为OpenCV格式
            img = self.pil_to_cv2(self.original_image)
            
            try:
                # 添加噪点
                if noise_type_spinner.text == 'Gaussian':
                    noise = np.random.normal(0, noise_slider.value * 25, img.shape).astype(np.uint8)
                    noisy = cv2.add(img, noise)
                elif noise_type_spinner.text == 'Salt & Pepper':
                    noisy = img.copy()
                    # 盐噪点
                    salt = np.random.random(img.shape[:2]) < noise_slider.value / 2
                    noisy[salt] = 255
                    # 椒噪点
                    pepper = np.random.random(img.shape[:2]) < noise_slider.value / 2
                    noisy[pepper] = 0
                else:  # Speckle
                    noise = np.random.normal(0, noise_slider.value, img.shape).astype(np.uint8)
                    noisy = cv2.add(img, img * noise / 255)
                
                # 转回PIL格式
                temp_img = self.cv2_to_pil(noisy)
                
                # 更新预览
                fd, temp_path = tempfile.mkstemp(suffix='.png')
                os.close(fd)
                temp_img.save(temp_path, format='PNG')
                preview.source = temp_path
                preview.reload()
                os.unlink(temp_path)
            except Exception as e:
                print(f"Error adding noise: {e}")
        
        def apply_changes(instance):
            if not self.original_image:
                self.original_image = self.pil_image.copy()
            
            # 转换为OpenCV格式
            img = self.pil_to_cv2(self.original_image)
            
            try:
                # 添加噪点
                if noise_type_spinner.text == 'Gaussian':
                    noise = np.random.normal(0, noise_slider.value * 25, img.shape).astype(np.uint8)
                    noisy = cv2.add(img, noise)
                elif noise_type_spinner.text == 'Salt & Pepper':
                    noisy = img.copy()
                    # 盐噪点
                    salt = np.random.random(img.shape[:2]) < noise_slider.value / 2
                    noisy[salt] = 255
                    # 椒噪点
                    pepper = np.random.random(img.shape[:2]) < noise_slider.value / 2
                    noisy[pepper] = 0
                else:  # Speckle
                    noise = np.random.normal(0, noise_slider.value, img.shape).astype(np.uint8)
                    noisy = cv2.add(img, img * noise / 255)
                
                # 转回PIL格式
                self.pil_image = self.cv2_to_pil(noisy)
                self.update_image_display()
                popup.dismiss()
            except Exception as e:
                print(f"Error adding noise: {e}")
        
        def reset_changes(instance):
            if self.original_image:
                self.pil_image = self.original_image.copy()
                noise_slider.value = 0.1
                self.update_image_display()
        
        noise_slider.bind(value=update_preview)
        noise_type_spinner.bind(text=update_preview)
        apply_button.bind(on_press=apply_changes)
        reset_button.bind(on_press=reset_changes)
        cancel_button.bind(on_press=popup.dismiss)
        popup.open()

    def apply_vignette(self, instance):
        """应用晕影效果"""
        if not self.pil_image:
            return
            
        self.save_state()
        # 转换为OpenCV格式
        img = self.pil_to_cv2(self.pil_image)
        
        # 创建晕影遮罩
        rows, cols = img.shape[:2]
        kernel_x = cv2.getGaussianKernel(cols, cols/4)
        kernel_y = cv2.getGaussianKernel(rows, rows/4)
        kernel = kernel_y * kernel_x.T
        mask = kernel / kernel.max()
        
        # 应用晕影效果
        vignette = img.copy()
        for i in range(3):
            vignette[:,:,i] = vignette[:,:,i] * mask
        
        # 转回PIL格式
        self.pil_image = self.cv2_to_pil(vignette)
        self.update_image_display()

    def __del__(self):
        # 清理临时文件
        for temp_file in [self.temp_file, self.preview_temp_file]:
            if temp_file and os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except:
                    pass

class ImageEditorApp(App):
    def build(self):
        return ImageEditor()

if __name__ == '__main__':
    ImageEditorApp().run() 
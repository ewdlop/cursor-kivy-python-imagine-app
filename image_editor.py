from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from PIL import Image as PILImage, ImageEnhance, ImageFilter
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
        
        # 创建顶部按钮区域（两行）
        self.button_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=100)
        
        # 第一行按钮
        self.button_row1 = BoxLayout(size_hint_y=None, height=50)
        self.load_button = Button(text='Load Image', on_press=self.show_file_chooser)
        self.rotate_button = Button(text='Rotate', on_press=self.rotate_image)
        self.flip_h_button = Button(text='Flip H', on_press=self.flip_horizontal)
        self.flip_v_button = Button(text='Flip V', on_press=self.flip_vertical)
        self.grayscale_button = Button(text='Grayscale', on_press=self.grayscale_image)
        self.brightness_button = Button(text='Brightness', on_press=self.show_brightness_dialog)
        self.contrast_button = Button(text='Contrast', on_press=self.show_contrast_dialog)
        
        # 第二行按钮
        self.button_row2 = BoxLayout(size_hint_y=None, height=50)
        self.filter_button = Button(text='Filters', on_press=self.show_filter_dialog)
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
        for button in [self.filter_button, self.crop_button, self.resize_button,
                      self.undo_button, self.redo_button, self.save_button]:
            self.button_row2.add_widget(button)
        
        # 将两行按钮添加到按钮布局
        self.button_layout.add_widget(self.button_row1)
        self.button_layout.add_widget(self.button_row2)
        
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
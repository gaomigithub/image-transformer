#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片格式转换工具
支持将tif/PNG/WebP格式转换为常用格式(png, jpg)
支持批量调整缩放比例、文件大小、图片质量
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.ttk import Progressbar
from PIL import Image
import threading
import glob
from datetime import datetime
import io


class ImageConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("图片格式转换工具")
        self.root.geometry("750x600")
        
        # 设置窗口图标和样式
        self.root.configure(bg='#f0f0f0')
        
        # 初始化变量
        self.folder_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.output_format = tk.StringVar(value="jpg")
        self.current_file = tk.StringVar()
        self.progress_var = tk.DoubleVar()
        self.is_converting = False
        
        # 调整选项变量
        self.adjustment_type = tk.StringVar(value="none")  # none, scale, filesize, quality
        self.scale_percentage = tk.StringVar(value="100")
        self.target_filesize = tk.StringVar(value="1024")
        self.quality_level = tk.StringVar(value="10")
        
        # 绑定输入路径变化事件
        self.folder_path.trace('w', self.on_input_path_changed)
        
        self.setup_ui()
    
    def on_input_path_changed(self, *args):
        """输入路径变化时自动更新输出路径"""
        input_path = self.folder_path.get()
        if input_path and os.path.exists(input_path):
            # 生成当前日期字符串 (YYYYMMDD格式)
            current_date = datetime.now().strftime("%Y%m%d")
            output_folder = os.path.join(input_path, f"imgTrans-{current_date}")
            self.output_path.set(output_folder)
            self.log_message(f"输出路径已自动设置为: {output_folder}")
    
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="图片格式转换工具", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 输入文件夹选择
        ttk.Label(main_frame, text="输入文件夹:").grid(row=1, column=0, 
                                                     sticky=tk.W, pady=5)
        
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), 
                        pady=5, padx=(10, 0))
        input_frame.columnconfigure(0, weight=1)
        
        self.folder_entry = ttk.Entry(input_frame, textvariable=self.folder_path,
                                     width=50)
        self.folder_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(input_frame, text="浏览", 
                  command=self.browse_input_folder).grid(row=0, column=1, padx=(5, 0))
        
        # 输出文件夹选择
        ttk.Label(main_frame, text="输出文件夹:").grid(row=2, column=0, 
                                                     sticky=tk.W, pady=5)
        
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), 
                         pady=5, padx=(10, 0))
        output_frame.columnconfigure(0, weight=1)
        
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_path,
                                     width=50)
        self.output_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(output_frame, text="浏览", 
                  command=self.browse_output_folder).grid(row=0, column=1, padx=(5, 0))
        
        # 输出格式选择
        ttk.Label(main_frame, text="输出格式:").grid(row=3, column=0, 
                                                   sticky=tk.W, pady=5)
        
        format_frame = ttk.Frame(main_frame)
        format_frame.grid(row=3, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        self.format_combo = ttk.Combobox(format_frame, textvariable=self.output_format,
                                        values=["jpg", "png"], state="readonly", width=15)
        self.format_combo.grid(row=0, column=0)
        
        # 批量调整选项框架
        adjustment_frame = ttk.LabelFrame(main_frame, text="批量调整选项", padding="10")
        adjustment_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), 
                             pady=10)
        adjustment_frame.columnconfigure(1, weight=1)
        
        # 不调整选项
        ttk.Radiobutton(adjustment_frame, text="不调整", 
                       variable=self.adjustment_type, value="none").grid(row=0, column=0, sticky=tk.W, pady=2)
        
        # 缩放比例选项
        scale_frame = ttk.Frame(adjustment_frame)
        scale_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Radiobutton(scale_frame, text="缩放比例:", 
                       variable=self.adjustment_type, value="scale").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(scale_frame, textvariable=self.scale_percentage, width=10).grid(row=0, column=1, padx=(5, 2))
        ttk.Label(scale_frame, text="%").grid(row=0, column=2, sticky=tk.W)
        ttk.Label(scale_frame, text="(如：90表示缩小到原图的90%)", 
                 foreground="gray").grid(row=0, column=3, padx=(10, 0), sticky=tk.W)
        
        # 文件大小选项
        filesize_frame = ttk.Frame(adjustment_frame)
        filesize_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Radiobutton(filesize_frame, text="文件大小:", 
                       variable=self.adjustment_type, value="filesize").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(filesize_frame, textvariable=self.target_filesize, width=10).grid(row=0, column=1, padx=(5, 2))
        ttk.Label(filesize_frame, text="KB").grid(row=0, column=2, sticky=tk.W)
        ttk.Label(filesize_frame, text="(如：1024表示输出约1MB大小的图片)", 
                 foreground="gray").grid(row=0, column=3, padx=(10, 0), sticky=tk.W)
        
        # 图片质量选项
        quality_frame = ttk.Frame(adjustment_frame)
        quality_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Radiobutton(quality_frame, text="图片质量:", 
                       variable=self.adjustment_type, value="quality").grid(row=0, column=0, sticky=tk.W)
        quality_scale = ttk.Scale(quality_frame, from_=1, to=10, variable=self.quality_level, 
                                 orient=tk.HORIZONTAL, length=150)
        quality_scale.grid(row=0, column=1, padx=(5, 10))
        self.quality_label = ttk.Label(quality_frame, text="10")
        self.quality_label.grid(row=0, column=2)
        ttk.Label(quality_frame, text="(1=最小，10=最佳质量)", 
                 foreground="gray").grid(row=0, column=3, padx=(10, 0), sticky=tk.W)
        
        # 绑定质量滑块变化事件
        quality_scale.configure(command=self.on_quality_changed)
        
        # 转换按钮
        self.convert_button = ttk.Button(main_frame, text="开始转换", 
                                        command=self.start_conversion,
                                        style='Accent.TButton')
        self.convert_button.grid(row=5, column=0, columnspan=3, pady=20)
        
        # 进度条框架
        progress_frame = ttk.LabelFrame(main_frame, text="转换进度", padding="10")
        progress_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), 
                           pady=10)
        progress_frame.columnconfigure(0, weight=1)
        
        # 当前处理文件显示
        self.current_file_label = ttk.Label(progress_frame, 
                                           textvariable=self.current_file,
                                           foreground='blue')
        self.current_file_label.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # 进度条
        self.progress_bar = Progressbar(progress_frame, variable=self.progress_var,
                                       maximum=100, length=400)
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # 进度百分比
        self.progress_label = ttk.Label(progress_frame, text="0%")
        self.progress_label.grid(row=2, column=0, pady=5)
        
        # 日志框架
        log_frame = ttk.LabelFrame(main_frame, text="转换日志", padding="10")
        log_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), 
                      pady=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # 日志文本框
        self.log_text = tk.Text(log_frame, height=5, width=60)
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 配置主框架行权重
        main_frame.rowconfigure(7, weight=1)
    
    def on_quality_changed(self, value):
        """质量滑块变化时更新标签"""
        self.quality_label.config(text=f"{int(float(value))}")
    
    def browse_input_folder(self):
        """浏览输入文件夹"""
        folder = filedialog.askdirectory(title="选择包含图片的输入文件夹")
        if folder:
            self.folder_path.set(folder)
            self.log_message(f"选择输入文件夹: {folder}")
    
    def browse_output_folder(self):
        """浏览输出文件夹"""
        folder = filedialog.askdirectory(title="选择输出文件夹")
        if folder:
            self.output_path.set(folder)
            self.log_message(f"选择输出文件夹: {folder}")
    
    def log_message(self, message):
        """添加日志消息"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def validate_inputs(self):
        """验证输入参数"""
        if self.adjustment_type.get() == "scale":
            try:
                scale = float(self.scale_percentage.get())
                if scale <= 0 or scale > 200:
                    messagebox.showerror("错误", "缩放比例必须在0-200%之间！")
                    return False
            except ValueError:
                messagebox.showerror("错误", "请输入有效的缩放比例数字！")
                return False
        
        elif self.adjustment_type.get() == "filesize":
            try:
                filesize = int(self.target_filesize.get())
                if filesize <= 0:
                    messagebox.showerror("错误", "目标文件大小必须大于0KB！")
                    return False
            except ValueError:
                messagebox.showerror("错误", "请输入有效的文件大小数字！")
                return False
        
        return True
    
    def start_conversion(self):
        """开始转换"""
        if not self.folder_path.get():
            messagebox.showerror("错误", "请选择输入文件夹！")
            return
        
        if not self.output_path.get():
            messagebox.showerror("错误", "请选择输出文件夹！")
            return
        
        if not os.path.exists(self.folder_path.get()):
            messagebox.showerror("错误", "选择的输入文件夹不存在！")
            return
        
        if not self.validate_inputs():
            return
        
        # 禁用转换按钮
        self.convert_button.config(state='disabled')
        self.is_converting = True
        
        # 清空日志
        self.log_text.delete(1.0, tk.END)
        
        # 记录调整设置
        adjustment_type = self.adjustment_type.get()
        if adjustment_type != "none":
            if adjustment_type == "scale":
                self.log_message(f"调整设置: 缩放比例 {self.scale_percentage.get()}%")
            elif adjustment_type == "filesize":
                self.log_message(f"调整设置: 目标文件大小 {self.target_filesize.get()}KB")
            elif adjustment_type == "quality":
                self.log_message(f"调整设置: 图片质量等级 {int(float(self.quality_level.get()))}/10")
        
        # 在新线程中执行转换
        conversion_thread = threading.Thread(target=self.convert_images)
        conversion_thread.daemon = True
        conversion_thread.start()
    
    def adjust_image_by_filesize(self, img, target_size_kb, output_format):
        """根据目标文件大小调整图片"""
        target_size = target_size_kb * 1024  # 转换为字节
        
        # 二分查找合适的质量参数
        low_quality = 10
        high_quality = 95
        
        for _ in range(10):  # 最多尝试10次
            mid_quality = (low_quality + high_quality) // 2
            
            # 测试当前质量下的文件大小
            buffer = io.BytesIO()
            save_kwargs = {}
            if output_format.lower() == 'jpg':
                save_kwargs['quality'] = mid_quality
                save_kwargs['optimize'] = True
            
            img.save(buffer, format=output_format.upper(), **save_kwargs)
            current_size = buffer.tell()
            
            if abs(current_size - target_size) <= target_size * 0.1:  # 10%误差范围内
                buffer.seek(0)
                return buffer.getvalue(), mid_quality
            elif current_size > target_size:
                high_quality = mid_quality - 1
            else:
                low_quality = mid_quality + 1
            
            if low_quality > high_quality:
                break
        
        # 如果无法达到目标大小，使用最接近的质量
        buffer = io.BytesIO()
        save_kwargs = {}
        if output_format.lower() == 'jpg':
            save_kwargs['quality'] = max(10, min(95, mid_quality))
            save_kwargs['optimize'] = True
        
        img.save(buffer, format=output_format.upper(), **save_kwargs)
        buffer.seek(0)
        return buffer.getvalue(), max(10, min(95, mid_quality))
    
    def convert_images(self):
        """转换图片"""
        try:
            input_folder = self.folder_path.get()
            output_folder = self.output_path.get()
            output_format = self.output_format.get()
            adjustment_type = self.adjustment_type.get()
            
            # 查找支持的图片文件（扩展更多格式支持）
            supported_formats = [
                # 原有格式
                '*.tif', '*.tiff', '*.png', '*.webp', 
                '*.TIF', '*.TIFF', '*.PNG', '*.WEBP',
                # 扩展格式
                '*.jpg', '*.jpeg', '*.gif', '*.bmp', 
                '*.JPG', '*.JPEG', '*.GIF', '*.BMP'
            ]
            all_files = []
            
            for format_pattern in supported_formats:
                files = glob.glob(os.path.join(input_folder, format_pattern))
                all_files.extend(files)
            
            if not all_files:
                self.log_message("在选择的输入文件夹中未找到支持的图片文件 (tif, png, webp, jpg, gif, bmp)")
                messagebox.showinfo("提示", "未找到支持的图片文件")
                self.finish_conversion()
                return
            
            total_files = len(all_files)
            self.log_message(f"找到 {total_files} 个图片文件")
            
            # 创建输出文件夹
            os.makedirs(output_folder, exist_ok=True)
            self.log_message(f"输出文件夹: {output_folder}")
            
            converted_count = 0
            failed_count = 0
            
            for i, file_path in enumerate(all_files):
                if not self.is_converting:
                    break
                
                try:
                    # 更新当前处理文件
                    filename = os.path.basename(file_path)
                    self.current_file.set(f"正在处理: {filename}")
                    
                    # 转换图片
                    with Image.open(file_path) as img:
                        original_size = img.size
                        
                        # 处理调整选项
                        if adjustment_type == "scale":
                            # 缩放比例调整
                            scale = float(self.scale_percentage.get()) / 100
                            new_size = (int(original_size[0] * scale), int(original_size[1] * scale))
                            img = img.resize(new_size, Image.Resampling.LANCZOS)
                            self.log_message(f"  缩放: {original_size} -> {new_size}")
                        
                        # 如果是RGBA模式且要转换为jpg，需要转换为RGB
                        if output_format.lower() == 'jpg' and img.mode in ('RGBA', 'LA'):
                            # 创建白色背景
                            background = Image.new('RGB', img.size, (255, 255, 255))
                            if img.mode == 'RGBA':
                                background.paste(img, mask=img.split()[-1])  # 使用alpha通道作为mask
                            else:
                                background.paste(img)
                            img = background
                        
                        # 生成输出文件名
                        name_without_ext = os.path.splitext(filename)[0]
                        output_filename = f"{name_without_ext}.{output_format}"
                        output_path = os.path.join(output_folder, output_filename)
                        
                        # 保存转换后的图片
                        save_kwargs = {}
                        
                        if adjustment_type == "filesize":
                            # 文件大小调整
                            target_kb = int(self.target_filesize.get())
                            img_data, used_quality = self.adjust_image_by_filesize(img, target_kb, output_format)
                            with open(output_path, 'wb') as f:
                                f.write(img_data)
                            actual_size = len(img_data) // 1024
                            self.log_message(f"  文件大小: 目标{target_kb}KB -> 实际{actual_size}KB (质量:{used_quality})")
                            
                        elif adjustment_type == "quality":
                            # 图片质量调整
                            quality_level = int(float(self.quality_level.get()))
                            if output_format.lower() == 'jpg':
                                # 将1-10级别映射到JPEG质量10-95
                                jpeg_quality = int(10 + (quality_level - 1) * 85 / 9)
                                save_kwargs['quality'] = jpeg_quality
                                save_kwargs['optimize'] = True
                                self.log_message(f"  质量调整: 等级{quality_level}/10 (JPEG质量:{jpeg_quality})")
                            else:
                                # PNG格式使用压缩级别
                                png_compress = 9 - int((quality_level - 1) * 8 / 9)  # 1->8, 10->0
                                save_kwargs['compress_level'] = png_compress
                                self.log_message(f"  质量调整: 等级{quality_level}/10 (PNG压缩:{png_compress})")
                            
                            img.save(output_path, **save_kwargs)
                            
                        else:
                            # 默认保存设置
                            if output_format.lower() == 'jpg':
                                save_kwargs['quality'] = 95
                                save_kwargs['optimize'] = True
                            
                            img.save(output_path, **save_kwargs)
                        
                        converted_count += 1
                        self.log_message(f"✓ 转换成功: {filename} -> {output_filename}")
                
                except Exception as e:
                    failed_count += 1
                    self.log_message(f"✗ 转换失败: {filename} - {str(e)}")
                
                # 更新进度条
                progress = (i + 1) / total_files * 100
                self.progress_var.set(progress)
                self.progress_label.config(text=f"{progress:.1f}%")
                self.root.update_idletasks()
            
            # 转换完成
            self.current_file.set("转换完成")
            self.log_message(f"\n转换完成！成功: {converted_count}, 失败: {failed_count}")
            
            if converted_count > 0:
                messagebox.showinfo("完成", 
                                  f"转换完成！\n成功转换: {converted_count} 个文件\n失败: {failed_count} 个文件\n输出文件夹: {output_folder}")
            
        except Exception as e:
            self.log_message(f"转换过程中发生错误: {str(e)}")
            messagebox.showerror("错误", f"转换过程中发生错误: {str(e)}")
        
        finally:
            self.finish_conversion()
    
    def finish_conversion(self):
        """完成转换，重置UI状态"""
        self.is_converting = False
        self.convert_button.config(state='normal')
        self.progress_var.set(0)
        self.progress_label.config(text="0%")


def main():
    """主函数"""
    root = tk.Tk()
    
    # 设置主题样式
    style = ttk.Style()
    
    # 尝试使用现代主题
    try:
        style.theme_use('vista')  # Windows 10风格
    except:
        try:
            style.theme_use('clam')  # 备选主题
        except:
            pass  # 使用默认主题
    
    # 自定义按钮样式
    style.configure('Accent.TButton', font=('Arial', 10, 'bold'))
    
    app = ImageConverter(root)
    
    # 设置窗口关闭事件
    def on_closing():
        if app.is_converting:
            if messagebox.askokcancel("退出", "转换正在进行中，确定要退出吗？"):
                app.is_converting = False
                root.destroy()
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # 启动主循环
    root.mainloop()


if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片格式转换工具打包脚本
自动化PyInstaller打包过程
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def clean_build_dirs():
    """清理之前的构建目录"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"清理目录: {dir_name}")
            shutil.rmtree(dir_name)
    
    # 清理.spec文件
    spec_files = list(Path('.').glob('*.spec'))
    for spec_file in spec_files:
        print(f"清理文件: {spec_file}")
        spec_file.unlink()

def check_pyinstaller():
    """检查PyInstaller是否已安装"""
    try:
        result = subprocess.run(['pyinstaller', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"PyInstaller版本: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("PyInstaller未安装，请先运行：pip install -r requirements_build.txt")
        return False

def build_executable():
    """构建可执行文件"""
    if not check_pyinstaller():
        return False
    
    print("开始打包程序...")
    
    # PyInstaller命令参数
    cmd = [
        'pyinstaller',
        '--onefile',                    # 打包成单个文件
        '--windowed',                   # Windows下隐藏控制台窗口
        '--name=图片格式转换工具',         # 设置可执行文件名称
        '--add-data=README.md;.',       # 包含README文件
        '--hidden-import=PIL._tkinter_finder',  # 确保PIL与tkinter兼容
        '--hidden-import=tkinter',      # 确保包含tkinter
        '--hidden-import=PIL.Image',    # 确保包含PIL.Image
        '--clean',                      # 清理临时文件
        'image_converter.py'            # 主程序文件
    ]
    
    try:
        # 执行打包命令
        result = subprocess.run(cmd, check=True)
        
        if result.returncode == 0:
            print("\n✅ 打包成功！")
            print(f"📁 可执行文件位置: {os.path.abspath('dist')}")
            print("📋 可执行文件: 图片格式转换工具.exe")
            
            # 检查文件大小
            exe_path = os.path.join('dist', '图片格式转换工具.exe')
            if os.path.exists(exe_path):
                size_mb = os.path.getsize(exe_path) / (1024 * 1024)
                print(f"📏 文件大小: {size_mb:.1f} MB")
            
            return True
        else:
            print("❌ 打包失败")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ 打包过程中出现错误: {e}")
        return False

def create_portable_package():
    """创建便携版打包"""
    dist_dir = Path('dist')
    if not dist_dir.exists():
        print("❌ 未找到dist目录，请先执行打包")
        return
    
    # 创建便携版文件夹
    portable_dir = Path('ImageConverter_Portable')
    if portable_dir.exists():
        shutil.rmtree(portable_dir)
    
    portable_dir.mkdir()
    
    # 复制可执行文件
    exe_file = dist_dir / '图片格式转换工具.exe'
    if exe_file.exists():
        shutil.copy2(exe_file, portable_dir / '图片格式转换工具.exe')
    
    # 复制说明文件
    if Path('README.md').exists():
        shutil.copy2('README.md', portable_dir / '使用说明.md')
    
    # 创建快速启动说明
    quick_start = portable_dir / '快速开始.txt'
    with open(quick_start, 'w', encoding='utf-8') as f:
        f.write("""图片格式转换工具 - 快速开始

使用方法：
1. 双击"图片格式转换工具.exe"启动程序
2. 选择包含图片的输入文件夹
3. 选择输出格式和调整选项
4. 点击"开始转换"

支持格式：
- 输入：TIF、TIFF、PNG
- 输出：JPG、PNG

功能特性：
- 批量格式转换
- 缩放比例调整
- 文件大小控制
- 图片质量调整

注意事项：
- 程序为便携版，无需安装
- 转换后的文件默认保存在输入文件夹的子目录中
- 详细说明请查看"使用说明.md"

版本信息：
- 基于Python开发
- 使用PIL/Pillow图像处理库
""")
    
    print(f"✅ 便携版已创建: {portable_dir.absolute()}")

def main():
    """主函数"""
    print("=" * 50)
    print("图片格式转换工具 - 打包脚本")
    print("=" * 50)
    
    # 清理构建目录
    clean_build_dirs()
    
    # 构建可执行文件
    if build_executable():
        print("\n" + "=" * 50)
        
        # 询问是否创建便携版
        choice = input("是否创建便携版打包？(y/n): ").lower()
        if choice in ['y', 'yes', '是']:
            create_portable_package()
        
        print("\n🎉 打包完成！")
        print("\n📝 使用说明：")
        print("1. 将dist目录中的exe文件分发给其他用户")
        print("2. 用户双击exe文件即可直接使用")
        print("3. 无需安装Python环境或任何依赖")
        
    else:
        print("\n❌ 打包失败，请检查错误信息")
        sys.exit(1)

if __name__ == "__main__":
    main() 
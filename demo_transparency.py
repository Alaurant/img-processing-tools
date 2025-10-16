#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
透明背景处理演示
展示保留透明背景和转换为白色背景的区别
"""

import tempfile
from pathlib import Path
from PIL import Image, ImageDraw
from image_converter import ImageConverter

def create_test_image_with_transparency():
    """创建一个带透明背景的测试图片"""
    # 创建一个带透明背景的图片
    img = Image.new('RGBA', (200, 200), (0, 0, 0, 0))  # 完全透明背景
    
    # 绘制一个半透明的圆形
    draw = ImageDraw.Draw(img)
    draw.ellipse([50, 50, 150, 150], fill=(255, 0, 0, 128))  # 半透明红色圆形
    
    # 绘制一个完全不透明的矩形
    draw.rectangle([75, 75, 125, 125], fill=(0, 255, 0, 255))  # 不透明绿色矩形
    
    return img

def demo_transparency_handling():
    """演示透明背景处理"""
    print("透明背景处理演示")
    print("=" * 50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        
        # 创建测试图片
        test_img = create_test_image_with_transparency()
        test_img.save(test_dir / 'transparent_test.png')
        print(f"创建测试图片: {test_dir / 'transparent_test.png'}")
        
        # 方法1: 保留透明背景（默认）
        print("\n1. 保留透明背景（默认）:")
        converter_transparent = ImageConverter(quality=75, preserve_transparency=True)
        success1, total1 = converter_transparent.batch_convert(str(test_dir), str(test_dir / 'transparent_bg'))
        
        # 方法2: 转换为白色背景
        print("\n2. 转换为白色背景:")
        converter_white = ImageConverter(quality=75, preserve_transparency=False)
        success2, total2 = converter_white.batch_convert(str(test_dir), str(test_dir / 'white_bg'))
        
        # 比较文件大小
        white_bg_file = test_dir / 'white_bg' / 'transparent_test.webp'
        transparent_bg_file = test_dir / 'transparent_bg' / 'transparent_test.webp'
        
        if white_bg_file.exists() and transparent_bg_file.exists():
            white_size = white_bg_file.stat().st_size
            transparent_size = transparent_bg_file.stat().st_size
            
            print(f"\n文件大小比较:")
            print(f"白色背景版本: {white_size} bytes")
            print(f"透明背景版本: {transparent_size} bytes")
            print(f"大小差异: {transparent_size - white_size} bytes")
            
            if transparent_size > white_size:
                print("透明背景版本文件更大，因为需要存储透明度信息")
            else:
                print("白色背景版本文件更大，可能是因为压缩效果更好")
        
        print(f"\n演示完成！")
        print(f"透明背景版本保存在: {test_dir / 'transparent_bg'}")
        print(f"白色背景版本保存在: {test_dir / 'white_bg'}")

if __name__ == '__main__':
    demo_transparency_handling() 
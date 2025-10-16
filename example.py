#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片转换器使用示例
"""

from image_converter import ImageConverter

def example_usage():
    """使用示例"""
    
    # 创建转换器实例，设置质量为75%，默认保留透明背景
    converter = ImageConverter(quality=75)
    
    # 示例1: 基本转换
    print("示例1: 基本转换")
    print("将当前目录下的图片转换为WebP格式")
    success, total = converter.batch_convert('.')
    print(f"转换结果: {success}/{total} 个文件成功转换\n")
    
    # 示例2: 指定输出目录
    print("示例2: 指定输出目录")
    print("将图片转换到指定目录")
    success, total = converter.batch_convert('.', './my_webp_images')
    print(f"转换结果: {success}/{total} 个文件成功转换\n")
    
    # 示例3: 不同质量设置
    print("示例3: 高质量转换")
    high_quality_converter = ImageConverter(quality=90)
    success, total = high_quality_converter.batch_convert('.', './high_quality_webp')
    print(f"高质量转换结果: {success}/{total} 个文件成功转换\n")

if __name__ == '__main__':
    print("图片转换器使用示例")
    print("=" * 50)
    example_usage() 
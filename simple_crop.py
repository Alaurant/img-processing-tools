#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的边框裁剪测试
"""

from PIL import Image

def simple_crop_borders(img):
    """简单的边框裁剪"""
    width, height = img.size
    
    # 获取边缘颜色
    top_color = img.getpixel((width//2, 0))
    bottom_color = img.getpixel((width//2, height-1))
    left_color = img.getpixel((0, height//2))
    right_color = img.getpixel((width-1, height//2))
    
    print(f"边缘颜色: 上={top_color}, 下={bottom_color}, 左={left_color}, 右={right_color}")
    
    # 简单的边框检测（只检查前几行/列）
    top_border = 0
    for y in range(min(10, height)):
        if img.getpixel((width//2, y)) == top_color:
            top_border = y + 1
        else:
            break
    
    bottom_border = height
    for y in range(height-1, max(height-10, -1), -1):
        if img.getpixel((width//2, y)) == bottom_color:
            bottom_border = y
        else:
            break
    
    left_border = 0
    for x in range(min(10, width)):
        if img.getpixel((x, height//2)) == left_color:
            left_border = x + 1
        else:
            break
    
    right_border = width
    for x in range(width-1, max(width-10, -1), -1):
        if img.getpixel((x, height//2)) == right_color:
            right_border = x
        else:
            break
    
    print(f"检测到的边框: 上={top_border}, 下={bottom_border}, 左={left_border}, 右={right_border}")
    
    # 如果检测到边框，进行裁剪
    if top_border > 0 or bottom_border < height or left_border > 0 or right_border < width:
        crop_box = (left_border, top_border, right_border, bottom_border)
        return img.crop(crop_box)
    
    return img

# 测试
if __name__ == '__main__':
    # 创建一个测试图片
    img = Image.new('RGB', (300, 200), color='black')
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    draw.rectangle([20, 20, 280, 180], fill='white')
    
    print(f"原始尺寸: {img.size}")
    cropped = simple_crop_borders(img)
    print(f"裁剪后尺寸: {cropped.size}") 
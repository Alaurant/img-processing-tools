#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch Image Converter Tool
Converts images to WebP format with customizable quality
"""

import os
import sys
from pathlib import Path
from PIL import Image
import argparse
from typing import List, Tuple

class ImageConverter:
    def __init__(self, quality: int = 75, preserve_transparency: bool = True, crop_borders: bool = False, scale_factor: float = None):
        """
        Initialize image converter
        
        Args:
            quality: WebP quality (0-100)
            preserve_transparency: Whether to preserve transparent background (default True)
            crop_borders: Whether to automatically crop borders (default False)
            scale_factor: Scale ratio (e.g., 0.5 means half size), None means no scaling
        """
        self.quality = quality
        self.preserve_transparency = preserve_transparency
        self.should_crop_borders = crop_borders
        self.scale_factor = scale_factor
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.gif'}
    
    def crop_borders(self, img: Image.Image) -> Image.Image:
        """
        Automatically crop image borders
        
        Args:
            img: PIL Image object
            
        Returns:
            Cropped image
        """
        if not self.should_crop_borders:
            return img
            
        # Get image dimensions
        width, height = img.size
        
        # Get edge color (average of multiple points)
        def get_edge_color(positions):
            colors = []
            for pos in positions:
                try:
                    colors.append(img.getpixel(pos))
                except:
                    pass
            if not colors:
                return None
            if isinstance(colors[0], int):  # Grayscale
                return sum(colors) // len(colors)
            else:  # RGB
                r = sum(c[0] for c in colors) // len(colors)
                g = sum(c[1] for c in colors) // len(colors)
                b = sum(c[2] for c in colors) // len(colors)
                return (r, g, b)
        
        # Sample multiple edge points
        top_positions = [(width//4, 0), (width//2, 0), (width*3//4, 0)]
        bottom_positions = [(width//4, height-1), (width//2, height-1), (width*3//4, height-1)]
        left_positions = [(0, height//4), (0, height//2), (0, height*3//4)]
        right_positions = [(width-1, height//4), (width-1, height//2), (width-1, height*3//4)]
        
        top_color = get_edge_color(top_positions)
        bottom_color = get_edge_color(bottom_positions)
        left_color = get_edge_color(left_positions)
        right_color = get_edge_color(right_positions)
        
        # More careful border detection
        # Detect top border
        top_border = 0
        for y in range(min(50, height)):
            uniform_row = True
            for x in range(0, width, max(1, width//20)):  # Sample check
                if img.getpixel((x, y)) != top_color:
                    uniform_row = False
                    break
            if uniform_row:
                top_border = y + 1
            else:
                break
        
        # Detect bottom border
        bottom_border = height
        for y in range(height-1, max(height-50, -1), -1):
            uniform_row = True
            for x in range(0, width, max(1, width//20)):  # Sample check
                if img.getpixel((x, y)) != bottom_color:
                    uniform_row = False
                    break
            if uniform_row:
                bottom_border = y
            else:
                break
        
        # Color tolerance function
        def is_similar_color(color1, color2, tolerance=30):
            if isinstance(color1, int) and isinstance(color2, int):  # Grayscale
                return abs(color1 - color2) <= tolerance
            elif isinstance(color1, tuple) and isinstance(color2, tuple):  # RGB
                return (abs(color1[0] - color2[0]) <= tolerance and 
                       abs(color1[1] - color2[1]) <= tolerance and 
                       abs(color1[2] - color2[2]) <= tolerance)
            return False
        
        # Detect left border - more careful column-by-column check
        left_border = 0
        for x in range(min(400, width)):
            uniform_col = True
            for y in range(0, height, max(1, height//5)):  # Denser sampling check
                if not is_similar_color(img.getpixel((x, y)), left_color, 30):
                    uniform_col = False
                    break
            if uniform_col:
                left_border = x + 1
            else:
                break
        
        # Detect right border - more careful column-by-column check
        right_border = width
        for x in range(width-1, max(width-400, -1), -1):
            uniform_col = True
            for y in range(0, height, max(1, height//5)):  # Denser sampling check
                if not is_similar_color(img.getpixel((x, y)), right_color, 30):
                    uniform_col = False
                    break
            if uniform_col:
                right_border = x
            else:
                break
        
        # If borders detected, perform cropping
        if top_border > 0 or bottom_border < height or left_border > 0 or right_border < width:
            crop_box = (left_border, top_border, right_border, bottom_border)
            return img.crop(crop_box)
        
        return img
    
    def resize_image(self, img: Image.Image) -> Image.Image:
        """
        Resize image by specified ratio
        
        Args:
            img: PIL Image object
            
        Returns:
            Resized image
        """
        if self.scale_factor is None:
            return img
            
        original_width, original_height = img.size
        
        # Calculate new dimensions
        new_width = int(original_width * self.scale_factor)
        new_height = int(original_height * self.scale_factor)
        
        # Ensure new dimensions are at least 1 pixel
        new_width = max(1, new_width)
        new_height = max(1, new_height)
            
        # Use high-quality resampling algorithm for scaling
        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        print(f"  Scaling: {original_width}x{original_height} -> {new_width}x{new_height} (ratio: {self.scale_factor})")
        return resized_img
        
    def convert_image(self, input_path: Path, output_dir: Path) -> bool:
        """
        Convert single image to WebP format
        
        Args:
            input_path: Input image path
            output_dir: Output directory
            
        Returns:
            bool: Whether conversion was successful
        """
        try:
            # Open image
            with Image.open(input_path) as img:
                # Process image mode
                if img.mode in ('RGBA', 'LA', 'P'):
                    if self.preserve_transparency:
                        # Preserve transparent background
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        # Keep RGBA mode, WebP supports transparency
                    else:
                        # Convert to white background
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Apply border cropping
                if self.should_crop_borders:
                    original_size = img.size
                    img = self.crop_borders(img)
                    if img.size != original_size:
                        print(f"  Border cropping: {original_size} -> {img.size}")
                
                # Apply proportional scaling
                if self.scale_factor:
                    img = self.resize_image(img)
                
                # Generate output filename
                output_filename = input_path.stem + '.webp'
                output_path = output_dir / output_filename
                
                # Save as WebP format
                img.save(output_path, 'WEBP', quality=self.quality, optimize=True)
                
                print(f"✓ Conversion successful: {input_path.name} -> {output_filename}")
                return True
                
        except Exception as e:
            print(f"✗ Conversion failed: {input_path.name} - {str(e)}")
            return False
    
    def batch_convert(self, input_dir: str, output_dir: str = None) -> Tuple[int, int]:
        """
        Batch convert images
        
        Args:
            input_dir: Input directory path
            output_dir: Output directory path (optional, default is input_dir/webp_output)
            
        Returns:
            Tuple[int, int]: (success count, total count)
        """
        input_path = Path(input_dir)
        if not input_path.exists():
            print(f"Error: Input directory does not exist: {input_dir}")
            return 0, 0
            
        # Set output directory
        if output_dir is None:
            output_path = input_path / 'webp_output'
        else:
            output_path = Path(output_dir)
            
        # Create output directory
        output_path.mkdir(exist_ok=True)
        
        # Find all supported image files
        image_files = []
        for ext in self.supported_formats:
            image_files.extend(input_path.glob(f'*{ext}'))
            image_files.extend(input_path.glob(f'*{ext.upper()}'))
        
        if not image_files:
            print(f"No supported image files found in directory {input_dir}")
            print(f"Supported formats: {', '.join(self.supported_formats)}")
            return 0, 0
            
        print(f"Found {len(image_files)} image files")
        print(f"Output directory: {output_path}")
        print(f"WebP quality: {self.quality}%")
        print(f"Preserve transparency: {'Yes' if self.preserve_transparency else 'No'}")
        print(f"Auto crop borders: {'Yes' if self.should_crop_borders else 'No'}")
        if self.scale_factor:
            print(f"Proportional scaling: {self.scale_factor} (resize to {self.scale_factor*100:.0f}% of original size)")
        print("-" * 50)
        
        # Batch conversion
        success_count = 0
        for image_file in image_files:
            if self.convert_image(image_file, output_path):
                success_count += 1
                
        print("-" * 50)
        print(f"Conversion completed: {success_count}/{len(image_files)} files successfully converted")
        
        return success_count, len(image_files)

def main():
    parser = argparse.ArgumentParser(description='Batch convert images to WebP format')
    parser.add_argument('input_dir', help='Input directory path')
    parser.add_argument('-o', '--output', help='Output directory path (optional)')
    parser.add_argument('-q', '--quality', type=int, default=75, 
                       help='WebP quality (0-100, default: 75)')
    parser.add_argument('-w', '--white-bg', action='store_true',
                       help='Convert to white background (default preserves transparency)')
    parser.add_argument('-c', '--crop', action='store_true',
                       help='Auto crop borders (detect and remove solid color borders)')
    parser.add_argument('-s', '--scale', type=float, 
                       help='Scale ratio (e.g., 0.5 means half size)')
    
    args = parser.parse_args()
    
    # Validate quality parameter
    if not 0 <= args.quality <= 100:
        print("Error: Quality parameter must be between 0-100")
        sys.exit(1)
    
    # Validate scale ratio parameter
    scale_factor = None
    if args.scale:
        if not 0 < args.scale <= 1:
            print("Error: Scale ratio must be between 0-1 (e.g., 0.5 means half size)")
            sys.exit(1)
        scale_factor = args.scale
    
    # Create converter and execute conversion
    converter = ImageConverter(quality=args.quality, preserve_transparency=not args.white_bg, 
                             crop_borders=args.crop, scale_factor=scale_factor)
    success, total = converter.batch_convert(args.input_dir, args.output)
    
    if success == 0:
        sys.exit(1)

if __name__ == '__main__':
    main()
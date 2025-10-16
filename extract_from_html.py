#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract images from HTML content
For cases where you have HTML content but can't access the website directly
"""

import re
import requests
import os
from pathlib import Path
from website_downloader import WebsiteImageDownloader

def extract_images_from_html_content(html_content: str, output_dir: str = None) -> int:
    """
    Extract and download images from HTML content
    
    Args:
        html_content: The HTML content containing image URLs
        output_dir: Directory to save downloaded images
        
    Returns:
        Number of successfully downloaded images
    """
    
    # Create output directory in Downloads folder if not specified
    if output_dir is None:
        from datetime import datetime
        downloads_path = Path.home() / "Downloads"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = downloads_path / f"extracted_images_{timestamp}"
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Extract image URLs using regex patterns
    image_urls = set()
    
    # Pattern for direct image URLs in the HTML
    url_patterns = [
        r'src=["\']([^"\']*\.(?:jpg|jpeg|png|gif|webp|bmp|tiff)[^"\']*)["\']',
        r'https?://[^"\'\s<>]*\.(?:jpg|jpeg|png|gif|webp|bmp|tiff)[^"\'\s<>]*',
    ]
    
    for pattern in url_patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        for match in matches:
            if match.startswith(('http://', 'https://')):
                image_urls.add(match)
    
    print(f"Found {len(image_urls)} image URLs")
    
    if not image_urls:
        print("No image URLs found in the provided HTML content")
        return 0
    
    # Use the downloader to download images
    downloader = WebsiteImageDownloader()
    
    success_count = 0
    for i, img_url in enumerate(list(image_urls), 1):
        try:
            # Generate filename from URL
            filename = os.path.basename(img_url.split('?')[0])  # Remove query parameters
            if not filename or '.' not in filename:
                filename = f"image_{i:03d}.jpg"
            
            # Clean filename
            filename = downloader.sanitize_filename(filename)
            save_path = output_path / filename
            
            # Avoid conflicts
            counter = 1
            original_save_path = save_path
            while save_path.exists():
                name, ext = os.path.splitext(original_save_path)
                save_path = Path(f"{name}_{counter}{ext}")
                counter += 1
            
            print(f"[{i}/{len(image_urls)}] Downloading: {img_url}")
            
            if downloader.download_image(img_url, save_path):
                success_count += 1
                print(f"✓ Saved as: {save_path.name}")
            else:
                print(f"✗ Download failed")
                
        except Exception as e:
            print(f"✗ Error processing {img_url}: {str(e)}")
            continue
    
    print("-" * 50)
    print(f"Download completed: {success_count}/{len(image_urls)} images successfully downloaded")
    print(f"Saved to directory: {output_path.absolute()}")
    
    return success_count

def main():
    # The HTML content you provided
    html_content = '''<div><div class="media-viewer media-viewer--no-sidebar">
    <div class="media-viewer__gallery">
        <div data-media-viewer="" class="pswp pswp--desktop pswp--supports-fs pswp--open pswp--notouch pswp--css_animation pswp--svg pswp--zoom-allowed pswp--visible pswp--animated-in" role="dialog" aria-hidden="false" style="position: fixed; opacity: 1;">
            <div class="pswp__bg" style="opacity: 1;"></div>
            <div class="pswp__scroll-wrap">
                <div class="pswp__container" data-slide-container="" style="transform: translate3d(0px, 0px, 0px);">
                    <div class="pswp__item" style="display: block; transform: translate3d(-436px, 0px, 0px);"><div class="pswp__zoom-wrap" style="transform: translate3d(0px, 44px, 0px) scale(1);"><img class="pswp__img" src="https://i2.au.reastatic.net/768x1280-resize,r=33,g=40,b=46/c6f11e67deb61401cfd9c0be7fb7a4b7a9fce356b44394dae90d77596955e26b/image.jpg" style="opacity: 1; width: 389px; height: 648px;"></div></div>
                    <div class="pswp__item" style="transform: translate3d(0px, 0px, 0px);"><div class="pswp__zoom-wrap" style="transform: translate3d(0px, 109px, 0px) scale(1);"><div class="pswp__img pswp__img--placeholder pswp__img--placeholder--blank" style="width: 389px; height: 519px; display: none;"></div><img class="pswp__img" src="https://i2.au.reastatic.net/600x800-resize,extend,r=33,g=40,b=46/73b116b598e66028b81a21626eaa01851f9c0bdfa97deb2a92dd66b531b104c2/image.jpg" style="display: block; width: 389px; height: 519px;"></div></div>
                    <div class="pswp__item" style="display: block; transform: translate3d(436px, 0px, 0px);"><div class="pswp__zoom-wrap" style="transform: translate3d(0px, 109px, 0px) scale(1);"><img class="pswp__img" src="https://i2.au.reastatic.net/600x800-resize,extend,r=33,g=40,b=46/bafb462b19a557fe7f83af0563b4eada6a08e6d41a1571f71180af8528ab3914/image.jpg" style="opacity: 1; width: 389px; height: 519px;"></div></div>
                </div>
                <div class="pswp__ui">
                    <div data-topbar="" class="pswp__top-bar">
                        <div data-topbar-counter="" class="pswp__counter">1 / 23</div>
                        <button class="pswp__button pswp__button--close" title="Close (Esc)"></button>
                        <button class="pswp__button pswp__button--zoom" title="Zoom in/out"></button>
                        <div class="pswp__preloader">
                            <div class="pswp__preloader__icn">
                                <div class="pswp__preloader__cut">
                                    <div class="pswp__preloader__donut"></div>
                                </div>
                            </div>
                        </div>
                        <div class="quicklinks">
                            <button data-link-floorplan="" style="background-image: url(https://argonaut.au.reastatic.net/resi-property/prod/listing-experience-web/floorplan-lg-4a9069cb95378fcefaa4.svg)" class="quicklinks__link" title="Floorplan"></button>
                            <button data-link-video="" data-link-walkthroughvideo="" style="background-image: url(https://argonaut.au.reastatic.net/resi-property/prod/listing-experience-web/play-lg-df2b0ae9b26b5d918d97.svg)" class="quicklinks__link" title="Video" disabled="true"></button>
                            <button data-link-virtualtour="" style="background-image: url(https://argonaut.au.reastatic.net/resi-property/prod/listing-experience-web/3d-lg-eb06e7e6a7356e92711f.svg)" class="quicklinks__link" title="Virtual tour" disabled="true"></button>
                        </div>
                    </div>
                    <button class="pswp__button pswp__button--arrow--left" title="Previous (arrow left)"><span style="background-image: url(https://argonaut.au.reastatic.net/resi-property/prod/listing-experience-web/arrow-left-small-ca8e765d85c82c7da112.svg)"> </span>
                    </button>
                    <button class="pswp__button pswp__button--arrow--right" title="Next (arrow right)"><span style="background-image: url(https://argonaut.au.reastatic.net/resi-property/prod/listing-experience-web/arrow-right-small-05fe8ad4ac48c12d1645.svg)"> </span>
                    </button>
                    <div class="pswp__caption pswp__element--disabled">
                        <div class="pswp__caption__center"></div>
                    </div>
                </div>
            </div>
            <div id="mv-external-media"></div>
        </div>
    </div>
</div></div>'''
    
    print("Extracting images from HTML content...")
    success_count = extract_images_from_html_content(html_content)
    
    if success_count > 0:
        print(f"\n✅ Successfully extracted {success_count} images!")
        
        # Get the output directory that was created
        from datetime import datetime
        downloads_path = Path.home() / "Downloads"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_dir = downloads_path / f"extracted_images_{timestamp}"
        
        # Convert to WebP and save in same folder
        print("Converting to WebP format...")
        from image_converter import ImageConverter
        converter = ImageConverter(quality=75, preserve_transparency=True, crop_borders=True)
        webp_output_dir = temp_dir / "webp_converted"
        conv_success, total = converter.batch_convert(str(temp_dir), str(webp_output_dir))
        
        if conv_success > 0:
            print(f"✅ Successfully converted {conv_success}/{total} images to WebP!")
            print(f"📁 WebP images saved to: {webp_output_dir}")
        else:
            print("❌ WebP conversion failed")

if __name__ == "__main__":
    main()
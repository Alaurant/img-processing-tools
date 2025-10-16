#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Website Image Downloader Tool
Downloads all images from a specified website
"""

import os
import requests
import urllib.parse
from pathlib import Path
from bs4 import BeautifulSoup
import time
import random
from typing import List, Set
import re

class WebsiteImageDownloader:
    def __init__(self, max_images: int = 50, timeout: int = 10):
        """
        Initialize website image downloader
        
        Args:
            max_images: Maximum number of images to download
            timeout: Request timeout in seconds
        """
        self.max_images = max_images
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.svg'}
    
    def is_valid_image_url(self, url: str) -> bool:
        """Check if URL is a valid image link"""
        parsed = urllib.parse.urlparse(url.lower())
        path = parsed.path
        return any(path.endswith(ext) for ext in self.image_extensions)
    
    def get_absolute_url(self, base_url: str, relative_url: str) -> str:
        """Convert relative URL to absolute URL"""
        return urllib.parse.urljoin(base_url, relative_url)
    
    def extract_images_from_html(self, html: str, base_url: str) -> Set[str]:
        """Extract image URLs from HTML with special handling for realestate.com.au"""
        soup = BeautifulSoup(html, 'html.parser')
        image_urls = set()
        
        # Check if this is realestate.com.au
        if 'realestate.com.au' in base_url:
            print("Detected realestate.com.au - using specialized extraction")
            
            # Look for PhotoSwipe gallery images
            pswp_images = soup.find_all('img', class_='pswp__img')
            for img in pswp_images:
                src = img.get('src')
                if src:
                    image_urls.add(src)
            
            # Look for media viewer images
            media_images = soup.find_all('img', class_=re.compile(r'.*media.*|.*photo.*|.*image.*', re.I))
            for img in media_images:
                src = img.get('src')
                if src:
                    image_urls.add(src)
            
            # Look in script tags for image URLs (for dynamically loaded content)
            scripts = soup.find_all('script', string=True)
            for script in scripts:
                script_content = script.string or ''
                # Find realestate image URLs in JavaScript
                js_images = re.findall(r'["\'](https?://[^"\']*au\.reastatic\.net[^"\']*\.(?:jpg|jpeg|png|gif|webp)[^"\']*)["\']', script_content, re.I)
                for img_url in js_images:
                    image_urls.add(img_url)
        
        # Generic extraction as fallback
        # Find img tags
        for img in soup.find_all('img'):
            for attr in ['src', 'data-src', 'data-original']:
                src = img.get(attr)
                if src:
                    absolute_url = self.get_absolute_url(base_url, src)
                    image_urls.add(absolute_url)
        
        # Extract URLs from HTML content using regex
        url_patterns = [
            r'src=["\']([^"\']*\.(?:jpg|jpeg|png|gif|webp|bmp|tiff)[^"\']*)["\']',
            r'https?://[^"\'\s]*\.(?:jpg|jpeg|png|gif|webp|bmp|tiff)[^"\'\s]*',
        ]
        
        for pattern in url_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                if isinstance(match, str) and match.startswith(('http://', 'https://')):
                    image_urls.add(match)
        
        # Filter out small images and icons
        filtered_urls = set()
        for url in image_urls:
            if not any(skip in url.lower() for skip in ['icon', 'logo', 'button', '16x16', '32x32']):
                filtered_urls.add(url)
        
        return filtered_urls
    
    def download_image(self, url: str, save_path: Path) -> bool:
        """Download single image"""
        try:
            response = self.session.get(url, timeout=self.timeout, stream=True)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if not content_type.startswith('image/'):
                return False
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return True
            
        except Exception as e:
            print(f"Download failed {url}: {str(e)}")
            return False
    
    def sanitize_filename(self, filename: str) -> str:
        """Clean filename by removing illegal characters"""
        # Remove or replace illegal characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Limit filename length
        if len(filename) > 200:
            name, ext = os.path.splitext(filename)
            filename = name[:195] + ext
        return filename
    
    def download_from_website(self, url: str, output_dir: str = None) -> int:
        """
        Download all images from website
        
        Args:
            url: Website URL
            output_dir: Output directory, default is downloaded_images
            
        Returns:
            Number of successfully downloaded images
        """
        if output_dir is None:
            output_dir = 'downloaded_images'
            
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        print(f"Accessing website: {url}")
        
        try:
            # Try multiple times with increasing delays
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # Add random delay before requesting to avoid rate limiting
                    if attempt == 0:
                        delay = random.uniform(3, 8)
                    else:
                        delay = random.uniform(10, 20) * (attempt + 1)
                    
                    print(f"Attempt {attempt + 1}: Waiting {delay:.1f}s before request...")
                    time.sleep(delay)
                    
                    # Get webpage content
                    response = self.session.get(url, timeout=self.timeout)
                    response.raise_for_status()
                    break  # Success, exit retry loop
                    
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 429 and attempt < max_retries - 1:
                        print(f"Rate limited (429), retrying in longer delay...")
                        continue
                    else:
                        raise
                except Exception as e:
                    if attempt < max_retries - 1:
                        print(f"Request failed: {e}, retrying...")
                        continue
                    else:
                        raise
            
            # Extract image URLs
            image_urls = self.extract_images_from_html(response.text, url)
            print(f"Found {len(image_urls)} image links")
            
            if not image_urls:
                print("No image links found")
                return 0
            
            # Limit download count
            image_urls = list(image_urls)[:self.max_images]
            print(f"Will download first {len(image_urls)} images")
            print("-" * 50)
            
            success_count = 0
            for i, img_url in enumerate(image_urls, 1):
                try:
                    # Generate filename
                    parsed_url = urllib.parse.urlparse(img_url)
                    filename = os.path.basename(parsed_url.path)
                    
                    if not filename or not any(filename.lower().endswith(ext) for ext in self.image_extensions):
                        # If can't get filename from URL, generate one
                        ext = '.jpg'  # Default extension
                        content_type = ''
                        try:
                            head_response = self.session.head(img_url, timeout=5)
                            content_type = head_response.headers.get('content-type', '').lower()
                            if 'png' in content_type:
                                ext = '.png'
                            elif 'gif' in content_type:
                                ext = '.gif'
                            elif 'webp' in content_type:
                                ext = '.webp'
                        except:
                            pass
                        filename = f"image_{i:03d}{ext}"
                    
                    filename = self.sanitize_filename(filename)
                    save_path = output_path / filename
                    
                    # Avoid filename conflicts
                    counter = 1
                    original_save_path = save_path
                    while save_path.exists():
                        name, ext = os.path.splitext(original_save_path)
                        save_path = Path(f"{name}_{counter}{ext}")
                        counter += 1
                    
                    print(f"[{i}/{len(image_urls)}] Downloading: {img_url}")
                    
                    if self.download_image(img_url, save_path):
                        success_count += 1
                        print(f"✓ Saved as: {save_path.name}")
                    else:
                        print(f"✗ Download failed")
                    
                    # Add random delay between downloads to avoid being blocked
                    download_delay = random.uniform(1, 3)
                    time.sleep(download_delay)
                    
                except Exception as e:
                    print(f"✗ Processing failed {img_url}: {str(e)}")
                    continue
            
            print("-" * 50)
            print(f"Download completed: {success_count}/{len(image_urls)} images successfully downloaded")
            print(f"Saved to directory: {output_path.absolute()}")
            
            return success_count
            
        except Exception as e:
            print(f"Website access failed: {str(e)}")
            return 0

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Download images from website')
    parser.add_argument('url', help='Website URL')
    parser.add_argument('-o', '--output', default='downloaded_images', help='Output directory (default: downloaded_images)')
    parser.add_argument('-m', '--max', type=int, default=50, help='Maximum download count (default: 50)')
    parser.add_argument('-t', '--timeout', type=int, default=10, help='Timeout in seconds (default: 10)')
    
    args = parser.parse_args()
    
    downloader = WebsiteImageDownloader(max_images=args.max, timeout=args.timeout)
    success_count = downloader.download_from_website(args.url, args.output)
    
    if success_count == 0:
        exit(1)

if __name__ == '__main__':
    main()
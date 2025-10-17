#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Image Processing Tool - Streamlit Web Application
Provides three main features:
1. Download images from website links and convert to WebP
2. Upload image files and convert to WebP (with optional cropping)
3. Batch process local folders
"""

import streamlit as st
import tempfile
import shutil
from pathlib import Path
import zipfile
import io
from PIL import Image
import os
import time
import re
import hashlib
import hmac

# Import our functionality modules
from image_converter import ImageConverter

# Security Configuration
DEFAULT_PASSWORD = "Brisbane2025"

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return hmac.compare_digest(hash_password(password), hashed)

def check_authentication():
    """Check if user is authenticated"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("🔐 Secure Image Converter")
        st.warning("Please enter the password to access the application")

        password = st.text_input("Password:", type="password", key="login_password")

        if st.button("Login", type="primary"):
            hashed_password = hash_password(DEFAULT_PASSWORD)
            if verify_password(password, hashed_password):
                st.session_state.authenticated = True
                st.success("Authentication successful! Redirecting...")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid password. Access denied.")
                time.sleep(2)

        st.markdown("---")
        st.info("🛡️ This application is password protected for security reasons.")
        st.stop()

    # Add logout button in sidebar if authenticated
    with st.sidebar:
        if st.button("🚪 Logout", type="secondary"):
            st.session_state.authenticated = False
            st.rerun()

def setup_page():
    """Setup page configuration"""
    st.set_page_config(
        page_title="Image Converter Tool",
        page_icon="🖼️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🖼️ Image Converter Tool")
    st.markdown("---")

def create_download_zip(files_dir: Path, zip_name: str = "converted_images.zip"):
    """Create ZIP file for download"""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for file_path in files_dir.glob("*.webp"):
            zip_file.write(file_path, file_path.name)
    zip_buffer.seek(0)
    return zip_buffer

def sanitize_filename(filename: str) -> str:
    """Convert filename to lowercase with dashes, SEO-friendly"""
    # Remove file extension
    name_without_ext = os.path.splitext(filename)[0]

    # Convert to lowercase
    name = name_without_ext.lower()

    # Replace spaces and underscores with dashes
    name = re.sub(r'[\s_]+', '-', name)

    # Remove special characters except dashes and alphanumeric
    name = re.sub(r'[^a-z0-9\-]', '', name)

    # Remove multiple consecutive dashes
    name = re.sub(r'-+', '-', name)

    # Remove leading/trailing dashes
    name = name.strip('-')

    # If name is empty, use 'image'
    if not name:
        name = 'image'

    return name

def validate_uploaded_file(uploaded_file) -> bool:
    """Validate uploaded file for security"""
    # Check file size (limit to 50MB)
    if uploaded_file.size > 50 * 1024 * 1024:
        return False

    # Check file extension
    allowed_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif'}
    file_ext = os.path.splitext(uploaded_file.name)[1].lower()
    if file_ext not in allowed_extensions:
        return False

    return True


def feature_file_upload():
    """Feature 2: File upload and conversion"""
    st.header("📁 Upload Image Files for Conversion")

    # Use dynamic key for file uploader to enable clearing
    uploader_key = st.session_state.get('file_uploader_key', 0)

    uploaded_files = st.file_uploader(
        "Select image files",
        type=['png', 'jpg', 'jpeg', 'bmp', 'tiff', 'gif'],
        accept_multiple_files=True,
        key=f"file_uploader_{uploader_key}"
    )

    # Show clear button only when files are uploaded, positioned right after uploader
    if uploaded_files:
        if st.button("🗑️ Clear All", type="secondary", help="Clear all uploaded images"):
            # Clear the file uploader by resetting session state
            if 'file_uploader_key' in st.session_state:
                st.session_state.file_uploader_key += 1
            else:
                st.session_state.file_uploader_key = 0
            st.rerun()
    
    if uploaded_files:
        # Validate uploaded files
        valid_files = []
        invalid_files = []

        for uploaded_file in uploaded_files:
            if validate_uploaded_file(uploaded_file):
                valid_files.append(uploaded_file)
            else:
                invalid_files.append(uploaded_file.name)

        if invalid_files:
            st.error(f"Invalid files (too large or unsupported format): {', '.join(invalid_files)}")

        if not valid_files:
            st.stop()

        uploaded_files = valid_files
        st.info(f"Selected {len(uploaded_files)} valid files")
        
        # Rename settings
        st.subheader("🏷️ Rename Settings")
        col1, col2 = st.columns([2, 1])
        with col1:
            rename_base = st.text_input("Base name for renamed files (optional):", placeholder="product-image")
        with col2:
            enable_rename = st.checkbox("Enable batch rename", value=False)
        
        # Conversion settings
        st.subheader("⚙️ Conversion Settings")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            quality = st.slider("WebP Quality ", 0, 100, 75)
        with col2:
            preserve_transparency = st.checkbox("Preserve transparency ", value=True)
        with col3:
            crop_borders = st.checkbox("Auto crop borders ", value=False)
        with col4:
            scale_factor = st.selectbox("Scale ratio ", [None, 0.5, 0.7, 0.8, 0.9], index=0)
        
        if st.button("Convert to WebP", type="primary"):
            # Create temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                input_dir = temp_path / "input"
                output_dir = temp_path / "output"
                input_dir.mkdir()
                output_dir.mkdir()
                
                # Save uploaded files with optional renaming
                if enable_rename and rename_base.strip():
                    sanitized_base = sanitize_filename(rename_base)

                    # Save files temporarily to get their creation time
                    temp_files_info = []
                    for uploaded_file in uploaded_files:
                        temp_path = input_dir / f"temp_{uploaded_file.name}"
                        with open(temp_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())

                        # Get file creation/modification time
                        file_stat = temp_path.stat()
                        creation_time = file_stat.st_ctime

                        temp_files_info.append({
                            'path': temp_path,
                            'original_name': uploaded_file.name,
                            'creation_time': creation_time,
                            'extension': Path(uploaded_file.name).suffix
                        })

                    # Sort by creation time (oldest to newest)
                    sorted_files_info = sorted(temp_files_info, key=lambda x: x['creation_time'])

                    # Rename files with sequential numbers
                    for idx, file_info in enumerate(sorted_files_info, start=1):
                        new_filename = f"{sanitized_base}-{idx}{file_info['extension']}"
                        new_path = input_dir / new_filename

                        # Rename the temp file to the final name
                        file_info['path'].rename(new_path)
                else:
                    # Save with original names
                    for uploaded_file in uploaded_files:
                        file_path = input_dir / uploaded_file.name
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                
                # Convert images
                with st.spinner("Converting images..."):
                    converter = ImageConverter(
                        quality=quality,
                        preserve_transparency=preserve_transparency,
                        crop_borders=crop_borders,
                        scale_factor=scale_factor
                    )
                    success, total = converter.batch_convert(str(input_dir), str(output_dir))
                
                if success > 0:
                    st.success(f"Successfully converted {success}/{total} images")
                    
                    # Show rename preview if enabled
                    if enable_rename and rename_base.strip():
                        st.info("✅ Files have been renamed with SEO-friendly names")
                    
                    # Provide ZIP download parallel to conversion results
                    zip_buffer = create_download_zip(output_dir)
                    st.download_button(
                        label="📥 Download Converted Images (ZIP)",
                        data=zip_buffer.getvalue(),
                        file_name="uploaded_images_converted.zip",
                        mime="application/zip"
                    )
                    
                    # Display conversion results
                    webp_files = list(output_dir.glob("*.webp"))
                    if webp_files:
                        st.subheader("Conversion Results:")
                        
                        # Create columns to display images
                        cols = st.columns(min(3, len(webp_files)))
                        for i, webp_file in enumerate(webp_files):
                            with cols[i % 3]:
                                st.write(f"**{webp_file.name}**")
                                converted_image = Image.open(webp_file)
                                st.image(converted_image, use_column_width=True)
                else:
                    st.error("Conversion failed. Please check if the image files are valid")

def feature_batch_process():
    """Feature 3: Batch processing instructions (local folders)"""
    st.header("📂 Batch Process Local Folders")
    
    st.info("""
    💡 **Use command-line tools for batch processing:**
    
    Due to browser security limitations, local folders cannot be directly accessed. Please use the following command-line tools:
    """)
    
    st.code("""
# Basic usage
python image_converter.py /path/to/your/images

# Custom output directory and quality
python image_converter.py /path/to/your/images -o /path/to/output -q 80

# Enable auto cropping and scaling
python image_converter.py /path/to/your/images -c -s 0.8

# Convert to white background
python image_converter.py /path/to/your/images -w
    """, language="bash")
    
    st.markdown("""
    **Parameter descriptions:**
    - `-o, --output`: Output directory path
    - `-q, --quality`: WebP quality (0-100)
    - `-w, --white-bg`: Convert transparent background to white
    - `-c, --crop`: Auto crop borders
    - `-s, --scale`: Scale ratio (e.g., 0.8)
    """)
    
    # Display supported formats
    st.subheader("Supported Image Formats")
    formats = ["JPG/JPEG", "PNG", "BMP", "TIFF/TIF", "GIF"]
    cols = st.columns(len(formats))
    for i, fmt in enumerate(formats):
        with cols[i]:
            st.success(fmt)

def main():
    """Main function"""
    setup_page()

    # Check authentication first
    check_authentication()
    
    # Sidebar feature selection
    st.sidebar.title("Feature Selection")
    feature = st.sidebar.selectbox(
        "Choose feature:",
        ["📁 File Upload Conversion", "📂 Batch Processing Instructions"]
    )
    
    # Sidebar information
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    ### 📋 Feature Description
    
    **📁 File Upload Conversion**  
    - Upload local image files
    - Batch rename with SEO-friendly names
    - Convert to WebP format with cropping
    - Real-time preview of conversion results
    
    **📂 Batch Processing**
    - Process large amounts of local images
    - Use command-line tools
    - Support more advanced options
    """)
    
    # Display corresponding feature based on selection
    if feature == "📁 File Upload Conversion":
        feature_file_upload()
    else:
        feature_batch_process()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "🖼️ Image Converter Tool | Support Multiple Formats to WebP | Auto Optimization and Compression"
        "</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
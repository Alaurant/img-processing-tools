# Image Processing Tool

A comprehensive Python toolkit for batch image conversion and processing, featuring both command-line tools and a modern web interface.

## Features

### Command Line Tools
- **Batch Image Converter**: Convert images to WebP format with customizable quality
- **Website Image Downloader**: Download all images from websites automatically
- Support for multiple image formats: JPG, JPEG, PNG, BMP, TIFF, GIF
- Preserve or convert transparent backgrounds
- Automatic border cropping detection
- Image scaling with high-quality resampling
- Detailed progress reporting

### Web Interface (Streamlit)
- **🌐 Website Image Download**: Extract and download images from websites, then convert to WebP
- **📁 File Upload Conversion**: Upload local files for conversion with real-time preview
- **📂 Batch Processing Guide**: Instructions for processing large local image collections

## Installation

### Dependencies

```bash
pip install -r requirements.txt
```

Or install individually:

```bash
pip install Pillow requests beautifulsoup4 streamlit
```

## Usage

### 1. Web Interface (Recommended for beginners)

Launch the Streamlit web application:

```bash
streamlit run streamlit_app.py
```

This provides an intuitive interface with three main features:
- Download images from websites and convert them
- Upload files directly for conversion  
- View batch processing instructions

### 2. Command Line - Batch Image Conversion

#### Basic Usage

```bash
python image_converter.py <input_directory>
```

Example:
```bash
python image_converter.py ./images
```

This converts all images in `./images` directory to WebP format and saves them to `./images/webp_output`.

#### Advanced Options

**Specify output directory:**
```bash
python image_converter.py <input_directory> -o <output_directory>
```

**Custom quality:**
```bash
python image_converter.py ./images -q 80
```

**Convert transparent background to white:**
```bash
python image_converter.py ./images -w
```

**Auto crop borders:**
```bash
python image_converter.py ./images -c
```

**Scale images:**
```bash
python image_converter.py ./images -s 0.8
```

**Combined example:**
```bash
python image_converter.py ./my_photos -o ./webp_photos -q 85 -c -s 0.9
```

### 3. Command Line - Website Image Download

```bash
python website_downloader.py <website_url>
```

**With options:**
```bash
python website_downloader.py https://example.com -o ./downloaded_images -m 30 -t 15
```

## Command Line Parameters

### Image Converter (`image_converter.py`)

- `input_dir`: Input directory path (required)
- `-o, --output`: Output directory path (optional)
- `-q, --quality`: WebP quality 0-100 (default: 75)
- `-w, --white-bg`: Convert transparent background to white (default: preserve transparency)
- `-c, --crop`: Auto crop borders (detect and remove solid color borders)
- `-s, --scale`: Scale ratio (e.g., 0.5 means half size)

### Website Downloader (`website_downloader.py`)

- `url`: Website URL (required)
- `-o, --output`: Output directory (default: downloaded_images)
- `-m, --max`: Maximum download count (default: 50)
- `-t, --timeout`: Timeout in seconds (default: 10)

## Supported Image Formats

**Input formats:**
- JPG/JPEG
- PNG  
- BMP
- TIFF/TIF
- GIF

**Output format:**
- WebP (optimized for web use with excellent compression)

## Key Features Explained

### Transparency Handling
- **Default**: Preserves transparent backgrounds (larger file size, better quality)
- **With `-w` flag**: Converts transparency to white background (smaller file size)

### Auto Border Cropping
- Detects solid color borders automatically
- Removes unnecessary padding around images
- Uses intelligent sampling to avoid false positives

### Image Scaling
- High-quality Lanczos resampling
- Maintains aspect ratio
- Scale factor between 0 and 1 (e.g., 0.8 = 80% of original size)

### Website Image Download
- Extracts images from `<img>` tags and CSS backgrounds
- Handles lazy-loaded images (`data-src` attributes)
- Automatic filename generation with conflict resolution
- Respectful downloading with delays between requests

## Sample Output

```
Found 5 image files
Output directory: /path/to/images/webp_output
WebP quality: 75%
Preserve transparency: Yes
Auto crop borders: No
--------------------------------------------------
✓ Conversion successful: photo1.jpg -> photo1.webp
✓ Conversion successful: photo2.png -> photo2.webp
  Border cropping: (1200, 800) -> (1100, 750)
✓ Conversion successful: photo3.gif -> photo3.webp
✗ Conversion failed: corrupted.jpg - cannot identify image file
  Scaling: 1920x1080 -> 1536x864 (ratio: 0.8)
✓ Conversion successful: photo4.tiff -> photo4.webp
--------------------------------------------------
Conversion completed: 4/5 files successfully converted
```

## File Structure

```
img/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── image_converter.py        # Main batch converter
├── website_downloader.py     # Website image downloader
├── streamlit_app.py         # Web interface
├── simple_crop.py           # Legacy cropping tool
├── demo_transparency.py     # Transparency handling demo
└── example.py              # Basic usage example
```

## Notes

1. **Performance**: WebP generally provides 25-50% better compression than JPEG with similar quality
2. **Compatibility**: WebP is supported by all modern browsers and most image viewers
3. **Quality**: Quality setting of 75-85 is recommended for most use cases
4. **Transparency**: Use `-w` flag only if you need smaller files and don't need transparency
5. **Border Cropping**: Works best with images that have solid-colored borders
6. **Website Download**: Respects robots.txt and includes delays to avoid overwhelming servers

## Troubleshooting

**"No images found"**: Check that your input directory contains supported image formats

**"Conversion failed"**: Usually indicates a corrupted image file - check the specific error message

**"Website access failed"**: The website may be blocking automated requests or may be temporarily unavailable

**Memory issues**: For very large images, consider using the scale option to reduce memory usage

## License

This project is open source. Feel free to modify and distribute according to your needs.
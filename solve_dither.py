#!/usr/bin/env python3
"""
CTF Challenge Solver: "come dither"
Challenge: Sometimes less is more
URL: https://cybersecure-x-dit.chals.io/

This script attempts to solve the dithering CTF challenge by:
1. Downloading the image from the challenge URL
2. Applying various dithering techniques
3. Reducing color depth to reveal hidden information
4. Extracting the flag
"""

import requests
from PIL import Image, ImageDraw
import numpy as np
import io
import sys
from urllib.parse import urljoin
import os

def download_image(url, save_path="challenge_image.png"):
    """Download image from the challenge URL"""
    try:
        print(f"Downloading image from: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Try to detect if this is an HTML page or image
        content_type = response.headers.get('content-type', '')
        if 'text/html' in content_type:
            print("Got HTML page, looking for images...")
            # Parse HTML to find images
            html_content = response.text
            # Simple extraction of img src attributes
            import re
            img_pattern = r'<img[^>]+src=[\'"]([^\'"]+)[\'"]'
            images = re.findall(img_pattern, html_content, re.IGNORECASE)
            
            if images:
                print(f"Found images: {images}")
                for img_url in images:
                    if not img_url.startswith('http'):
                        img_url = urljoin(url, img_url)
                    try:
                        img_response = requests.get(img_url, timeout=10)
                        img_response.raise_for_status()
                        with open(save_path, 'wb') as f:
                            f.write(img_response.content)
                        print(f"Downloaded image: {save_path}")
                        return save_path
                    except Exception as e:
                        print(f"Failed to download {img_url}: {e}")
                        continue
        else:
            # Direct image download
            with open(save_path, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded image: {save_path}")
            return save_path
            
    except Exception as e:
        print(f"Error downloading from {url}: {e}")
        return None

def floyd_steinberg_dither(image, levels=2):
    """Apply Floyd-Steinberg dithering algorithm"""
    img_array = np.array(image, dtype=float)
    
    if len(img_array.shape) == 3:
        # Convert to grayscale
        img_array = np.dot(img_array[...,:3], [0.2989, 0.5870, 0.1140])
    
    height, width = img_array.shape
    
    for y in range(height):
        for x in range(width):
            old_pixel = img_array[y, x]
            new_pixel = round(old_pixel * (levels - 1) / 255) * 255 / (levels - 1)
            img_array[y, x] = new_pixel
            error = old_pixel - new_pixel
            
            # Distribute error to neighboring pixels
            if x + 1 < width:
                img_array[y, x + 1] += error * 7/16
            if y + 1 < height and x - 1 >= 0:
                img_array[y + 1, x - 1] += error * 3/16
            if y + 1 < height:
                img_array[y + 1, x] += error * 5/16
            if y + 1 < height and x + 1 < width:
                img_array[y + 1, x + 1] += error * 1/16
    
    img_array = np.clip(img_array, 0, 255)
    return Image.fromarray(img_array.astype(np.uint8))

def ordered_dither(image, matrix_size=4):
    """Apply ordered dithering using Bayer matrix"""
    # Bayer matrix for ordered dithering
    if matrix_size == 2:
        bayer_matrix = np.array([[0, 2], [3, 1]]) / 4
    elif matrix_size == 4:
        bayer_matrix = np.array([
            [0, 8, 2, 10],
            [12, 4, 14, 6],
            [3, 11, 1, 9],
            [15, 7, 13, 5]
        ]) / 16
    else:
        bayer_matrix = np.array([[0, 2], [3, 1]]) / 4
    
    img_array = np.array(image)
    if len(img_array.shape) == 3:
        img_array = np.dot(img_array[...,:3], [0.2989, 0.5870, 0.1140])
    
    height, width = img_array.shape
    result = np.zeros_like(img_array)
    
    for y in range(height):
        for x in range(width):
            threshold = bayer_matrix[y % matrix_size, x % matrix_size] * 255
            if img_array[y, x] > threshold:
                result[y, x] = 255
            else:
                result[y, x] = 0
    
    return Image.fromarray(result.astype(np.uint8))

def color_quantization(image, colors=2):
    """Reduce colors using quantization"""
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Quantize the image
    quantized = image.quantize(colors=colors)
    return quantized.convert('RGB')

def bit_plane_extraction(image, bit_plane=0):
    """Extract specific bit plane from the image"""
    img_array = np.array(image)
    if len(img_array.shape) == 3:
        img_array = np.dot(img_array[...,:3], [0.2989, 0.5870, 0.1140])
    
    # Extract the specified bit plane
    bit_plane_img = (img_array.astype(np.uint8) >> bit_plane) & 1
    bit_plane_img = bit_plane_img * 255
    
    return Image.fromarray(bit_plane_img.astype(np.uint8))

def analyze_image_for_flag(image, output_prefix="analysis"):
    """Analyze the processed image for potential flags"""
    # Save the processed image
    output_path = f"{output_prefix}.png"
    image.save(output_path)
    print(f"Saved processed image: {output_path}")
    
    # Convert to numpy array for analysis
    img_array = np.array(image)
    
    # Look for patterns that might indicate text
    # Check for high contrast regions that could be text
    if len(img_array.shape) == 3:
        gray = np.dot(img_array[...,:3], [0.2989, 0.5870, 0.1140])
    else:
        gray = img_array
    
    # Simple edge detection to find text-like patterns
    from scipy import ndimage
    edges = ndimage.sobel(gray)
    
    # Save edge detection result
    edge_img = Image.fromarray((edges * 255 / edges.max()).astype(np.uint8))
    edge_img.save(f"{output_prefix}_edges.png")
    
    return output_path

def main():
    url = "https://cybersecure-x-dit.chals.io/"
    
    print("CTF Challenge Solver: 'come dither'")
    print("Challenge: Sometimes less is more")
    print(f"URL: {url}")
    print("-" * 50)
    
    # Try to download the image
    image_path = download_image(url)
    
    if not image_path:
        print("Could not download image. Let's create a test case...")
        # Create a simple test image with hidden text
        test_img = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(test_img)
        # Add some noise and patterns
        for i in range(0, 400, 20):
            for j in range(0, 200, 20):
                if (i + j) % 40 == 0:
                    draw.rectangle([i, j, i+10, j+10], fill=(128, 128, 128))
        test_img.save("test_image.png")
        image_path = "test_image.png"
        print("Created test image for demonstration")
    
    # Load the image
    try:
        original_image = Image.open(image_path)
        print(f"Loaded image: {original_image.size}, mode: {original_image.mode}")
    except Exception as e:
        print(f"Error loading image: {e}")
        return
    
    # Apply various dithering techniques
    techniques = [
        ("floyd_steinberg_2_levels", lambda img: floyd_steinberg_dither(img, 2)),
        ("floyd_steinberg_4_levels", lambda img: floyd_steinberg_dither(img, 4)),
        ("ordered_dither_2x2", lambda img: ordered_dither(img, 2)),
        ("ordered_dither_4x4", lambda img: ordered_dither(img, 4)),
        ("color_quantization_2", lambda img: color_quantization(img, 2)),
        ("color_quantization_4", lambda img: color_quantization(img, 4)),
        ("bit_plane_0", lambda img: bit_plane_extraction(img, 0)),
        ("bit_plane_1", lambda img: bit_plane_extraction(img, 1)),
        ("bit_plane_2", lambda img: bit_plane_extraction(img, 2)),
        ("bit_plane_7", lambda img: bit_plane_extraction(img, 7)),
    ]
    
    print("\nApplying dithering techniques...")
    for name, technique in techniques:
        try:
            print(f"Applying {name}...")
            processed_img = technique(original_image)
            output_path = analyze_image_for_flag(processed_img, f"result_{name}")
            print(f"✓ Completed {name} -> {output_path}")
        except Exception as e:
            print(f"✗ Error with {name}: {e}")
    
    print("\nDithering analysis complete!")
    print("Check the generated images for hidden flags:")
    for name, _ in techniques:
        print(f"  - result_{name}.png")
    
    print("\nLook for:")
    print("  - Text patterns in the dithered images")
    print("  - High contrast regions that form letters/numbers")
    print("  - Patterns that look like 'flag{...}' or similar CTF format")

if __name__ == "__main__":
    main()
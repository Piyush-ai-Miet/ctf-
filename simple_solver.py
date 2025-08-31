#!/usr/bin/env python3
"""
Simple CTF Dithering Challenge Solver
Usage: python3 simple_solver.py <image_url_or_path>
"""

import sys
import requests
from PIL import Image
import numpy as np

def download_image(url):
    """Download image from URL"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Check if it's HTML
        if 'text/html' in response.headers.get('content-type', ''):
            print("Got HTML page. Looking for images...")
            import re
            from urllib.parse import urljoin
            
            img_pattern = r'<img[^>]+src=[\'"]([^\'"]+)[\'"]'
            images = re.findall(img_pattern, response.text, re.IGNORECASE)
            
            if images:
                img_url = images[0]
                if not img_url.startswith('http'):
                    img_url = urljoin(url, img_url)
                
                img_response = requests.get(img_url, timeout=10)
                img_response.raise_for_status()
                
                with open('challenge_image.png', 'wb') as f:
                    f.write(img_response.content)
                return 'challenge_image.png'
        else:
            with open('challenge_image.png', 'wb') as f:
                f.write(response.content)
            return 'challenge_image.png'
            
    except Exception as e:
        print(f"Error downloading: {e}")
        return None

def apply_dithering_techniques(image_path):
    """Apply key dithering techniques to reveal hidden content"""
    
    try:
        img = Image.open(image_path)
        print(f"Loaded: {img.size}, mode: {img.mode}")
        
        # Convert to grayscale if needed
        if img.mode != 'L':
            gray = img.convert('L')
        else:
            gray = img
        
        # Technique 1: Simple threshold (most common)
        threshold_values = [64, 96, 128, 160, 192]
        for thresh in threshold_values:
            binary = gray.point(lambda x: 0 if x < thresh else 255, '1')
            binary.save(f'result_threshold_{thresh}.png')
            print(f"✓ Threshold {thresh} -> result_threshold_{thresh}.png")
        
        # Technique 2: Floyd-Steinberg dithering
        img_array = np.array(gray, dtype=float)
        height, width = img_array.shape
        
        for y in range(height - 1):
            for x in range(1, width - 1):
                old_pixel = img_array[y, x]
                new_pixel = 255 if old_pixel > 127 else 0
                img_array[y, x] = new_pixel
                error = old_pixel - new_pixel
                
                img_array[y, x + 1] += error * 7/16
                img_array[y + 1, x - 1] += error * 3/16
                img_array[y + 1, x] += error * 5/16
                img_array[y + 1, x + 1] += error * 1/16
        
        result = Image.fromarray(np.clip(img_array, 0, 255).astype(np.uint8))
        result.save('result_floyd_steinberg.png')
        print("✓ Floyd-Steinberg dithering -> result_floyd_steinberg.png")
        
        # Technique 3: Bit plane extraction
        img_array = np.array(gray)
        for bit in [0, 1, 2, 7]:
            bit_plane = (img_array >> bit) & 1
            bit_plane = bit_plane * 255
            bit_img = Image.fromarray(bit_plane.astype(np.uint8))
            bit_img.save(f'result_bitplane_{bit}.png')
            print(f"✓ Bit plane {bit} -> result_bitplane_{bit}.png")
        
        # Technique 4: Color quantization (if original was color)
        if img.mode == 'RGB':
            for colors in [2, 4, 8]:
                quantized = img.quantize(colors=colors)
                quantized.save(f'result_quantized_{colors}.png')
                print(f"✓ Quantized {colors} colors -> result_quantized_{colors}.png")
        
        print("\n🔍 Check all generated images for hidden text/flags!")
        print("Look for patterns that form readable text or flag format.")
        
    except Exception as e:
        print(f"Error processing image: {e}")

def main():
    print("CTF Dithering Challenge Solver")
    print("=" * 40)
    
    if len(sys.argv) != 2:
        print("Usage: python3 simple_solver.py <image_url_or_path>")
        print("Example: python3 simple_solver.py https://cybersecure-x-dit.chals.io/")
        return
    
    input_path = sys.argv[1]
    
    if input_path.startswith('http'):
        print(f"Downloading from: {input_path}")
        image_path = download_image(input_path)
        if not image_path:
            print("Failed to download image")
            return
    else:
        image_path = input_path
        print(f"Using local file: {image_path}")
    
    apply_dithering_techniques(image_path)

if __name__ == "__main__":
    main()
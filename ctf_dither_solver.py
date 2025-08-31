#!/usr/bin/env python3
"""
CTF Solution: "come dither" Challenge
Points: 250
Hint: Sometimes less is more
URL: https://cybersecure-x-dit.chals.io/

This script provides a complete solution for dithering-based CTF challenges.
It downloads the image and applies various dithering techniques to reveal hidden flags.
"""

import requests
from PIL import Image
import numpy as np
import sys
import os
from urllib.parse import urljoin
import re

class DitherCTFSolver:
    def __init__(self):
        self.output_dir = "results"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def download_challenge_image(self, url):
        """Download image from the CTF challenge URL"""
        print(f"🌐 Downloading from: {url}")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '').lower()
            
            if 'text/html' in content_type:
                print("📄 Got HTML page, extracting images...")
                return self._extract_images_from_html(response.text, url)
            elif any(img_type in content_type for img_type in ['image/', 'application/octet-stream']):
                print("🖼️  Direct image download")
                image_path = os.path.join(self.output_dir, 'challenge_image.png')
                with open(image_path, 'wb') as f:
                    f.write(response.content)
                return image_path
            else:
                print(f"❌ Unexpected content type: {content_type}")
                return None
                
        except Exception as e:
            print(f"❌ Download failed: {e}")
            return None
    
    def _extract_images_from_html(self, html_content, base_url):
        """Extract image URLs from HTML and download them"""
        # Look for img tags
        img_patterns = [
            r'<img[^>]+src=[\'"]([^\'"]+)[\'"]',
            r'src=[\'"]([^\'"]*\.(?:png|jpg|jpeg|gif|bmp|webp))[\'"]'
        ]
        
        for pattern in img_patterns:
            images = re.findall(pattern, html_content, re.IGNORECASE)
            
            for img_url in images:
                if not img_url.startswith('http'):
                    img_url = urljoin(base_url, img_url)
                
                try:
                    print(f"📥 Downloading image: {img_url}")
                    img_response = requests.get(img_url, timeout=10)
                    img_response.raise_for_status()
                    
                    image_path = os.path.join(self.output_dir, 'challenge_image.png')
                    with open(image_path, 'wb') as f:
                        f.write(img_response.content)
                    
                    print(f"✅ Downloaded: {image_path}")
                    return image_path
                    
                except Exception as e:
                    print(f"❌ Failed to download {img_url}: {e}")
                    continue
        
        print("❌ No images found in HTML")
        return None
    
    def apply_threshold_dithering(self, image, output_prefix):
        """Apply simple threshold-based dithering"""
        results = []
        
        # Convert to grayscale if needed
        if image.mode != 'L':
            gray = image.convert('L')
        else:
            gray = image
        
        # Try different threshold values
        thresholds = [32, 64, 96, 128, 160, 192, 224]
        
        for thresh in thresholds:
            binary = gray.point(lambda x: 0 if x < thresh else 255, '1')
            output_path = os.path.join(self.output_dir, f"{output_prefix}_threshold_{thresh}.png")
            binary.save(output_path)
            results.append(output_path)
            print(f"  ✓ Threshold {thresh}")
        
        return results
    
    def apply_floyd_steinberg_dithering(self, image, output_prefix):
        """Apply Floyd-Steinberg error diffusion dithering"""
        # Convert to grayscale
        if image.mode != 'L':
            gray = image.convert('L')
        else:
            gray = image
        
        img_array = np.array(gray, dtype=float)
        height, width = img_array.shape
        
        # Apply Floyd-Steinberg dithering
        for y in range(height - 1):
            for x in range(1, width - 1):
                old_pixel = img_array[y, x]
                new_pixel = 255 if old_pixel > 127 else 0
                img_array[y, x] = new_pixel
                error = old_pixel - new_pixel
                
                # Distribute error to neighboring pixels
                img_array[y, x + 1] += error * 7/16
                img_array[y + 1, x - 1] += error * 3/16
                img_array[y + 1, x] += error * 5/16
                img_array[y + 1, x + 1] += error * 1/16
        
        result = Image.fromarray(np.clip(img_array, 0, 255).astype(np.uint8))
        output_path = os.path.join(self.output_dir, f"{output_prefix}_floyd_steinberg.png")
        result.save(output_path)
        print(f"  ✓ Floyd-Steinberg dithering")
        
        return [output_path]
    
    def extract_bit_planes(self, image, output_prefix):
        """Extract individual bit planes from the image"""
        results = []
        
        # Convert to grayscale
        if image.mode != 'L':
            gray = image.convert('L')
        else:
            gray = image
        
        img_array = np.array(gray)
        
        # Extract each bit plane
        for bit in range(8):
            bit_plane = (img_array >> bit) & 1
            bit_plane = bit_plane * 255
            bit_img = Image.fromarray(bit_plane.astype(np.uint8))
            output_path = os.path.join(self.output_dir, f"{output_prefix}_bitplane_{bit}.png")
            bit_img.save(output_path)
            results.append(output_path)
            print(f"  ✓ Bit plane {bit}")
        
        return results
    
    def apply_color_quantization(self, image, output_prefix):
        """Apply color quantization (palette reduction)"""
        results = []
        
        if image.mode != 'RGB':
            rgb_image = image.convert('RGB')
        else:
            rgb_image = image
        
        # Try different numbers of colors
        color_counts = [2, 4, 8, 16]
        
        for colors in color_counts:
            quantized = rgb_image.quantize(colors=colors)
            rgb_quantized = quantized.convert('RGB')
            output_path = os.path.join(self.output_dir, f"{output_prefix}_quantized_{colors}.png")
            rgb_quantized.save(output_path)
            results.append(output_path)
            print(f"  ✓ Quantized to {colors} colors")
        
        return results
    
    def solve_challenge(self, image_path_or_url):
        """Main solver function"""
        print("🚀 CTF Dithering Challenge Solver")
        print("=" * 50)
        
        # Download or load image
        if image_path_or_url.startswith('http'):
            image_path = self.download_challenge_image(image_path_or_url)
            if not image_path:
                print("❌ Failed to download image")
                return
        else:
            image_path = image_path_or_url
            print(f"📂 Using local file: {image_path}")
        
        # Load the image
        try:
            image = Image.open(image_path)
            print(f"📊 Image info: {image.size}, mode: {image.mode}")
        except Exception as e:
            print(f"❌ Error loading image: {e}")
            return
        
        # Apply different dithering techniques
        output_prefix = "result"
        all_results = []
        
        print("\n🎨 Applying dithering techniques...")
        
        print("1️⃣ Threshold dithering...")
        all_results.extend(self.apply_threshold_dithering(image, output_prefix))
        
        print("2️⃣ Floyd-Steinberg dithering...")
        all_results.extend(self.apply_floyd_steinberg_dithering(image, output_prefix))
        
        print("3️⃣ Bit plane extraction...")
        all_results.extend(self.extract_bit_planes(image, output_prefix))
        
        if image.mode in ['RGB', 'RGBA']:
            print("4️⃣ Color quantization...")
            all_results.extend(self.apply_color_quantization(image, output_prefix))
        
        # Summary
        print(f"\n🎯 Analysis complete! Generated {len(all_results)} images.")
        print(f"📁 Results saved in: {self.output_dir}/")
        print("\n🔍 Look for:")
        print("   • Text patterns in black and white images")
        print("   • Flag format: flag{...} or similar")
        print("   • High contrast regions forming letters")
        print("   • Readable text that wasn't visible before")
        
        print(f"\n📋 Generated files:")
        for result in all_results:
            print(f"   • {os.path.basename(result)}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 ctf_dither_solver.py <image_url_or_path>")
        print("Example: python3 ctf_dither_solver.py https://cybersecure-x-dit.chals.io/")
        print("Example: python3 ctf_dither_solver.py challenge_image.png")
        return
    
    solver = DitherCTFSolver()
    solver.solve_challenge(sys.argv[1])

if __name__ == "__main__":
    main()
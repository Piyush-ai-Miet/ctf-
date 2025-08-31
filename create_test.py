#!/usr/bin/env python3
"""
Create a test image that demonstrates the dithering technique
This simulates what the actual CTF challenge might look like
"""

from PIL import Image, ImageDraw, ImageFont
import numpy as np
import random

def create_hidden_flag_image():
    """Create an image with a hidden flag that's revealed through dithering"""
    
    # Create base image
    width, height = 800, 400
    img = Image.new('RGB', (width, height), color=(128, 128, 128))
    draw = ImageDraw.Draw(img)
    
    # Add random noise pattern
    for _ in range(1000):
        x = random.randint(0, width-1)
        y = random.randint(0, height-1)
        color = random.randint(100, 155)
        draw.point((x, y), fill=(color, color, color))
    
    # Create hidden text - this will be revealed through dithering
    hidden_text = "flag{d1th3r_r3v34ls_s3cr3ts}"
    
    # Create a temporary image for the text
    text_img = Image.new('L', (width, height), 0)
    text_draw = ImageDraw.Draw(text_img)
    
    try:
        # Try to use a larger font
        font = ImageFont.truetype("/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf", 40)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    # Get text size and center it
    bbox = text_draw.textbbox((0, 0), hidden_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    text_x = (width - text_width) // 2
    text_y = (height - text_height) // 2
    
    # Draw the text in white
    text_draw.text((text_x, text_y), hidden_text, fill=255, font=font)
    
    # Convert text image to array
    text_array = np.array(text_img)
    img_array = np.array(img)
    
    # Embed the text subtly - it will only be visible after dithering
    # Add the text as slight variations in the lower bit planes
    for y in range(height):
        for x in range(width):
            if text_array[y, x] > 0:  # Where text exists
                # Modify the image slightly - this will be revealed by dithering
                for c in range(3):  # RGB channels
                    current = img_array[y, x, c]
                    # Add subtle variation that becomes visible after thresholding
                    if current < 128:
                        img_array[y, x, c] = max(0, current - 30)
                    else:
                        img_array[y, x, c] = min(255, current + 30)
    
    # Create final image
    result_img = Image.fromarray(img_array.astype(np.uint8))
    
    # Add more noise to make it harder to see
    draw = ImageDraw.Draw(result_img)
    for _ in range(2000):
        x = random.randint(0, width-1)
        y = random.randint(0, height-1)
        color = random.randint(90, 165)
        draw.point((x, y), fill=(color, color, color))
    
    return result_img

def main():
    print("Creating test dithering challenge image...")
    
    # Create the challenge image
    challenge_img = create_hidden_flag_image()
    challenge_img.save('test_challenge.png')
    print("✓ Created test_challenge.png")
    
    print("\nTo solve this test challenge:")
    print("1. Run: python3 simple_solver.py test_challenge.png")
    print("2. Look at the generated images for the hidden flag")
    print("3. The flag should become visible in one of the dithered versions")
    
    # Also create a simple version that demonstrates the concept
    simple_img = Image.new('L', (400, 200), 128)
    draw = ImageDraw.Draw(simple_img)
    
    # Add the flag text with subtle contrast
    flag_text = "flag{test123}"
    try:
        font = ImageFont.truetype("/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf", 30)
    except:
        font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), flag_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    text_x = (400 - text_width) // 2
    text_y = (200 - text_height) // 2
    
    # Draw text with very subtle contrast (only 10 levels difference)
    draw.text((text_x, text_y), flag_text, fill=118, font=font)
    
    simple_img.save('simple_test.png')
    print("✓ Created simple_test.png (easier version)")

if __name__ == "__main__":
    main()
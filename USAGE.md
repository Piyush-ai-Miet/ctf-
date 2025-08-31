# How to Use the CTF Dithering Solver

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install pillow requests numpy scipy
   ```

2. **Run the solver:**
   ```bash
   python3 ctf_dither_solver.py https://cybersecure-x-dit.chals.io/
   ```

3. **Check results:**
   Look in the `results/` folder for generated images with revealed flags.

## Files in this Repository

- **`ctf_dither_solver.py`** - Main comprehensive solver script
- **`simple_solver.py`** - Simplified version for basic use
- **`solve_dither.py`** - Original advanced solver with analysis
- **`create_test.py`** - Creates test images to demonstrate the technique
- **`README.md`** - Detailed documentation and theory
- **`USAGE.md`** - This file with usage instructions

## Example Commands

```bash
# Solve the actual CTF challenge
python3 ctf_dither_solver.py https://cybersecure-x-dit.chals.io/

# Test with a local image file
python3 ctf_dither_solver.py challenge_image.png

# Create and solve a test case
python3 create_test.py
python3 ctf_dither_solver.py simple_test.png

# Use the simple solver
python3 simple_solver.py https://cybersecure-x-dit.chals.io/
```

## What to Look For

After running the solver, check the generated images for:

1. **Text patterns** - Look for readable text that appears in the dithered versions
2. **Flag format** - Search for patterns like `flag{...}`, `ctf{...}`, etc.
3. **High contrast regions** - Areas that form letters or numbers
4. **Threshold images** - Often the flag is revealed at specific threshold values
5. **Bit planes** - Sometimes flags are hidden in specific bit planes (especially 0, 1, 2, or 7)

## Expected Output

The solver will generate multiple images:
- `result_threshold_X.png` - Different threshold values (32, 64, 96, 128, 160, 192, 224)
- `result_floyd_steinberg.png` - Floyd-Steinberg dithered version
- `result_bitplane_X.png` - Individual bit planes (0-7)
- `result_quantized_X.png` - Color-reduced versions (2, 4, 8, 16 colors)

## Manual Alternative

If you prefer manual analysis, you can use image editing tools:

### GIMP:
1. Open the image
2. Go to Image → Mode → Indexed Color
3. Set maximum colors to 2-8
4. Try different dithering options
5. Look for revealed text patterns

### ImageMagick:
```bash
# Apply Floyd-Steinberg dithering
convert image.png -dither FloydSteinberg -colors 2 result.png

# Apply threshold
convert image.png -threshold 50% result.png
```

## Troubleshooting

- **Can't download image**: Check internet connection or try downloading manually
- **No flag visible**: Try all generated images carefully, sometimes the flag is subtle
- **Script errors**: Ensure all dependencies are installed with `pip install`
- **URL blocked**: Some networks block CTF sites, try from a different network

## Tips for Success

1. **Be patient** - Check all generated images carefully
2. **Look at different sizes** - Sometimes zooming in/out helps spot text
3. **Try manual tools** - If the script doesn't work, try GIMP or similar tools
4. **Check bit planes** - Often flags are hidden in the least significant bit planes
5. **Vary parameters** - The optimal threshold or technique depends on the specific challenge
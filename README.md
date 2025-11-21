# Microscope Stitching Demo

## Overview
This project demonstrates a system that:
1.  Captures images continuously (from a camera or simulation).
2.  Stitches them into a single panorama.
3.  Compares the result with a reference "Original" image.

## Setup
1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage
Run the main script:
```bash
python main.py
```

### Controls
- **Simulation Mode** (Default): Automatically reads images from the `image/` folder, stitches them, and compares.
- **Real Camera Mode**:
    1.  Open `main.py`.
    2.  Change `USE_SIMULATION = True` to `USE_SIMULATION = False`.
    3.  Run `python main.py`.
    4.  Press **'c'** to capture frames manually (or modify code to auto-capture).
    5.  Press **'s'** to stop capturing and perform stitching.
    6.  Press **'q'** to quit.

## Comparison Feature
To test the comparison accuracy:
1.  Run the demo once in simulation mode. It will generate `stitched_output.jpg`.
2.  Rename `stitched_output.jpg` to `original.jpg`.
3.  Run the demo again.
4.  The similarity score should be close to 1.0 (100%).

## Files
- `main.py`: Main entry point.
- `camera_capture.py`: Handles camera input and simulation.
- `stitcher.py`: Handles image stitching using OpenCV.
- `fast_stitcher.py`: Fast stitching implementation (3-10x faster).
- `comparator.py`: Handles image comparison using SSIM.

## Performance

By default, the project uses **FastStitcher** for better performance:
- **3-10x faster** than standard OpenCV Stitcher
- Uses ORB features + incremental stitching
- Suitable for sequential microscope images

To switch between methods, edit `main.py`:
```python
USE_FAST_STITCHER = True  # True = Fast, False = Standard
```

See `PERFORMANCE.md` for detailed comparison and optimization tips.


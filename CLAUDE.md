# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

herakoi is a motion-sensing sonification experiment that converts visual properties of images into sound using hand-tracking via webcam. Users "touch" pixels in an image with their hands, and the color/saturation of those pixels are converted to MIDI notes and sent to a virtual MIDI keyboard.

**Key Technologies:**
- MediaPipe for hand landmark detection
- OpenCV for video capture and image processing
- MIDI (mido + python-rtmidi) for sound output
- HSV color space for pixel-to-sound mapping

## Build and Installation

Install in development mode:
```bash
pip install -e .
```

Install from PyPI:
```bash
pip install herakoi
```

**Platform-specific notes:**
- macOS ARM64 (Apple Silicon): Uses `mediapipe-silicon` package
- Other platforms: Uses standard `mediapipe` package
- This is handled automatically via conditional dependencies in [pyproject.toml](pyproject.toml)

## Running herakoi

Basic usage:
```bash
herakoi path/to/image.jpg
```

With options:
```bash
herakoi image.jpg --notes C2 B6 --volume 20 --mode single --box 2 --video 0
```

Run as Python module:
```bash
python -m herakoi image.jpg
```

## Command-Line Options

- `--notes LOW HIGH`: Define pitch range (e.g., `--notes C4 B6`)
- `--volume N`: Set low volume threshold in percentage (0-100)
- `--mode MODE`: Select mode: `single`, `adaptive`, or `scan`
- `--box N`: Sonification box size as percentage of frame (default: 2)
- `--video N`: Video source index (default: 0 for primary webcam)
- `--switch`: Invert color-brightness mapping
- `--imgonly`: Toggle between image-only and split view

**Interactive controls while running:**
- `q`: Quit
- Left/Right arrow keys: Navigate through multiple images
- Up/Down arrow keys: Switch between modes

## Architecture

### Entry Points

The CLI is defined in [pyproject.toml](pyproject.toml):
```toml
[project.scripts]
herakoi = "herakoi:basic"
```

- [herakoi/\_\_init\_\_.py](herakoi/__init__.py): Contains `basic()` function which parses CLI arguments
- [herakoi/\_\_main\_\_.py](herakoi/__main__.py): Enables `python -m herakoi` execution
- [herakoi/core.py](herakoi/core.py): Contains all core functionality

### Core Components

**[herakoi/core.py](herakoi/core.py)** contains three main classes/functions:

1. **`gethsv` class**: Converts BGR images to HSV color space
   - Handles monochrome image detection
   - Applies HSV clipping to avoid cyclic color map issues (line 48)

2. **`start` class**: Main application controller
   - Initializes MIDI virtual port
   - Sets up webcam capture with OpenCV
   - Initializes MediaPipe hand tracking
   - Manages the main event loop
   - Handles keyboard input for image/mode switching

3. **`run()` method**: Core processing loop (lines 224-352)
   - Captures webcam frames
   - Detects hand landmarks using MediaPipe
   - Maps hand positions to image coordinates
   - Converts HSV values at hand positions to MIDI notes/velocity
   - Sends MIDI messages

### Operating Modes

Three modes implemented in `run()` method:

1. **`single`** (default): Uses left hand index finger position, or averages both hands if present
2. **`adaptive`**: Dynamically adjusts sonification box size based on pinch gesture (distance between index finger and thumb)
3. **`scan`**: Uses right hand for x-coordinate and left hand for y-coordinate to control a sonification point

### Pixel-to-Sound Mapping

**`getmex()` method** (lines 175-190) converts pixel properties to MIDI:

- **Normal mode** (`--switch` not set):
  - Hue (H) → MIDI pitch (note)
  - Brightness/Value (V) → MIDI velocity (volume)

- **Switched mode** (`--switch` flag):
  - Brightness (V) → MIDI pitch
  - Hue (H) → MIDI velocity

For monochrome images, automatically maps brightness to pitch.

### Hand Tracking

**MediaPipe hand landmarks:**
- `self.opindex = 8`: Index finger tip (landmark #8)
- `self.opthumb = 4`: Thumb tip (landmark #4)

In `adaptive` mode, distance between these landmarks controls sonification box size.

### MIDI Implementation

- Creates virtual MIDI port named "herakoi" (configurable)
- Sends notes on MIDI channel 8
- `panic()` method (lines 356-359): Sends note_off for all notes 0-127 to prevent stuck notes

## Coordinate Systems

- **Webcam frame**: Captured by OpenCV, flipped horizontally for mirror effect (line 243)
- **Image coordinates**: Target image in BGR/HSV format
- **MediaPipe landmarks**: Normalized coordinates (0.0-1.0) converted to pixel coordinates
- **`rescale()` method** (lines 208-220): Crops webcam frame to match target image aspect ratio

## Important Implementation Details

1. **Image preprocessing**: Images are converted to HSV; hue values >150 are clipped to 0 to avoid red wraparound issues ([core.py:48](herakoi/core.py#L48))

2. **Note calculation**: Uses `nametopitch()` function ported from pretty-midi package to convert note names (e.g., "C4") to MIDI note numbers ([core.py:53-66](herakoi/core.py#L53-L66))

3. **Position smoothing**: Notes only change when hand moves more than `pxshift` pixels (default: 2% of image dimension) to prevent jitter ([core.py:315](herakoi/core.py#L315))

4. **Timing control**:
   - `toctime`: Delay before note_on (default: 0.05s)
   - `offtime`: Duration before note_off on movement (default: 0.05s)

## Package Structure

```
herakoi/
├── __init__.py      # CLI argument parsing, basic() entry point
├── __main__.py      # Module execution entry point
└── core.py          # All core functionality (gethsv, start, run, etc.)
```

All core logic is in a single [core.py](herakoi/core.py) file (~360 lines). No subdirectories or modules.

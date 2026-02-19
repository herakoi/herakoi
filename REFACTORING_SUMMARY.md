# Herakoi Code Refactoring Summary

This document summarizes the complete refactoring of `herakoi/core.py` to improve code readability and maintainability.

## Overview

The refactoring focused on replacing cryptic abbreviations and unclear variable names with descriptive, self-documenting identifiers. The logic and functionality remain identical, but the code is now significantly easier to understand.

---

## Global Constants & Variables

| Original | Refactored | Purpose |
|----------|------------|---------|
| `vlims_` | `DEFAULT_VELOCITY_RANGE` | MIDI velocity (volume) range (40-127) |
| `flims_` | `DEFAULT_NOTE_RANGE` | MIDI note (pitch) range (48-95, C2-B5) |
| `scrw`, `scrh` | `screen_width`, `screen_height` | Screen dimensions |
| `fill` | `window_fill_ratio` | Window fill ratio (1.00) |
| `pressed` | `keyboard_input` | Global keyboard input state |

---

## Class: `gethsv` → `ImageToHSV`

Converts BGR images to HSV color space for sonification.

### Attributes Renamed

| Original | Refactored | Purpose |
|----------|------------|---------|
| `inp` | `image_path` | Path to input image file |
| `h`, `w` | `height`, `width` | Image dimensions |
| `mono` | `is_monochrome` | Whether image is monochrome |

### Improvements
- Added comments explaining monochrome detection logic
- Clarified hue clipping purpose (avoid red color wraparound)

---

## Class: `start` → `HerakoiPlayer`

Main application controller for hand tracking and MIDI output.

### Attributes Renamed

| Original | Refactored | Purpose |
|----------|------------|---------|
| `switch` | `invert_color_mapping` | Whether to swap hue/brightness mapping |
| `imgpath` | `image_paths` | List of image file paths |
| `imginit` | `current_image_index` | Current image index |
| `modlist` | `available_modes` | List of available modes |
| `modinit` | `current_mode_index` | Current mode index |
| `valname` | `virtual_port_name` | MIDI virtual port name |
| `midiout` | `midi_output` | MIDI output object |
| `opvideo` | `video_capture` | OpenCV video capture object |
| `opmusic` | `target_image` | Target image (ImageToHSV object) |
| `mphands`, `mpdraws` | `mediapipe_hands`, `mediapipe_drawing` | MediaPipe utilities |
| `opindex`, `opthumb` | `index_finger_tip`, `thumb_tip` | Landmark indices (8, 4) |
| `oppatch` | `sonification_box_size` | Sonification sampling box size |
| `opcolor` | `hand_colors` | Hand tracking visualization colors |

---

## Functions Refactored

### `nametopitch()` → `note_name_to_midi_pitch()`

Converts note names (e.g., "C4", "F#5") to MIDI pitch numbers (0-127).

**Changes:**
- Added comprehensive docstring
- `name` → `note_name` parameter
- `accen_map` → `accidental_map`

---

### `getmex()` → `pixel_to_midi()`

Converts pixel HSV values to MIDI note and velocity.

**Parameter Changes:**

| Original | Refactored | Purpose |
|----------|------------|---------|
| `posx` | `position` | [x, y] coordinates in image |
| `box` | `box_size` | [width, height] of sampling box |
| `vlims` | `velocity_range` | (min, max) MIDI velocity values |
| `flims` | `note_range` | (min, max) MIDI note values |
| `fout`, `vout` | `midi_note`, `midi_velocity` | Return values |

**Internal Refactoring:**
- Nested function `getval()` → `extract_midi_value()`
- `img` → `image_channel`
- `clip` → `output_range`
- `val` → `median_value`
- `vmidi` → `midi_value`
- Added detailed docstrings and inline comments

---

### `posndraw()` → `get_hand_position_and_draw()`

Extracts hand position and optionally draws landmarks.

**Parameter Changes:**

| Original | Refactored | Purpose |
|----------|------------|---------|
| `marks` | `hand_landmarks` | MediaPipe hand landmarks |
| `label` | `hand_label` | 'Left' or 'Right' |
| `posix` | `position` | [x, y, depth] return value |

**Improvements:**
- Added comprehensive docstring
- `point` → `finger_point`
- Clarified circle radius calculation (depth-based)

---

### `rescale()` → `crop_frame_to_aspect_ratio()`

Crops webcam frame to match target image aspect ratio.

**Improvements:**
- Much clearer function name
- Added docstring explaining purpose
- `wk`, `wi`, `hk`, `hi` → `target_width/height`, `crop_margin`

---

### `panic()` → `stop_all_notes()`

Stops all currently playing MIDI notes.

**Improvements:**
- Self-explanatory function name
- Added docstring

---

## `run()` Method - Complete Refactor

The main processing loop was the most cryptic part. Here's the comprehensive variable mapping:

### Method Parameters

| Original | Refactored | Purpose |
|----------|------------|---------|
| `vlims` | `velocity_range` | MIDI velocity range |
| `flims` | `note_range` | MIDI note range |

### Loop Variables

| Original | Refactored | Purpose |
|----------|------------|---------|
| `imgonly` | `show_image_only` | Display mode flag |
| `ophands` | `hand_tracker` | MediaPipe Hands object |
| `onmusic` | `note_is_playing` | Whether a note is currently playing |
| `pxshift` | `movement_threshold_pixels` | Min movement to change notes |
| `toctime` | `note_on_delay` | Delay before note_on (0.05s) |
| `offtime` | `note_change_delay` | Delay before note can change |
| `tictime` | `last_position_time` | Timestamp of last position |

### Frame Processing

| Original | Refactored | Purpose |
|----------|------------|---------|
| `opframe` | `webcam_frame` | Webcam BGR frame |
| `imframe` | `rgb_frame` | RGB frame for MediaPipe |
| `immusic` | `target_image_display` | Target image copy for drawing |
| `imhands` | `hand_tracking_results` | MediaPipe detection results |
| `mixframe` | `display_frame` | Final combined display |

### MIDI Variables

| Original | Refactored | Purpose |
|----------|------------|---------|
| `bhmidif` | `final_midi_note` | Final MIDI note (both hands) |
| `bhmidiv` | `final_midi_velocity` | Final MIDI velocity (both hands) |
| `rhmidif` | `right_hand_note` | Right hand MIDI note |
| `rhmidiv` | `right_hand_velocity` | Right hand MIDI velocity |

### Position Variables

| Original | Refactored | Purpose |
|----------|------------|---------|
| `pxmusic` | `hand_position` or `scan_position` | Hand/sonification position |
| `pxmusicold` | `previous_hand_position` | Previous position for movement calc |
| `pxpatch` | `box_size` | Sonification box dimensions |
| `pxindex` | `index_finger` | Index finger landmark |
| `pxthumb` | `thumb` | Thumb landmark |

### Hand Tracking Loop

| Original | Refactored | Purpose |
|----------|------------|---------|
| `mi` | `hand_index` | Hand index in loop |
| `immarks` | `hand_landmarks` | Current hand landmarks |
| `imlabel` | `hand_label` | 'Left' or 'Right' |

### Display Variables

| Original | Refactored | Purpose |
|----------|------------|---------|
| `hm`, `wm` | `display_height`, `display_width` | Display dimensions |
| `hr`, `wr` | `window_height`, `window_width` | Window dimensions |

---

## Code Structure Improvements

### Documentation
- Added comprehensive docstrings to all classes and methods
- Added inline comments explaining logic flow
- Documented parameter types and return values

### Mode-Specific Logic
- **Scan Mode**: Clearly separated with comments explaining "Right hand controls X, left hand controls Y"
- **Adaptive Mode**: Explained pinch gesture controlling box size
- **Single Mode**: Clarified fixed box size behavior

### MIDI Handling
- Replaced cryptic timing logic with clear variable names
- Explained note_on delay and note_change_delay
- Clarified movement threshold for triggering note changes

### Display Logic
- Separated image-only and split-view logic
- Clarified aspect ratio calculations
- Improved window sizing logic readability

---

## Summary

The refactoring transformed ~360 lines of cryptic code into clear, self-documenting code. Key improvements:

1. **Eliminated cryptic abbreviations**: `bhmidif` → `final_midi_note`, `opmusic` → `target_image`
2. **Descriptive names**: `panic()` → `stop_all_notes()`, `getmex()` → `pixel_to_midi()`
3. **Added documentation**: Docstrings and inline comments throughout
4. **Preserved functionality**: All original logic remains intact

The code is now **significantly easier to understand, maintain, and extend**.
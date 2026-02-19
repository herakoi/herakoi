import argparse

import numpy as np
import scipy.interpolate
import re

import cv2
import mediapipe as mp
import pygame

import tkinter
import tkinter.filedialog as filedialog

from pynput import keyboard
from pynput.keyboard import Key

import mido
import mingus.core.scales
import rtmidi

import time
import sys

DEFAULT_VELOCITY_RANGE = (40, 127)  # MIDI velocity (volume) range
DEFAULT_NOTE_RANGE = ('C2', 'B5')   # MIDI note (pitch) range

# Screen dimensions - will be initialized when needed
screen_width = None
screen_height = None
window_fill_ratio = 1.00

pygame.init()

global keyboard_input; keyboard_input = None
global screen;         screen         = None

# Convert BGR image into HSV for sonification
# -------------------------------------
class ImageToHSV:
  def __init__(self, image_path):
    self.bgr = cv2.imread(image_path)

    self.height, self.width, _ = self.bgr.shape

    self.hsv = cv2.cvtColor(self.bgr, cv2.COLOR_BGR2HSV)

    # Check if image is monochrome (all channels equal)
    self.is_monochrome = np.logical_and((self.bgr[...,0]==self.bgr[...,1]).all(),
                                        (self.bgr[...,1]==self.bgr[...,2]).all())

    if self.is_monochrome:
      # For monochrome images, use brightness as hue
      self.hsv[...,0] = self.hsv[...,2].copy()
    else:
      # Clip high hue values to avoid red color wraparound
      self.hsv[self.hsv[...,0]>150.00, 0] = 0.00

# Convert note name (e.g., "C4", "F#5") to MIDI pitch number
# Ported from the pretty-midi package
# -------------------------------------
def note_name_to_midi_pitch(note_name):
    """Convert a note name like 'C4' or 'F#5' to MIDI pitch number (0-127)"""
    pitch_map = {'C': 0, 'D': 2, 'E':  4, 'F':  5, 'G': 7, 'A': 9, 'B': 11}
    accidental_map = {'#': 1,  '': 0, 'b': -1, '!': -1}

    try:
      match = re.match(r'^(?P<n>[A-Ga-g])(?P<off>[#b!]?)(?P<oct>[+-]?\d+)$', note_name)

      pitch = match.group('n').upper()
      offset = accidental_map[match.group('off')]
      octave = int(match.group('oct'))
    except:
      raise ValueError('Improper note format: {0}'.format(note_name))

    return 12 * (octave + 1) + pitch_map[pitch] + offset

# Initialize screen dimensions
# -------------------------------------
def init_screen_dimensions():
  global screen_width, screen_height
  if screen_width is not None and screen_height is not None:
    return  # Already initialized

  try:
    # Try using system_profiler on macOS to avoid Tkinter/pynput threading conflict
    import subprocess
    import platform

    if platform.system() == 'Darwin':  # macOS
      result = subprocess.run(['system_profiler', 'SPDisplaysDataType'],
                              capture_output=True, text=True, timeout=2)
      for line in result.stdout.split('\n'):
        if 'Resolution' in line:
          parts = line.strip().split()
          if len(parts) >= 4:
            screen_width  = int(parts[1])
            screen_height = int(parts[3])
            break
  except:
    pass

  # Fallback to common screen resolution if detection failed
  if screen_width is None or screen_height is None:
    screen_width  = 1920
    screen_height = 1080

# Keyboard press handler for navigation
# -------------------------------------
def on_press(key):
  global keyboard_input
  if key == Key.esc:   keyboard_input = 'esc'
  if key == Key.right: keyboard_input = 'right'
  if key == Key.left:  keyboard_input = 'left'
  if key == Key.up:    keyboard_input = 'up'
  if key == Key.down:  keyboard_input = 'down'

# Build the herakoi player
# =====================================
class HerakoiPlayer:
  def __init__(self, image=None, mode='single', port={}, video=0, box=2, switch=True, **kwargs):
    global keyboard_input
    global screen

    self.listener = keyboard.Listener(on_press=on_press)
    self.listener.start()

    self.invert_color_mapping = switch

    if image is None:
      tkinter.Tk().withdraw()
      image_paths = filedialog.askopenfilenames()

      if len(image_paths) < 1: sys.exit(1)
    else: image_paths = image

    if isinstance(image_paths, str): image_paths = [image_paths]

    current_image_index = 0

    available_modes = ['single', 'adaptive', 'scan']
    if mode not in available_modes:
      raise NotImplementedError('"{0}" mode is unknown'.format(mode))
    elif mode == 'party':
      raise NotImplementedError('"party mode" not implemented yet')

    current_mode_index = available_modes.index(mode)

    self.virtual_port_name = 'herakoi'

  # Build virtual MIDI port
  # -------------------------------------
    midinew = rtmidi.MidiOut()

    if midinew.get_ports(): midinew.open_port(port.get('value', 0))
    else: midinew.open_virtual_port(port.get('name', self.virtual_port_name))

    self.midi_output = mido.open_output(port.get('name', self.virtual_port_name), virtual=True)

  # Start capture from webcam
  # -------------------------------------
    self.fullscreen_mode = kwargs.get('fullscreen', False)
    self.pad_fullscreen   = kwargs.get('pad', False) if self.fullscreen_mode else False

    if self.fullscreen_mode:
      init_screen_dimensions()
      screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)

    while True:
      self.video_capture = cv2.VideoCapture(video)
      self.target_image  = ImageToHSV(image_paths[current_image_index])

      if not self.fullscreen_mode:
        cv2.namedWindow('mixframe', cv2.WINDOW_NORMAL)

      self.mediapipe_hands   = mp.solutions.hands
      self.mediapipe_drawing = mp.solutions.drawing_utils
      self.mediapipe_style   = mp.solutions.drawing_styles

      self.index_finger_tip = 8
      self.thumb_tip        = 4

      if mode == 'adaptive':
        self.sonification_box_size = None
      else:
        self.sonification_box_size = np.minimum(self.target_image.width, self.target_image.height)
        self.sonification_box_size = int(np.clip((box / 100) * self.sonification_box_size, 2, None))

      self.hand_colors = {'Left':  (0, 255,   0),
                          'Right': (0, 255, 255)}

      if 'volume' in kwargs:
        velocity_range = (np.interp(kwargs['volume'], (0, 100), (0, 127)), 127)
      else: velocity_range = DEFAULT_VELOCITY_RANGE

      note_range = kwargs.get('notes', DEFAULT_NOTE_RANGE)

      note_match = [re.match(r'^(?P<n>[A-Ga-g])(?P<off>[#b!]?)(?P<oct>[+-]?\d+)$', note_range[0]),
                    re.match(r'^(?P<n>[A-Ga-g])(?P<off>[#b!]?)(?P<oct>[+-]?\d+)$', note_range[1])]
      note_range = [note_name_to_midi_pitch(n) for n in note_range]

      if 'scale' in kwargs:
        musical_scale = getattr(mingus.core.scales, kwargs['scale'][0].capitalize())
        musical_scale = musical_scale(kwargs['scale'][1])
      else:
        musical_scale = mingus.core.scales.Chromatic('C')

      scale_notes = []
      for pi in range(int(note_match[0].group('oct')), int(note_match[1].group('oct')) + 1):
        for si in musical_scale.ascending():
          scale_notes.append('{0}{1}'.format(si, pi))
      scale_notes = np.array([note_name_to_midi_pitch(si) for si in scale_notes])

      scale_notes = scale_notes[np.logical_and(scale_notes >= note_range[0], scale_notes <= note_range[1])]

      self.note_interpolator = scipy.interpolate.interp1d(
          np.linspace(self.target_image.hsv[..., 2 if self.invert_color_mapping else 0].min(),
                      self.target_image.hsv[..., 2 if self.invert_color_mapping else 0].max(),
                      scale_notes.shape[0]),
          scale_notes, kind='nearest-up')

      self.velocity_interpolator = scipy.interpolate.interp1d(
          np.linspace(self.target_image.hsv[..., 0 if self.invert_color_mapping else 2].min(),
                      self.target_image.hsv[..., 0 if self.invert_color_mapping else 2].max(),
                      10),
          np.linspace(velocity_range[0], velocity_range[1], 10), kind='linear')

      self.run(mode, vlims=velocity_range, flims=note_range, **kwargs)

      if keyboard_input == 'esc':
        break
      else:
        if keyboard_input in ['right', 'left']:
          if keyboard_input == 'right':
            current_image_index = current_image_index + 1 if current_image_index < (len(image_paths) - 1) else 0
          elif keyboard_input == 'left':
            current_image_index = current_image_index - 1 if current_image_index > 0 else len(image_paths) - 1

        if keyboard_input in ['up', 'down']:
          if keyboard_input == 'up':
            current_mode_index = current_mode_index + 1 if current_mode_index < (len(available_modes) - 1) else 0
          elif keyboard_input == 'down':
            current_mode_index = current_mode_index - 1 if current_mode_index > 0 else len(available_modes) - 1

          mode = available_modes[current_mode_index]
          print('changin mode to "{0}"'.format(mode), current_mode_index)

        keyboard_input = None


# Convert pixel HSV values to MIDI note and velocity
# =====================================
  def pixel_to_midi(self, position, box_size):
    """Convert pixel HSV values at a given position to MIDI note and velocity.

    Args:
      position: [x, y] coordinates in image space
      box_size: [width, height] of the sampling box around the position
    Returns:
      (midi_note, midi_velocity): integer MIDI values
    """
    def extract_midi_value(image_channel):
      median_value = np.median(
          image_channel[
              np.clip(position[1] - box_size[1]//2, 0, self.target_image.height - 1):
              np.clip(position[1] + box_size[1]//2, 0, self.target_image.height - 1),
              np.clip(position[0] - box_size[0]//2, 0, self.target_image.width  - 1):
              np.clip(position[0] + box_size[0]//2, 0, self.target_image.width  - 1)])
      midi_value = 0 if np.isnan(median_value) else median_value
      return midi_value

    midi_note     = self.note_interpolator(extract_midi_value(self.target_image.hsv[..., 2 if self.invert_color_mapping else 0]))
    midi_velocity = self.velocity_interpolator(extract_midi_value(self.target_image.hsv[..., 0 if self.invert_color_mapping else 2]))

    return int(midi_note), int(midi_velocity)

# Draw hand landmarks and return finger tip position
# =====================================
  def get_hand_position_and_draw(self, frame, hand_landmarks, hand_label, draw=True):
    """Extract index finger position and optionally draw hand landmarks.

    Args:
      frame: BGR image to draw on
      hand_landmarks: MediaPipe hand landmarks object
      hand_label: 'Left' or 'Right'
      draw: whether to draw landmarks on frame
    Returns:
      [x, y, depth] position of index finger tip in pixel coordinates
    """
    if draw: self.mediapipe_drawing.draw_landmarks(frame, hand_landmarks, self.mediapipe_hands.HAND_CONNECTIONS, None)

    finger_point = hand_landmarks.landmark[self.index_finger_tip]
    position = [int(finger_point.x * frame.shape[1]),
                int(finger_point.y * frame.shape[0]),
                np.abs(finger_point.z) * 300]

    if draw and self.sonification_box_size is not None:
      # Circle radius is depth-based for visual feedback
      cv2.circle(frame, (position[0], position[1]), np.clip(int(position[2]), 2, None), self.hand_colors[hand_label], -1)

    return position

# Crop webcam frame to match target image aspect ratio
# =====================================
  def crop_frame_to_aspect_ratio(self, image):
    """Crop webcam frame so its aspect ratio matches the target image."""
    if image.shape[1] > image.shape[0]:
      if (self.target_image.width < self.target_image.height) or \
         (self.target_image.height / self.target_image.width) > (image.shape[0] / image.shape[1]):
        target_width = (self.target_image.width / self.target_image.height) * image.shape[0]
        crop_margin  = int(0.50 * (image.shape[1] - target_width))
        return image[:, crop_margin:-crop_margin]
      else:
        target_height = (self.target_image.height / self.target_image.width) * image.shape[1]
        crop_margin   = int(0.50 * (image.shape[0] - target_height))
        return image[crop_margin:-crop_margin, :]
    else:
      return image

# Main processing loop
# =====================================
  def run(self, mode='single', **kwargs):
    global keyboard_input

    # Initialize screen dimensions if needed
    init_screen_dimensions()

    show_image_only = kwargs.get('imgonly', False)

    hand_tracker = self.mediapipe_hands.Hands(max_num_hands=2 if mode == 'scan' else 1)

    note_is_playing = False

    movement_threshold_pixels = kwargs.get('shift', 2)
    movement_threshold_pixels = (movement_threshold_pixels / 100) * np.minimum(self.target_image.width, self.target_image.height)

    note_on_delay     = kwargs.get('toc', 0.05)
    note_change_delay = kwargs.get('off', 0.05)
    last_position_time = time.time()

    while True:
      _, webcam_frame = self.video_capture.read()

      webcam_frame = self.crop_frame_to_aspect_ratio(webcam_frame)

      webcam_frame = cv2.flip(webcam_frame, 1)
      rgb_frame    = cv2.cvtColor(webcam_frame, cv2.COLOR_BGR2RGB)

      target_image_display = self.target_image.bgr.copy()
      hand_tracking_results = hand_tracker.process(rgb_frame)

      final_midi_note     = None
      final_midi_velocity = None

      if hand_tracking_results.multi_hand_landmarks:
        if mode == 'scan':
          # Scan mode: right hand controls X, left hand controls Y
          scan_position = [0, 0, 50]
          for hand_index, hand_landmarks in enumerate(hand_tracking_results.multi_hand_landmarks):
            hand_label = hand_tracking_results.multi_handedness[hand_index].classification[0].label

            self.mediapipe_drawing.draw_landmarks(target_image_display, hand_landmarks, self.mediapipe_hands.HAND_CONNECTIONS, None)
            self.mediapipe_drawing.draw_landmarks(webcam_frame, hand_landmarks, self.mediapipe_hands.HAND_CONNECTIONS, None)

            px, py, _ = self.get_hand_position_and_draw(target_image_display, hand_landmarks, hand_label, False)

            if hand_label == 'Right': scan_position[0] = px
            if hand_label == 'Left':  scan_position[1] = py

            box_size = [self.sonification_box_size, self.sonification_box_size]

          cv2.circle(target_image_display, (scan_position[0], scan_position[1]), scan_position[2], (255, 255, 255), -1)

          final_midi_note, final_midi_velocity = self.pixel_to_midi(scan_position, box_size)

        else:
          for hand_index, hand_landmarks in enumerate(hand_tracking_results.multi_hand_landmarks):
            hand_label = hand_tracking_results.multi_handedness[hand_index].classification[0].label

            _ = self.get_hand_position_and_draw(webcam_frame, hand_landmarks, hand_label, True)

            if self.sonification_box_size is None:
              # Adaptive mode: pinch gesture controls box size
              index_finger = hand_landmarks.landmark[self.index_finger_tip]
              thumb        = hand_landmarks.landmark[self.thumb_tip]
              box_size     = [int(np.abs(index_finger.x - thumb.x) * target_image_display.shape[1]),
                              int(np.abs(index_finger.y - thumb.y) * target_image_display.shape[0])]

              _ = self.get_hand_position_and_draw(target_image_display, hand_landmarks, hand_label, True)
              hand_position = [0.50 * (index_finger.x + thumb.x),
                               0.50 * (index_finger.y + thumb.y),
                               0.50 * (index_finger.z + thumb.z)]

              for im in [target_image_display, webcam_frame]:
                cv2.rectangle(im, (int(thumb.x        * im.shape[1]), int(thumb.y        * im.shape[0])),
                                  (int(index_finger.x * im.shape[1]), int(index_finger.y * im.shape[0])),
                                  self.hand_colors[hand_label], 1)
                cv2.circle(im, (int(hand_position[0] * im.shape[1]), int(hand_position[1] * im.shape[0])), 2, self.hand_colors[hand_label], -1)

              hand_position = [int(hand_position[0] * target_image_display.shape[1]),
                               int(hand_position[1] * target_image_display.shape[0]),
                               int(hand_position[2] * 300)]

            else:
              # Single mode: fixed box size, index finger controls position
              hand_position = self.get_hand_position_and_draw(target_image_display, hand_landmarks, hand_label, True)
              box_size      = [self.sonification_box_size, self.sonification_box_size]

            if (mode in ['single', 'adaptive'] and hand_label == 'Left') or (mode == 'party'):
              final_midi_note, final_midi_velocity = self.pixel_to_midi(hand_position, box_size)

            if mode in ['single', 'adaptive'] and hand_label == 'Right':
              right_hand_note, right_hand_velocity = self.pixel_to_midi(hand_position, box_size)

              final_midi_note     = right_hand_note     if final_midi_note     is None else int(0.50 * (right_hand_note     + final_midi_note))
              final_midi_velocity = right_hand_velocity if final_midi_velocity is None else int(0.50 * (right_hand_velocity + final_midi_velocity))

        if mode in ['single', 'adaptive', 'scan']:
          if (final_midi_note is not None) and (final_midi_velocity is not None):
            if time.time() - last_position_time > note_on_delay and not note_is_playing:
              self.midi_output.send(mido.Message('note_on', channel=8, note=final_midi_note, velocity=final_midi_velocity))
              previous_hand_position = hand_position
              note_is_playing = True

            if time.time() - last_position_time > note_on_delay + note_change_delay and \
               np.hypot(previous_hand_position[0] - hand_position[0], previous_hand_position[1] - hand_position[1]) > movement_threshold_pixels:
              self.midi_output.send(mido.Message('note_off', channel=8, note=final_midi_note))
              self.stop_all_notes(); note_is_playing = False

              last_position_time = time.time()
          else: self.stop_all_notes()
      else: self.stop_all_notes()

      display_frame = target_image_display

      if self.fullscreen_mode:
        display_height, display_width, _ = display_frame.shape

        if self.pad_fullscreen:
          if (display_height / display_width) > (screen_height / screen_width):
            resized_frame = cv2.resize(display_frame, None, fx=screen_height / display_height, fy=screen_height / display_height)
            display_frame = np.zeros((screen_height, screen_width, display_frame.shape[2]), dtype=display_frame.dtype)
            display_frame[:, (screen_width - resized_frame.shape[1])//2:(screen_width - resized_frame.shape[1])//2 + resized_frame.shape[1], :] = resized_frame.copy()
          else:
            resized_frame = cv2.resize(display_frame, None, fx=screen_width / display_width, fy=screen_width / display_width)
            display_frame = np.zeros((screen_height, screen_width, display_frame.shape[2]), dtype=display_frame.dtype)
            display_frame[(screen_height - resized_frame.shape[0])//2:(screen_height - resized_frame.shape[0])//2 + resized_frame.shape[0], :, :] = resized_frame.copy()
        else:
          if (display_height / display_width) > (screen_height / screen_width):
            display_frame = cv2.resize(display_frame, None, fx=screen_width / display_width, fy=screen_width / display_width)
            display_frame = display_frame[(display_frame.shape[0] - screen_height)//2:(display_frame.shape[0] - screen_height)//2 + screen_height, :, :]
          else:
            display_frame = cv2.resize(display_frame, None, fx=screen_height / display_height, fy=screen_height / display_height)
            display_frame = display_frame[:, (display_frame.shape[1] - screen_width)//2:(display_frame.shape[1] - screen_width)//2 + screen_width, :]

        if not show_image_only:
          webcam_frame = cv2.resize(webcam_frame, None,
                                    fx=0.20 * display_frame.shape[0] / webcam_frame.shape[0],
                                    fy=0.20 * display_frame.shape[0] / webcam_frame.shape[0])
          display_frame[    int(0.01 * display_frame.shape[0]):webcam_frame.shape[0] + int(0.01 * display_frame.shape[0]),
                        -webcam_frame.shape[1] - int(0.01 * display_frame.shape[0]):  -int(0.01 * display_frame.shape[0])] = webcam_frame

        display_frame = cv2.rotate(display_frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        display_frame = cv2.flip(display_frame, 0)
        display_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
        display_frame = pygame.surfarray.make_surface(display_frame)

        screen.blit(display_frame, (0, 0))
        pygame.display.update()
      else:
        if not show_image_only:
          webcam_frame  = cv2.resize(webcam_frame, None,
                                     fx=target_image_display.shape[0] / webcam_frame.shape[0],
                                     fy=target_image_display.shape[0] / webcam_frame.shape[0])

          display_frame = np.zeros((max(webcam_frame.shape[0], target_image_display.shape[0]),
                                    webcam_frame.shape[1] + target_image_display.shape[1], 3), dtype=np.uint8)
          display_frame[:webcam_frame.shape[0],        :webcam_frame.shape[1],         :] = webcam_frame
          display_frame[:target_image_display.shape[0], webcam_frame.shape[1]:,         :] = target_image_display

        display_height, display_width, _ = display_frame.shape

        if   (display_height / display_width) > (screen_height / screen_width):
          window_height = int((0.90 if show_image_only else window_fill_ratio) * screen_height)
          window_width  = int((0.90 if show_image_only else window_fill_ratio) * screen_height * display_width / display_height)
        elif (display_height / display_width) <= (screen_height / screen_width):
          window_height = int((0.90 if show_image_only else window_fill_ratio) * screen_width * display_height / display_width)
          window_width  = int((0.90 if show_image_only else window_fill_ratio) * screen_width)

      # Show the combined image in a window
        cv2.imshow('mixframe', display_frame)
        cv2.resizeWindow('mixframe', window_width, window_height)

      if (cv2.waitKey(1) & 0xFF == ord('q')) or (keyboard_input is not None): break

    self.video_capture.release()
    cv2.destroyAllWindows()
    cv2.waitKey(1)

# Stop all currently playing MIDI notes
# =====================================
  def stop_all_notes(self):
    """Send note_off for all MIDI notes to prevent stuck notes."""
    for note in range(0, 127):
      self.midi_output.send(mido.Message('note_off', channel=8, note=note))
    self.midi_output.reset()

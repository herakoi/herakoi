import numpy as np

import mediapipe as mp
import cv2

import mido
import rtmidi

import time

# ------------------------

midiout = rtmidi.MidiOut()

if midiout.get_ports(): midiout.open_port(0)
else: midiout.open_virtual_port('sonic')

mpHands = mp.solutions.hands
mpDraw  = mp.solutions.drawing_utils
mpStyle = mp.solutions.drawing_styles
hands   = mpHands.Hands(max_num_hands=2)

# Init cpu time to compute frames per second
pTime = 0
cTime = 0
 
# Init image read
musimage_path = 'JWST.png'
musimage = cv2.imread(musimage_path)
musimage_h, musimage_w, _ = musimage.shape

musimage_HSV = cv2.cvtColor(musimage, cv2.COLOR_BGR2HSV)
musimage_hue = musimage_HSV[:,:,0].copy()
musimage_bri = musimage_HSV[:,:,2].copy()

cap = cv2.VideoCapture(0)

lhbox = 10; lhcol = (0,255,0)
rhbox = 10; rhcol = (0,255,255)

while True:
  success, frame = cap.read()
  frame = cv2.flip(frame, 1)
  frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

  music = np.copy(musimage)
  results = hands.process(frameRGB)
  
  if results.multi_hand_landmarks:
    for hi, handLms in enumerate(results.multi_hand_landmarks):

      mpDraw.draw_landmarks(frame,handLms,mpHands.HAND_CONNECTIONS,None)
      mpDraw.draw_landmarks(music,handLms,mpHands.HAND_CONNECTIONS,None)

      hand_label = results.multi_handedness[hi].classification[0].label

      h, w, c = frame.shape
      for li, lm in enumerate(handLms.landmark):
        cx, cy = int(lm.x *w), int(lm.y*h)
        if li==8:
          if   hand_label=='Left' : color = lhcol
          elif hand_label=='Right': color = rhcol
        else: color = (0,0,0)
        
        cv2.circle(frame,(cx,cy),np.clip(-int(lm.z*200),2,None),color,-1)

      lm = handLms.landmark[8]
      
      lhpos = [int(lm.x*musimage_w/2),int(lm.y*musimage_h/2),122]
      rhpos = [int(lm.x*musimage_w/2),int(lm.y*musimage_h/2),1]
      if   hand_label=='Left' :
        lhpos = [int(lm.x*musimage_w),
                 int(lm.y*musimage_h),
                 np.abs(lm.z)]
        cv2.circle(music,(lhpos[0],lhpos[1]),np.clip(-int(lm.z*300),2,None),lhcol,-1)

      elif hand_label=='Right':
        rhpos = [int(lm.x*musimage_w),
                 int(lm.y*musimage_h),
                 np.abs(lm.z)]
        cv2.circle(music,(rhpos[0],rhpos[1]),np.clip(-int(lm.z*300),2,None),rhcol,-1)

      freq = np.mean(musimage_hue[np.clip(lhpos[1]-lhbox//2,0,musimage_h-1):np.clip(lhpos[1]+lhbox//2,0,musimage_h-1),
                                  np.clip(lhpos[0]-lhbox//2,0,musimage_2-1):np.clip(lhpos[0]+lhbox//2,0,musimage_2-1)])
      freq = 0 if np.isnan(freq) else freq
      freq = int(np.interp(freq,(0,255),(48,95)))

      velo = np.mean(musimage_bri[np.clip(lhpos[1]-lhbox//2,0,musimage_h-1):np.clip(lhpos[1]+lhbox//2,0,musimage_h),
                                  np.clip(lhpos[0]-lhbox//2,0,musimage_w-1):np.clip(lhpos[0]+lhbox//2,0,musimage_w)])
      velo = 0 if np.isnan(velo) else velo
      velo = int(np.interp(velo,(0,255),(0,127)))

      note_on  = mido.Message('note_on',channel=9,note=freq,velocity=velo).bytes()
      note_off = mido.Message('note_off',channel=9,note=freq,velocity=0).bytes()

      midiout.send_message(note_on)
      midiout.send_message(note_off)

  cv2.imshow('frame', frame)
  cv2.imshow('musimage', music)
 
  if cv2.waitKey(1) & 0xFF == ord('q'):
    break

cap.release()
cv2.destroyAllWindows()
import numpy as np

import mediapipe as mp
import cv2

import mido
import rtmidi
import rtmidi.midiconstants as midiconst

import time

# ------------------------

def encode(status,data1=None,data2=None,channel=None):
  msg = [(status & 0xF0) | (channel-1 & 0xF)]
  if data1 is not None:
    msg.append(data1 & 0x7F)
  
    if data2 is not None:
      msg.append(data2 & 0x7F)

  return msg

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
musimage_sat = musimage_HSV[:,:,1].copy()
musimage_bri = musimage_HSV[:,:,2].copy()

musimage_hue_val = (musimage_hue.min(),musimage_hue.max())
musimage_bri_val = (musimage_bri.min(),musimage_bri.max())

cap = cv2.VideoCapture(0)

lhbox = 50; lhcol = (0,255,0)
rhbox = 50; rhcol = (0,255,255)

toc = 0.01
tic = time.time()

lhold = [int(musimage_w/2),int(musimage_h/2),122]
rhold = [int(musimage_w/2),int(musimage_h/2),122]
while True:
  success, frame = cap.read()
  frame = cv2.flip(frame, 1)
  frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

  music = np.copy(musimage)
  results = hands.process(frameRGB)
  
  lhfreq, lhvelo = 63, 0
  rhfreq, rhvelo = 63, 0
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

      lhhue = np.mean(musimage_hue[np.clip(lhpos[1]-lhbox//2,0,musimage_h-1):np.clip(lhpos[1]+lhbox//2,0,musimage_h-1),
                                   np.clip(lhpos[0]-lhbox//2,0,musimage_w-1):np.clip(lhpos[0]+lhbox//2,0,musimage_w-1)])

      lhsat = np.mean(musimage_sat[np.clip(lhpos[1]-lhbox//2,0,musimage_h-1):np.clip(lhpos[1]+lhbox//2,0,musimage_h-1),
                                   np.clip(lhpos[0]-lhbox//2,0,musimage_w-1):np.clip(lhpos[0]+lhbox//2,0,musimage_w-1)])

      lhbri = np.mean(musimage_bri[np.clip(lhpos[1]-lhbox//2,0,musimage_h-1):np.clip(lhpos[1]+lhbox//2,0,musimage_h),
                                   np.clip(lhpos[0]-lhbox//2,0,musimage_w-1):np.clip(lhpos[0]+lhbox//2,0,musimage_w)])

      rhhue = np.mean(musimage_hue[np.clip(rhpos[1]-rhbox//2,0,musimage_h-1):np.clip(rhpos[1]+rhbox//2,0,musimage_h-1),
                                   np.clip(rhpos[0]-rhbox//2,0,musimage_w-1):np.clip(rhpos[0]+rhbox//2,0,musimage_w-1)])

      rhsat = np.mean(musimage_sat[np.clip(rhpos[1]-rhbox//2,0,musimage_h-1):np.clip(rhpos[1]+rhbox//2,0,musimage_h-1),
                                   np.clip(rhpos[0]-rhbox//2,0,musimage_w-1):np.clip(rhpos[0]+rhbox//2,0,musimage_w-1)])

      rhbri = np.mean(musimage_bri[np.clip(rhpos[1]-rhbox//2,0,musimage_h-1):np.clip(rhpos[1]+rhbox//2,0,musimage_h),
                                   np.clip(rhpos[0]-rhbox//2,0,musimage_w-1):np.clip(rhpos[0]+rhbox//2,0,musimage_w)])

      lhfval = musimage_hue_val
      lhvval = musimage_bri_val
      lhfreq = lhhue; lhfreq = 0 if np.isnan(lhfreq) else lhfreq; lhfreq = int(np.interp(lhfreq,lhfval,(48,95)))
      lhvelo = lhbri; lhvelo = 0 if np.isnan(lhvelo) else lhvelo; lhvelo = int(np.interp(lhvelo,lhvval,(0,127)))

      rhfval = musimage_hue_val
      rhvval = musimage_bri_val
      rhfreq = rhhue; rhfreq = 0 if np.isnan(rhfreq) else rhfreq; rhfreq = int(np.interp(rhfreq,rhfval,(48,95)))
      rhvelo = rhbri; rhvelo = 0 if np.isnan(rhvelo) else rhvelo; rhvelo = int(np.interp(rhvelo,rhvval,(0,127)))

      if np.abs(time.time()-tic)>toc:
        if np.hypot(lhpos[0]-lhold[0],lhpos[1]-lhold[1])>1.00E-03*np.hypot(musimage_w,musimage_h):
          midiout.send_message(encode(midiconst.NOTE_ON,lhfreq,lhvelo,channel=8)); lhold = lhpos.copy()
          midiout.send_message(encode(midiconst.NOTE_ON,rhfreq,rhvelo,channel=9)); rhold = rhpos.copy()

        time.sleep(0.01)
        midiout.send_message(encode(midiconst.NOTE_OFF,lhfreq,0,channel=8))
        midiout.send_message(encode(midiconst.NOTE_OFF,lhfreq,0,channel=9))
        tic = time.time()

        lhold = lhpos.copy()
    else:
      midiout.send_message(encode(midiconst.NOTE_OFF,lhfreq,0,channel=8))
      midiout.send_message(encode(midiconst.NOTE_OFF,lhfreq,0,channel=9))

  cv2.imshow('frame', frame)
  cv2.imshow('musimage', music)
 
  if cv2.waitKey(1) & 0xFF == ord('q'):
    break

cap.release()
cv2.destroyAllWindows()
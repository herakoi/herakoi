import numpy as np

import cv2
import mediapipe as mp

import mido
import rtmidi
import rtmidi.midiconstants as ctmidi

import sys

class gethsv:
  def __init__(self,inp):
    self.bgr = cv2.imread(inp)
    self.hsv = cv2.cvtColor(self.bgr,cv2.COLOR_BGR2HSV)

    self.h, self.w, _ = self.bgr.shape

# Build the herakoi player
# =====================================
class start:
  def __init__(self,port={},video=0,**kwargs):

  # Run-time checks
  # -------------------------------------
    if len(sys.argv)<2:
      print('Error > image path is missing')
      sys.exit(42)

    self.valname = 'herakoi'

  # Build virtual MIDI port
  # -------------------------------------

    midinew = rtmidi.MidiOut()

    if midinew.get_ports(): midinew.open_port(port.get('value',0))
    else: midinew.open_virtual_port(port.get('name',self.valname))

    self.midiout = mido.open_output(port.get('name',self.valname),virtual=True)

  # Start capture from webcam
  # -------------------------------------

    self.opvideo = cv2.VideoCapture(video)
    self.opmusic = gethsv(sys.argv[1])

    self.mphands = mp.solutions.hands
    self.mpdraws = mp.solutions.drawing_utils
    self.mpstyle = mp.solutions.drawing_styles

    self.opindex = 8
    self.opcolor = {'Left': (0,255,  0), 
                   'Right': (0,255,255)}
    self.run()


# Convert H and B to note and volume
# =====================================
  def getmex(self,posx,box=10,vlims=(50,127),flims=(48,95)):
    musichue = np.median(self.opmusic.hsv[np.clip(posx[1]-box//2,0,self.opmusic.h-1):np.clip(posx[1]+box//2,0,self.opmusic.h-1),
                                          np.clip(posx[0]-box//2,0,self.opmusic.w-1):np.clip(posx[0]+box//2,0,self.opmusic.w-1),0])

    musicbri = np.median(self.opmusic.hsv[np.clip(posx[1]-box//2,0,self.opmusic.h-1):np.clip(posx[1]+box//2,0,self.opmusic.h-1),
                                          np.clip(posx[0]-box//2,0,self.opmusic.w-1):np.clip(posx[0]+box//2,0,self.opmusic.w-1),2])

    fmidi = musichue; fmidi = 0 if np.isnan(fmidi) else fmidi; fmidi = int(np.interp(fmidi,(self.opmusic.hsv[...,0].min(),self.opmusic.hsv[...,0].max()),flims))
    vmidi = musicbri; vmidi = 0 if np.isnan(vmidi) else vmidi; vmidi = int(np.interp(vmidi,(self.opmusic.hsv[...,2].min(),self.opmusic.hsv[...,2].max()),vlims))

    return fmidi, vmidi


# Draw and return hand markers position
# =====================================
  def posndraw(self,immusic,imframe,immarks):
    self.mpdraws.draw_landmarks(imframe,immarks,self.mphands.HAND_CONNECTIONS,None)
    self.mpdraws.draw_landmarks(immusic,immarks,self.mphands.HAND_CONNECTIONS,None)

    imlabel = imhands.multi_handedness[mi].classification[0].label
    impoint = immarks.landmark[self.opindex]

    pxmusic = [int(impoint.x*self.opmusic.w),
               int(impoint.y*self.opmusic.h),np.abs(impoint.z)*300]
    pxframe = [int(impoint.x*imframe.shape[1]),
               int(impoint.y*imframe.shape[0]),np.abs(impoint.z)*300]

    cv2.circle(immusic,(pxmusic[0],pxmusic[1]),np.clip(int(pxmusic[2]),2,None),self.opcolor[imlabel],-1)
    cv2.circle(imframe,(pxframe[0],pxframe[1]),np.clip(int(pxframe[2]),2,None),self.opcolor[imlabel],-1)

    return pxmusic


# Run herakoi
# =====================================
  def run(self,mode='single',**kwargs)
    ophands = self.mphands.Hands(max_num_hands=2)

    while True:
      _, imframe = self.opvideo.read()
      imframe = cv2.flip(imframe,1)
      imframe = cv2.cvtColor(imframe,cv2.COLOR_BGR2RGB)

      immusic = self.opmusic.bgr.copy()
      imhands = ophands.process(imframe)

      if imhands.multi_hand_landmarks:
        if mode=='mode': single(imframe,immusic,imhands)


# Single-user mode
# =====================================
  def single(self,**kwargs):

    ophands = self.mphands.Hands(max_num_hands=2)

    while True:
      _, imframe = self.opvideo.read()
      imframe = cv2.flip(imframe,1)
      imframe = cv2.cvtColor(imframe,cv2.COLOR_BGR2RGB)

      immusic = self.opmusic.bgr.copy()
      imhands = ophands.process(imframe)

      bhmidif = None
      bhmidiv = None
      if imhands.multi_hand_landmarks:
        for mi, immarks in enumerate(imhands.multi_hand_landmarks):
          pxmusic = posndraw(immusic,imframe,immarks)

          if imLabel=='Left':
            bhmidif, bhmidiv = self.getmex(pxmusic)
          if imLabel=='Right':
            rhmidif, rhmidiv = self.getmex(pxmusic)

            bhmidif = rhmidif if bhmidif is None else int(0.50*(rhmidif+bhmidif))
            bhmidiv = rhmidiv if bhmidiv is None else int(0.50*(rhmidiv+bhmidiv))
        

# Single-user mode
# =====================================
  def party(self,**kwargs):
    ophands = self.mphands.Hands(max_num_hands=kwargs.get('max_num_hands',100))

    while True:
      _, imframe = self.opvideo.read()
      imframe = cv2.flip(imframe,1)
      imframe = cv2.cvtColor(imframe,cv2.COLOR_BGR2RGB)

      immusic = self.opmusic.bgr.copy()
      imhands = ophands.process(imframe)

      if imhands.multi_hand_landmarks:
        for mi, immarks in enumerate(imhands.multi_hand_landmarks):
          pxmusic = posndraw(immusic,imframe,immarks)

          ohmidif, ohmidiv = self.getmex(pxmusic)
    
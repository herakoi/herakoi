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

vlims_ = (40,127) 
flims_ = ('C2','B5')

root = tkinter.Tk()
scrw = root.winfo_screenwidth()
scrh = root.winfo_screenheight()
fill = 1.00
root.withdraw()

pygame.init()

global pressed; pressed = None
global  screen; screen  = None

# Convert BGR image into HSV
# -------------------------------------
class gethsv:
  def __init__(self,inp):
    self.bgr = cv2.imread(inp)

    self.h, self.w, _ = self.bgr.shape

    self.hsv = cv2.cvtColor(self.bgr,cv2.COLOR_BGR2HSV)
    
    self.mono = np.logical_and((self.bgr[...,0]==self.bgr[...,1]).all(),
                               (self.bgr[...,1]==self.bgr[...,2]).all())

    if self.mono:
      self.hsv[...,0] = self.hsv[...,2].copy()
    else:
      self.hsv[self.hsv[...,0]>150.00,0] = 0.00

# Convert key name
# Ported from the pretty-midi package
# -------------------------------------
def nametopitch(name):
    pitch_map = {'C': 0, 'D': 2, 'E':  4, 'F':  5, 'G': 7, 'A': 9, 'B': 11}
    accen_map = {'#': 1,  '': 0, 'b': -1, '!': -1}

    try:
      match = re.match(r'^(?P<n>[A-Ga-g])(?P<off>[#b!]?)(?P<oct>[+-]?\d+)$',name)

      pitch = match.group('n').upper()
      offset = accen_map[match.group('off')]
      octave = int(match.group('oct'))
    except:
      raise ValueError('Improper note format: {0}'.format(name))

    return 12*(octave+1)+pitch_map[pitch]+offset

# Keyboard press
# -------------------------------------
def on_press(key):
  global pressed
  if key == Key.esc:   pressed = 'esc'
  if key == Key.right: pressed = 'right'
  if key == Key.left:  pressed = 'left'
  if key == Key.up:    pressed = 'up'
  if key == Key.down:  pressed = 'down'

# Build the herakoi player
# =====================================
class start:
  def __init__(self,image=None,mode='single',port={},video=0,box=2,switch=True,**kwargs):
    global pressed
    global screen

    self.listener = keyboard.Listener(on_press=on_press)
    self.listener.start()  

    self.switch = switch

    if image is None:
      tkinter.Tk().withdraw()
      imgpath = filedialog.askopenfilenames()
        
      if len(imgpath)<1: sys.exit(1)
    else: imgpath = image

    if isinstance(imgpath,str): imgpath = [imgpath]

    imginit = 0

    modlist = ['single','adaptive','scan']
    if mode not in modlist:
      raise NotImplementedError('"{0}" mode is unknown'.format(mode))
    elif mode=='party':
      raise NotImplementedError('"party mode" not implemented yet')

    modinit = modlist.index(mode)

    self.valname = 'herakoi'

  # Build virtual MIDI port
  # -------------------------------------
    midinew = rtmidi.MidiOut()

    if midinew.get_ports(): midinew.open_port(port.get('value',0))
    else: midinew.open_virtual_port(port.get('name',self.valname))

    self.midiout = mido.open_output(port.get('name',self.valname),virtual=True)

  # Start capture from webcam
  # -------------------------------------
    self.imgfull = kwargs.get('fullscreen',False)
    self.padfull = kwargs.get('pad',False) if self.imgfull else False

    if self.imgfull:
      screen = pygame.display.set_mode((scrw,scrh),pygame.FULLSCREEN)

    while True:
      self.opvideo = cv2.VideoCapture(video)
      self.opmusic = gethsv(imgpath[imginit])

      if not self.imgfull:
        cv2.namedWindow('mixframe',cv2.WINDOW_NORMAL)

      self.mphands = mp.solutions.hands
      self.mpdraws = mp.solutions.drawing_utils
      self.mpstyle = mp.solutions.drawing_styles

      self.opindex = 8
      self.opthumb = 4
      
      if mode=='adaptive':
        self.oppatch = None
      else:
        self.oppatch = np.minimum(self.opmusic.w,self.opmusic.h)
        self.oppatch = int(np.clip((box/100)*self.oppatch,2,None))
      
      self.opcolor = {'Left': (0,255,  0), 
                     'Right': (0,255,255)}

      if 'volume' in kwargs:
        vlims = (np.interp(kwargs['volume'],(0,100),(0,127)),127)
      else: vlims = vlims_

      flims = kwargs.get('notes',flims_)

      match = [re.match(r'^(?P<n>[A-Ga-g])(?P<off>[#b!]?)(?P<oct>[+-]?\d+)$',flims[0]),
               re.match(r'^(?P<n>[A-Ga-g])(?P<off>[#b!]?)(?P<oct>[+-]?\d+)$',flims[1])]
      flims = [nametopitch(f) for f in flims]

      if 'scale' in kwargs:
        refscale = getattr(mingus.core.scales,kwargs['scale'][0].capitalize())
        refscale = refscale(kwargs['scale'][1])
      else:
        refscale = mingus.core.scales.Chromatic('C')
      
      linscale = []
      for pi in range(int(match[0].group('oct')),int(match[1].group('oct'))+1):
        for si in refscale.ascending():
          linscale.append('{0}{1}'.format(si,pi))
      linscale = np.array([nametopitch(si) for si in linscale])

      linscale = linscale[np.logical_and(linscale>=flims[0],linscale<=flims[1])]

      self.finterp = scipy.interpolate.interp1d(np.linspace(self.opmusic.hsv[...,2 if self.switch else 0].min(),
                                                            self.opmusic.hsv[...,2 if self.switch else 0].max(),
                                                            linscale.shape[0]),
                                                   linscale,kind='nearest-up')

      self.vinterp = scipy.interpolate.interp1d(np.linspace(self.opmusic.hsv[...,0 if self.switch else 2].min(),
                                                            self.opmusic.hsv[...,0 if self.switch else 2].max(),
                                                            10),
                                                np.linspace(vlims[0],vlims[1],10),kind='linear')
      
      self.run(mode,vlims=vlims,flims=flims,**kwargs)

      if pressed=='esc':
        break
      else:
        if pressed in ['right','left']:
          if pressed=='right':
            imginit = imginit+1 if imginit<(len(imgpath)-1) else 0
          elif pressed=='left':
            imginit = imginit-1 if imginit>0 else len(imgpath)-1

        if pressed in ['up','down']:
          if pressed=='up':
            modinit = modinit+1 if modinit<(len(modlist)-1) else 0
          elif pressed=='down':
            modinit = modinit-1 if modinit>0 else len(modlist)-1

          mode = modlist[modinit]
          print('changin mode to "{0}"'.format(mode),modinit)

        pressed = None


# Convert H and B to note and loudness
# =====================================
  def getmex(self,posx,box):
    def getval(img):
      val = np.median(img[np.clip(posx[1]-box[1]//2,0,self.opmusic.h-1):np.clip(posx[1]+box[1]//2,0,self.opmusic.h-1),
                          np.clip(posx[0]-box[0]//2,0,self.opmusic.w-1):np.clip(posx[0]+box[0]//2,0,self.opmusic.w-1)])
      vmidi = 0 if np.isnan(val) else val
      return vmidi

    fout = self.finterp(getval(self.opmusic.hsv[...,2 if self.switch else 0]))
    vout = self.vinterp(getval(self.opmusic.hsv[...,0 if self.switch else 2]))

    return int(fout), int(vout)

# Draw and return hand markers position
# =====================================
  def posndraw(self,frame,marks,label,draw=True):
    if draw: self.mpdraws.draw_landmarks(frame,marks,self.mphands.HAND_CONNECTIONS,None)

    point = marks.landmark[self.opindex]
    posix = [int(point.x*frame.shape[1]),
             int(point.y*frame.shape[0]),np.abs(point.z)*300]

    if draw and self.oppatch is not None: 
      cv2.circle(frame,(posix[0],posix[1]),np.clip(int(posix[2]),2,None),self.opcolor[label],-1)

    return posix

# Rescale image according to input
# =====================================
  def rescale(self,image):
    if image.shape[1]>image.shape[0]:
      if (self.opmusic.w<self.opmusic.h) or \
         (self.opmusic.h/self.opmusic.w)>(image.shape[0]/image.shape[1]):
        wk = (self.opmusic.w/self.opmusic.h)*image.shape[0]
        wi = int(0.50*(image.shape[1]-wk))     
        return image[:,wi:-wi]
      else: 
        hk = (self.opmusic.h/self.opmusic.w)*image.shape[1]
        hi = int(0.50*(image.shape[0]-hk))
        return image[hi:-hi,:]
    else:
      return image

# Single-user mode
# =====================================
  def run(self,mode='single',**kwargs):
    global pressed

    imgonly = kwargs.get('imgonly',False)

    ophands = self.mphands.Hands(max_num_hands=2 if mode=='scan' else 1)

    onmusic = False

    pxshift = kwargs.get('shift',2)
    pxshift = (pxshift/100)*np.minimum(self.opmusic.w,self.opmusic.h)

    toctime = kwargs.get('toc',0.05)
    offtime = kwargs.get('off',0.05)
    tictime = time.time()

    while True:
      _, opframe = self.opvideo.read()

      opframe = self.rescale(opframe)

      opframe = cv2.flip(opframe,1)
      imframe = cv2.cvtColor(opframe,cv2.COLOR_BGR2RGB)

      immusic = self.opmusic.bgr.copy()
      imhands = ophands.process(imframe)

      bhmidif = None
      bhmidiv = None

      if imhands.multi_hand_landmarks:
        if mode=='scan':
          pxmusic = [0,0,50]
          for mi, immarks in enumerate(imhands.multi_hand_landmarks):
            imlabel = imhands.multi_handedness[mi].classification[0].label
            
            self.mpdraws.draw_landmarks(immusic,immarks,self.mphands.HAND_CONNECTIONS,None)
            self.mpdraws.draw_landmarks(opframe,immarks,self.mphands.HAND_CONNECTIONS,None)

            px, py, _ = self.posndraw(immusic,immarks,imlabel,False)

            if imlabel=='Right': pxmusic[0] = px
            if imlabel=='Left':  pxmusic[1] = py

            pxpatch = [self.oppatch,self.oppatch]

          cv2.circle(immusic,(pxmusic[0],pxmusic[1]),pxmusic[2],(255,255,255),-1)

          bhmidif, bhmidiv = self.getmex(pxmusic,pxpatch)

        else:
          for mi, immarks in enumerate(imhands.multi_hand_landmarks):
            imlabel = imhands.multi_handedness[mi].classification[0].label

            _       = self.posndraw(opframe,immarks,imlabel,True)

            if self.oppatch is None:
              pxindex = immarks.landmark[self.opindex]
              pxthumb = immarks.landmark[self.opthumb]
              pxpatch = [int(np.abs(pxindex.x-pxthumb.x)*immusic.shape[1]),
                         int(np.abs(pxindex.y-pxthumb.y)*immusic.shape[0])]

              _ = self.posndraw(immusic,immarks,imlabel,True)
              pxmusic = [0.50*(pxindex.x+pxthumb.x),0.50*(pxindex.y+pxthumb.y),0.50*(pxindex.z+pxthumb.z)]

              for im in [immusic,opframe]:
                cv2.rectangle(im,(int(pxthumb.x*im.shape[1]),int(pxthumb.y*im.shape[0])),
                                 (int(pxindex.x*im.shape[1]),int(pxindex.y*im.shape[0])),self.opcolor[imlabel],1)
                cv2.circle(im,(int(pxmusic[0]*im.shape[1]),int(pxmusic[1]*im.shape[0])),2,self.opcolor[imlabel],-1)
 
              pxmusic = [int(pxmusic[0]*immusic.shape[1]),
                         int(pxmusic[1]*immusic.shape[0]),int(pxmusic[2]*300)]

            else:
              pxmusic = self.posndraw(immusic,immarks,imlabel,True)
              pxpatch = [self.oppatch,self.oppatch]

            if (mode in ['single','adaptive'] and imlabel=='Left') or (mode=='party'):
              bhmidif, bhmidiv = self.getmex(pxmusic,pxpatch)
            
            if (mode in ['single','adaptive'] and imlabel=='Right'):
              rhmidif, rhmidiv = self.getmex(pxmusic,pxpatch)

              bhmidif = rhmidif if bhmidif is None else int(0.50*(rhmidif+bhmidif))
              bhmidiv = rhmidiv if bhmidiv is None else int(0.50*(rhmidiv+bhmidiv))

        if mode in ['single','adaptive','scan']:
          if (bhmidif is not None) and (bhmidiv is not None):
            if time.time()-tictime>toctime and not onmusic:
              self.midiout.send(mido.Message('note_on',channel=8,note=bhmidif,velocity=bhmidiv))
              pxmusicold = pxmusic
              onmusic = True

            if time.time()-tictime>toctime+offtime and np.hypot(pxmusicold[0]-pxmusic[0],pxmusicold[1]-pxmusic[1])>pxshift:
              self.midiout.send(mido.Message('note_off',channel=8,note=bhmidif))
              self.panic(); onmusic = False
              
              tictime = time.time()
          else: self.panic()
      else: self.panic()

      mixframe = immusic

      if self.imgfull:
        hm, wm, _ = mixframe.shape

        if self.padfull:
          if (hm/wm)>(scrh/scrw):
            resframe = cv2.resize(mixframe,None,fx=scrh/hm,fy=scrh/hm)
            mixframe = np.zeros((scrh,scrw,mixframe.shape[2]),dtype=mixframe.dtype)
            mixframe[:,(scrw-resframe.shape[1])//2:(scrw-resframe.shape[1])//2+resframe.shape[1],:] = resframe.copy()
          else:    
            resframe = cv2.resize(mixframe,None,fx=scrw/wm,fy=scrw/wm)
            mixframe = np.zeros((scrh,scrw,mixframe.shape[2]),dtype=mixframe.dtype)
            mixframe[(scrh-resframe.shape[0])//2:(scrh-resframe.shape[0])//2+resframe.shape[0],:,:] = resframe.copy()
        else:
          if (hm/wm)>(scrh/scrw): 
            mixframe = cv2.resize(mixframe,None,fx=scrw/wm,fy=scrw/wm)
            mixframe = mixframe[(mixframe.shape[0]-scrh)//2:(mixframe.shape[0]-scrh)//2+scrh,:,:]
          else:
            mixframe = cv2.resize(mixframe,None,fx=scrh/hm,fy=scrh/hm)
            mixframe = mixframe[:,(mixframe.shape[1]-scrw)//2:(mixframe.shape[1]-scrw)//2+scrw,:]

        if not imgonly:            
          opframe  = cv2.resize(opframe,None,fx=0.20*mixframe.shape[0]/opframe.shape[0],
                                             fy=0.20*mixframe.shape[0]/opframe.shape[0])
          mixframe[                  int(0.01*mixframe.shape[0]):opframe.shape[0]+int(0.01*mixframe.shape[0]),
                   -opframe.shape[1]-int(0.01*mixframe.shape[0]):                -int(0.01*mixframe.shape[0])] = opframe
        
        mixframe = cv2.rotate(mixframe, cv2.ROTATE_90_COUNTERCLOCKWISE)
        mixframe = cv2.flip(mixframe,0)
        mixframe = cv2.cvtColor(mixframe, cv2.COLOR_BGR2RGB)
        mixframe = pygame.surfarray.make_surface(mixframe)
        
        screen.blit(mixframe,(0,0))
        pygame.display.update()
      else:
        if not imgonly:
          opframe = cv2.resize(opframe,None,fx=immusic.shape[0]/opframe.shape[0],fy=immusic.shape[0]/opframe.shape[0])

          mixframe = np.zeros((max(opframe.shape[0], immusic.shape[0]), opframe.shape[1] + immusic.shape[1], 3), dtype=np.uint8)
          mixframe[:opframe.shape[0],:opframe.shape[1],:] = opframe
          mixframe[:immusic.shape[0],opframe.shape[1]:,:] = immusic

        hm, wm, _ = mixframe.shape

        if   (hm/wm)>(scrh/scrw):
          hr = int((0.90 if imgonly else fill)*scrh)
          wr = int((0.90 if imgonly else fill)*scrh*wm/hm)
        elif (hm/wm)<=(scrh/scrw):
          hr = int((0.90 if imgonly else fill)*scrw*hm/wm)
          wr = int((0.90 if imgonly else fill)*scrw)

      # Show the combined image in a window
        cv2.imshow('mixframe',mixframe)
        cv2.resizeWindow('mixframe',wr,hr)

      if (cv2.waitKey(1) & 0xFF == ord('q')) or (pressed is not None): break

    self.opvideo.release()
    cv2.destroyAllWindows()
    cv2.waitKey(1)

# Turn off all MIDI notes
# =====================================
  def panic(self):
    for note in range(0,127):
      self.midiout.send(mido.Message('note_off',channel=8,note=note))
    self.midiout.reset()

import numpy as np

import mediapipe as mp
import cv2

import mido
import rtmidi
import rtmidi.midiconstants as ctmidi

import time
import sys

# ------------------------

NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
OCTAVES = list(range(11))
NOTES_IN_OCTAVE = len(NOTES)

def number_to_note(number: int) -> tuple:
    octave = number // NOTES_IN_OCTAVE
    assert octave in OCTAVES, errors['notes']
    assert 0 <= number <= 127, errors['notes']
    note = NOTES[number % NOTES_IN_OCTAVE]

    return note, octave

# ------------------------

def encode(status,data1=None,data2=None,channel=None):
  msg = [(status & 0xF0) | (channel-1 & 0xF)]
  if data1 is not None:
    msg.append(data1 & 0x7F)
  
    if data2 is not None:
      msg.append(data2 & 0x7F)

  return msg

# ------------------------

midinew = rtmidi.MidiOut()

if midinew.get_ports(): midinew.open_port(0)
else: midinew.open_virtual_port('sonic')

midiout = mido.open_output('sonic',virtual=True)

mpHands = mp.solutions.hands
mpDraws = mp.solutions.drawing_utils
mpStyle = mp.solutions.drawing_styles
opHands = mpHands.Hands(max_num_hands=10)

cvVideo = cv2.VideoCapture(0)

opIndex = 8
opColor = {'Left': (0,255,  0), 
          'Right': (0,255,255)}

# ------------------------

imInput = sys.argv[1]
opMusic = cv2.imread(imInput)
opMusicH, opMusicW, _ = opMusic.shape

opMusicHSV = cv2.cvtColor(opMusic,cv2.COLOR_BGR2HSV)
opMusicHue = opMusicHSV[:,:,0].copy(); ctMusicHue = (opMusicHue.min(),opMusicHue.max())
opMusicSat = opMusicHSV[:,:,1].copy(); ctMusicSat = (opMusicSat.min(),opMusicSat.max())
opMusicBri = opMusicHSV[:,:,2].copy(); ctMusicBri = (opMusicBri.min(),opMusicBri.max())

opVideo = cv2.VideoCapture(0)

off = 0.05
toc = 0.05
tic = time.time()

onMusic = False

lhMusicBox = 10
lhMusicOld = [int(opMusicW/2),int(opMusicH/2),122]

rhMusicBox = 10
rhMusicOld = [int(opMusicW/2),int(opMusicH/2),122]

bhMidiFold = 63

print(' ')
while True:
  _, imFrame = opVideo.read()
  imFrame = cv2.flip(imFrame,1)
  imFrameRGB = cv2.cvtColor(imFrame,cv2.COLOR_BGR2RGB)

  imMusic = opMusic.copy()
  imHands = opHands.process(imFrameRGB)

  lhMidiF, lhMidiV = 63, 0
  rhMidiF, rhMidiV = 63, 0
  bhMidiF, bhMidiV = 63, 0
  if imHands.multi_hand_landmarks:
    bhMidiF = None
    bhMidiV = None

    for mi, imMarks in enumerate(imHands.multi_hand_landmarks):

      opFrameH, opFrameW, _ = imFrame.shape

      mpDraws.draw_landmarks(imFrame,imMarks,mpHands.HAND_CONNECTIONS,None)
      mpDraws.draw_landmarks(imMusic,imMarks,mpHands.HAND_CONNECTIONS,None)

      imLabel = imHands.multi_handedness[mi].classification[0].label
      imPoint = imMarks.landmark[opIndex]

      pxMusic = [int(imPoint.x*opMusicW),int(imPoint.y*opMusicH),np.abs(imPoint.z)*300]
      pxFrame = [int(imPoint.x*opFrameW),int(imPoint.y*opFrameH),np.abs(imPoint.z)*300]

      cv2.circle(imMusic,(pxMusic[0],pxMusic[1]),np.clip(int(pxMusic[2]),2,None),opColor[imLabel],-1)
      cv2.circle(imFrame,(pxFrame[0],pxFrame[1]),np.clip(int(pxFrame[2]),2,None),opColor[imLabel],-1)

    # ----------

      if imLabel=='Left':
        lhMusicPos = pxMusic

        lhMusicHue = np.mean(opMusicHue[np.clip(lhMusicPos[1]-lhMusicBox//2,0,opMusicH-1):np.clip(lhMusicPos[1]+lhMusicBox//2,0,opMusicH-1),
                                        np.clip(lhMusicPos[0]-lhMusicBox//2,0,opMusicW-1):np.clip(lhMusicPos[0]+lhMusicBox//2,0,opMusicW-1)])

        lhMusicSat = np.mean(opMusicSat[np.clip(lhMusicPos[1]-lhMusicBox//2,0,opMusicH-1):np.clip(lhMusicPos[1]+lhMusicBox//2,0,opMusicH-1),
                                        np.clip(lhMusicPos[0]-lhMusicBox//2,0,opMusicW-1):np.clip(lhMusicPos[0]+lhMusicBox//2,0,opMusicW-1)])

        lhMusicBri = np.mean(opMusicBri[np.clip(lhMusicPos[1]-lhMusicBox//2,0,opMusicH-1):np.clip(lhMusicPos[1]+lhMusicBox//2,0,opMusicH),
                                        np.clip(lhMusicPos[0]-lhMusicBox//2,0,opMusicW-1):np.clip(lhMusicPos[0]+lhMusicBox//2,0,opMusicW)])

        lhMidiF = lhMusicHue; lhMidiF = 0 if np.isnan(lhMidiF) else lhMidiF; lhMidiF = int(np.interp(lhMidiF,ctMusicHue,(48,95)))
        lhMidiV = lhMusicBri; lhMidiV = 0 if np.isnan(lhMidiV) else lhMidiV; lhMidiV = int(np.interp(lhMidiV,ctMusicBri,(50,127)))

        bhMidiF = lhMidiF
        bhMidiV = lhMidiV

      if imLabel=='Right':
        rhMusicPos = pxMusic

        rhMusicHue = np.mean(opMusicHue[np.clip(rhMusicPos[1]-rhMusicBox//2,0,opMusicH-1):np.clip(rhMusicPos[1]+rhMusicBox//2,0,opMusicH-1),
                                        np.clip(rhMusicPos[0]-rhMusicBox//2,0,opMusicW-1):np.clip(rhMusicPos[0]+rhMusicBox//2,0,opMusicW-1)])

        rhMusicSat = np.mean(opMusicSat[np.clip(rhMusicPos[1]-rhMusicBox//2,0,opMusicH-1):np.clip(rhMusicPos[1]+rhMusicBox//2,0,opMusicH-1),
                                        np.clip(rhMusicPos[0]-rhMusicBox//2,0,opMusicW-1):np.clip(rhMusicPos[0]+rhMusicBox//2,0,opMusicW-1)])

        rhMusicBri = np.mean(opMusicBri[np.clip(rhMusicPos[1]-rhMusicBox//2,0,opMusicH-1):np.clip(rhMusicPos[1]+rhMusicBox//2,0,opMusicH),
                                        np.clip(rhMusicPos[0]-rhMusicBox//2,0,opMusicW-1):np.clip(rhMusicPos[0]+rhMusicBox//2,0,opMusicW)])

        rhMidiF = rhMusicHue; rhMidiF = 0 if np.isnan(rhMidiF) else rhMidiF; rhMidiF = int(np.interp(rhMidiF,ctMusicHue,(21,107)))
        rhMidiV = rhMusicBri; rhMidiV = 0 if np.isnan(rhMidiV) else rhMidiV; rhMidiV = int(np.interp(rhMidiV,ctMusicBri,(10,127)))

        bhMidiF = rhMidiF if bhMidiF is None else int(0.50*(rhMidiF+bhMidiF))
        bhMidiV = rhMidiV if bhMidiV is None else int(0.50*(rhMidiV+bhMidiV))
    
    if bhMidiF is not None:
      if time.time()-tic>toc and not onMusic:
        midiout.send(mido.Message('note_on',channel=8,note=bhMidiF,velocity=bhMidiV)); bhMidiFold = bhMidiF
        onMusic = True
        
        onPosixOld = pxMusic

      if time.time()-tic>toc+off and np.hypot(onPosixOld[0]-pxMusic[0],onPosixOld[1]-pxMusic[1])>50:
        for note in range(27,108):
          midiout.send(mido.Message('note_off',channel=8,note=note))

        midiout.send(mido.Message('note_off',channel=8,note=bhMidiF))
        midiout.reset()
        onMusic = False
        tic = time.time()
    else:
      for note in range(27,108):
        midiout.send(mido.Message('note_off',channel=8,note=note))

    print(number_to_note(bhMidiF),end='\r')
    bhMidiF, bhMidiV = 63, 0

    # ----------

  else:
    for note in range(27,108):
      midiout.send(mido.Message('note_off',channel=8,note=note))

  cv2.imshow('imFrame',imFrame)
  cv2.imshow('imMusic',imMusic)
 
  if cv2.waitKey(1) & 0xFF == ord('q'): break

opVideo.release()
cv2.destroyAllWindows()
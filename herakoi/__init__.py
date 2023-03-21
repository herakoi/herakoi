from .core import *

def basic():
  pars = argparse.ArgumentParser()
  pars.add_argument('image',
                    help='Input image',
                    nargs='?')
  pars.add_argument('--notes',
                    help='Define the pitch range (as note+octave format; e.g., C4)',
                    nargs=2,default=['C1','B8'],metavar=('low','high'))
  pars.add_argument('--volume',
                    help='Change the low volume threshold (in percentage)',
                    default=20,metavar=('volume'),type=float)
  pars.add_argument('--mode',
                    help='Select herakoi mode [single/adaptive/scan]',
                    default='single',metavar=('mode'))
  pars.add_argument('--box',
                    help='sonification box size in units of frame percentage',
                    default=2,metavar=('box'),type=float)
  pars.add_argument('--switch',action='store_true')
  args = pars.parse_args()

  print(args.switch)

  start(image=args.image,mode=args.mode,notes=(args.notes[0],args.notes[1]),volume=args.volume,box=args.box,switch=args.switch)
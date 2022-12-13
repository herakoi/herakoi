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
                    nargs=1,default=['20'],metavar=('volume',))

  args = pars.parse_args()

  start(image=args.image,mode='single',notes=(args.notes[0],args.notes[1]),volume=float(args.volume[0]))
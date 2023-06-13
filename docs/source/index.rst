.. herakoi documentation master file, created by
   sphinx-quickstart on Tue Jun 13 11:50:48 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

herakoi
===================================

``herakoi`` is a motion-sensing sonification experiment.

It leverages a machine learning-based algorithm for performing hand recognition and to track in real time the position of your hands in the scene observed by a webcam connected to your computer. The model landmark coordinates of your hands are re-projected onto the pixel coordinates of your favorite image. The visual properties of the "touched" pixels (at the moment, color and saturation) are then converted into sound properties of your favorite instrument, which you can choose from your favorite virtual MIDI keyboard.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation.rst
# Herakoi 

Herakoi is a motion-sensing sonification experiment. 

It uses a Machine Learning (ML)-based algorithm for hand recognition to track in real-time the position of your hands in the scene observed by a webcam connected to your computer. The model landmarks coordinates of your hands are then re-projected onto the pixel coordinates of your favorite image. The visual properties of the "touched" pixels (color and saturation %check: write more?%) are then converted into sound properties of your favorite instrument, which you can choose from your favorite virtual MIDI keyboard. %check: write more?%

In this way, you can hear the sound of any images, for educational, artistic, or just-fun purposes!

Fully written in python, Herakoi requires relatively little computational power and can be run on different on the most popular operating systems (macOS, Microsoft Windows, Linux). 


## Installation

A little intro about the installation. 

%check: add a section Requirments?%

%check% Make sure you have python 3 installed on your computer. If not we suggest you to install it along with the Anaconda Distribution % check: really necessary?% at https://www.anaconda.com/products/distribution. This will ensure that you have the standard libreries (e.g., numpy, time, sys) already installed. You can install the other required libraries through pip:

```bash
pip install opencv-python
pip install mediapipe
pip install mediapipe-silicon
pip install python-rtmidi
```

## Usage

A little intro about how to run Herakoi.

things to mention:

- open your favorite MIDI virtual keyboard and then run herakoi.py 
- which parameters will change the sound output and how to change them in the code.

- how smal / large should be the image sizes?
- which MIDI players did we test (GarageBand, l'altro che non mi ricordo il nome etc..)
- possibile problema con le videocamere virtuali spesso pre-installate sui computers
- shall we write here possible caveats? or maybe start a new section "Caveats and Future Improvments"?

*** 


```bash
python herakoi.py your_favorite_image.jpeg

- open GarageBand
```




## FAQs

A list of frequently asked questions

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change, or contact the authors.

## License

% dovremmo usare una cosa tipo Creative Commons.. poi vediamo bene come formulare la frase %

# herakoi 

`herakoi` is a motion-sensing sonification experiment. 

It uses a Machine Learning (ML)-based algorithm for hand recognition to track in real-time the position of your hands in the scene observed by a webcam connected to your computer. The model landmarks coordinates of your hands are then re-projected onto the pixel coordinates of your favorite image. The visual properties of the "touched" pixels (at the moment, color and saturation) are then converted into sound properties of your favorite instrument, which you can choose from your favorite virtual MIDI keyboard.

In this way, you can hear the sound of any images, for educational, artistic, or just-fun purposes!

Fully written in python, `herakoi` requires relatively little computational power and can be run on different on the most popular operating systems (macOS, Microsoft Windows, Linux). 


## Installation

`herakoi` runs on python 3, so make sure to have it installed on your computer. The most stable release of `herakoi` can then be installed through [pip](https://pip.pypa.io/en/stable/) simply as

```bash
pip install herakoi
```
This will install `herakoi` as well as all the necessary dependencies. Before firing up `herakoi`, you however have to install an additional package, [`mediapipe`](https://google.github.io/mediapipe/). In general, you should be able to do so via

```bash
pip install mediapipe
```
If your computer is instead equipped with an Apple Silicon chip, you should use

```
pip install mediapipe-silicon
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

A list of frequently asked questions.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change, or contact the authors.

## License
Copyright 2022 Michele Ginolfi, Luca Di Mascolo, and contributors.
herakoi is free software made available under the MIT License. For details see the LICENSE file.

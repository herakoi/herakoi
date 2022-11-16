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

1. download the `init.py` file from this GitHub repository
2. run `python init.py path_to_your_favorite_image`
3. open your favorite MIDI virtual keyboard
4. have fun!


## FAQs

A list of frequently asked questions.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change, or contact the authors.

## License
Copyright 2022 Michele Ginolfi, Luca Di Mascolo, and contributors.

herakoi is a free software made available under the MIT License. For details see the LICENSE file.

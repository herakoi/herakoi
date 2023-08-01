# herakoi 


[![DOI](https://zenodo.org/badge/515594944.svg)](https://zenodo.org/badge/latestdoi/515594944)
![PyPI version](https://img.shields.io/pypi/v/herakoi) [![Documentation Status](https://readthedocs.org/projects/herakoi/badge/?version=latest)](https://herakoi.readthedocs.io/en/latest/?badge=latest)

`herakoi` is a motion-sensing sonification experiment. 

It uses a Machine Learning (ML)-based algorithm for hand recognition to track in real-time the position of your hands in the scene observed by a webcam connected to your computer. The model landmarks coordinates of your hands are then re-projected onto the pixel coordinates of your favorite image. The visual properties of the "touched" pixels (at the moment, color and saturation) are then converted into sound properties of your favorite instrument, which you can choose from your favorite virtual MIDI keyboard.

In this way, you can hear the sound of any images, for educational, artistic, or just-fun purposes!

Fully written in python, `herakoi` requires relatively little computational power and can be run on different on the most popular operating systems (macOS, Microsoft Windows, Linux). 

## Usage

1. run `herakoi path_to_your_favorite_image`
2. open your favorite MIDI player (e.g., if you run `herakoi` on an Apple computer, GarageBang is a good option) 
3. have fun!

You can customize your `herakoi` by using the following flags:
* `--notes XX YY`, that will allow the pitch to span the range from the note `XX` and `YY` (with `XX` equal to, e.g., C4 for middle C)
* `--volume ZZ`, that will set lower threshold for the note volume (with `ZZ` in percentage)
* `--switch`, inverting the color-brightness mapping 

## FAQs

A list of frequently asked questions.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change, or contact the authors.

## License
Copyright 2022 Michele Ginolfi, Luca Di Mascolo, and contributors.

herakoi is a free software made available under the MIT License. For details see the LICENSE file.

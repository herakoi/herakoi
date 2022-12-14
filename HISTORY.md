## v0.1.5
* Added mapping switch 

## v0.1.4
* HSV clipping to limit issue with cyclic color map
* Fix of bug on `--volume` input conversion

## v0.1.3
* Update of the `herakoi` access point to allow for `--notes` and `--volume` keywords
* Addition of size check to switch the rescaling dimension in the case the aspect ratio of a horizontal image is larger than the webcam frame
* Correction of a minor bug in the `rescale` function, that was using the webcame frame as reference instead of the sonified image
* Introduction of an alternative for selecting an image via the system default file browser (implemented using `tkinter`)

## v0.1.2
* Updated documentation

## v0.1.1
* Implementation of entry point for running `herakoi` as CLI command

## v0.1.0 
* Initial release

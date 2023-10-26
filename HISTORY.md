## v0.2.1
* exit shortcut using the `esc` button
* minor bug fixes

## v0.2.0
* First official release
* Video capture keyword

## v0.1.7b
* Automatic switch to mediapipe/mediapipe-silicon

## v0.1.7
* Merged images into a mixed frame
* Added support to image gallery and scroll with left/right keys
* Added the possibility to go through modes using the up/down keys
* Reintroduced `switch` mode to swap the hue/brightness mapping

## v0.1.6
* New `--box` command line keyword to control sonification box size (if not adaptive)
* Introduction of mode for adaptively updating the sonification box size according to the pinch size
* Removed the `switch` mode and introduction of automatic check for monochromatic images, with pitch and loudness bound to pixel brightness
* Introduction of `mode` control from command line (with `--mode [single/adaptive/scan/party]`)
* New `adaptive` mode to control the size of the sonification box with the pinch 
* Introduction of `scan` mode to use right/left hand to control the x/y coordinate of the sonified box

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

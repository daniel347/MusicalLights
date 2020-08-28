# MusicalLights

A sound reactive light controller for use with a Raspberry Pi and a Neopixel LED light strip. Originally the system was designed to control Christmas tree lighting. Since the raspberry pi does not have an ADC for a microphone input, a seperate device is used. The secondary device (e.g. a laptop) records data from a microphone and performs some audio processing. The results are transferred via bluetooth to the Raspberry Pi, which determines the colours and brightnesses of the LEDs.

The Laptop side code includes a GUI to vary parameters which controls the reactions of the light to sound properties. A simulator is also included to show the variation of light brightnesses on a Christmas tree.

## Basic operation

The lights are divided into a number of sections, each of which reacts differently to the music properties. Currently, two music modes are included, Loudness and Frequency Range.

### Light Modes

#### Frequency Range

This mode determines the brightness of the LEDs based on the volume of audio over a frequency range given for each light section. The frequency range of each light section may be altered in the GUI

#### Loudness 

This mode is most useful for a sequence of light sections arranged vertically (e.g. lights on different layers of a christmas tree). The height of the light (the number of sections illuminated) varies based on the loudness of the music. THe louder the music the more sections of lights are illuminated. The loudness threshold to activate each light may be set in the GUi using the sliders provided.

### Colour Modes

#### Spectrum

The entire set of lights shows a spectrum of colours, which shifts with time over the range of lights.

#### Beat Based

Changes the colour of the entire set of lights through a series of preset colours (Which may be set in the GUI), switching colours at the beat of the music. THe beat is determined by finding an increase in overall loundess (RMS value of the audio signal).

#### Alternating

Alternates between two colours (The first two colours in the colour list) with a fixed frequency

##### Single Colour

Colour is set as the first colour in the colour list and does not change

## Areas for development

 - Blacklist audio port see rpi_w281x readme
 - Work out the stupid Bluetooth issues
 - If the LED update runs without updates to brightness it flickers - why?


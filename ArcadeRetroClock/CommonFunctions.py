# To Do
# =====
#
# - create a function that can display items twice as big as normal (i.e. zoom a sprite by pixel doubling)
# - make a function to copy a sprite to a virus playfield
# - use the new pacmaze drawing technique to create sprites
#


# make sure we use setpixel to draw, not .SetPixel.  We need to always update the buffer.


# The buffer is a 2D array.  32 lines of 64 pixels
# BUFFER[V][H]  

# We write to the LED directory for simplicity
# We write to the Canvas and swap to the LED for speed
# We write to the ScreenArray buffer so we know what is on the screen in case we
# need to check it


#------------------------------------------------------------------------------
#                                                                            --
#                                                                            --
#                                                                            --
#   This is a collection of classes and functions from my                    --
#   BIG LED project.                                                         --
#                                                                            --
#   Copyright 2021 William McEvoy                                            --
#                                                                            --
#   Version: 0.1                                                             --
#------------------------------------------------------------------------------
#                                                                            --
#------------------------------------------------------------------------------

import GlobalVariables as gv
import time
import gc
import random
import os
from configparser import SafeConfigParser
import sys



#RGB Matrix
from rgbmatrix import graphics
from rgbmatrix import RGBMatrix, RGBMatrixOptions




from datetime import datetime, timedelta
from random import randint
#import argparse
import copy
import numpy
import math
import subprocess
import traceback
import unicornhathd as unicorn



#For capturing keypresses
import curses

#Crypto
from pycoingecko import CoinGeckoAPI


#JSON
import requests
import simplejson as json




#--------------------------------------
# Global Variables                   --
#--------------------------------------

KeyboardSpeed  = 15
ConfigFileName = "ClockConfig.ini"



#--------------------------------------
# UnicornHD Display                  --
#--------------------------------------

#HatWidth, gv.HatHeight = unicorn.get_shape()
#unicorn.set_layout(unicorn.AUTO)
#unicorn.rotation(180)
#unicorn.brightness(1)






#------------------------------------------------------------------------------
# COLORS                                                                     --
#------------------------------------------------------------------------------


def ApplyGamma(color,TheGamma):
  #Need to round to integer
  NewColor = int(color * TheGamma)
  
  if NewColor > 255: NewColor = 255
  
  #print ("Old:",color," New:",NewColor)
  return NewColor




#Yellow
YellowR = ApplyGamma(220,gv.Gamma)
YellowG = ApplyGamma(220,gv.Gamma)
YellowB = ApplyGamma(0,gv.Gamma)

#Red
RedR = ApplyGamma(100,gv.Gamma)
RedG = ApplyGamma(0,gv.Gamma)
RedB = ApplyGamma(0,gv.Gamma)

#HighRed
HighRedR = ApplyGamma(225,gv.Gamma)
HighRedG = ApplyGamma(0,gv.Gamma)
HighRedB = ApplyGamma(0,gv.Gamma)

#MedRed
MedRedR = ApplyGamma(100,gv.Gamma)
MedRedG = ApplyGamma(0,gv.Gamma)
MedRedB = ApplyGamma(0,gv.Gamma)

#Orange
OrangeR = ApplyGamma(100,gv.Gamma)
OrangeG = ApplyGamma(50,gv.Gamma)
OrangeB = ApplyGamma(0,gv.Gamma)


#Purple
PurpleR = ApplyGamma(75,gv.Gamma)
PurpleG = ApplyGamma(0,gv.Gamma)
PurpleB = ApplyGamma(75,gv.Gamma)

#Green
GreenR = ApplyGamma(0,gv.Gamma)
GreenG = ApplyGamma(100,gv.Gamma)
GreenB = ApplyGamma(0,gv.Gamma)

#HighGreen
HighGreenR = ApplyGamma(0,gv.Gamma)
HighGreenG = ApplyGamma(225,gv.Gamma)
HighGreenB = ApplyGamma(0,gv.Gamma)

#MedGreen
MedGreenR = ApplyGamma(0,gv.Gamma)
MedGreenG = ApplyGamma(155,gv.Gamma)
MedGreenB = ApplyGamma(0,gv.Gamma)

#LowGreen
LowGreenR = ApplyGamma(0,gv.Gamma)
LowGreenG = ApplyGamma(100,gv.Gamma)
LowGreenB = ApplyGamma(0,gv.Gamma)

#DarkGreen
DarkGreenR = ApplyGamma(0,gv.Gamma)
DarkGreenG = ApplyGamma(45,gv.Gamma)
DarkGreenB = ApplyGamma(0,gv.Gamma)


#Blue
BlueR = ApplyGamma(0,gv.Gamma)
BlueG = ApplyGamma(0,gv.Gamma)
BlueB = ApplyGamma(100,gv.Gamma)

#WhiteLow
WhiteLowR = ApplyGamma(45,gv.Gamma)
WhiteLowG = ApplyGamma(45,gv.Gamma)
WhiteLowB = ApplyGamma(45,gv.Gamma)

#WhiteMed
WhiteMedR = ApplyGamma(100,gv.Gamma)
WhiteMedG = ApplyGamma(100,gv.Gamma)
WhiteMedB = ApplyGamma(100,gv.Gamma)

#WhiteHigh
WhiteHighR = ApplyGamma(225,gv.Gamma)
WhiteHighG = ApplyGamma(225,gv.Gamma)
WhiteHighB = ApplyGamma(225,gv.Gamma)

#Character Colors
PacR = ApplyGamma(YellowR,gv.Gamma)
PacG = ApplyGamma(YellowG,gv.Gamma)
PacB = ApplyGamma(YellowB,gv.Gamma)


#Red
Ghost1R = ApplyGamma(150,gv.Gamma)
Ghost1G = ApplyGamma(0,gv.Gamma)
Ghost1B = ApplyGamma(0,gv.Gamma)

#Orange
Ghost2R = ApplyGamma(130,gv.Gamma)
Ghost2G = ApplyGamma(75,gv.Gamma)
Ghost2B = ApplyGamma(0,gv.Gamma)

#Purple
Ghost3R = ApplyGamma(125,gv.Gamma)
Ghost3G = ApplyGamma(0,gv.Gamma)
Ghost3B = ApplyGamma(125,gv.Gamma)

#LightBlue
Ghost4R = ApplyGamma(0,gv.Gamma)
Ghost4G = ApplyGamma(150,gv.Gamma)
Ghost4B = ApplyGamma(150,gv.Gamma)


#Dots
DotR = ApplyGamma(95,gv.Gamma)
DotG = ApplyGamma(95,gv.Gamma)
DotB = ApplyGamma(95,gv.Gamma)

DotRGB = (DotR,DotG,DotB)

#Wall
WallR = ApplyGamma(10,gv.Gamma)
WallG = ApplyGamma(10,gv.Gamma)
WallB = ApplyGamma(100,gv.Gamma)

WallRGB = (WallR,WallG,WallB)


#PowerPills
PillR = ApplyGamma(0,gv.Gamma)
PillG = ApplyGamma(200,gv.Gamma)
PillB = ApplyGamma(0,gv.Gamma)

BlueGhostR = ApplyGamma(0,gv.Gamma)
BlueGhostG = ApplyGamma(0,gv.Gamma)
BlueGhostB = ApplyGamma(200,gv.Gamma)






#HighRed
SDHighRedR = ApplyGamma(255,gv.Gamma)
SDHighRedG = ApplyGamma(0,gv.Gamma)
SDHighRedB = ApplyGamma(0,gv.Gamma)


#MedRed
SDMedRedR = ApplyGamma(175,gv.Gamma)
SDMedRedG = ApplyGamma(0,gv.Gamma)
SDMedRedB = ApplyGamma(0,gv.Gamma)


#LowRed
SDLowRedR = ApplyGamma(100,gv.Gamma)
SDLowRedG = ApplyGamma(0,gv.Gamma)
SDLowRedB = ApplyGamma(0,gv.Gamma)

#DarkRed
SDDarkRedR = ApplyGamma(45,gv.Gamma)
SDDarkRedG = ApplyGamma(0,gv.Gamma)
SDDarkRedB = ApplyGamma(0,gv.Gamma)

# Red RGB Tuples
HighRed = (SDHighRedR,SDHighRedG,SDHighRedB)
MedRed  = (SDMedRedR ,SDMedRedG ,SDMedRedB)
LowRed  = (SDLowRedR ,SDLowRedG ,SDLowRedB)
DarkRed = (SDDarkRedR,SDDarkRedG,SDDarkRedB)
ShadowRed = (25,0,0)


#HighOrange
SDHighOrangeR = ApplyGamma(255,gv.Gamma)
SDHighOrangeG = ApplyGamma(128,gv.Gamma)
SDHighOrangeB = ApplyGamma(0,gv.Gamma)

#MedOrange
SDMedOrangeR = ApplyGamma(200,gv.Gamma)
SDMedOrangeG = ApplyGamma(100,gv.Gamma)
SDMedOrangeB = ApplyGamma(0,gv.Gamma)

#LowOrange
SDLowOrangeR = ApplyGamma(155,gv.Gamma)
SDLowOrangeG = ApplyGamma(75,gv.Gamma)
SDLowOrangeB = ApplyGamma(0,gv.Gamma)

#DarkOrange
SDDarkOrangeR = ApplyGamma(100,gv.Gamma)
SDDarkOrangeG = ApplyGamma(45,gv.Gamma)
SDDarkOrangeB = ApplyGamma(0,gv.Gamma)

HighOrange = (SDHighOrangeR,SDHighOrangeG,SDHighOrangeB)
MedOrange  = (SDMedOrangeR, SDMedOrangeG, SDMedOrangeB)
LowOrange  = (SDLowOrangeR, SDLowOrangeG, SDLowOrangeB)
DarkOrange = (SDDarkOrangeR,SDDarkOrangeG,SDDarkOrangeB)
ShadowOrange = (50,20,0)

# High = (R,G,B)
# Med  = (R,G,B)
# Low  = (R,G,B)
# Dark = (R,G,B)


#SDHighPurple
SDHighPurpleR = ApplyGamma(230,gv.Gamma)
SDHighPurpleG = ApplyGamma(0,gv.Gamma)
SDHighPurpleB = ApplyGamma(255,gv.Gamma)

#MedPurple
SDMedPurpleR = ApplyGamma(105,gv.Gamma)
SDMedPurpleG = ApplyGamma(0,gv.Gamma)
SDMedPurpleB = ApplyGamma(155,gv.Gamma)

#SDLowPurple
SDLowPurpleR = ApplyGamma(75,gv.Gamma)
SDLowPurpleG = ApplyGamma(0,gv.Gamma)
SDLowPurpleB = ApplyGamma(120,gv.Gamma)


#SDDarkPurple
SDDarkPurpleR = ApplyGamma(45,gv.Gamma)
SDDarkPurpleG = ApplyGamma(0,gv.Gamma)
SDDarkPurpleB = ApplyGamma(45,gv.Gamma)

# Purple RGB Tuples
HighPurple = (SDHighPurpleR,SDHighPurpleG,SDHighPurpleB)
MedPurple  = (SDMedPurpleR ,SDMedPurpleG ,SDMedPurpleB)
LowPurple  = (SDLowPurpleR ,SDLowPurpleG ,SDLowPurpleB)
DarkPurple = (SDDarkPurpleR,SDDarkPurpleG,SDDarkPurpleB)
ShadowPurple = (25,0,25)





#HighGreen
SDHighGreenR = ApplyGamma(0,gv.Gamma)
SDHighGreenG = ApplyGamma(255,gv.Gamma)
SDHighGreenB = ApplyGamma(0,gv.Gamma)

#MedGreen
SDMedGreenR = ApplyGamma(0,gv.Gamma)
SDMedGreenG = ApplyGamma(200,gv.Gamma)
SDMedGreenB = ApplyGamma(0,gv.Gamma)

#LowGreen
SDLowGreenR = ApplyGamma(0,gv.Gamma)
SDLowGreenG = ApplyGamma(100,gv.Gamma)
SDLowGreenB = ApplyGamma(0,gv.Gamma)

#DarkGreen
SDDarkGreenR = ApplyGamma(0,gv.Gamma)
SDDarkGreenG = ApplyGamma(45,gv.Gamma)
SDDarkGreenB = ApplyGamma(0,gv.Gamma)

#Green tuples
HighGreen = (SDHighGreenR,SDHighGreenG,SDHighGreenB)
MedGreen  = (SDMedGreenR,SDMedGreenG,SDMedGreenB)
LowGreen  = (SDLowGreenR,SDLowGreenG,SDLowGreenB)
DarkGreen = (SDDarkGreenR,SDDarkGreenG,SDDarkGreenB)
ShadowGreen = (0,35,0)




#HighBlue
SDHighBlueR = ApplyGamma(0,gv.Gamma)
SDHighBlueG = ApplyGamma(0,gv.Gamma)
SDHighBlueB = ApplyGamma(255,gv.Gamma)


#MedBlue
SDMedBlueR = ApplyGamma(0,gv.Gamma)
SDMedBlueG = ApplyGamma(0,gv.Gamma)
SDMedBlueB = ApplyGamma(175,gv.Gamma)

#LowBlue
SDLowBlueR = ApplyGamma(0,gv.Gamma)
SDLowBlueG = ApplyGamma(0,gv.Gamma)
SDLowBlueB = ApplyGamma(100,gv.Gamma)

#DarkBlue
SDDarkBlueR = ApplyGamma(0,gv.Gamma)
SDDarkBlueG = ApplyGamma(0,gv.Gamma)
SDDarkBlueB = ApplyGamma(45,gv.Gamma)


# Blue RGB Tuples
HighBlue = (SDHighBlueR,SDHighBlueG,SDHighBlueB)
MedBlue  = (SDHighBlueR,SDHighBlueG,SDHighBlueB)
LowBlue  = (SDHighBlueR,SDHighBlueG,SDHighBlueB)
DarkBlue = (SDHighBlueR,SDHighBlueG,SDHighBlueB)
ShadowBlue = (0,0,25)




#WhiteMax
SDMaxWhiteR = ApplyGamma(255,gv.Gamma)
SDMaxWhiteG = ApplyGamma(255,gv.Gamma)
SDMaxWhiteB = ApplyGamma(255,gv.Gamma)

#WhiteHigh
SDHighWhiteR = ApplyGamma(255,gv.Gamma)
SDHighWhiteG = ApplyGamma(255,gv.Gamma)
SDHighWhiteB = ApplyGamma(255,gv.Gamma)

#WhiteMed
SDMedWhiteR = ApplyGamma(150,gv.Gamma)
SDMedWhiteG = ApplyGamma(150,gv.Gamma)
SDMedWhiteB = ApplyGamma(150,gv.Gamma)

#WhiteLow
SDLowWhiteR = ApplyGamma(100,gv.Gamma)
SDLowWhiteG = ApplyGamma(100,gv.Gamma)
SDLowWhiteB = ApplyGamma(100,gv.Gamma)

#WhiteDark
SDDarkWhiteR = ApplyGamma(35,gv.Gamma)
SDDarkWhiteG = ApplyGamma(35,gv.Gamma)
SDDarkWhiteB = ApplyGamma(35,gv.Gamma)


# White RGB Tuples
MaxWhite  = (SDMaxWhiteR,SDMaxWhiteG,SDMaxWhiteB)
HighWhite = (SDHighWhiteR,SDHighWhiteG,SDHighWhiteB)
MedWhite  = (SDHighWhiteR,SDHighWhiteG,SDHighWhiteB)
LowWhite  = (SDHighWhiteR,SDHighWhiteG,SDHighWhiteB)
DarkWhite = (SDHighWhiteR,SDHighWhiteG,SDHighWhiteB)
ShadowWhite = (15,15,15)


#YellowMax
SDMaxYellowR = ApplyGamma(255,gv.Gamma)
SDMaxYellowG = ApplyGamma(255,gv.Gamma)
SDMaxYellowB = ApplyGamma(0,gv.Gamma)


#YellowHigh
SDHighYellowR = ApplyGamma(215,gv.Gamma)
SDHighYellowG = ApplyGamma(215,gv.Gamma)
SDHighYellowB = ApplyGamma(0,gv.Gamma)

#YellowMed
SDMedYellowR = ApplyGamma(175,gv.Gamma)
SDMedYellowG = ApplyGamma(175,gv.Gamma)
SDMedYellowB = ApplyGamma(0,gv.Gamma)

#YellowLow
SDLowYellowR = ApplyGamma(100,gv.Gamma)
SDLowYellowG = ApplyGamma(100,gv.Gamma)
SDLowYellowB = ApplyGamma(0,gv.Gamma)


#YellowDark
SDDarkYellowR = ApplyGamma(55,gv.Gamma)
SDDarkYellowG = ApplyGamma(55,gv.Gamma)
SDDarkYellowB = ApplyGamma(0,gv.Gamma)


# Yellow RGB Tuples
MaxYellow  = (SDMaxYellowR,SDMaxYellowG,SDMaxYellowB)
HighYellow = (SDHighYellowR,SDHighYellowG,SDHighYellowB)
MedYellow  = (SDMedYellowR,SDMedYellowG,SDMedYellowB)
LowYellow  = (SDLowYellowR,SDLowYellowG,SDLowYellowB)
DarkYellow = (SDDarkYellowR,SDDarkYellowG,SDDarkYellowB)
ShadowYellow = (30,30,0)


#Pink
SDMaxPinkR = ApplyGamma(155,gv.Gamma)
SDMaxPinkG = ApplyGamma(0,gv.Gamma)
SDMaxPinkB = ApplyGamma(130,gv.Gamma)

SDHighPinkR = ApplyGamma(130,gv.Gamma)
SDHighPinkG = ApplyGamma(0,gv.Gamma)
SDHighPinkB = ApplyGamma(105,gv.Gamma)

SDMedPinkR = ApplyGamma(100,gv.Gamma)
SDMedPinkG = ApplyGamma(0,gv.Gamma)
SDMedPinkB = ApplyGamma(75,gv.Gamma)

SDLowPinkR = ApplyGamma(75,gv.Gamma)
SDLowPinkG = ApplyGamma(0,gv.Gamma)
SDLowPinkB = ApplyGamma(50,gv.Gamma)

SDDarkPinkR = ApplyGamma(45,gv.Gamma)
SDDarkPinkG = ApplyGamma(0,gv.Gamma)
SDDarkPinkB = ApplyGamma(50,gv.Gamma)


# Pink RGB Tuples
MaxPink  = (SDMaxPinkR,SDMaxPinkG,SDMaxPinkB)
HighPink = (SDHighPinkR,SDHighPinkG,SDHighPinkB)
MedPink  = (SDHighPinkR,SDHighPinkG,SDHighPinkB)
LowPink  = (SDHighPinkR,SDHighPinkG,SDHighPinkB)
DarkPink = (SDHighPinkR,SDHighPinkG,SDHighPinkB)
ShadowPink = (22,0,25)


#Cyan
SDMaxCyanR = ApplyGamma(0,gv.Gamma)
SDMaxCyanG = ApplyGamma(255,gv.Gamma)
SDMaxCyanB = ApplyGamma(255,gv.Gamma)

SDHighCyanR = ApplyGamma(0,gv.Gamma)
SDHighCyanG = ApplyGamma(150,gv.Gamma)
SDHighCyanB = ApplyGamma(150,gv.Gamma)

SDMedCyanR = ApplyGamma(0,gv.Gamma)
SDMedCyanG = ApplyGamma(100,gv.Gamma)
SDMedCyanB = ApplyGamma(100,gv.Gamma)

SDLowCyanR = ApplyGamma(0,gv.Gamma)
SDLowCyanG = ApplyGamma(75,gv.Gamma)
SDLowCyanB = ApplyGamma(75,gv.Gamma)

SDDarkCyanR = ApplyGamma(0,gv.Gamma)
SDDarkCyanG = ApplyGamma(50,gv.Gamma)
SDDarkCyanB = ApplyGamma(50,gv.Gamma)

# Cyan RGB Tuples
MaxCyan  = (SDMaxCyanR,SDMaxCyanG,SDMaxCyanB)
HighCyan = (SDHighCyanR,SDHighCyanG,SDHighCyanB)
MedCyan  = (SDHighCyanR,SDHighCyanG,SDHighCyanB)
LowCyan  = (SDHighCyanR,SDHighCyanG,SDHighCyanB)
DarkCyan = (SDHighCyanR,SDHighCyanG,SDHighCyanB)
ShadowCyan = (0,20,20)




ColorList = []
ColorList.append((0,0,0))
# 1 2 3 4
ColorList.append((SDDarkWhiteR,SDDarkWhiteG,SDDarkWhiteB))
ColorList.append((SDLowWhiteR,SDLowWhiteG,SDLowWhiteB))
ColorList.append((SDMedWhiteR,SDMedWhiteG,SDMedWhiteB))
ColorList.append((SDHighWhiteR,SDHighWhiteG,SDHighWhiteB))

# 5 6 7 8
ColorList.append((SDDarkRedR,SDDarkRedG,SDDarkRedB))
ColorList.append((SDLowRedR,SDLowRedG,SDLowRedB))
ColorList.append((SDMedRedR,SDMedRedG,SDMedRedB))
ColorList.append((SDHighRedR,SDHighRedG,SDHighRedB))

# 9 10 11 12
ColorList.append((SDDarkGreenR,SDDarkGreenG,SDDarkGreenB))
ColorList.append((SDLowGreenR,SDLowGreenG,SDLowGreenB))
ColorList.append((SDMedGreenR,SDMedGreenG,SDMedGreenB))
ColorList.append((SDHighGreenR,SDHighGreenG,SDHighGreenB))

# 13 14 15 16
ColorList.append((SDDarkBlueR,SDDarkBlueG,SDDarkBlueB))
ColorList.append((SDLowBlueR,SDLowBlueG,SDLowBlueB))
ColorList.append((SDMedBlueR,SDMedBlueG,SDMedBlueB))
ColorList.append((SDHighBlueR,SDHighBlueG,SDHighBlueB))

# 17 18 19 20
ColorList.append((SDDarkOrangeR,SDDarkOrangeG,SDDarkOrangeB))
ColorList.append((SDLowOrangeR,SDLowOrangeG,SDLowOrangeB))
ColorList.append((SDMedOrangeR,SDMedOrangeG,SDMedOrangeB))
ColorList.append((SDHighOrangeR,SDHighOrangeG,SDHighOrangeB))

# 21 22 23 24
ColorList.append((SDDarkYellowR,SDDarkYellowG,SDDarkYellowB))
ColorList.append((SDLowYellowR,SDLowYellowG,SDLowYellowB))
ColorList.append((SDMedYellowR,SDMedYellowG,SDMedYellowB))
ColorList.append((SDHighYellowR,SDHighYellowG,SDHighYellowB))

# 25 26 27 28
ColorList.append((SDDarkPurpleR,SDDarkPurpleG,SDDarkPurpleB))
ColorList.append((SDLowPurpleR,SDLowPurpleG,SDLowPurpleB))
ColorList.append((SDMedPurpleR,SDMedPurpleG,SDMedPurpleB))
ColorList.append((SDHighPurpleR,SDHighPurpleG,SDHighPurpleB))

# 29 30 31 32 33
ColorList.append((SDDarkPinkR,SDDarkPinkG,SDDarkPinkB))
ColorList.append((SDLowPinkR,SDLowPinkG,SDLowPinkB))
ColorList.append((SDMedPinkR,SDMedPinkG,SDMedPinkB))
ColorList.append((SDHighPinkR,SDHighPinkG,SDHighPinkB))
ColorList.append((SDMaxPinkR,SDMaxPinkG,SDMaxPinkB))


# 34 35 36 37 38
ColorList.append((SDDarkCyanR,SDDarkCyanG,SDDarkCyanB))
ColorList.append((SDLowCyanR,SDLowCyanG,SDLowCyanB))
ColorList.append((SDMedCyanR,SDMedCyanG,SDMedCyanB))
ColorList.append((SDHighCyanR,SDHighCyanG,SDHighCyanB))
ColorList.append((SDMaxCyanR,SDMaxCyanG,SDMaxCyanB))


# MAX
# 39 40 41 42 43 44 45
ColorList.append((255,  0,  0))  #MAX-RED    39
ColorList.append((  0,255,  0))  #MAX-GREEN  40
ColorList.append((  0,  0,255))  #MAX-BLUE   41
ColorList.append((255,255,0  ))  #MAX-YELLOW 42
ColorList.append((255,  0,255))  #MAX-PURPLE 43
ColorList.append((  0,255,255))  #MAX-CYAN   44
ColorList.append((255,255,255))  #MAX-WHITE  45

#max oragne is 20

ColorList.append((SDMaxCyanR,SDMaxCyanG,SDMaxCyanB))



BrightColorList = []
BrightColorList.append((0,0,0))
# 1 2 3
BrightColorList.append((SDLowWhiteR,SDLowWhiteG,SDLowWhiteB))
BrightColorList.append((SDMedWhiteR,SDMedWhiteG,SDMedWhiteB))
BrightColorList.append((SDHighWhiteR,SDHighWhiteG,SDHighWhiteB))

# 4 5 6
BrightColorList.append(LowRed)
BrightColorList.append(MedRed)
BrightColorList.append(HighRed)

# 7 8 9
BrightColorList.append((SDLowGreenR,SDLowGreenG,SDLowGreenB))
BrightColorList.append((SDMedGreenR,SDMedGreenG,SDMedGreenB))
BrightColorList.append((SDHighGreenR,SDHighGreenG,SDHighGreenB))

# 10 11 12
BrightColorList.append((SDLowBlueR,SDLowBlueG,SDLowBlueB))
BrightColorList.append((SDMedBlueR,SDMedBlueG,SDMedBlueB))
BrightColorList.append((SDHighBlueR,SDHighBlueG,SDHighBlueB))

# 13 14 15
BrightColorList.append((SDLowOrangeR,SDLowOrangeG,SDLowOrangeB))
BrightColorList.append((SDMedOrangeR,SDMedOrangeG,SDMedOrangeB))
BrightColorList.append((SDHighOrangeR,SDHighOrangeG,SDHighOrangeB))

# 16 17 18
BrightColorList.append((SDLowYellowR,SDLowYellowG,SDLowYellowB))
BrightColorList.append((SDMedYellowR,SDMedYellowG,SDMedYellowB))
BrightColorList.append((SDHighYellowR,SDHighYellowG,SDHighYellowB))

# 19 20 21
BrightColorList.append((SDLowPurpleR,SDLowPurpleG,SDLowPurpleB))
BrightColorList.append((SDMedPurpleR,SDMedPurpleG,SDMedPurpleB))
BrightColorList.append((SDHighPurpleR,SDHighPurpleG,SDHighPurpleB))

# 22 23 24
BrightColorList.append((SDMedPinkR,SDMedPinkG,SDMedPinkB))
BrightColorList.append((SDHighPinkR,SDHighPinkG,SDHighPinkB))
BrightColorList.append((SDMaxPinkR,SDMaxPinkG,SDMaxPinkB))


# 25 26 27
BrightColorList.append((SDMedCyanR,SDMedCyanG,SDMedCyanB))
BrightColorList.append((SDHighCyanR,SDHighCyanG,SDHighCyanB))
BrightColorList.append((SDMaxCyanR,SDMaxCyanG,SDMaxCyanB))









#ColorList.append((SDDarkR,SDDarkG,SDDarkB))
#ColorList.append((SDLowR,SDLowG,SDLowB))
#ColorList.append((SDMedR,SDMedG,SDMedB))
#ColorList.append((SDHighR,SDHighG,SDHighB))


#--> need to apply gamma to SD variables directly, as they are referenced later




# def ApplyGamma(r,g,b,gv.Gamma):
  # NewR = r * Gamma
  # NewG = g * Gamma
  # NewB = b * Gamma
  
  # if NewR > 255: NewR = 255
  # if NewG > 255: NewG = 255
  # if NewB > 255: NewB = 255
  # print ("Old:",r,g,b," New:",NewR,NewG,NewB)
  # return NewR,NewG,NewB

# if (Gamma > 1):
  # for index in range(1,38):
    # r,g,b = ColorList[index]
    # r,g,b = ApplyGamma(r,g,b,gv.Gamma)
    # ColorList[index] = r,g,b




#------------------------------------------------------------------------------
#                                                                            --
# BIG LED FUNCTIONS                                                          --
#                                                                            --
#------------------------------------------------------------------------------

def ClearBigLED():
  gv.TheMatrix.Clear()


def ClearBuffers():
  gv.ScreenArray  = [[]]
  gv.ScreenArray  = [[ (0,0,0) for i in range(gv.HatWidth)] for i in range(gv.HatHeight)]
  gv.Canvas.Clear()






#------------------------------------------------------------------------------
#   ____ _                                                                   --
#  / ___| | __ _ ___ ___  ___  ___                                           --
# | |   | |/ _` / __/ __|/ _ \/ __|                                          --
# | |___| | (_| \__ \__ \  __/\__ \                                          --
#  \____|_|\__,_|___/___/\___||___/                                          --
#                                                                            --
#------------------------------------------------------------------------------



#This is a custom function because UnicornHatHD does not have one !
def setpixels(TheBuffer):
  x = 0
  y = 0

  #Copy our old buffer to the new LED buffer.  This will be replaced.
  #ScreenArray = TheBuffer

  for y in range (gv.HatHeight):
    for x in range (gv.HatWidth):
      r,g,b = TheBuffer[y][x]
      setpixel(x,y,r,g,b)



      
def setpixelsWithClock(TheBuffer,ClockSprite,h,v):
  x = 0
  y = 0

  for y in range (gv.HatHeight):
    for x in range (gv.HatWidth):
      if (x >= h and x <= h+ClockSprite.width) and (y >= v and y <= v+ClockSprite.height):
        r = ClockSprite.r
        g = ClockSprite.g
        b = ClockSprite.b
      else:
        r,g,b = TheBuffer[y][x]
      setpixel(x,y,r,g,b)



      
      

def setpixel(x, y, r, g, b):

  if (CheckBoundary(x,y) == 0):
    gv.TheMatrix.SetPixel(x,y,r,g,b)
    gv.ScreenArray[y][x] = (r,g,b)

    
def setpixelRGB(x, y, RGB):
  r,g,b = RGB
  if (CheckBoundary(x,y) == 0):
    gv.TheMatrix.SetPixel(x,y,r,g,b)
    gv.ScreenArray[y][x] = (r,g,b)
    

def setpixelsLED(TheBuffer):
  x = 0
  y = 0

  for y in range (gv.HatHeight):
    for x in range (gv.HatWidth):
      
      r,g,b = TheBuffer[y][x]
      gv.TheMatrix.SetPixel(x,y,r,g,b)



#Bug fix because my HD is inverted horizontally
def getpixel(h,v):
  #print ("get hv:",h,v)
  r = 0
  g = 0
  b = 0
  #r,g,b = unicorn.get_pixel(abs(15-h),v)
  r,g,b = gv.ScreenArray[v][h]
  #print("Get pixel HV RGB:",h,v,"-",r,g,b)
  return r,g,b      


def ShowScreenArray():
  for h in range (0,gv.HatWidth):
    for v in range (0,gv.HatHeight):
      r,g,b = gv.ScreenArray[v][h]
      if (r + g + b > 0):
        #FlashDot(h,v,0.005)
        gv.TheMatrix.SetPixel(h,v,0,0,220)
        time.sleep(0.0)
        


  
  
def ClockTimer(seconds):
  global start_time
  elapsed_time = time.time() - start_time
  elapsed_hours, rem = divmod(elapsed_time, 3600)
  elapsed_minutes, elapsed_seconds = divmod(rem, 60)
  #print("Elapsed Time: {:0>2}:{:0>2}:{:05.2f}".format(int(elapsed_hours),int(elapsed_minutes),elapsed_seconds),end="\r")

  if (elapsed_seconds >= seconds ):
    start_time = time.time()
    return 1
  else:
    return 0
  
  
  
  
  
  
  
  
  
  
class Maze(object):
  def __init__(self, h,v, width, height):
    self.h         = h
    self.v         = v
    self.width     = width
    self.height    = height
    self.ColorList = {}
    self.TypeList  = {}
    self.map       = []
    self.StartHV   = []   #Start positions for creatures (e.g. ghosts, pacdot)
    

                 
  def LoadMap(self):
    mapchar = ""
    RGB     = (0,0,0)
    dottype = ""
    NumDots = 0
    r       = 0
    g       = 0
    b       = 0


    for y in range (0,self.height):
      print ("PacMaze.map[",y,"] =",self.map[y])


    #read the map string and process one character at a time
    #decode the color and type of dot to place
    for y in range (0,self.height):
      for x in range (0,self.width):
        mapchar = self.map[y][x]
        RGB     =  self.ColorList.get(mapchar)
        dottype =  self.TypeList.get(mapchar)
        setpixelRGB(self.h+x,self.v+y,RGB)
        #print ("RGB",RGB)
        r,g,b = RGB
        

        if (dottype == "dot"):
          NumDots = NumDots + 1
          gv.DotMatrix[self.h + x][self.v + y] = 1
          #FlashDot5(self.h + x,self.v + y,0.01)
        elif (dottype == "pill"):
          NumDots = NumDots + 1
          gv.DotMatrix[self.h + x][self.v + y] = 2
          #FlashDot5(self.h + x,self.v + y,0.01)

      
    return gv.DotMatrix, NumDots;  

  def GetStartingPositions(self):
    #Start pacdot in middle of bottom row, ghosts in middle
    PacHV = (0,0)
    Ghost1HV = (0,0)
    Ghost2HV = (0,0)
    Ghost3HV = (0,0)
    Ghost4HV = (0,0)

    PacHV    = self.h + (self.width // 2)   , self.v + (self.height   -2),
    Ghost1HV = self.h + (self.width // 2) -2, self.v + (self.height // 2),
    Ghost2HV = self.h + (self.width // 2) -1, self.v + (self.height // 2),
    Ghost3HV = self.h + (self.width // 2)   , self.v + (self.height // 2),
    Ghost4HV = self.h + (self.width // 2) +1, self.v + (self.height // 2)

    #print (PacHV)

    return (PacHV, Ghost1HV,Ghost2HV,Ghost3HV,Ghost4HV)
           
      
    


  








class TextMap(object):
  #A text map is a series of same length strings that are used to visually layout a map
  def __init__(self, h,v, width, height):
    self.h         = h
    self.v         = v
    self.width     = width
    self.height    = height
    self.ColorList = {}
    self.TypeList  = {}
    self.map       = []



  def CopyMapToColorSprite(self):
    mapchar = ""
    RGB     = (0,0,0)
    dottype = ""
    NumDots = 0

    #read the map string and process one character at a time
    #decode the color and type of dot to place
    for y in range (0,self.height):
      print ("PacMaze.map[",y,"] =",self.map[y])
      for x in range (0,self.width):
        mapchar = self.map[y][x]
        RGB     =  self.ColorList.get(mapchar)
        dottype =  self.TypeList.get(mapchar)
        setpixelRGB(self.h+x,self.v+y,RGB)
        #print ("RGB",RGB)
        if (dottype == "dot"):
          NumDots = NumDots + 1
          gv.DotMatrix[self.h + x][self.v + y] = 1
          #FlashDot5(self.h + x,self.v + y,0.01)
        elif (dottype == "pill"):
          NumDots = NumDots + 1
          gv.DotMatrix[self.h + x][self.v + y] = 2
          #FlashDot5(self.h + x,self.v + y,0.01)
      
    return gv.DotMatrix, NumDots;  



    

                 














  
  
class Sprite(object):
  def __init__(self,width,height,r,g,b,grid):
    self.width  = width
    self.height = height
    self.r      = r
    self.g      = g
    self.b      = b
    self.grid   = grid
    self.name   = "?"

  
  
  
  
  
  def DisplayIncludeBlack(self,h1,v1):
    x = 0,
    y = 0
    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
      
      if self.grid[count] == 1:
        if (CheckBoundary(x+h1,y+v1) == 0):
          gv.TheMatrix.SetPixel(x+h1,y+v1,self.r,self.g,self.b)
      elif self.grid[count] == 0:
        if (CheckBoundary(x+h1,y+v1) == 0):
          gv.TheMatrix.SetPixel(x+h1,y+v1,0,0,0)
    #unicorn.show()
    #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)



  def Display(self,h1,v1):
    x = 0,
    y = 0
    #print ("Display:",self.width, self.height, self.r, self.g, self.b,v1,h1)
    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
      #print("Count:",count,"xy",x,y)
      if self.grid[count] == 1:
        if (CheckBoundary(x+h1,y+v1) == 0):
          gv.TheMatrix.SetPixel(x+h1,y+v1,self.r,self.g,self.b)
    #unicorn.show()


  def CopySpriteToBuffer(self,h1,v1):
    #Does the same as Display, but does not call show(), allowing calling function to further modify the Buffer
    #before displaying
    x = 0,
    y = 0
    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
      #print("Count:",count,"xy",x,y)
      if self.grid[count] == 1:
        if (CheckBoundary(x+h1,y+v1) == 0):
          gv.TheMatrix.SetPixel(x+h1,y+v1,self.r,self.g,self.b)
      elif self.grid[count] == 0:
        if (CheckBoundary(x+h1,y+v1) == 0):
          gv.TheMatrix.SetPixel(x+h1,y+v1,0,0,0)
    #unicorn.show()
    
    

  def EraseNoShow(self,h1,v1):
    #This function draws a black sprite, erasing the sprite.  
    #It does NOT call #unicorn.show(), which would cause a visilble blink
    x = 0
    y = 0
    #print ("Erase:",self.width, self.height, self.r, self.g, self.b,v1,h1)
    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
      #print("Count:",count,"xy",x,y)
      if self.grid[count] == 1:
        if (CheckBoundary(x+h1,y+v1) == 0):
          #gv.TheMatrix.SetPixel(x+h1,y+v1,0,0,0)
          gv.TheMatrix.SetPixel(x+h1,y+v1,0,0,0)

    
  def Erase(self,h1,v1):
    #This function draws a black sprite, erasing the sprite.  This may be useful for
    #a future "floating over the screen" type of sprite motion
    #It is pretty fast now, seems just as fast as blanking whole screen using off() or clear()
    x = 0
    y = 0
    #print ("Erase:",self.width, self.height, self.r, self.g, self.b,v1,h1)
    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
      #print("Count:",count,"xy",x,y)
      if self.grid[count] == 1:
        if (CheckBoundary(x+h1,y+v1) == 0):
          #gv.TheMatrix.SetPixel(x+h1,y+v1,0,0,0)
          gv.TheMatrix.SetPixel(x+h1,y+v1,0,0,0)
    #unicorn.show()
    #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)

  def HorizontalFlip(self):
    x = 0
    y = 0
    flipgrid = []
    
    #print ("flip:",self.width, self.height)
    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
      #print("Count:",count,"xy",x,y)
      #print("Calculations: ",(y*self.height)+ self.height-x-1)  
      flipgrid.append(self.grid[(y*self.height)+ self.height-x-1])  
    #print("Original:", str(self.grid))
    #print("Flipped :", str(flipgrid))
    self.grid = flipgrid      

    
  def Scroll(self,h,v,direction,moves,delay):
    #print("Entering Scroll")
    x = 0
    oldh = 0
    #Buffer = copy.deepcopy(unicorn.get_pixels())
    
    #modifier is used to increment or decrement the location
    if direction == "right" or direction == "down":
      modifier = 1
    else: 
      modifier = -1
    
    #print("Modifier:",modifier)
    
    if direction == "left" or direction == "right":
      #print ("Direction: ",direction)  
      for count in range (0,moves):
        h = h + (modifier)
        #erase old sprite
        if count >= 1:
          oldh = h - modifier
          #print ("Scroll:",self.width, self.height, self.r, self.g, self.b,h,v)
          gv.TheMatrix.Clear()

        #draw new sprite
        self.Display(h,v)
        #unicorn.show()
        #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
        time.sleep(delay)

        #Check for keyboard input
        r = random.randint(0,50)
        if (r == 0):
          Key = PollKeyboard()


    if direction == "up" or direction == "down":
      for count in range (0,moves):
        v = v + (modifier)
        #erase old sprite
        if count >= 1:
          oldv = v - modifier
          #self.Erase(h,oldv)
          setpixels(Buffer)
            
        #draw new sprite
        self.Display(h,v)
        #unicorn.show()
        #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
        time.sleep(delay)
        #Check for keyboard input
        r = random.randint(0,5)
        if (r == 0):
          Key = PollKeyboard()
        

        
  
  def ScrollAcrossScreen(self,h,v,direction,ScrollSleep):
    #print ("--ScrollAcrossScreen--")
    #print ("width height",self.width,self.height)
    if (direction == "right"):
      self.Scroll((0- self.width),v,"right",(gv.HatWidth + self.width),ScrollSleep)
    elif (direction == "left"):
      self.Scroll(gv.HatWidth-1,v,"left",(gv.HatWidth + self.width),ScrollSleep)
    elif (direction == "up"):
      self.Scroll(h,gv.HatWidth-1,"left",(gv.HatWidth + self.height),ScrollSleep)


  def DisplayNoBlack(self,h1,v1):
    x = 0,
    y = 0

    #print ("Display:",self.width, self.height, self.r, self.g, self.b,v1,h1)
    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
      if (CheckBoundary(x+h1,y+v1) == 0):
        if (not(self.r == 0 and self.g == 0 and self.b == 0)):
          gv.TheMatrix.SetPixel(x+h1,y+v1,self.r,self.g,self.b)
    


  def Float(self,h,v,direction,moves,delay):
    #Scroll across the screen, floating over the background
    
    x = 0
    oldh = 0
    #Capture Background
    Buffer = copy.deepcopy(unicorn.get_pixels())
    
    #modifier is used to increment or decrement the location
    if direction == "right" or direction == "down":
      modifier = 1
    else: 
      modifier = -1
    
    #print("Modifier:",modifier)
    
    
    
    if direction == "left" or direction == "right":
      #print ("Direction: ",direction)  
      
      for count in range (0,moves):
        h = h + (modifier)
        #erase old sprite
        #print ("Erasing Frame HV:",oldf," ",h,v)
        setpixels(Buffer)

        if count >= 1:
          oldh = h - modifier
          
        #draw new sprite
        self.Display(h,v)
        #unicorn.show() 
        #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
        time.sleep(delay)

      #Check for keyboard input
      r = random.randint(0,5)
      if (r == 0):
        Key = PollKeyboard()

  
  def FloatAcrossScreen(self,h,v,direction,ScrollSleep):
    if (direction == "right"):
      self.Float((0- self.width),v,"right",(gv.HatWidth + self.width),ScrollSleep)
    elif (direction == "left"):
      self.Float(gv.HatWidth-1,v,"left",(gv.HatWidth + self.width),ScrollSleep)
    elif (direction == "up"):
      self.Float(h,gv.HatWidth-1,"left",(gv.HatWidth + self.height),ScrollSleep)





#--------------------------------------
# Armada                             --
#--------------------------------------


#Asteroids
WaveStartV           = -5
WaveMinSpeed         = 5     #The fastest the wave of asteroids can fall
WaveSpeedRange       = 40    #how much variance in the wave speed min and max
AsteroidMinSpeed     = 80    #lower the number the faster the movement (based on ticks)
AsteroidMaxSpeed     = 120  
AsteroidSpawnChance  = 100   #lower the number the greater the chance
AsteroidsToDrop      = 1     #Number of asteroids to drop at a time
MaxAsteroidsInWave         = 200
MinAsteroidsInWave         = 1



class AsteroidWave(object):

  def __init__(
    self,
    AsteroidCount    = gv.AsteroidsInWaveMin,
    AsteroidMinSpeed = gv.AsteroidMinSpeed,
    AsteroidMaxSpeed = gv.AsteroidMaxSpeed
    ):

    self.AsteroidCount      = AsteroidCount
    self.AsteroidMinSpeed   = gv.AsteroidMinSpeed
    self.AsteroidMaxSpeed   = gv.AsteroidMaxSpeed
    self.Asteroids          = []
    self.TotalDropped       = 0
    self.TotalAlive         = 0
    self.Alive              = True
    self.WaveCount          = 1
    self.WaveDropSpeed      = gv.WaveDropSpeed


    self.Explosion = ColorAnimatedSprite(
      h      = 0 , 
      v      = 0, 
      name   = 'Debris',
      width  = 3, 
      height = 1,
      frames = 7,
      currentframe = 0,
      framerate    = 50,
      grid=[]
    )

    self.Explosion.grid.append(      [        0,45, 0      ]    )
    self.Explosion.grid.append(      [       45,20,45      ]    )
    self.Explosion.grid.append(      [       20,20,20      ]    )
    self.Explosion.grid.append(      [        8, 8, 8      ]    )
    self.Explosion.grid.append(      [        8, 6, 8      ]    )
    self.Explosion.grid.append(      [        6, 5, 6      ]    )
    self.Explosion.grid.append(      [        5, 5, 5      ]    )



  def CreateAsteroidWave(self):
      #Make an wave of asteroids
      r,g,b = BrightColorList[random.randint(1,27)]

      self.Asteroids = []      

      print("--Create Asteroids:",self.AsteroidCount," RGB:",r,g,b)
      for i in range(0,self.AsteroidCount):
        print ("Asteroid:",i)
        self.Asteroids.append(Ship(
          h = -1,
          v = -1,
          r = r,
          g = g,
          b = b,
          direction     = 3,
          scandirection = 3,
          speed         = random.randint(self.AsteroidMinSpeed,self.AsteroidMaxSpeed),
          alive         = 1,
          lives         = 1,
          name          = 'Asteroid',
          score         = 0,
          exploding     = 0)
        )
        self.Asteroids[i].alive       = 1
        self.Asteroids[i].Droppeded   = 0
        self.Asteroids[i].Explosion   = copy.deepcopy(self.Explosion)      
        self.Asteroids[i].Explosion.h = -1
        self.Asteroids[i].Explosion.v = -1
        self.Asteroids[i].Explosion.alive     = 0
        self.Asteroids[i].Explosion.alive     = 0
        self.Asteroids[i].Explosion.exploding = 0

      self.UpdateCounts()
      print("Wave Alive:",self.Alive," AsteroidCount:",self.AsteroidCount,"TotalAlive:",self.TotalAlive," TotalDropped:",self.TotalDropped)
      print ("--end--")
      return


  def UpdateCounts(self):
    AsteroidsAlive   = 0
    AsteroidsDropped = 0
    #print("Updating counts.  Asteroids:",self.AsteroidCount)    

    for i in range(0,self.AsteroidCount):

      if self.Asteroids[i].alive == 1:
        AsteroidsAlive = AsteroidsAlive + 1
        #FlashDot(self.Asteroids[i].h,self.Asteroids[i].v,0.01)
        #print("stuck:",self.Asteroids[i].h,self.Asteroids[i].v,self.Asteroids[i].alive,self.Asteroids[i].lives,self.Asteroids[i].speed,self.Asteroids[i].r,self.Asteroids[i].g,self.Asteroids[i].b,self.Asteroids[i].name)
      if self.Asteroids[i].dropped == 1:
        AsteroidsDropped = AsteroidsDropped + 1

      

    self.TotalAlive   = AsteroidsAlive
    self.TotalDropped = AsteroidsDropped
    
    if(self.TotalAlive >0):
      self.Alive = True
    else:
      self.Alive = False
      self.TotalAlive = 0

    #print("Update Counts:  Wave.Alive:",self.Alive," AsteroidCount:",self.AsteroidCount,"TotalAlive:",self.TotalAlive," TotalDropped:",self.TotalDropped)

    return



  def DropAsteroids(self,AsteroidsToDrop,Playfield):
      
    
    self.UpdateCounts()
    i = 0
    AsteroidsDropped = 0
    StartH           = 0
    StartV           = -5
    tries            = 0  # we are goign to try to a maximum of 255 times then exit, so we don't slow down game


    if (self.TotalAlive <= AsteroidsToDrop):
      AsteroidsToDrop = self.TotalAlive

    print("AsteroidsToDrop:",AsteroidsToDrop,"Asteroids in wave:",self.AsteroidCount)


    #Place asteroids to drop on the playfield
    i = 0
    while (AsteroidsDropped < AsteroidsToDrop and tries < 255 and i < self.AsteroidCount): 
      if (self.Asteroids[i].alive == 1 and self.Asteroids[i].dropped == 0):
        StartV = 0
        StartH = random.randint(gv.SpaceDotMinH,gv.SpaceDotMaxH)
        print("Drop Asteroid i:",i)
        #find unoccupied spot
        while (Playfield[StartV][StartH].name != 'EmptyObject' and tries <= 255):
          tries = tries + 1
          StartH = random.randint(gv.SpaceDotMinH,gv.SpaceDotMaxH)      

        if (tries < 255):        
          self.Asteroids[i].h       = random.randint(gv.SpaceDotMinH,gv.SpaceDotMaxH)
          self.Asteroids[i].v       = StartV
          self.Asteroids[i].dropped = 1
          AsteroidsDropped          = AsteroidsDropped + 1
          self.Asteroids[i].Display()

        else:
          break

      i = i + 1
        
    self.UpdateCounts()





#--------------------------------------
# VirusWorld                         --
#--------------------------------------

# Ideas:
# - Mutations happen
# - if virus is mutating, track that in the object itself
# - possible mutations: speed, turning eraticly
# - aggression, defence can be new attributes
# - need a new object virus dot
# - when a virus conquers an area, remove part of the wall and scroll to the next area
# - areas may have dormant viruses that are only acivated once in a while
# - 

class VirusWorld(object):
#Started out as an attempt to make cars follow shapes.  I was not happy with the results so I converted into a petri dish of viruses
  def __init__(self,name,width,height,Map,Playfield,CurrentRoomH,CurrentRoomV,DisplayH, DisplayV, mutationrate, replicationrate,mutationdeathrate,VirusStartSpeed):
    self.name      = name
    self.width     = width
    self.height    = height
    self.Map       = ([[]])
    self.Playfield = ([[]])
    self.CurrentRoomH = CurrentRoomH
    self.CurrentRoomV = CurrentRoomV
    self.DisplayH     = DisplayH
    self.DisplayV     = DisplayV
    self.mutationrate      = mutationrate
    self.replicationrate   = replicationrate
    self.mutationdeathrate = mutationdeathrate
    self.VirusStartSpeed   = VirusStartSpeed

    self.Map             = [[0 for i in range(self.width)] for i in range(self.height)]
    self.Playfield       = [[EmptyObject('EmptyObject') for i in range(self.width)] for i in range(self.height)]
    self.walllives       = gv.VirusFoodWallLives
    self.Viruses = []



  def AddRandomVirusesToPlayfield(self,VirusesToAdd=25):
    AddedCount = 0
    
    while (AddedCount <= VirusesToAdd):
      h = random.randint(15,self.width-2) #we use a 15 pixel offset because of other display items
      v = random.randint(2,self.height-2)
      #print ("hv",h,v,self.Playfield[v][h].name)
      if (self.Playfield[v][h].name == 'EmptyObject' or
          self.Playfield[v][h].name == 'WallBreakable'
        ):
        #print("empty")
        r,g,b = BrightColorList[random.randint(1,27)]
        VirusName = str(r) + '-' + str(g) + '-' + str(b)
        self.Playfield[v][h] = Virus(h,v,0,0,r,g,b,1,1, self.VirusStartSpeed   ,1,10,VirusName,0,0,10,'West',0,self.mutationrate,0,self.replicationrate,self.mutationdeathrate)
        self.Viruses.append(self.Playfield[v][h])
        AddedCount = AddedCount + 1
          
          
      


  def CopyTextMapToPlayfield(self,TextMap):
    mapchar = ""
    r = 0
    g = 0
    b = 0
    h = 0
    v = 0
    dottype   = ""
    VirusName = ""
    self.Playfield = ([[]])
    self.Playfield = [[EmptyObject('EmptyObject') for i in range(TextMap.width)] for i in range(TextMap.height)]
    self.Viruses = []


    #read the map string and process one character at a time
    #decode the color and type of dot to place
    for y in range (0,TextMap.height):
      print (TextMap.map[y])
      for x in range (0,TextMap.width):
        mapchar = TextMap.map[y][x]
        r,g,b   = TextMap.ColorList.get(mapchar)
        dottype = TextMap.TypeList.get(mapchar)
        h = x #+ TextMap.h
        v = y #+ TextMap.v
        
        
        if (dottype == "virus"):
          VirusName = str(r) + '-' + str(g) + '-' + str(b)
          
          #(h,v,dh,dv,r,g,b,direction,scandirection,speed,alive,lives,name,score,exploding,radarrange,destination,mutationtype,mutationrate, mutationfactor, replicationrate):
          self.Playfield[v][h] = Virus(h,v,0,0,r,g,b,1,1, self.VirusStartSpeed   ,1,10,VirusName,0,0,10,'West',0,self.mutationrate,0,self.replicationrate,self.mutationdeathrate)
          #self.Playfield[y][x].direction = PointTowardsObject8Way(x,y,height/2,width/2)

          self.Viruses.append(self.Playfield[v][h])
        elif (dottype == "wall"):
          self.Playfield[v][h] = Wall(h,v,r,g,b,1,1,'Wall')

        elif (dottype == "wallbreakable"):
          self.Playfield[v][h] = Wall(h,v,r,g,b,1,self.walllives,'WallBreakable')

        

      
    return



  def CopyMapToPlayfield(self):
    #This function is run once to populate the playfield with viruses, based on the map drawing
    #XY is actually implemented as YX.  Counter intuitive, but it works.

    width   = self.width 
    height  = self.height
    self.Viruses = []
    print ("Map width height:",width,height)
    VirusName = ""
   
    print ("RD - CopyMapToPlayfield - Width Height: ", width,height)
    x = 0
    y = 0
    
    
    print ("width height: ",width,height)
    
    for y in range (0,height):
      #print (*self.Map[y])
  
      for x in range(0,width):
        #print ("RD xy color: ",x,y, self.Map[y][x])
        SDColor = self.Map[y][x]
  
        print(str(SDColor).rjust(3,' '),end='')

        if (SDColor == 1):
          r = SDDarkWhiteR
          g = SDDarkWhiteG
          b = SDDarkWhiteB
          self.Playfield[y][x] = Wall(x,y,r,g,b,1,1,'Wall')


        elif (SDColor == 2):
          r = SDDarkWhiteR + 30
          g = SDDarkWhiteG + 30
          b = SDDarkWhiteB + 30
                                    #(h,v,r,g,b,alive,lives,name):
          self.Playfield[y][x] = Wall(x,y,r,g,b,1,10,'Wall')
          #print ("Copying wallbreakable to playfield hv: ",y,x)

        elif (SDColor == 3):
          r = SDDarkWhiteR + 50
          g = SDDarkWhiteG + 50
          b = SDDarkWhiteB + 50
                                    #(h,v,r,g,b,alive,lives,name):
          self.Playfield[y][x] = Wall(x,y,r,g,b,1,10,'Wall')
          #print ("Copying wallbreakable to playfield hv: ",y,x)

        elif (SDColor == 4):
          r = SDDarkWhiteR 
          g = SDDarkWhiteG
          b = SDDarkWhiteR + 60
                                    #(h,v,r,g,b,alive,lives,name):
          self.Playfield[y][x] = Wall(x,y,r,g,b,1,self.walllives,'WallBreakable')
          #print ("Copying wallbreakable to playfield hv: ",y,x)


        #color 5 and up represents moving viruses.
        #We used to let the viruses  have a random direction, but that quickly turns into chaos
        #now each virus will be steered towards the center of the map

        elif (SDColor >=5):
          r,g,b =  ColorList[SDColor]
          VirusName = str(r) + '-' + str(g) + '-' + str(b)
          
          #(h,v,dh,dv,r,g,b,direction,scandirection,speed,alive,lives,name,score,exploding,radarrange,destination,mutationtype,mutationrate, mutationfactor, replicationrate):
          self.Playfield[y][x] = Virus(x,y,x,y,r,g,b,1,1, self.VirusStartSpeed   ,1,10,VirusName,0,0,10,'West',0,self.mutationrate,0,self.replicationrate,self.mutationdeathrate)


          #self.Playfield[y][x].direction = random.randint(1,8)
          self.Playfield[y][x].direction = PointTowardsObject8Way(x,y,height/2,width/2)
          self.Viruses.append(self.Playfield[y][x])
        else:
          #print ('EmptyObject')
          self.Playfield[y][x] = EmptyObject('EmptyObject')
      print('')

    self.DebugPlayfield()
    return;







  def CopySpriteToPlayfield(self,TheSprite,h,v, ColorTuple=(-1,-1,-1),ObjectType = 'Wall',Filler='EmptyObject'):
    #Copy a regular sprite to the Playfield.  Sprite will be treated as a wall.

    #print ("Copying sprite to playfield:",TheSprite.name, ObjectType, Filler)

    width   = self.width 
    height  = self.height
    
    if (ColorTuple == (-1,-1,-1)):
      r = TheSprite.r
      g = TheSprite.g
      b - TheSprite.b
    else:
      r,g,b   = ColorTuple

    #Copy sprite to map 
    for count in range (0,(TheSprite.width * TheSprite.height)):
      y,x = divmod(count,TheSprite.width)

    #check the sprite grid at location[count] to see if it has a 1 or zero.  Remember the grid is a simple array.
    #I was young and new when I first wrote the first sprite functions, and did not understand arrays in python.  :)
      if TheSprite.grid[count] != 0:
        if (ObjectType == 'Wall'):
          self.Playfield[y+v][x+h] = Wall(x,y,r,g,b,1,1,'Wall')
        elif(ObjectType == 'WallBreakable'):
          self.Playfield[y+v][x+h] = Wall(x,y,r,g,b,1,1,'WallBreakable')
        elif(ObjectType == 'Virus'):
          self.Playfield[y+v][x+h] = Virus(x,y,x,y,r,g,b,1,1, self.VirusStartSpeed   ,1,10,'?',0,0,10,'West',0,self.mutationrate,0,self.replicationrate,self.mutationdeathrate)
      else:
        if (Filler == 'EmptyObject'):
          self.Playfield[y+v][x+h] = EmptyObject('EmptyObject')
        elif (Filler == 'DarkWall'):
          #dark wall
          self.Playfield[y+v][x+h] = Wall(x,y,5,5,5,1,1,'Wall')
        else:
          self.Playfield[y+v][x+h] = EmptyObject('EmptyObject')

           
    return;



  # def DisplayWindow(self,h,v):
    # #This function accepts h,v coordinates for the entire map (e.g. 1,8  20,20,  64,64)    
    # #Displays what is on the playfield currently, including walls, cars, etc.
    # r = 0
    # g = 0
    # b = 0
    # count = 0
        

    # for V in range(0,gv.HatWidth):
      # for H in range (0,gv.HatHeight):
        # #print ("DisplayWindow hv HV: ",h,v,H,V) 
        # name = self.Playfield[v+V][h+H].name
        # #print ("Display: ",name,V,H)
        # if (name == 'EmptyObject'):
          # r = 0
          # g = 0
          # b = 0          

        # else:
          # r = self.Playfield[v+V][h+H].r
          # g = self.Playfield[v+V][h+H].g
          # b = self.Playfield[v+V][h+H].b
          
        # #Our map is an array of arrays [v][h] but we draw h,v
        # gv.TheMatrix.SetPixel(H,V,r,g,b)
    
    # #unicorn.show()
    # #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)



  def DisplayWindow(self,h,v,ZoomFactor = 0):
    #This function accepts h,v coordinates for the entire map (e.g. 1,8  20,20,  64,64)    
    #Displays what is on the playfield currently, including walls, cars, etc.
    #Zoom factor is used to shrink/expand the display
    r = 0
    g = 0
    b = 0
    count = 0
    H_modifier = 0
    V_modifier = 0
    
    HIndentFactor = 0    
    VIndentFactor = 0    



    if (ZoomFactor > 1):
      H_modifier = (1 / gv.HatWidth ) * ZoomFactor * 2  #BigLED is 2 times wider than tall. Hardcoding now, will fix later. 
      V_modifier = (1 / gv.HatHeight ) * ZoomFactor
      NewHeight = round(gv.HatHeight * V_modifier)
      NewWidth  = round(gv.HatWidth * H_modifier)


      HIndentFactor = (gv.HatWidth / 2)  - (NewWidth /2)
      VIndentFactor = (gv.HatHeight / 2) - (NewHeight /2)
    else:
      IndentFactor = 0

    #print("gv.HatWidth",gv.HatWidth," NewWidth",NewWidth," ZoomFactor:",ZoomFactor,"HV_modifier",HV_modifier, "IndentFactor:",IndentFactor)

    for V in range(0,gv.HatHeight):
      for H in range (0,gv.HatWidth):
        #print ("DisplayWindow hv HV: ",h,v,H,V) 
        name = self.Playfield[v+V][h+H].name
        #print ("Display: ",name,V,H)
        if (name == 'EmptyObject'):
          r = 0
          g = 0
          b = 0          

        else:
          r = self.Playfield[v+V][h+H].r
          g = self.Playfield[v+V][h+H].g
          b = self.Playfield[v+V][h+H].b
          
        #Our map is an array V of array H  [V][1,2,3,4...etc]
        if (ZoomFactor > 0):
          gv.TheMatrix.SetPixel((H * H_modifier) + HIndentFactor ,(V * V_modifier) + VIndentFactor,r,g,b)
        
    

        else:
          gv.TheMatrix.SetPixel(H,V,r,g,b)
    
    #unicorn.show()
    #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)



  def DisplayWindowZoom(self,h,v,Z1=8,Z2=1,ZoomSleep=0.05):
    #uses playfield to display items

    if (Z1 <= Z2):
      for Z in range (Z1,Z2):
        gv.TheMatrix.Clear()
        self.DisplayWindow(h,v,Z)
        time.sleep(ZoomSleep)
        
    else:
      for Z in reversed(range(Z2,Z1)):
        gv.TheMatrix.Clear()        
        self.DisplayWindow(h,v,Z)
        time.sleep(ZoomSleep)
        


            
  def DisplayWindowWithSprite(self,h,v,ClockSprite):
    #This function accepts h,v coordinates for the entire map (e.g. 1,8  20,20,  64,64)    
    #Displays what is on the playfield currently, including walls, cars, etc.
    r = 0
    g = 0
    b = 0
    count = 0
        

    for V in range(0,gv.HatWidth):
      for H in range (0,gv.HatHeight):
         
        name = self.Playfield[v+V][h+H].name
        #print ("Display: ",name,V,H)
        if (name == 'EmptyObject'):
          r = 0
          g = 0
          b = 0          

        else:
          r = self.Playfield[v+V][h+H].r
          g = self.Playfield[v+V][h+H].g
          b = self.Playfield[v+V][h+H].b
          
        #Our map is an array of arrays [v][h] but we draw h,v
        gv.TheMatrix.SetPixel(H,V,r,g,b)

    #Display clock at current location
    #Clock hv will allow external functions to slide clock all over screen

    #print ("Clock info  hv on: ",ClockSprite.h,ClockSprite.v,ClockSprite.on)
    ClockSprite.CopySpriteToBuffer(ClockSprite.h,ClockSprite.v)
        
    #unicorn.show()
    #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)




  def CountVirusesInWindow(self,h,v):
    #This function accepts h,v coordinates for the entire map (e.g. 1,8  20,20,  64,64) 
    #and counts how many items are in the area
    count = 0
        
    for V in range(0,gv.HatWidth):
      for H in range (0,gv.HatHeight):
         
        name = self.Playfield[v+V][h+H].name
        #print ("Display: ",name,V,H)
        if (name not in ('EmptyObject',"Wall","WallBreakable")):
          count = count + 1
    return count;






  def DebugPlayfield(self):
    #Show contents of playfield - in text window, for debugging purposes
    
    width   = self.width 
    height  = self.height
    print ("Map width height:",width,height)
  
    x = 0
    y = 0
    
    for V in range(0,height):
      for H in range (0,width):
         
        name = self.Playfield[V][H].name
        #print ("Display: ",name,V,H)
        if (name == 'EmptyObject'):
          print ('  ',end='')

        #draw border walls
        elif (name == 'Wall' and (V == 0 or V == height-1)):
          print(' _',end='')
        
        #draw border walls
        elif (name == 'Wall' and (H == 0 or H == width-1)):
          print(' |',end='')
          
        #draw interior
        elif (name == 'Wall'):
          print (' #',end='')

        #draw interior
        elif (name == 'WallBreakable'):
          print (' o',end='')

        elif (self.Playfield[V][H].alive == 1):
          print (' .',end='')
        else:
          print (' X',end='')
          #print ("Name:",name," alive:",self.Playfield[V][H].alive)

          #time.sleep(1)

      print('')



  def FindClosestObject(self,SourceH,SourceV, Radius = 10, ObjectType = 'WallBreakable'):
    #Find the HV co-ordinates of the closest playfield object
    #
    #print("Searching for nearby food SourceH SourceV Radius ObjectType",SourceH, SourceV, Radius, ObjectType)
    #Prepare co-ordinates for search grid
    StartX = SourceH - Radius
    StopX  = SourceH + Radius
    StartY = SourceV - Radius
    StopY  = SourceV + Radius
    
    
    ClosestX     = -1
    ClosestY     = -1
    MinDistance  = 9999
    Distance     = 0

    #Check boundaries
    if (StartX < 0):
      StartX = 0
    if (StartX > gv.HatWidth-1):
      StartX = gv.HatWidth-1
    if (StartY < 0):
      StartY = 0
    if (StartY > gv.HatHeight-1):
      StartY = gv.HatHeight-1

    if (StopX < 0):
      StopX = 0
    if (StopX > gv.HatWidth-1):
      StopX = gv.HatWidth-1
    if (StopY < 0):
      StopY = 0
    if (StopY > gv.HatHeight-1):
      StopY = gv.HatHeight-1
        

    #print("Start XY Stop XY",StartX,StartY, StopX, StopY)
    
    for x in range(StartX,StopX):
      for y in range(StartY, StopY):
        #Look for object on the playfield
        #print ("searching xy: ",x,y, " found ",self.Playfield[y][x].name)

        #remember playfield coordinates are swapped
        if (self.Playfield[y][x].name == ObjectType):
          Distance = GetDistanceBetweenDots(SourceH,SourceV,x,y)
          #print ("Distance: ",Distance, " MinDistance:",MinDistance, "xy:",x,y)
          if (Distance <= MinDistance):
            MinDistance = Distance
            ClosestX = x
            ClosestY = y
      
    #FlashDot5(ClosestX,ClosestY,0.003)
    return ClosestX,ClosestY;


















class Virus(object):
  
  def __init__(self,h,v,dh,dv,r,g,b,direction,scandirection,speed,alive,lives,name,score,exploding,radarrange,destination,mutationtype,mutationrate,mutationfactor,replicationrate,mutationdeathrate):

    self.h               = h         # location on playfield (e.g. 10,35)
    self.v               = v         # location on playfield (e.g. 10,35)
    self.dh              = dh        # location on display   (e.g. 3,4) 
    self.dv              = dv        # location on display   (e.g. 3,4) 
    self.r               = r
    self.g               = g
    self.b               = b
    self.direction       = direction      #direction of travel
    self.scandirection   = scandirection  #direction of scanners, if equipped
    self.speed           = speed
    self.alive           = 1
    self.lives           = 3
    self.name            = name
    self.score           = 0
    self.exploding       = 0
    self.radarrange      = 20
    self.destination     = ""
    self.mutationtype    = mutationtype
    self.mutationrate    = mutationrate      #high number, greater chance 
    self.mutationfactor  = mutationfactor    #used to impact amount of mutation
    self.internalcounter = 0                 #used to count moves between mutation affects (i.e. turn left every 3 moves)
    self.replicationrate = replicationrate    
    self.mutationdeathrate = mutationdeathrate
    self.replications      = 0
    self.mutations         = 0
    self.infectionchance   = gv.InfectionChance
    self.chanceofdying     = gv.ChanceOfDying
    self.eating            = False
    self.clumping          = True


  def Display(self):
    if (self.alive == 1):
      gv.TheMatrix.SetPixel(self.h,self.v,self.r,self.g,self.b)
     # print("display HV:", self.h,self.v)
      #unicorn.show()
      #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
  
      
  def Erase(self):
    gv.TheMatrix.SetPixel(self.h,self.v,0,0,0)
    #unicorn.show()
    #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)


  #Lower is faster!
  def AdjustSpeed(self, increment):
    speed = self.speed + increment
    if (speed > gv.VirusBottomSpeed):
      speed = gv.VirusBottomSpeed
    elif (speed < gv.VirusTopSpeed):
      speed = gv.VirusTopSpeed

    self.speed = speed
    #print("Adjust speed: ",speed, increment)
    return;

  #Lower is faster!
  def AdjustInfectionChance(self, increment):
    infectionchance = self.infectionchance + increment

    if (infectionchance > gv.InfectionChance):
      infectionchance = gv.InfectionChance
    elif (infectionchance < 1):
      infectionchance = 1

    self.infectionchance = infectionchance
    return;



  def Mutate(self):
    global MaxMutations
    global MutationTypes

    x              = 0
    #number of possible mutations
    # direction
    #   - left 1,2
    #   - left 1,2,3
    #   - right 1,2
    #   - left 1,2,3
    # speed up
    # speed down
    # wobble
    # slow curves left
    # slow curves right
    

    mutationrate   = self.mutationrate
    mutationtype   = self.mutationtype
    mutationfactor = self.mutationfactor
    speed          = self.speed
    MinSpeed       = 1  #* gv.CPUModifier
    MaxSpeed       = 10 #* gv.CPUModifier   #higher = slower!
    r              = 0
    g              = 0
    b              = 0
    name           = 0


    #Mutations can be deadly
    self.mutations += 1
    if ((random.randint(1,self.mutationdeathrate) == 1)
       or (self.mutations >= gv.MaxMutations)):
      self.alive = 0
      self.lives = 0
      self.speed = 999999
      self.name  = 'EmptyObject'
      self.r     = 0
      self.g     = 0
      self.b     = 0
    else:


      #print ("--Virus mutation!--")
      mutationtype = random.randint(1,gv.MutationTypes)

      
      #Mutations get a new name and color
      x = random.randint(1,gv.MutationTypes)
      if (x == 1):
        #Big Red
        r = random.randint(gv.MinBright,gv.MaxBright)
        g = 0
        b = 0
        
      if (x == 2):
        #booger
        r = 0
        g = random.randint(gv.MinBright,gv.MaxBright)
        b = 0

      if (x == 3):
        #BlueWhale
        r = 0
        g = 0
        b = random.randint(gv.MinBright,gv.MaxBright)

      if (x == 4):
        #pinky
        r = random.randint(gv.MinBright,gv.MaxBright)
        g = 0
        b = random.randint(gv.MinBright,gv.MaxBright)

      if (x == 5):
        #MellowYellow
        r = random.randint(gv.MinBright,gv.MaxBright)
        g = random.randint(gv.MinBright,gv.MaxBright)
        b = 0

      if (x == 6):
        #undead
        r = 0
        g = random.randint(gv.MinBright,gv.MaxBright)
        b = random.randint(gv.MinBright,gv.MaxBright)



    
      #Directional Behavior - turns left a little
      if (mutationtype == 1):
        #print ("Mutation: turn left a little", self.speed, mutationfactor)
        mutationfactor       = random.randint(1,2)
        self.AdjustInfectionChance(mutationfactor * -1)

      #Directional Behavior - turns left a lot
      elif (mutationtype == 2):
        #print ("Mutation: turn left a lot", self.speed, mutationfactor)
        mutationfactor       = random.randint(2,3)
        self.AdjustInfectionChance(mutationfactor * -1)

      #Directional Behavior - turns right a little
      elif (mutationtype == 3):
        #print ("Mutation: turn right a little", self.speed, mutationfactor)
        mutationfactor    = random.randint(1,2)
        self.AdjustInfectionChance(mutationfactor * -1)

      #Directional Behavior - turns right a lot
      elif (mutationtype == 4):
        #print ("Mutation: turn right a lot", self.speed, mutationfactor)
        mutationfactor       = random.randint(2,3)
        self.AdjustInfectionChance(mutationfactor * -1)

      #Speed up and infect at a higher rate
      elif (mutationtype == 5):
        mutationfactor = 2
        self.AdjustInfectionChance(mutationfactor * -1)
        self.AdjustSpeed(mutationfactor * -1)
        #print ("Mutation: speed up", self.speed, mutationfactor)
        if (speed < 1):
          speed = 1

      #Speed down
      elif (mutationtype == 6):
        mutationfactor = 1
        self.AdjustSpeed(mutationfactor)
        self.AdjustInfectionChance(mutationfactor * -1)

        #print ("Mutation: slow down", self.speed, mutationfactor)

      #wobble
      elif (mutationtype == 7):
        mutationfactor = random.randint(1,10)
        self.clumping  = False
        #print ("Mutation: wobble",mutationfactor)
        self.AdjustSpeed(mutationfactor)
        self.AdjustInfectionChance(mutationfactor * -1)

        #swamp mix
        r = random.randint(gv.MinBright,gv.MaxBright)
        g = random.randint(gv.MinBright,gv.MaxBright)
        b = random.randint(gv.MinBright,gv.MaxBright)


      #slow turn left
      elif (mutationtype == 8):
        mutationfactor = random.randint(gv.SlowTurnMinMoves,gv.SlowTurnMaxMoves)  #higher is slower!
        #print ("Mutation: slow LEFT turn every (",mutationfactor,") moves")
        self.AdjustSpeed(1)
        #swamp mix
        r = random.randint(gv.MinBright,gv.MaxBright)
        g = random.randint(gv.MinBright,gv.MaxBright)
        b = random.randint(gv.MinBright,gv.MaxBright)


      #slow turn right
      elif (mutationtype == 9):
        mutationfactor = random.randint(gv.SlowTurnMinMoves,gv.SlowTurnMaxMoves)  #higher is slower!
        #print ("Mutation: slow righ turn every (",mutationfactor,") moves")
        self.AdjustSpeed(1)
        #swamp mix
        r = random.randint(gv.MinBright,gv.MaxBright)
        g = random.randint(gv.MinBright,gv.MaxBright)
        b = random.randint(gv.MinBright,gv.MaxBright)


      #Clumping on
      elif (mutationtype == 10):
        self.clumping = True
        self.AdjustSpeed(mutationfactor)
        #Purple Haze
        r = random.randint(gv.MinBright,gv.MaxBright)
        g = 0
        b = 255

        
      #Update common properties
      self.r              = r
      self.g              = g
      self.b              = b
      if (self.name != 'Wall' and self.name != 'WallBreakable'):
        self.name           = "" + str(self.r) + ' -' + str(self.g)+ ' -' + str(self.b)
      self.mutationtype   = mutationtype
      self.mutationfactor = mutationfactor
      #print ("TheSpeed: ",self.speed)
    
    return;



  def IncreaseBrightness(self,increment):
      
    self.r = self.r + (255 / self.r * increment)
    self.g = self.g + (255 / self.g * increment)
    self.b = self.b + (255 / self.b * increment)
    
    if (self.r > 255):
      self.r = 255
    if (self.g > 255):
      self.g = 255
    if (self.b > 255):
      self.b = 255
    



def VirusWorldScanAround(Virus,Playfield):
  # hv represent car location
  # ScanH and ScanV is where we are scanning
  
  #print ("== Scan in Front of Virus ==")
  
  ScanDirection = Virus.direction
  ScanH         = 0
  ScanV         = 0
  h             = Virus.h
  v             = Virus.v
  Item          = ''
  ItemList      = ['EmptyObject']
  count         = 0    #represents number of spaces to scan

#         2 1 3
#         5 x 6                              
#           4   
  
  #FlashDot2(h,v,0.005)

  #Scan in front
  ScanH, ScanV = CalculateDotMovement8Way(h,v,Virus.direction)
  ItemList.append(Playfield[ScanV][ScanH].name)
  
  
  #Scan left diagonal
  ScanDirection = TurnLeft8Way(Virus.direction)
  ScanH, ScanV = CalculateDotMovement8Way(h,v,ScanDirection)
  ItemList.append(Playfield[ScanV][ScanH].name)
  
  #Scan right diagonal
  ScanDirection = TurnRight8Way(Virus.direction)
  ScanH, ScanV = CalculateDotMovement8Way(h,v,ScanDirection)
  ItemList.append(Playfield[ScanV][ScanH].name)
  
  #Scan behind
  ScanDirection = ReverseDirection8Way(Virus.direction)
  ScanH, ScanV = CalculateDotMovement8Way(h,v,ScanDirection)
  ItemList.append(Playfield[ScanV][ScanH].name)
  
  #Scan left
  ScanDirection = TurnLeft8Way(TurnLeft8Way(Virus.direction))
  ScanH, ScanV = CalculateDotMovement8Way(h,v,ScanDirection)
  ItemList.append(Playfield[ScanV][ScanH].name)


  #Scan right
  ScanDirection = TurnRight8Way(TurnRight8Way(Virus.direction))
  ScanH, ScanV = CalculateDotMovement8Way(h,v,ScanDirection)
  ItemList.append(Playfield[ScanV][ScanH].name)


  return ItemList;




def IsThereAVirusNearby(h,v,direction,VirusName,Playfield):
  # hv represent desired target location
  # ScanH and ScanV is where we are scanning
  
  #print ("== Scan in Front of Virus ==")
  
  ScanDirection = direction
  ScanH         = 0
  ScanV         = 0

#         7 1 2
#         6 x 3                              
#         5 z 4    x = proposed location, z = current location
  

  #Scan in front
  ScanH, ScanV = CalculateDotMovement8Way(h,v,ScanDirection)
  if (Playfield[ScanV][ScanH].name == VirusName):
    return 1;
  
  
  #Scan front right diagonal
  ScanDirection = TurnRight8Way(ScanDirection)
  ScanH, ScanV = CalculateDotMovement8Way(h,v,ScanDirection)
  if (Playfield[ScanV][ScanH].name == VirusName):
    return 1;
  
  #Scan right 
  ScanDirection = TurnRight8Way(ScanDirection)
  ScanH, ScanV = CalculateDotMovement8Way(h,v,ScanDirection)
  if (Playfield[ScanV][ScanH].name == VirusName):
    return 1;
  
  #Scan behind right diagonal
  ScanH, ScanV = CalculateDotMovement8Way(h,v,ScanDirection)
  if (Playfield[ScanV][ScanH].name == VirusName):
    return 1;
  
  #We don't Scan behind because that is where the virus is!
  ScanDirection = TurnRight8Way(ScanDirection)
  ScanH, ScanV = CalculateDotMovement8Way(h,v,ScanDirection)
  #if (Playfield[ScanV][ScanH].name == VirusName):
  #  return 1;


  #Scan behind left diagonal
  ScanH, ScanV = CalculateDotMovement8Way(h,v,ScanDirection)
  if (Playfield[ScanV][ScanH].name == VirusName):
    return 1;


  #Scan left
  ScanDirection = TurnRight8Way(TurnRight8Way(ScanDirection))
  ScanH, ScanV = CalculateDotMovement8Way(h,v,ScanDirection)
  if (Playfield[ScanV][ScanH].name == VirusName):
    return 1;

  #Scan front left diagonal
  ScanH, ScanV = CalculateDotMovement8Way(h,v,ScanDirection)
  if (Playfield[ScanV][ScanH].name == VirusName):
    return 1;





def CountNearbyViruses(h,v,direction,VirusName,Playfield):
  #this function returns the number of viruses nearby with the same name
  # hv represent current location
  # ScanH and ScanV is where we are scanning
  
  #print ("== Scan in Front of Virus ==")
  
  ScanDirection = direction
  ScanH         = 0
  ScanV         = 0
  count         = 0
  

#         7 1 2
#         6 x 3                              
#         5 z 4    x = proposed location, z = current location
  

  #Scan in front
  ScanH, ScanV = CalculateDotMovement8Way(h,v,ScanDirection)
  if (Playfield[ScanV][ScanH].name == VirusName):
    count = count + 1
  
  
  #Scan front right diagonal
  ScanDirection = TurnRight8Way(ScanDirection)
  ScanH, ScanV = CalculateDotMovement8Way(h,v,ScanDirection)
  if (Playfield[ScanV][ScanH].name == VirusName):
    count = count + 1
  
  #Scan right 
  ScanDirection = TurnRight8Way(ScanDirection)
  ScanH, ScanV = CalculateDotMovement8Way(h,v,ScanDirection)
  if (Playfield[ScanV][ScanH].name == VirusName):
    count = count + 1
  
  #Scan behind right diagonal
  ScanH, ScanV = CalculateDotMovement8Way(h,v,ScanDirection)
  if (Playfield[ScanV][ScanH].name == VirusName):
    count = count + 1
  
  #Scan behind
  ScanDirection = TurnRight8Way(ScanDirection)
  ScanH, ScanV = CalculateDotMovement8Way(h,v,ScanDirection)
  if (Playfield[ScanV][ScanH].name == VirusName):
    count = count + 1


  #Scan behind left diagonal
  ScanH, ScanV = CalculateDotMovement8Way(h,v,ScanDirection)
  if (Playfield[ScanV][ScanH].name == VirusName):
    count = count + 1


  #Scan left
  ScanDirection = TurnRight8Way(TurnRight8Way(ScanDirection))
  ScanH, ScanV = CalculateDotMovement8Way(h,v,ScanDirection)
  if (Playfield[ScanV][ScanH].name == VirusName):
    count = count + 1

  #Scan front left diagonal
  ScanH, ScanV = CalculateDotMovement8Way(h,v,ScanDirection)
  if (Playfield[ScanV][ScanH].name == VirusName):
    count = count + 1

  return count;



def CountVirusesBehind(h,v,direction,VirusName,Playfield):
  #this function returns the number of viruses behind
  # hv represent current location
  # ScanH and ScanV is where we are scanning
  
  #print ("== Scan in Front of Virus ==")
  
  ScanDirection = direction
  ScanH         = 0
  ScanV         = 0
  count         = 0
  

#         . . .
#         . z .                              
#         1 2 3    z = current location
  

  #Scan behind left diagonal
  ScanDirection = TurnLeft8Way(ScanDirection)
  ScanH, ScanV = CalculateDotMovement8Way(h,v,ScanDirection)
  ScanDirection = TurnLeft8Way(ScanDirection)
  ScanH, ScanV = CalculateDotMovement8Way(h,v,ScanDirection)
  if (Playfield[ScanV][ScanH].name == VirusName):
    count = count + 1
  
  
  #Scan behind
  ScanDirection = TurnLeft8Way(ScanDirection)
  ScanH, ScanV = CalculateDotMovement8Way(h,v,ScanDirection)
  if (Playfield[ScanV][ScanH].name == VirusName):
    count = count + 1
  
  #Scan behind right diagonal
  ScanH, ScanV = CalculateDotMovement8Way(h,v,ScanDirection)
  if (Playfield[ScanV][ScanH].name == VirusName):
    count = count + 1
  

  return count;












# ----------------------
# -- Animated Sprites --
# ----------------------

class AnimatedSprite(object):
  def __init__(self,width,height,r,g,b,frames,grid):
    self.width  = width
    self.height = height
    self.r      = r
    self.g      = g
    self.b      = b
    self.frames = frames
    self.grid   = []

  def Display(self,h1,v1,frame):
    x = 0,
    y = 0

    #print ("Display:",self.width, self.height, self.r, self.g, self.b,v1,h1)
    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
      #print("Count:",count,"xy",x,y, " frame: ", frame)
      if self.grid[frame][count] == 1:
        if (CheckBoundary(x+h1,y+v1) == 0):
          gv.TheMatrix.SetPixel(x+h1,y+v1,self.r,self.g,self.b)
    #unicorn.show() 


  def DisplayNoBlack(self,h1,v1,frame):
    x = 0,
    y = 0

    #print ("Display:",self.width, self.height, self.r, self.g, self.b,v1,h1)
    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
      #print("Count:",count,"xy",x,y, " frame: ", frame)
      if self.grid[frame][count] == 1:
        if (CheckBoundary(x+h1,y+v1) == 0):
          if (not(self.r == 0 and self.g == 0 and self.b == 0)):
            gv.TheMatrix.SetPixel(x+h1,y+v1,self.r,self.g,self.b)
    #unicorn.show() 



  def Erase(self,h1,v1,frame):
    #This function draws a black sprite, erasing the sprite.  This may be useful for
    #a future "floating over the screen" type of sprite motion
    #It is pretty fast now, seems just as fast as blanking whole screen using off() or clear()
    x = 0
    y = 0
    #print ("Erase:",self.width, self.height, self.r, self.g, self.b,v1,h1)
    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
      #print("Count:",count,"xy",x,y)
      if self.grid[frame][count] == 1:
        if (CheckBoundary(x+h1,y+v1) == 0):
          #gv.TheMatrix.SetPixel(x+h1,y+v1,255,255,255)
          #unicorn.show()
          #time.sleep(0.05)
          gv.TheMatrix.SetPixel(x+h1,y+v1,0,0,0)

          
  def EraseSpriteFromPlayfield(self,Playfield):
    #Erase the sprite by writing 'EmptyObject' to every spot on the playfield occupied by the sprite
    x     = 0
    y     = 0
    count = 0



    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
      if (CheckBoundary(x+h1,y+v1) == 0):
        #gv.TheMatrix.SetPixel(x+h1,y+v1,0,0,0)
        Playfield[y+v1][x+h1] = gv.EmptyObject
        #FlashDot(x+h1,y+v1,0.002)
    return Playfield



  def HorizontalFlip(self):
    #Attempting to speed things up by disabling garbage collection
    gc.disable()
    for f in range(0,self.frames + 1):
      x = 0
      y = 0
      flipgrid = []
      #print ("flip:",self.width, self.height)
      for count in range (0,(self.width * self.height )):
        y,x = divmod(count,self.width)
        #print("Count:",count,"xy",x,y)
        #print("Calculations: ",(y*self.height)+ self.height-x-1)  
        flipgrid.append(self.grid[f][(y*self.height)+ self.height-x-1])  
      #print("Original:", str(self.grid[f]))
      #print("Flipped :", str(flipgrid))
      self.grid[f] = flipgrid      
    gc.enable()
          
  def Scroll(self,h,v,direction,moves,delay):
    #print("AnimatedSprite.scroll")
    x = 0
    oldh = 0
    #Capture Background
    Buffer = copy.deepcopy(unicorn.get_pixels())
    
    #modifier is used to increment or decrement the location
    if direction == "right" or direction == "down":
      modifier = 1
    else: 
      modifier = -1
    
    #print("Modifier:",modifier)
    
    #we use f to iterate the animation frames
    f = self.frames
    if direction == "left" or direction == "right":
      #print ("Direction: ",direction)  
      
      for count in range (0,moves):
        oldf = f
        f = f+1
        if (f > self.frames):
          f = 0
        h = h + (modifier)
        #erase old sprite
        #print ("Erasing Frame HV:",oldf," ",h,v)
        if count >= 1:
          oldh = h - modifier
          #print ("Scroll:",self.width, self.height, self.r, self.g, self.b,h,v)
          self.Erase(oldh,v,oldf)
        #draw new sprite
        setpixels(Buffer)
        self.Display(h,v,f)
        #unicorn.show() 
        #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
        time.sleep(delay)

        #Check for keyboard input
        r = random.randint(0,5)
        if (r == 0):
          Key = PollKeyboard()



  def ScrollWithFrames(self,h,v,direction,moves,delay):
    #print("Entering Scroll")
    x    = 0
    oldh = 0
    Buffer = copy.deepcopy(unicorn.get_pixels())
    
    #modifier is used to increment or decrement the location
    if direction == "right" or direction == "down":
      modifier = 1
    else: 
      modifier = -1
    
    #print("Modifier:",modifier)
    oldf = self.frames
    #we use f to iterate the animation frames
    f = self.frames
    if direction == "left" or direction == "right":
      for count in range (0,moves):
        #print ("Count:",count)
        if (count >= 1):
          oldh = h
          #print ("Erasing Frame: ", oldf, " hv: ",oldh,v)
          self.Erase(oldh,v,oldf+1)
        h = h + (modifier)
        #print ("incrementing H:",h)

        #Check for keyboard input
        r = random.randint(0,25)
        if (r == 0):
          Key = PollKeyboard()

        #Animate Each Frame
        for f in range (0, self.frames+1):
          #erase old sprite
          oldf = f-1
          if oldf < 0:
            oldf = self.frames
          #print ("Erasing Frame: ", oldf, " hv: ",h,v)
          self.Erase(h,v,oldf)
          setpixels(Buffer)
            
          #draw new sprite
          #print ("Display Frame: ", f, " hv: ",h,v)
          self.Display(h,v,f)
          #unicorn.show()
          #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)

          time.sleep(delay)
          self.Erase(h,v,f)

       
  
  def ScrollAcrossScreen(self,h,v,direction,ScrollSleep):
    if (direction == "right"):
      self.Scroll((0- self.width),v,"right",(gv.HatWidth + self.width),ScrollSleep)
    elif (direction == "left"):
      self.Scroll(gv.HatWidth-1,v,"left",(gv.HatWidth + self.width),ScrollSleep)
    elif (direction == "up"):
      self.Scroll(h,gv.HatWidth-1,"left",(gv.HatWidth + self.height),ScrollSleep)





  def Float(self,h,v,direction,moves,delay):
    #Scroll across the screen, floating over the background
    
    x = 0
    oldh = 0
    #Capture Background
    Buffer = copy.deepcopy(unicorn.get_pixels())
    
    #modifier is used to increment or decrement the location
    if direction == "right" or direction == "down":
      modifier = 1
    else: 
      modifier = -1
    
    #print("Modifier:",modifier)
    
    #we use f to iterate the animation frames
    f = self.frames
    if direction == "left" or direction == "right":
      #print ("Direction: ",direction)  
      
      for count in range (0,moves):
        oldf = f
        f = f+1
        if (f > self.frames):
          f = 0
        h = h + (modifier)
        #erase old sprite
        #print ("Erasing Frame HV:",oldf," ",h,v)
        setpixels(Buffer)

        if count >= 1:
          oldh = h - modifier
          #print ("Scroll:",self.width, self.height, self.r, self.g, self.b,h,v)
          
        #draw new sprite
        self.DisplayNoBlack(h,v,f)
        #unicorn.show() 
        #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
        time.sleep(delay)

        #Check for keyboard input
        r = random.randint(0,5)
        if (r == 0):
          Key = PollKeyboard()

  
  def FloatAcrossScreen(self,h,v,direction,ScrollSleep):
    if (direction == "right"):
      self.Float((0- self.width),v,"right",(gv.HatWidth + self.width),ScrollSleep)
    elif (direction == "left"):
      self.Float(gv.HatWidth-1,v,"left",(gv.HatWidth + self.width),ScrollSleep)
    elif (direction == "up"):
      self.Float(h,gv.HatWidth-1,"left",(gv.HatWidth + self.height),ScrollSleep)





  def Animate(self,h,v,delay,direction):
    x = 0,
    y = 0,
    Buffer = copy.deepcopy(unicorn.get_pixels())
    
    if (direction == 'forward'):
      for f in range (0,self.frames+1):
        self.Display(h,v,f)
        #unicorn.show()
        #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
        time.sleep(delay)
        setpixels(Buffer)
    else:  
      for f in range (0,self.frames+1):
        self.Display(h,v,(self.frames-f))
        #unicorn.show()
        #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
        time.sleep(delay)
        setpixels(Buffer)
      
      





      


# ----------------------------
# -- Color Animated Sprites --
# ----------------------------

class ColorAnimatedSprite(object):
  def __init__(self,h,v,name,width,height,frames,currentframe,framerate,grid):
    self.h      = h
    self.v      = v
    self.name   = name
    self.width  = width
    self.height = height
    self.frames = frames
    self.currentframe = currentframe
    self.framerate    = framerate #how many ticks per frame of animation, higher the number the slower the animation
    self.grid         = []        #holds numbers that indicate color of the pixel
    self.ticks        = 0         #used for calculating when the next frame should be displayed


  


  def Display(self,h1,v1):
    x = 0
    y = 0
    r = 0
    g = 0
    b = 0
    frame = self.currentframe
    
    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
      #print ("Name:",self.name," Frame:",frame, " Count: ",count, "Width Height",self.width,self.height )
      #print ("self.grid[frame][count]:",self.grid[frame][count] )
      if(self.grid[frame][count] >= 0):
        if (CheckBoundary((x+h1),y+v1) == 0):
          r,g,b =  ColorList[self.grid[frame][count]]
          #print ("CAS - Display - rgb",r,g,b)
          if (r > -1 and g > -1 and b > -1):
            gv.TheMatrix.SetPixel(x+h1,y+v1,r,g,b)
            setpixel(x+h1,y+v1,r,g,b)
    #unicorn.show() 


  def DisplayNoBlack(self,h1,v1):
    #Treat black pixels in sprite as transparent
    x = 0
    y = 0
    r = 0
    g = 0
    b = 0
    frame = self.currentframe
    
    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
      #print ("Name:",self.name," Frame:",frame, " Count: ",count, "Width Height",self.width,self.height )
      #print ("self.grid[frame][count]:",self.grid[frame][count] )
      if(self.grid[frame][count] >= 0):
        if (CheckBoundary((x+h1),y+v1) == 0):
          r,g,b =  ColorList[self.grid[frame][count]]
          #print ("CAS - Display - rgb",r,g,b)
          if (not(r == 0 and g == 0 and b == 0)):
            gv.TheMatrix.SetPixel(x+h1,y+v1,r,g,b)
    #unicorn.show() 


  def DisplayAnimated(self,h1 = -1, v1 = -1):
    #Treat black pixels in sprite as transparent -- maybe? Not yet.  Currently erasing.
    x = 0
    y = 0
    r = 0
    g = 0
    b = 0
    
    if (h1 < 0):
      h1 = self.h
    if (v1 < 0):
      v1 = self.v

    self.ticks = self.ticks + 1
   

    if (self.ticks == self.framerate):
      self.currentframe = self.currentframe + 1
      self.ticks        = 0

    if (self.currentframe >= self.frames):
      self.currentframe = 0


    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
      

      if (CheckBoundary((x+h1),y+v1) == 0):
        r,g,b =  ColorList[self.grid[self.currentframe][count]]
        gv.TheMatrix.SetPixel(x+h1,y+v1,r,g,b)

       

    
    return
   


  def Erase(self):
    #This function draws a black sprite, erasing the sprite.  This may be useful for
    #a future "floating over the screen" type of sprite motion
    #It is pretty fast now, seems just as fast as blanking whole screen using off() or clear()
    x = 0
    y = 0
    h1 = self.h
    v1 = self.v
    frame = self.currentframe
    #print ("CAS - Erase - width hieigh HV currentframe",self.width, self.height, h1,v1,frame)
    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
     # print("Count:",count,"xy",x,y)
     # print ("CAS - Erase Frame Count",frame,count)
      if self.grid[frame][count] > 0:
        if (CheckBoundary(abs(15-(x+h1)),y+v1) == 0):
         # print ("CAS - Erase HV:",x+h1,y+v1)
          gv.TheMatrix.SetPixel(x+h1,y+v1,0,0,0)

          
  def EraseLocation(self,h,v):
    x = 0
    y = 0
    frame = self.currentframe

    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)

 
      if self.grid[frame][count] > 0:
        if (CheckBoundary((x+h),y+v) == 0):
          #print ("CAS - EraseLocation HV:",x+h,y+v)
          gv.TheMatrix.SetPixel(x+h,y+v,0,0,0)
          

  def EraseSpriteFromPlayfield(self,Playfield):
    #Erase the sprite by writing 'EmptyObject' to every spot on the playfield occupied by the sprite
    x     = 0
    y     = 0
    count = 0


    width   = self.width 
    height  = self.height
    h       = self.h
    v       = self.v
    frame   = self.currentframe
  


    for count in range (0,(width * height)):
      y,x = divmod(count,width)

      if (CheckBoundary(x+h,y+v) == 0):
        gv.TheMatrix.SetPixel(x+h,y+v,0,0,0)
        Playfield[y+v][x+h] = gv.EmptyObject
    return Playfield



          
  def Scroll(self,h,v,direction,moves,delay):
    #print("CAS - Scroll -   HV Direction moves Delay", h,v,direction,moves,delay)
    x = 0
    oldh = 0
    r = 0
    g = 0
    b = 0
    
    #Capture Background
    Buffer = copy.deepcopy(unicorn.get_pixels())
    
    #modifier is used to increment or decrement the location
    if direction == "right" or direction == "down":
      modifier = 1
    else: 
      modifier = -1
    
    #print("Modifier:",modifier)
    
    #we use f to iterate the animation frames
    f = self.frames
    if direction == "left" or direction == "right":
      #print ("CAS - Scroll - Direction: ",direction)  
      
      for count in range (0,moves):
        #print ("CAS - Scroll - currentframe: ",self.currentframe)
        if (self.currentframe < (self.frames-1)):
          self.currentframe = self.currentframe + 1
        else:
          self.currentframe = 0
        h = h + (modifier)
        if count >= 1:
          oldh = h - modifier

        #draw new sprite
        #self.setpixels(Buffer)
          
        self.Display(h,v)
        #unicorn.show()
        #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
        time.sleep(delay)


  def ScrollWithFrames(self,h,v,direction,moves,delay):
    #print("CAS - ScrollWithFrames - HV direction moves delay", h,v,direction,moves,delay)
    x    = 0
    oldh = 0
    Buffer = copy.deepcopy(unicorn.get_pixels())
    self.currentframe = 0
    self.ticks = self.ticks + 1


    #modifier is used to increment or decrement the location
    if direction == "right" or direction == "down":
      modifier = 1
    else: 
      modifier = -1
    
    #print("Modifier:",modifier)
    oldf = self.frames
    #we use f to iterate the animation frames
    f = self.frames
    if direction == "left" or direction == "right":
      for count in range (0,moves):
        #print ("Count:",count)
        if (count >= 1):
          oldh = h
          h = h + (modifier)
          #print ("CAS - SWF - H oldh modifier",h,oldh,modifier)
        

        for f in range (0, self.frames+1):
          #erase old sprite
          #setpixels(Buffer)
          setpixels(Buffer)

          #draw new sprite
         #print ("CAS - SWF - currentframe: ",self.currentframe)
          self.Display(h,v)
          #unicorn.show()
          #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)

          #Increment current frame counter (taking into account framerate)
          
          m,r = divmod(self.ticks, self.framerate)
          if (r == 0):
            if (self.currentframe < (self.frames-1)):
              self.currentframe = self.currentframe + 1
            else:
              self.currentframe = 0
              self.ticks        = 0
              
          time.sleep(delay)
          
  def HorizontalFlip(self):
    #print ("CAS - Horizontalflip width heigh frames",self.width, self.height,self.frames)
    for f in range(0,self.frames):
      x = 0
      y = 0
      cells = (self.width * self.height)

      flipgrid = []
      #print ("Frame: ",f)
      #print ("cells: ",cells)
      for count in range (0,cells):
        y,x = divmod(count,self.width)
       #print("y,x = divmod(",count,self.width,"): ",y,x)
        #print ("cell to flip: ",((y*self.width)+ self.width-x-1), "value: ",self.grid[f][((y*self.width)+ self.width-x-1)])
        
        flipgrid.append(self.grid[f][((y*self.width)+ self.width-x-1)])  

      #print("Original:", str(self.grid[f]))
      #print("Flipped :", str(flipgrid))
      self.grid[f] = flipgrid      
    #print ("Done Flipping")
    
       
  
  def ScrollAcrossScreen(self,h,v,direction,ScrollSleep):
    if (direction == "right"):
      self.Scroll((0- self.width),v,"right",(gv.HatWidth + self.width),ScrollSleep)
    elif (direction == "left"):
      self.Scroll(gv.HatWidth-1,v,"left",(gv.HatWidth + self.width),ScrollSleep)
    elif (direction == "up"):
      self.Scroll(h,gv.HatWidth-1,"left",(gv.HatWidth + self.height),ScrollSleep)



  def Float(self,h,v,direction,moves,delay):
    #print("CAS - Scroll -   HV Direction moves Delay", h,v,direction,moves,delay)
    x = 0
    oldh = 0
    r = 0
    g = 0
    b = 0
    
    #Capture Background
    Buffer = copy.deepcopy(unicorn.get_pixels())
    
    #modifier is used to increment or decrement the location
    if direction == "right" or direction == "down":
      modifier = 1
    else: 
      modifier = -1
    
    #print("Modifier:",modifier)
    
    #we use f to iterate the animation frames
    f = self.frames
    if direction == "left" or direction == "right":
      #print ("CAS - Scroll - Direction: ",direction)  
      
      for count in range (0,moves):
        #print ("CAS - Scroll - currentframe: ",self.currentframe)
        if (self.currentframe < (self.frames-1)):
          self.currentframe = self.currentframe + 1
        else:
          self.currentframe = 0
        h = h + (modifier)
        if count >= 1:
          oldh = h - modifier

        #draw new sprite
        setpixels(Buffer)
          
        self.DisplayNoBlack(h,v)
        #unicorn.show()
        #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
        time.sleep(delay)



  def FloatAcrossScreen(self,h,v,direction,ScrollSleep):
    if (direction == "right"):
      self.Float((0- self.width),v,"right",(gv.HatWidth + self.width),ScrollSleep)
    elif (direction == "left"):
      self.Float(gv.HatWidth-1,v,"left",(gv.HatWidth + self.width),ScrollSleep)
    elif (direction == "up"):
      self.Float(h,gv.HatWidth-1,"left",(gv.HatWidth + self.height),ScrollSleep)


  def Animate(self,h,v,direction,delay):
   #print("CAS - Animate - HV delay ",h,v,delay,)
    x = 0,
    y = 0,
    Buffer = copy.deepcopy(unicorn.get_pixels())
    
    if (direction == 'forward'):
      for f in range (0,self.frames):
        #erase old sprite
        #setpixels(Buffer)
        #draw new sprite
        self.Display(h,v)
        #unicorn.show()
        #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)

        #Increment current frame counter
        if (self.currentframe < (self.frames-1)):
          self.currentframe = self.currentframe + 1
        else:
          self.currentframe = 0
          
        time.sleep(delay)
        

    else:  
      for f in range (0,self.frames+1):
        #erase old sprite
        #setpixels(Buffer)
        setpixels(Buffer)
        #draw new sprite
        #print ("CAS - Animate - currentframe: ",self.currentframe)
        self.Display(h,v)
        #unicorn.show()
        #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)

        #Increment current frame counter
        if (self.currentframe <= (self.frames-1)):
          self.currentframe = self.currentframe -1
        else:
          self.currentframe = self.frames
          
        #time.sleep(delay)
      

  #Draw the sprite using an affect like in the movie Tron 
  def LaserScan(self,h1,v1,speed):
    x = 0
    y = 0
    r = 0
    g = 0
    b = 0
    frame = self.currentframe
    #print ("CAS - LaserScan -")
    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
      if(self.grid[frame][count] >= 0):
        if (CheckBoundary((x+h1),y+v1) == 0):
          r,g,b =  ColorList[self.grid[frame][count]]
          if (r > 0 or g > 0 or b > 0):
            gv.TheMatrix.SetPixel((x+h1),y+v1,r,g,b)
            FlashDot4((x+h1),y+v1,speed)
      #unicorn.show() 
      #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
          
  def LaserErase(self,h1,v1,speed):
    x = 0
    y = 0
    r = 0
    g = 0
    b = 0
    frame = self.currentframe
    #print ("CAS - LaserErase -")
    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
      if(self.grid[frame][count] >= 0):
        if (CheckBoundary((x+h1),y+v1) == 0):
          r,g,b =  ColorList[self.grid[frame][count]]
          if (r > 0 or g > 0 or b > 0):
            FlashDot4((x+h1),y+v1,speed * 0.001)
            gv.TheMatrix.SetPixel((x+h1),y+v1,0,0,0)
      #unicorn.show() 
      #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)



    #unicorn.show() 

  def CopyAnimatedSpriteToPlayfield(self,Playfield, TheObject):
    #Copy an animated sprite to the Playfield. 
    #Animated can have different shapes per frame
    #Each spot on the playfield will contain a reference to the objecttype e.g. a ship

    width   = self.width 
    height  = self.height
    h       = TheObject.h - (width // 2)
    v       = TheObject.v - (height // 2)
    frame   = self.currentframe
  
    #Copy sprite to playfield
    for count in range (0,(width * height)):
      y,x = divmod(count,width)

      if(self.grid[frame][count] >= 0):
        if (CheckBoundary((x+h),y+v) == 0):
          r,g,b =  ColorList[self.grid[frame][count]]
          if (r > -1 and g > -1 and b > -1):
              Playfield[y+v][x+h] = TheObject
              #gv.TheMatrix.SetPixel(x+h1,y+v1,r,g,b)
          else:
              Playfield[y+v][x+h] = EmptyObject('EmptyObject')
              gv.TheMatrix.SetPixel(x+h1,y+v1,r,g,b)

           
    return Playfield;



# --------------------------
# -- Dot and Ship Sprites --
# --------------------------
      
      
class Dot(object):
  def __init__(self,h,v,r,g,b,direction,speed,alive,name,trail,score,maxtrail,erasespeed,HeadRGB=(100,100,100)):
    self.h          = h 
    self.v          = v
    self.r          = r
    self.g          = g
    self.b          = b
    self.direction  = direction
    self.speed      = speed
    self.alive      = 1
    self.name       = name
    self.trail      = [] # a list of tuples, holding hv coordinates of the dot trail
    self.score      = 0
    self.maxtrail   = 0
    self.erasespeed = erasespeed #sleep time for the erase trail function
    self.HeadRGB    = HeadRGB
    self.score      = 0




  def Display(self):
    #print("hv rgb",self.h,self.v,"-",self.r,self.g,self.b)

    gv.TheMatrix.SetPixel(self.h,self.v,self.r,self.g,self.b)
    gv.ScreenArray[self.v][self.h] = (self.r,self.g,self.b)


    #r,g,b = self.HeadRGB
    #gv.TheMatrix.SetPixel(self.h,self.v,r,g,b)
    
      
  def EraseTrail(self,direction,flash):
    r = self.r
    g = self.g
    b = self.b
    
    
    #Turn trail bright, then gradually fade
    if (flash == 'flash'):
      for x in range(25):
        newr = r + (100) - (2*x-1)
        newg = g + (100) - (2*x-1)
        newb = b + (100) - (2*x-1)
        if (newr > 255):
          newr = 255
        if (newg > 255):
          newg = 255
        if (newb > 255):
          newb = 255
        if (newr < r):
          newr = r 
        if (newg < g):
          newg = g
        if (newb < b):
          newb = b
          
        for i,dot in enumerate(self.trail):
          h = dot[0]
          v = dot[1]
          gv.TheMatrix.SetPixel(h,v,newr,newg,newb)
          gv.ScreenArray[v][h] = (newr,newg,newb)
          

      
    #Erase 
    if (direction == 'forward'):
      #print ("Erasing Trail: forward")
      #for i,dot in enumerate(self.trail):

#--> we need a faster way to go through the trail

      count = len(self.trail)
      for i in range (0,count):
        h = self.trail[i][0]
        v = self.trail[i][1]
                        
        gv.TheMatrix.SetPixel(h,v,255,255,255)
        time.sleep(self.erasespeed)
        gv.TheMatrix.SetPixel(h,v,0,0,0)
        gv.ScreenArray[v][h] = (0,0,0)
        

      
    else:
      print ("Erasing Trail: backward")
      count = len(self.trail)
      for i in range (count-1,0,-1):
        h = self.trail[i][0]
        v = self.trail[i][1]


      #for i,dot in reversed(list(enumerate(self.trail))):
        #h = dot[0]
        #v = dot[1]
        gv.TheMatrix.SetPixel(h,v,255,255,255)
        
        time.sleep(self.erasespeed)
        gv.TheMatrix.SetPixel(h,v,0,0,0)
        gv.ScreenArray[v][h] = (0,0,0)


  def ReverseWorm(self):
    self.h,self.v = self.trail[0]
    self.trail.reverse()
    self.direction = ReverseDirection(self.direction)
    #ShowScreenArray()
      
  def ColorizeTrail(self,r,g,b):
    print ("Colorize Trail: this loop seems wrong.  ")
    for i,dot in enumerate(self.trail):
      h = dot[0]
      v = dot[1]
      gv.TheMatrix.SetPixel(h,v,r,g,b)
      gv.ScreenArray[v][h] = (r,g,b)

    time.sleep(self.erasespeed * 1.5)
    
  def DisplayTrail(self):
      count = len(self.trail)
      print ("Displaying Trail:",count," dots")
      for i in range (0,count):
        h = self.trail[i][0]
        v = self.trail[i][1]
                        
        gv.TheMatrix.SetPixel(h,v,self.r,self.g,self.b)
        gv.ScreenArray[v][h] = (self.r,self.g,self.b)




  def Resurrect(self):
    #This function is used to bring a superworm back from the dead

    #Find and empty spot
    resurrected = 'N'
    count       = 0
    
    while (resurrected == 'N' and count <= gv.ResurrectionTries):
      count = count + 1
      h = random.randint(0,gv.HatWidth-1)
      v = random.randint(0,gv.HatHeight-1)
      r,g,b = getpixel(h,v)
      if (r == 0 and g == 0 and b == 0):
        resurrected = 'Y'
        self.alive     = 1
        self.h         = h
        self.v         = v
        self.direction = (random.randint(1,4))
        self.trail     = []
        self.trail     = [(h,v)]
        self.maxtrail  = gv.ResurrectedMaxTrail
        self.speed     = gv.StartSpeedLow
      
        print ("A holy resurrection!")


    return


  def IncreaseMaxTrailLength(self,length):
    if (self.maxtrail < gv.MaxTrailLength):
      self.maxtrail = self.maxtrail + 1
      

  def SetStartingPoint(self):
    done = 'N'
    while (done == 'N'):
      h = random.randint(gv.SuperWormStartMinH,gv.SuperWormStartMaxH)
      v = random.randint(gv.SuperWormStartMinV,gv.SuperWormStartMaxV)
      r,g,b = getpixel(h,v)

      if (r == 0 and g == 0 and b == 0):
        self.h         = h
        self.v         = v
        done = 'Y'


  def TrimTrail(self):
    if (len(self.trail) >= self.maxtrail):
      h,v = self.trail[0]
      setpixel(h,v,0,0,0)
      del self.trail[0]


  def Kill(self):
    self.alive = 0
    self.EraseTrail('forward','flash')
    setpixel(self.h,self.v,0,0,0)



      
class Ship(object):
  def __init__(self,h,v,r,g,b,direction,scandirection,speed,alive,lives,name,score,exploding):
    self.h          = h 
    self.v          = v
    self.r          = r
    self.g          = g
    self.b          = b
    self.direction  = direction
    self.scandirection = scandirection
    self.speed      = speed
    self.alive      = 1
    self.lives      = 1
    self.name       = name
    self.score      = 0
    self.exploding  = 0
    self.dropped    = 0
    

  def Display(self):
    #print("display HV:", self.h,self.v)

    if (self.alive == 1):
      gv.TheMatrix.SetPixel(self.h,self.v,self.r,self.g,self.b)
      gv.ScreenArray[self.v][self.h] = (self.r,self.g,self.b)
      

      
      
  def Erase(self):
    if (CheckBoundary(self.h,self.v) == 0):
      gv.TheMatrix.SetPixel(self.h,self.v,0,0,0)
      gv.ScreenArray[self.v][self.h] = (0,0,0)
    
      
  def Flash(self):
    sleep = gv.FlashSleep * 0.75
    LowR  = int(self.r * 0.75)
    LowG  = int(self.g * 0.75)
    LowB  = int(self.b * 0.75)
    HighR = int(self.r * 1.5)
    HighG = int(self.g * 1.5)
    HighB = int(self.b * 1.5)
    
    if (LowR < 0 ):
      LowR = 0
    if (LowG < 0 ):
      LowG = 0
    if (LowB < 0 ):
      LowBB = 0
    
    if (HighR > 255):
      HighR = 255
    if (HighG > 255):
      HighG = 255
    if (HighB > 255):
      HighB = 255
      
    gv.TheMatrix.SetPixel(self.h,self.v,HighR,HighG,HighB)
    #unicorn.show()
    #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
    time.sleep(sleep)
    gv.TheMatrix.SetPixel(self.h,self.v,self.r,self.g,self.b)
    #unicorn.show()
    gv.TheMatrix.SetPixel(self.h,self.v,LowR,LowG,LowB)
    #unicorn.show()
    time.sleep(sleep)
    #unicorn.show()
    gv.TheMatrix.SetPixel(self.h,self.v,HighR,HighG,HighB)
    #unicorn.show()
    time.sleep(sleep)
    gv.TheMatrix.SetPixel(self.h,self.v,self.r,self.g,self.b)
    #unicorn.show()
    gv.TheMatrix.SetPixel(self.h,self.v,LowR,LowG,LowB)
    #unicorn.show()
    time.sleep(sleep)
    #unicorn.show()
    #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
  


# I tried including a color animated sprite in this class, but could
# not figure out the syntax.
# The workaround is to simply define a ship sprite that goes along with this object
class AnimatedShip(object):
  def __init__(self,h,v,direction,scandirection,speed,alive,lives,name,score,exploding):
    self.h              = h 
    self.v              = v
    self.direction      = direction
    self.scandirection  = scandirection
    self.speed          = speed
    self.alive          = 1
    self.lives          = 3
    self.name           = name
    self.score          = 0
    self.exploding      = 0
    

     
class Wall(object):
  def __init__(self,h,v,r,g,b,alive,lives,name):
    self.h          = h 
    self.v          = v
    self.r          = r
    self.g          = g
    self.b          = b
    self.alive      = 1
    self.lives      = lives
    self.name       = name
    

  def Display(self):
    if (self.alive == 1):
      gv.TheMatrix.SetPixel(self.h,self.v,self.r,self.g,self.b)


      
  def Erase(self):
    gv.TheMatrix.SetPixel(self.h,self.v,0,0,0)

      
  def IncreaseBrightness(self,increment):
      
    self.r = (self.r + increment)
    self.g = (self.g + increment)
    self.b = (self.b + increment)
    
    if (self.r > 255):
      self.r = 255
    if (self.g > 255):
      self.g = 255
    if (self.b > 255):
      self.b = 255
    




class Door(object):
  def __init__(self,h,v,alive,locked,name):
    self.h          = h 
    self.v          = v
    self.alive      = 1
    self.locked     = 0
    self.name       = name

  def Display(self):
    #print("Door.Display - alive locked",self.alive,self.locked)
    if (self.alive == 1):
    
      if (self.locked == 1):
        gv.TheMatrix.SetPixel(self.h,self.v,SDLowPurpleR,SDLowPurpleG,SDLowPurpleB)
      else:
        gv.TheMatrix.SetPixel(self.h,self.v,SDDarkYellowR,SDDarkYellowG,SDDarkYellowB)
      
    

      
  def Erase(self):
    gv.TheMatrix.SetPixel(self.h,self.v,0,0,0)
    

      
      
# ----------------------------
# -- World Object           --
# ----------------------------

#DotZerk uses this one

class World(object):
  def __init__(self,name,width,height,Map,Playfield,CurrentRoomH,CurrentRoomV,DisplayH, DisplayV):
    self.name      = name
    self.width     = width
    self.height    = height
    self.Map       = ([[]])
    self.Playfield = ([[]])
    self.CurrentRoomH = 0
    self.CurrentRoomV = 0
    self.DisplayH     = 0
    self.DisplayV     = 0
    
    #(h,v,alive,locked,name):
    self.Door1 = Door(7,0,0,0,'Door')
    self.Door2 = Door(15,7,0,0,'Door')
    self.Door3 = Door(7,15,0,0,'Door')
    self.Door4 = Door(0,7,0,0,'Door')

    
    self.Map = [[0 for i in range(width)] for i in range(height)]

    #Playfield is the physical size of the Unicorn Hat (only in this game)
    self.Playfield = [[0 for i in range(gv.HatWidth)] for i in range(gv.HatWidth)]

  def Display(self):
    if (self.alive == 1):
      gv.TheMatrix.SetPixel(self.h,self.v,self.r,self.g,self.b)
      #unicorn.show()
    

  def DisplayWindow(self,h,v):
  
  #--> this is only the request to display.  The actual co-ordinates need to be fixed!
  
  
    #This function accepts h,v coordinates for the entire map (e.gv. 1,8  20,20,  64,64)    
    #The window to be displayed starts at the input co-ordinates and is HatWitdth x gv.HatHeight in size from that point.
    #hv = location on map/playfield
    #HV = physical screen.  
    #check boundaries
    
    #print ("DisplayWindow h v gv.HatWidth self.width: ",h,v,gv.HatWidth,self.width)
    #Check Boundaries
    if (h + gv.HatWidth >= self.width):
      print ("WIDTH ERROR: Invalid coordinates passed to DisplayWindow hv: ",h,v)
      h = self.width - gv.HatWidth
    if (v + gv.HatHeight >= self.height):
      print ("HEIGHT ERROR: Invalid coordinates passed to DisplayWindow hv: ",h,v)
      v = self.height - gv.HatHeight


    for V in range(0,gv.HatWidth):
      for H in range (0,gv.HatHeight):
        #The map was created visually for me the programmer
        #turns out the H and V are swapped.  Sorry!
        #print("WO - Display Window - HV hv",H,V,h,v)
          
        #print ("DisplayWindow - HV hv:",H,V,h,v)
        try:
          SDColor = self.Map[V+v][H+h]
          #print ("SDColor: ",SDColor)
        except:
          print ("########################")
          print ("ERROR: Diplay Window function encountered an out of index error.  HV hv",H,V,h,v)
        
        r,g,b =  ColorList[SDColor] 
        #print("WO - Display Window - SDColor rgb",SDColor,r,g,b)
        gv.TheMatrix.SetPixel(H,V,r,g,b)
        
  #WALL(h,v,r,g,b,alive,lives,name):
           
  def CopyMapToPlayfield(self):
    
        
    h = self.CurrentRoomH * gv.HatWidth
    v = self.CurrentRoomV * gv.HatWidth
    V = 0
    H = 0
    self.Door1.alive = 0
    self.Door2.alive = 0
    self.Door3.alive = 0
    self.Door4.alive = 0

    
    
    #print ("WO - self.CurrentRoomHV:",h,v,"==============================================")
    for V in range(0,gv.HatWidth):
      for H in range (0,gv.HatWidth):
        #print ("WO - CopyMapToPlayfield - Map[",V+v,"][",H+h,"] SDColor:",self.Map[V+v][H+h])
        
        if (self.Map[V+v][H+h] != 0):
          SDColor = self.Map[V+v][H+h]
          r,g,b =  ColorList[SDColor]
          #print ("WO - CopyMapToPlayfield - V+v H+h (rgb)",V+v,H+h,"(",r,g,b,")")
          
          #Doors are represented by SDLowYellow (21)
          #I decided to force their positions in order to cut down the complexity
          #They are alive if a door exists, otherwise the space is treated as a wall
          if (SDColor == 21):
            #print ("WO - CopyMapToPlayfield - placing door")
            if (H == 7 and V == 0):
              #print ("###Door1#########################################################################")
              self.Door1.alive = 1
              self.Door1.locked == 0
              self.Playfield[H][V] = self.Door1
            if (H == 15 and V == 7):
              #print ("###Door2#########################################################################")
              self.Door2.alive = 1
              self.Door2.locked == 0
              self.Playfield[H][V] = self.Door2
            if (H == 7 and V == 15):
              #print ("###Door3#########################################################################")
              self.Door3.alive = 1
              self.Door3.locked == 0
              self.Playfield[H][V] = self.Door3
            if (H == 0 and V == 7):
              #print ("###Door4#########################################################################")
              self.Door4.alive = 1
              self.Door4.locked == 0
              self.Playfield[H][V] = self.Door4
          
            #print ("Door1.alive:",Door1.alive)
            #print ("Door2.alive:",Door2.alive)
            #print ("Door3.alive:",Door3.alive)
            #print ("Door4.alive:",Door4.alive)
          
          else:
            self.Playfield[H][V] = Wall(H,V,r,g,b,1,1,'Wall')
            #print ("WO - CopyMapToPlayfield - placing wall")

          
      
      
  def DisplayPlayfield(self,ShowFlash):
    #print ("WO - Display Playfield")
    for y in range (0,gv.HatWidth):
      for x in range (0,gv.HatWidth):
        #print("WO - DisplayPlayfield XY: ",x,y,self.Playfield[x][y].name)
        if (self.Playfield[x][y].name == 'Door' ):
          print ("WO - DisplayPlayfield - Door found locked:",self.Playfield[x][y].locked)
        if (self.Playfield[x][y].name != 'EmptyObject' ):
          self.Playfield[x][y].Display()
          #unicorn.show()
          #print ("WO - DisplayPlayfield - self.Playfield[x][y].hv",self.Playfield[x][y].h,self.Playfield[x][y].v)
          if (ShowFlash == 1):
            FlashDot4(x,y,0.001)
          
          

  
    
  

  
  def ScrollMapRoom(self,direction,speed):

    ScrollH = 0
    SCrollV = 0

    #Scroll Up
    if (direction == 1):
      self.CurrentRoomV = self.CurrentRoomV - 1

      ScrollH = self.CurrentRoomH *gv.HatWidth
      ScrollV = self.CurrentRoomV *gv.HatWidth
          
      #We display the window gv.HatWidth times, moving it one column every time
      #this gives a neat scrolling effect
      for x in range (ScrollV+gv.HatWidth,ScrollV-1,-1):
        #print ("DZER X:",x)
        #print ("DZER ScrollMapRoom calling DisplayWindow ScrollH x:",ScrollH,x)
        self.DisplayWindow(ScrollH,x)
        #unicorn.show()
        #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
        
        #time.sleep(speed)
       

    
    #Scroll Down
    if (direction == 3):
      self.CurrentRoomV = self.CurrentRoomV + 1

      ScrollH = self.CurrentRoomH *gv.HatWidth
      ScrollV = self.CurrentRoomV *gv.HatWidth
          
      #We display the window 8 times, moving it one column every time
      #this gives a neat scrolling effect
      for x in range (ScrollV-gv.HatWidth,ScrollV+1):
        #print ("DZER X:",x)
        #print ("DZER calling DisplayWindow ScrollH x:",ScrollH,x)
        self.DisplayWindow(ScrollH,x)
        #unicorn.show()
        #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
        #time.sleep(speed)
      
    #Scroll right
    if (direction == 2):
      self.CurrentRoomH = self.CurrentRoomH + 1

      ScrollH = self.CurrentRoomH *gv.HatWidth
      ScrollV = self.CurrentRoomV *gv.HatWidth
          
      #We display the window gv.HatWidth times, moving it one column every time
      #this gives a neat scrolling effect
      for x in range (ScrollH-gv.HatWidth,ScrollH+1):
        #print ("DZER X:",x)
        #print ("DZER calling DisplayWindow x ScrollV:",x,ScrollV)
        self.DisplayWindow(x,ScrollV)
        #unicorn.show()
        #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
        #time.sleep(speed)
      
    
    #Scroll left
    elif (direction == 4):
      self.CurrentRoomH = self.CurrentRoomH -1
      ScrollH = self.CurrentRoomH *gv.HatWidth
      ScrollV = self.CurrentRoomV *gv.HatWidth
      #print("DZER - ScrollHV",ScrollH,ScrollV)
      for x in range (ScrollH+gv.HatWidth-1,ScrollH-1,-1):
        #print ("DZER X:",x)
        #print ("DZER calling DisplayWindow x ScrollV:",x,ScrollV)
        self.DisplayWindow(x,ScrollV)
        #unicorn.show()
        #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
        #time.sleep(speed)

        
        
        
        
        
        
        
        
        
            
# ----------------------------
# -- GameWorld Object       --
# ----------------------------

#Rallydot

#The GameWorld object 4s the entire game layout, the map, the playfield, etc.
#The map is how we draw the roads and structures.  The playfield holds all the objects currently in play.
#The playfield is populated with map objects (loaded from the map, they may have extra properties such as getting destroyed) and player objects
#A window into the playfield is then displayed on the unicorn hat grid.


class EmptyObject(object):
  def __init__(self,name='EmptyObject'):
    self.name  = name
    self.alive = 0
    self.lives = 0
    self.direction = 0
    self.h          = -1 
    self.v          = -1
    self.r          = 0
    self.g          = 0
    self.b          = 0
    self.scandirection = 0
    self.speed      = 0
    self.score      = 0
    self.exploding  = 0
    self.dropped    = 0

    
    
    
class GameWorld(object):
  def __init__(self,name,width,height,Map,Playfield,CurrentRoomH,CurrentRoomV,DisplayH, DisplayV):
    self.name      = name
    self.width     = width
    self.height    = height
    self.Map       = ([[]])
    self.Playfield = ([[]])
    self.CurrentRoomH = 0
    self.CurrentRoomV = 0
    self.DisplayH     = 0
    self.DisplayV     = 0
    
    
    #print ("RD - Initialize map and playfield  width height: ",self.width, self.height)
    self.Map       = [[0 for i in range(self.width)] for i in range(self.height)]
    self.Playfield = [[EmptyObject('EmptyObject') for i in range(self.width)] for i in range(self.height)]

    #print ("--Initializing map--")
    #print (*self.Map[0])
    #print (*self.Map[2])
    #print ("Map Length: ",len(self.Map[0]))
    #print ("Playfield Length",len(self.Playfield[0]))
    #print ("-------------------")
    

    
    
    
    
    

  def DisplayExplodingObjects(self,h,v):
    #This function accepts h,v coordinates for the entire map (e.gv. 1,8  20,20,  64,64)    
    #Displays what is on the playfield currently, including walls, cars, etc.
    r = 0
    g = 0
    b = 0
    count = 0

    for V in range(0,gv.HatHeight):
      for H in range (0,gv.HatWidth):
        if (v+V < self.height and h+H < self.height):
          name = self.Playfield[v+V][h+H].name
        
          if (name in ("Enemy") and self.Playfield[v+V][h+H].exploding == 1):
            #print("Exploding Object - h,v,name ",h,v,name)
            r = 0
            g = 0
            b = 0          
            
            #EXPLODE ENEMY CAR BOMBS
            #Source Car blows up
            self.Playfield[v+V][h+H].exploding = 0
            self.Playfield[v+V][h+H].lives = 0
            self.Playfield[v+V][h+H].alive = 0
            gv.TheMatrix.SetPixel(H,V,255,255,255)
            #remove dead object from playfield
            self.Playfield[v+V][h+H] = EmptyObject('EmptyObject') 
    #unicorn.show()
    #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)


    return;    
    
    

  def DisplayWindow(self,h,v):
    #This function accepts h,v coordinates for the entire map (e.gv. 1,8  20,20,  64,64)    
    #Displays what is on the playfield currently, including walls, cars, etc.
    r = 0
    g = 0
    b = 0
    count = 0


    #HV = 0-15
    #hv = position on playfield (virtual map)    

    for V in range(0,gv.HatHeight):
      for H in range (0,gv.HatWidth):
        #print("WO - Display Window - HV hv",H,V,h,v)
         
        if (v+V < self.height and h+H < self.height):
        
          name = self.Playfield[v+V][h+H].name
          
          if (name == 'EmptyObject'):
            r = 0
            g = 0
            b = 0          

          else:
            r = self.Playfield[v+V][h+H].r
            g = self.Playfield[v+V][h+H].g
            b = self.Playfield[v+V][h+H].b
            
          #Our map is an array of arrays [v][h] but we draw h,v
          gv.TheMatrix.SetPixel(H,V,r,g,b)
    
    #unicorn.show()
    #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
    return;
    
  def DisolveWindow(self,h,v,sleep):
    #This function accepts h,v coordinates for the entire map (e.gv. 1,8  20,20,  64,64)    
    #Draw the window with fancy effects
    r = 255
    g = 255
    b = 255
    count = 0


    #HV = 0-15
    #hv = position on playfield (virtual map)    

    for V in range(0,gv.HatHeight):
      for H in range (0,gv.HatWidth):
        #print("WO - Display Window - HV hv",H,V,h,v)
         
        if (v+V < self.height and h+H < self.height):
          name = self.Playfield[v+V][h+H].name
          
          if (name != 'EmptyObject'):
            gv.TheMatrix.SetPixel(H,V,r,g,b)
            #unicorn.show()
            #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
            time.sleep(sleep)
            gv.TheMatrix.SetPixel(H,V,0,0,0)
    #unicorn.show()
    #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
    return;
    

    
    
    
  def DisplayWindowWithSprite(self,h,v,TheSprite):
    #This function accepts h,v coordinates for the entire map (e.gv. 1,8  20,20,  64,64)    
    #Displays what is on the playfield currently, including walls, cars, etc.
    r = 0
    g = 0
    b = 0
    count = 0
        

    for V in range(0,gv.HatWidth):
      for H in range (0,gv.HatHeight):
        
                
        name = self.Playfield[v+V][h+H].name
        #print ("Display: ",name,V,H)
        if (name == 'EmptyObject'):
          r = 0
          g = 0
          b = 0          

        else:
          r = self.Playfield[v+V][h+H].r
          g = self.Playfield[v+V][h+H].g
          b = self.Playfield[v+V][h+H].b
          
        #Our map is an array of arrays [v][h] but we draw h,v
        gv.TheMatrix.SetPixel(H,V,r,g,b)

    #Display sprite at current location
    #sprite hv will allow external functions to slide sprite all over screen

    #print ("Clock info  hv on: ",TheSprite.h,TheSprite.v,TheSprite.on)
    TheSprite.CopySpriteToBuffer(TheSprite.h,TheSprite.v)
        
    #unicorn.show()
    #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)


    
        

        
        
        
        
        
  def UpdateObjectDisplayCoordinates(self,h,v):
    #This function looks at a window (an 8x8 display grid for the unicorn hat)
    #and updates the dh,dv location information for objects in that grid
    #This is useful if we want to blow something up on screen
    
    #scroll off
    for V in range(0,gv.HatHeight):
      for H in range (0,gv.HatWidth):
        name = self.Playfield[v+V][h+H].name
        if (name == "Player" or name == "Enemy" or name == "Fuel"):
          self.Playfield[v+V][h+H].dh = H
          self.Playfield[v+V][h+H].dv = V
          

  
  def CopyMapToPlayfield(self):
    #This function is run once to populate the playfield with wall objects, based on the map drawing
    #XY is actually implemented as YX.  Counter intuitive, but it works.

    width  = self.width 
    height = self.height 
   
    #print ("RD - CopyMapToPlayfield - Width Height: ", width,height)
    x = 0
    y = 0
    
    
    #print ("width height: ",width,height)
    
    for y in range (0,height):
      #print ("-------------------")
      #print (*self.Map[y])
  
      for x in range(0,width):
        #print ("RD xy color: ",x,y, self.Map[y][x])
        SDColor = self.Map[y][x]
        
        
  
        if (SDColor != 0):
          #print ("Wall")
          r,g,b =  ColorList[SDColor]
          #print ("RD xy: ",x,y," rgb(",r,g,b,")")
          self.Playfield[y][x] = Wall(x,y,r,g,b,1,1,'Wall')
        else:
          #print ('EmptyObject')
          self.Playfield[y][x] = EmptyObject('EmptyObject')
          
          
          
         
      
      
          
          
  def ScrollMapDots(self,direction,dots,speed):

    #we only want to scroll the number of dots, not the whole room
    #DisplayWindow has HV starting in upper left hand corner
    
    x = 0
    ScrollH = self.DisplayH
    ScrollV = self.DisplayV

    #print("ScrollMapDots - ScrollH ScrollV direction width",ScrollH,ScrollV, direction, self.width)
     
    #Scroll Up
    if (direction == 1):
      
      if (ScrollV - dots >= 0):
      
        for x in range (ScrollV-1,ScrollV-dots-1,-1):
          #print ("ScrollMapDots up: ScrollH x",ScrollH,x)
          self.DisplayWindow(ScrollH,x)
        ScrollV = x
         

    
    #Scroll Down
    if (direction == 3):
          
      if (ScrollV + gv.HatWidth + dots <= self.height):
        for x in range (ScrollV+1,ScrollV+dots+1):
          #print ("ScrollMapDots down: ScrollH x",ScrollH,x)
          self.DisplayWindow(ScrollH,x)
        ScrollV = x
      
    #Scroll right
    if (direction == 2):
      if (ScrollH + gv.HatWidth + dots  <= self.width):
        for x in range (ScrollH+1,ScrollH+dots+1):
          #print ("ScrollMapDots right: x ScrollV",x,ScrollV)
          self.DisplayWindow(x,ScrollV)
        ScrollH = x
      
    
    #Scroll left
    elif (direction == 4):
      if (ScrollH - dots >= 0):
        for x in range (ScrollH-1,ScrollH-dots-1,-1):
          #print ("ScrollMapDots left: x ScrollV",x,ScrollV)
          self.DisplayWindow(x,ScrollV)
        ScrollH = x


    #Set current room number
    self.CurrentRoomH,r = divmod(ScrollH,8)
    self.CurrentRoomV,r = divmod(ScrollV,8)
    self.DisplayH = ScrollH
    self.DisplayV = ScrollV
  
    #time.sleep(speed)


    
  def ScrollMapDots8Way(self,direction,dots,speed):

    #we only want to scroll the number of dots, not the whole room
    #DisplayWindow has HV starting in upper left hand corner
    
    x = 0
    ScrollH = self.DisplayH
    ScrollV = self.DisplayV

    #print("ScrollMapDots8Way - ScrollH ScrollV direction width",ScrollH,ScrollV, direction, self.width)
     
    #Scroll N
    if (direction == 1):
      
      if (ScrollV - dots >= 0):
      
        for x in range (ScrollV-1,ScrollV-dots-1,-1):
          self.DisplayWindow(ScrollH,x)
        ScrollV = x
         
    #Scroll NE
    if (direction == 2):
      
      #Scroll up and right
      if (ScrollV - dots >= 0):
        for x in range (ScrollV-1,ScrollV-dots-1,-1):
          self.DisplayWindow(ScrollH,x)
        ScrollV = x

      if (ScrollH + 8 + dots  <= self.width):
        for x in range (ScrollH+1,ScrollH+dots+1):
          self.DisplayWindow(x,ScrollV)
        ScrollH = x
         
         
    #Scroll E
    if (direction == 3):
      if (ScrollH + 8 + dots  <= self.width):
        for x in range (ScrollH+1,ScrollH+dots+1):
          self.DisplayWindow(x,ScrollV)
        ScrollH = x

    #Scroll SE
    
    #Scroll right then down
    if (direction == 4):
      if (ScrollH + 8 + dots  <= self.width):
        for x in range (ScrollH+1,ScrollH+dots+1):
          self.DisplayWindow(x,ScrollV)
        ScrollH = x

      if (ScrollV + 8 + dots <= self.height):
        for x in range (ScrollV+1,ScrollV+dots+1):
          self.DisplayWindow(ScrollH,x)
        ScrollV = x

        
        
         
    #Scroll S
    if (direction == 5):
          
      if (ScrollV + 8 + dots <= self.height):
        for x in range (ScrollV+1,ScrollV+dots+1):
          self.DisplayWindow(ScrollH,x)
        ScrollV = x
      
    
    #Scroll SW
    
    #Scroll down then left
    elif (direction == 6):
      if (ScrollH - dots >= 0):
        for x in range (ScrollH-1,ScrollH-dots-1,-1):
          self.DisplayWindow(x,ScrollV)
        ScrollH = x

      if (ScrollV + 8 + dots <= self.height):
        for x in range (ScrollV+1,ScrollV+dots+1):
          self.DisplayWindow(ScrollH,x)
        ScrollV = x
        
        
    #Scroll W
    elif (direction == 7):
      if (ScrollH - dots >= 0):
        for x in range (ScrollH-1,ScrollH-dots-1,-1):
          self.DisplayWindow(x,ScrollV)
        ScrollH = x
      
      
    #Scroll NW
    #Scroll upd then left
    elif (direction == 8):
      if (ScrollV - dots >= 0):
        for x in range (ScrollV-1,ScrollV-dots-1,-1):
          self.DisplayWindow(ScrollH,x)
        ScrollV = x

      if (ScrollH - dots >= 0):
        for x in range (ScrollH-1,ScrollH-dots-1,-1):
          self.DisplayWindow(x,ScrollV)
        ScrollH = x

    
    #time.sleep(0.5)
 


    #Set current room number
    self.CurrentRoomH,r = divmod(ScrollH,8)
    self.CurrentRoomV,r = divmod(ScrollV,8)
    self.DisplayH = ScrollH
    self.DisplayV = ScrollV
  




# -------------------------
# --      Cars           --
# -------------------------



class CarDot(object):
  
  def __init__(self,h,v,dh,dv,r,g,b,direction,scandirection,gear,currentgear,speed,alive,lives,name,score,exploding,radarrange,destination):
    self.h             = h         # location on playfield (e.gv. 10,35)
    self.v             = v         # location on playfield (e.gv. 10,35)
    self.dh            = dh        # location on display   (e.gv. 3,4) 
    self.dv            = dv        # location on display   (e.gv. 3,4) 
    self.r             = r
    self.g             = g
    self.b             = b
    self.direction     = direction      #direction of travel
    self.scandirection = scandirection  #direction of scanners, if equipped
    self.currentgear   = currentgear    
    self.speed         = speed
    self.alive         = 1
    self.lives         = 3
    self.name          = name
    self.score         = 0
    self.exploding     = 0
    self.radarrange    = 20
    self.destination   = ""
    
    #Hold speeds in a list, acting like gears
    self.gear = []
    self.gear.append(5)
    self.gear.append(4)
    self.gear.append(3)
    self.gear.append(2)
    self.gear.append(1)


  def Display(self):
    if (self.alive == 1):
      gv.TheMatrix.SetPixel(self.h,self.v,self.r,self.g,self.b)
     # print("display HV:", self.h,self.v)
      #unicorn.show()
      #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)

      
  def ShiftGear(self,direction):
    #Gears is a list with X gears
    #lists start counting at 0
    #Min gear = 0
    #Max gear = x-1

    NumGears = len(self.gear)

    if (direction == 'down'):
      self.currentgear = self.currentgear -1
    else:
      self.currentgear = self.currentgear +1
    
    #need to put in the CPUModifier here
    #don't let player go too fast or too slow
    if (self.name == "Player"):
      if self.currentgear > NumGears -2:
        self.currentgear = NumGears -2

      if self.currentgear <= 3:
        self.currentgear = 3
    
    
    if (self.currentgear > NumGears -1):
      self.currentgear = NumGears -1
    elif (self.currentgear < 0):
      self.currentgear = 0


      
    #adust speed based on current gear
    self.speed = self.gear[self.currentgear]
    #print ("Name: ", self.name, " Current Gear:",self.currentgear, " Speed: ",self.speed)
  
  
    return;  

  
  def Erase(self):
    gv.TheMatrix.SetPixel(self.h,self.v,0,0,0)
    #unicorn.show()
    #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)



  def AdjustSpeed(self, increment):
    speed = self.speed
    speed = self.speed + increment
    if (speed > 1000):
      speed = 1000
    elif (speed <= 1):
      speed = 1

    self.speed = speed
    return;






#------------------------------------------------------------------------------
# Network Display Classes                                                    --
#------------------------------------------------------------------------------

# class PixelSimDisplay():
  # #Created by Kareem Sultan - Dec 2020
  # def __init__(self, url, display_name, on_attach=None, on_detach=None):
    # self.url = url
    # self.display_name = display_name
    # self.on_attach = on_attach
    # self.on_detach = on_detach
    # #we don't send packet if it is duplicate of previous
    # self.PreviousPacketString = ""
    # self.PacketString = ""

    # #self.on_message = on_message

# #    try:
    # print("Defining connection:",self.display_name)
    # self.hub_connection = HubConnectionBuilder()\
        # .with_url(url, options={"verify_ssl":True, "access_token_factory":lambda: "dummytoken"})\
        # .configure_logging(logging.DEBUG)\
        # .with_automatic_reconnect({
            # "type": "raw",
            # "keep_alive_interval": 10,
            # "reconnect_interval": 5,
            # "max_attempts": 5
        # })\
        # .build()

    # print("--connection on--")
    # self.hub_connection.on("recieveMessage", print)
    # print("--connection on_open--")
    # self.hub_connection.on_open(self.on_connect)
    # print("--connection on_close--")
    # self.hub_connection.on_close(lambda: print("connection closed"))
    # print("---")

    # # except Exception as ErrorMessage:
      # # TheTrace = traceback.format_exc()
      # # print("")
      # # print("")
      # # print("--------------------------------------------------------------")
      # # print("ERROR - Defining hub_connection")
      # # print(ErrorMessage)
      # # print("")
      # # #print("EXCEPTION")
      # # #print(sys.exc_info())
      # # print("")
      # # print ("TRACE")
      # # print (TheTrace)
      # # print("--------------------------------------------------------------")
      # # print("")
      # # print("")
      

  # def on_display_attached(self):
    # print("--Display attached--")
      

  # def on_connect(self):

      # print ("--on_connect start--")
    # #try:
      # print("---------------------------------------------------------------")
      # print("connection opened and handshake received ready to send messages")
      # self.hub_connection.send("AttachDisplay: ", [self.display_name])
      
      # if self.on_attach is not None and callable(self.on_attach):
              # print ("--calling on_attach--")
      # self.on_attach(self)
      # print("---------------------------------------------------------------")
      # print("--on_connect end--")



    # # except Exception as ErrorMessage:
      # # TheTrace = traceback.format_exc()
      # # print("")
      # # print("")
      # # print("--------------------------------------------------------------")
      # # print("ERROR - on_connect")
      # # print(ErrorMessage)
      # # print("")
      # # #print("EXCEPTION")
      # # #print(sys.exc_info())
      # # print("")
      # # print ("TRACE")
      # # print (TheTrace)
      # # print("--------------------------------------------------------------")
      # # print("")
      # # print("")
      # # time.sleep(5)
      
      
  # def connect(self):
    # try:
      # self.hub_connection.start()  
    
    # except Exception as ErrorMessage:
      # TheTrace = traceback.format_exc()
      # print("")
      # print("")
      # print("--------------------------------------------------------------")
      # print("ERROR - Connect")
      # print(ErrorMessage)
      # print("")
      # #print("EXCEPTION")
      # #print(sys.exc_info())
      # print("")
      # print ("TRACE")
      # print (TheTrace)
      # print("--------------------------------------------------------------")
      # print("")
      # print("")
      # time.sleep(5)

  
  # def disconnect(self):
    # try:
      # self.hub_connection.stop()
    # except Exception as ErrorMessage:
      # TheTrace = traceback.format_exc()
      # print("")
      # print("")
      # print("--------------------------------------------------------------")
      # print("ERROR - disconnect")
      # print(ErrorMessage)
      # print("")
      # #print("EXCEPTION")
      # #print(sys.exc_info())
      # print("")
      # print ("TRACE")
      # print (TheTrace)
      # print("--------------------------------------------------------------")
      # print("")
      # print("")
      # time.sleep(5)
  
  # def update(self):
    # #print ("PixelArray:",)
    # try:
      # print ("Sending message")  
      # self.hub_connection.send("sendMessage", [self.PacketString])
    # except Exception as ErrorMessage:
      # TheTrace = traceback.format_exc()
      # print("")
      # print("")
      # print("--------------------------------------------------------------")
      # print("ERROR - update")
      # print(ErrorMessage)
      # print("")
      # #print("EXCEPTION")
      # #print(sys.exc_info())
      # print("")
      # print ("TRACE")
      # print (TheTrace)
      # print("--------------------------------------------------------------")
      # print("")
      # print("")
      # time.sleep(5)


  # #Send the message/packet
  # def SendPacket(self):
    
    # print ("Inputstring:",self.PacketString)
    # #print ("PrevString: ",self.PreviousPacketString[1:16])
    
    
    # try:
      
      # if (self.PreviousPacketString != self.PacketString ):
        # startTime = time.time()
        # #r = requests.post(url = self.URLEndpoint, data = PacketString, timeout=0.3) 
        # #r = self.TheSession.post(url = self.URLEndpoint, data = PacketString, timeout=self.timeout) 
        # self.update()
        # self.PreviousPacketString = self.PacketString
        # endTime = time.time()
        # totalTimeTaken = str(float(round((endTime - startTime ),3)))
        # print ("ElapsedTime:",totalTimeTaken)


      # else:
        # print ("--skip frame--")

        # #print ("PacketString:",self.PacketString[1:16])
        # #print ("PrevString:  ",self.PreviousPacketString[1:16])

    # except Exception as ErrorMessage:
      # TheTrace = traceback.format_exc()
      # print("")
      # print("")
      # print("--------------------------------------------------------------")
      # print("ERROR")
      # print(ErrorMessage)
      # print("")
      # #print("EXCEPTION")
      # #print(sys.exc_info())
      # print("")
      # print ("TRACE")
      # print (TheTrace)
      # print("--------------------------------------------------------------")
      # print("")
      # print("")
      # time.sleep(5)



  # #The HTTPDisplay object can capture the current Unicorn buffer and send that as a packet
  # def SendBufferPacket(self,width,height):
    # self.PacketString = ""
    # x = 0
    # y = 0
    # rgb = (0,0,0)
    # gv.HatWidth  = width
    # gv.HatHeight = height
    # UnicornBuffer = unicorn.get_pixels()
   
    # ints = []
   
    # for x in range(0,gv.HatHeight):
      # for y in range(0,gv.HatWidth):
        # r,g,b = UnicornBuffer[x][y]
        # self.PacketString = self.PacketString + '#%02x%02x%02x' % (r,g,b) + ","
        # #self.PacketString = self.PacketString + str(r) + "," + str(g) + "," + str(b) + ","
        # #ints.append(UnicornBuffer[x][y])
    # #pixel_string = ','.join(map(str, ints))

    
    # self.PacketString = self.PacketString[:-1]
    # #print (pixel_string)
    # #print (string)
    # #self.SendPacket([pixel_string])
    # #print ("PixelString ",self.PacketString[1:8])
    # self.SendPacket()
    # #self.SendPacket([string])
    # return;
  






#------------------------------------------------------------------------------
# SPRITES                                                                    --
#------------------------------------------------------------------------------


DigitList = []
#0
DigitList.append([1,1,1, 
                  1,0,1,
                  1,0,1,
                  1,0,1,
                  1,1,1])
#1
DigitList.append([0,0,1, 
                  0,0,1,
                  0,0,1,
                  0,0,1,
                  0,0,1])
#2
DigitList.append([1,1,1, 
                  0,0,1,
                  1,1,1,
                  1,0,0,
                  1,1,1])
#3
DigitList.append([1,1,1, 
                  0,0,1,
                  0,1,1,
                  0,0,1,
                  1,1,1])
#4
DigitList.append([1,0,1, 
                  1,0,1,
                  1,1,1,
                  0,0,1,
                  0,0,1])
               
#5  
DigitList.append([1,1,1, 
                  1,0,0,
                  1,1,1,
                  0,0,1,
                  1,1,1])
#6
DigitList.append([1,1,1, 
                  1,0,0,
                  1,1,1,
                  1,0,1,
                  1,1,1])
#7
DigitList.append([1,1,1, 
                  0,0,1,
                  0,1,0,
                  1,0,0,
                  1,0,0])
#8  
DigitList.append([1,1,1, 
                  1,0,1,
                  1,1,1,
                  1,0,1,
                  1,1,1])
#9  
DigitList.append([1,1,1, 
                  1,0,1,
                  1,1,1,
                  0,0,1,
                  0,0,1])
                    

# List of Digit Number Numeric sprites
DigitSpriteList = [Sprite(3,5,RedR,RedG,RedB,DigitList[i]) for i in range(0,10)]


AlphaList = []
#A
AlphaList.append([0,1,1,0,0,
                  1,0,0,1,0,
                  1,1,1,1,0,
                  1,0,0,1,0,
                  1,0,0,1,0])

#B
AlphaList.append([1,1,1,0,0,
                  1,0,0,1,0,
                  1,1,1,0,0,
                  1,0,0,1,0,
                  1,1,1,0,0])
#c
AlphaList.append([0,1,1,1,0,
                  1,0,0,0,0,
                  1,0,0,0,0,
                  1,0,0,0,0,
                  0,1,1,1,0])

#D
AlphaList.append([1,1,1,0,0,
                  1,0,0,1,0,
                  1,0,0,1,0,
                  1,0,0,1,0,
                  1,1,1,0,0])

#E
AlphaList.append([1,1,1,1,0,
                  1,0,0,0,0,
                  1,1,1,0,0,
                  1,0,0,0,0,
                  1,1,1,1,0])
                  
#F
AlphaList.append([1,1,1,1,0,
                  1,0,0,0,0,
                  1,1,1,0,0,
                  1,0,0,0,0,
                  1,0,0,0,0])

#G
AlphaList.append([0,1,1,1,0,
                  1,0,0,0,0,
                  1,0,1,1,0,
                  1,0,0,1,0,
                  0,1,1,1,0])

#H
AlphaList.append([1,0,0,1,0,
                  1,0,0,1,0,
                  1,1,1,1,0,
                  1,0,0,1,0,
                  1,0,0,1,0])
#I
AlphaList.append([0,1,1,1,0,
                  0,0,1,0,0,
                  0,0,1,0,0,
                  0,0,1,0,0,
                  0,1,1,1,0])
#J
AlphaList.append([0,1,1,1,0,
                  0,0,1,0,0,
                  0,0,1,0,0,
                  1,0,1,0,0,
                  0,1,0,0,0])
                  
#K
AlphaList.append([1,0,0,1,0,
                  1,0,1,0,0,
                  1,1,0,0,0,
                  1,0,1,0,0,
                  1,0,0,1,0])
#L
AlphaList.append([0,1,0,0,0,
                  0,1,0,0,0,
                  0,1,0,0,0,
                  0,1,0,0,0,
                  0,1,1,1,0])

#M
AlphaList.append([1,0,0,0,1,
                  1,1,0,1,1,
                  1,0,1,0,1,
                  1,0,0,0,1,
                  1,0,0,0,1])

#N
AlphaList.append([1,0,0,0,1,
                  1,1,0,0,1,
                  1,0,1,0,1,
                  1,0,0,1,1,
                  1,0,0,0,1])
#O
AlphaList.append([0,1,1,0,0,
                  1,0,0,1,0,
                  1,0,0,1,0,
                  1,0,0,1,0,
                  0,1,1,0,0])
#P
AlphaList.append([1,1,1,0,0,
                  1,0,0,1,0,
                  1,1,1,0,0,
                  1,0,0,0,0,
                  1,0,0,0,0])
#Q
AlphaList.append([0,1,1,1,0,
                  1,0,0,0,1,
                  1,0,0,0,1,
                  1,0,0,1,0,
                  0,1,1,0,1])
#R 
AlphaList.append([1,1,1,0,0,
                  1,0,0,1,0,
                  1,1,1,0,0,
                  1,0,1,0,0,
                  1,0,0,1,0])
#S
AlphaList.append([0,1,1,1,0,
                  1,0,0,0,0,
                  0,1,1,0,0,
                  0,0,0,1,0,
                  1,1,1,0,0])
#T
AlphaList.append([0,1,1,1,0,
                  0,0,1,0,0,
                  0,0,1,0,0,
                  0,0,1,0,0,
                  0,0,1,0,0])
#U
AlphaList.append([1,0,0,1,0,
                  1,0,0,1,0,
                  1,0,0,1,0,
                  1,0,0,1,0,
                  0,1,1,0,0])
#V
AlphaList.append([1,0,0,0,1,
                  1,0,0,0,1,
                  0,1,0,1,0,
                  0,1,0,1,0,
                  0,0,1,0,0])
#W
AlphaList.append([1,0,0,0,1,
                  1,0,0,0,1,
                  1,0,1,0,1,
                  0,1,0,1,0,
                  0,1,0,1,0])
#X
AlphaList.append([1,0,0,0,1,
                  0,1,0,1,0,
                  0,0,1,0,0,
                  0,1,0,1,0,
                  1,0,0,0,1])
#Y
AlphaList.append([0,1,0,1,0,
                  0,1,0,1,0,
                  0,0,1,0,0,
                  0,0,1,0,0,
                  0,0,1,0,0])
#Z
AlphaList.append([1,1,1,1,0,
                  0,0,0,1,0,
                  0,0,1,0,0,
                  0,1,0,0,0,
                  1,1,1,1,0])


                  
                  
# List of Alpha sprites
AlphaSpriteList = [Sprite(5,5,RedR,RedG,RedB,AlphaList[i]) for i in range(0,26)]



                  
                  
#space                  
SpaceSprite = Sprite(
  3,
  5,
  0,
  0,
  0,
  [0,0,0,
   0,0,0,
   0,0,0,
   0,0,0,
   0,0,0]
)

#Exclamation
ExclamationSprite = Sprite(
  3,
  5,
  0,
  0,
  0,
  [0,1,0,
   0,1,0,
   0,1,0,
   0,0,0,
   0,1,0]
)

#Period
PeriodSprite = Sprite(
  2,
  5,
  0,
  0,
  0,
  [0,0,
   0,0,
   0,0,
   0,0,
   0,1]
)




#QuestionMark
QuestionMarkSprite = Sprite(
  5,
  5,
  0,
  0,
  0,
  [0,0,1,1,0,
   0,0,0,1,0,
   0,0,1,1,0,
   0,0,0,0,0,
   0,0,1,0,0]
)


#PoundSignSprite
PoundSignSprite = Sprite(
  5,
  5,
  0,
  0,
  0,
  [0,1,0,1,0,
   1,1,1,1,1,
   0,1,0,1,0,
   1,1,1,1,1,
   0,1,0,1,0]
)



 
ColonSprite = Sprite(
  3,
  5,
  RedR,
  RedG,
  RedB,
  [0,0,0,
   0,1,0,
   0,0,0,
   0,1,0,
   0,0,0]
)



DashSprite = Sprite(
  3,
  5,
  RedR,
  RedG,
  RedB,
  [0,0,0,0,
   0,0,0,0,
   0,1,1,0,
   0,0,0,0,
   0,0,0,0]
)


#$
DollarSignSprite = Sprite(
  4,
  5,
  RedR,
  RedG,
  RedB,
  [0,1,1,1,
   1,0,1,0,
   0,1,1,0,
   0,0,1,1,
   1,1,1,0]
)





#------------------------------------------------------------------------------
# FUNCTIONS                                                                  --
#                                                                            --
#  These functions were created before classes were introduced.              --
#------------------------------------------------------------------------------



  
def ScrollSprite2(Sprite,h,v,direction,moves,r,g,b,delay):
  x = 0
  #modifier is used to increment or decrement the location
  if direction == "right" or direction == "down":
    modifier = 1
  else: 
    modifier = -1
  
  if direction == "left" or direction == "right":
    for count in range (0,moves):
      h = h + (modifier)
      #erase old sprite
      if count >= 1:
        DisplaySprite(Sprite,Sprite.width,Sprite.height,h-(modifier),v,0,0,0)
      #draw new sprite
      DisplaySprite(Sprite,Sprite.width,Sprite.height,h,v,r,g,b)
      #unicorn.show()
      #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
      time.sleep(delay)
  
  return;

 
  

def ScrollSprite(Sprite,width,height,Direction,startH,startV,stopH,stopV,r,g,b,delay):
  x = 0
  h = startH
  v = startV
  movesH = abs(startH - stopH)
  movesV = abs(startV - stopV)

  #modifier is used to increment or decrement the location
  if Direction == "right" or Direction == "down":
    modifier = 1
  else: 
    modifier = -1
  
  if Direction == "left" or Direction == "right":
    for count in range (0,movesH):
      #print ("StartH StartV StopH StopV X",startH,startV,stopH,stopV,x)
      h = h + (modifier)
      #erase old sprite
      if count >= 1:
        DisplaySprite(Sprite,width,height,h-(modifier),v,0,0,0)
      #draw new sprite
      DisplaySprite(Sprite,width,height,h,v,r,g,b)
      #unicorn.show()
      #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
      time.sleep(delay)
  
  return;
    
def DisplaySprite(Sprite,width,height,h,v,r,g,b):
  x = 0,
  y = 0
  
  for count in range (0,(width * height)):
    y,x = divmod(count,width)
    #print("Count:",count,"xy",x,y)
    if Sprite[count] == 1:
      if (CheckBoundary(x+h,y+v) == 0):
        gv.TheMatrix.SetPixel(x+h,y+v,r,g,b)
  return;    



def TrimSprite(Sprite1):
  height       = Sprite1.height
  width        = Sprite1.width
  newwidth     = 0
  elements     = height * width
  Empty        = 1
  Skipped      = 0
  EmptyColumns = []
  EmptyCount   = 0
  BufferX      = 0
  BufferColumn = [(0) for i in range(height)]
  
  i = 0
  x = 0
  y = 0

  
  for x in range (0,width):
    
    #Find empty columns, add them to a list
    Empty = 1  
    for y in range (0,height):
      i = x + (y * width)
      
      BufferColumn[y] = Sprite1.grid[i]
      if (Sprite1.grid[i] != 0):
        Empty = 0
    
    if (Empty == 0):
      newwidth =  newwidth + 1
    
    elif (Empty == 1):
      #print ("Found empty column: ",x)
      EmptyColumns.append(x)
      EmptyCount = EmptyCount +1

      
  BufferSprite = Sprite(
    newwidth,
    height,
    Sprite1.r,
    Sprite1.g,
    Sprite1.b,
    [0]*(newwidth*height)
    )
      
  #Now that we identified the empty columns, copy data and skip those columns
  for x in range (0,width):
    Skipped = 0
    
    for y in range (0,height):
      i = x + (y * width)
      b = BufferX + (y * newwidth)
      if (x in EmptyColumns):
        Skipped = 1
      else:
        BufferSprite.grid[b] = Sprite1.grid[i]
    
    
    #advance our Buffer column counter only if we skipped a column
    if (Skipped == 0):
      BufferX = BufferX + 1
    
    
  
  BufferSprite.width = newwidth
  
  
  
  #print (BufferSprite.grid)
  return BufferSprite



def LeftTrimSprite(Sprite1,Columns):
  height       = Sprite1.height
  width        = Sprite1.width
  newwidth     = 0
  elements     = height * width
  Empty        = 1
  Skipped      = 0
  EmptyColumns = []
  EmptyCount   = 0
  BufferX      = 0
  BufferColumn = [(0) for i in range(height)]
  
  i = 0
  x = 0
  y = 0

  
  for x in range (0,width):
    
    #Find empty columns, add them to a list
    Empty = 1  
    for y in range (0,height):
      i = x + (y * width)
      
      BufferColumn[y] = Sprite1.grid[i]
      if (Sprite1.grid[i] != 0):
        Empty = 0
    
    if (Empty == 0 or EmptyCount > Columns):
      newwidth =  newwidth + 1
    
    elif (Empty == 1):
      #print ("Found empty column: ",x)
      EmptyColumns.append(x)
      EmptyCount = EmptyCount +1

      
  BufferSprite = Sprite(
    newwidth,
    height,
    Sprite1.r,
    Sprite1.g,
    Sprite1.b,
    [0]*(newwidth*height)
    )
      
  #Now that we identified the empty columns, copy data and skip those columns
  for x in range (0,width):
    Skipped = 0
    
    for y in range (0,height):
      i = x + (y * width)
      b = BufferX + (y * newwidth)
      if (x in EmptyColumns):
        Skipped = 1
      else:
        BufferSprite.grid[b] = Sprite1.grid[i]
    
    
    #advance our Buffer column counter only if we skipped a column
    if (Skipped == 0):
      BufferX = BufferX + 1
    
    
  
  BufferSprite.width = newwidth
  
  
  
  #print (BufferSprite.grid)
  return BufferSprite
    
    
    
    

  
  
def CreateShortWordSprite(ShortWord):   

  ShortWord = ShortWord.upper()
  TheBanner = CreateBannerSprite(ShortWord)
      

  TheBanner.r = SDMedRedR
  TheBanner.g = SDMedRedG
  TheBanner.b = SDMedRedB
  
  
  #add variables to the object (python allows this, very cool!)
  TheBanner.h = (gv.HatWidth - TheBanner.width) / 2
  TheBanner.v = -4
  TheBanner.rgb = (SDMedGreenR,SDMedGreenG,SDMedGreenB)

  #used for displaying clock
  TheBanner.StartTime = time.time()

  #used for scrolling clock
  TheBanner.PauseStartTime = time.time()
  TheBanner.IsScrolling     = 0
  TheBanner.Delay           = 2
  TheBanner.PausePositionV  = 1
  TheBanner.PauseTimerOn    = 0
  
  TheBanner.on = 1
  TheBanner.DirectionIncrement = 1

  
  return TheBanner 



def ShowShortMessage(RaceWorld,PlayerCar,ShortMessage):
  moves = 1
  ShortMessageSprite    = CreateShortMessageSprite(ShortMessage)
  ShortMessageSprite.on = 1
  while (ShortMessageSprite.on == 1):
    RaceWorld.DisplayWindowWithSprite(PlayerCar.h-7,PlayerCar.v-7,ShortMessageSprite)
    MoveMessageSprite(moves,ShortMessageSprite)
    moves = moves + 1
    #print ("Message On")
    
  ShortMessageSprite.on = 0












def DrawDigit(Digit,h,v,r,g,b):
  #print ("Digit:",Digit)
  x = h
  y = v,
  width = 3
  height = 5  

  if Digit == 0:
    Sprite = ([1,1,1, 
               1,0,1,
               1,0,1,
               1,0,1,
               1,1,1])

  elif Digit == 1:
    Sprite = ([0,0,1, 
               0,0,1,
               0,0,1,
               0,0,1,
               0,0,1])

  elif Digit == 2:
    Sprite = ([1,1,1, 
               0,0,1,
               0,1,0,
               1,0,0,
               1,1,1])

  elif Digit == 3:
    Sprite = ([1,1,1, 
               0,0,1,
               0,1,1,
               0,0,1,
               1,1,1])

  elif Digit == 4:
    Sprite = ([1,0,1, 
               1,0,1,
               1,1,1,
               0,0,1,
               0,0,1])
               
  
  elif Digit == 5:
    Sprite = ([1,1,1, 
               1,0,0,
               1,1,1,
               0,0,1,
               1,1,1])

  elif Digit == 6:
    Sprite = ([1,1,1, 
               1,0,0,
               1,1,1,
               1,0,1,
               1,1,1])

  elif Digit == 7:
    Sprite = ([1,1,1, 
               0,0,1,
               0,1,0,
               1,0,0,
               1,0,0])
  
  elif Digit == 8:
    Sprite = ([1,1,1, 
               1,0,1,
               1,1,1,
               1,0,1,
               1,1,1])
  
  elif Digit == 9:
    Sprite = ([1,1,1, 
               1,0,1,
               1,1,1,
               0,0,1,
               0,0,1])
  

  DisplaySprite(Sprite,width,height,h,v,r,g,b)
  #unicorn.show()
  #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
  return;  





   

def CheckBoundaries(h,v,Direction):
  if v < 0:
    v = 0
    Direction = TurnRight(Direction)
  elif v > gv.HatHeight-1:
    v = gv.HatHeight-1
    Direction = TurnRight(Direction)
  elif h < 0:
    h = 0
    Direction = TurnRight(Direction)
  elif h > gv.HatWidth-1:
    h = gv.HatWidth-1
    Direction = TurnRight(Direction)
  return h,v,Direction

  
  
def CheckBoundary(h,v):
  BoundaryHit = 0
  if v < 0 or v > gv.HatHeight-1 or h < 0 or h > gv.HatWidth-1:
    BoundaryHit = 1
  return BoundaryHit;








  






def ShowDigitalClock(h,v,duration):
  Buffer = copy.deepcopy(unicorn.get_pixels())
  ClockSprite = CreateClockSprite(12)
  ClockSprite.r = SDLowRedR
  ClockSprite.g = SDLowRedG
  ClockSprite.b = SDLowRedB
  ClockSpriteBackground.DisplayIncludeBlack(h-2,v-1)
  ClockSprite.Display(h,v)
  #unicorn.show()
  #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
  time.sleep(duration)
  setpixels(Buffer)
  return;



def random_message(MessageFile):
  lines = open(MessageFile).read().splitlines()
  return random.choice(lines)

    


def SaveConfigData():
  
  global PacDotHighScore 
   
  print (" ")
  print ("--Save Config Data--")
  #we save the time to file as 5 minutes in future, which allows us to unplug the device temporarily
  #the time might be off, but it might be good enough
  
  AdjustedTime = (datetime.now() + timedelta(minutes=5)).strftime('%k:%M:%S')

  
  if (os.path.exists(ConfigFileName)):
    print ("Config file (",ConfigFileName,"): already exists")
    ConfigFile = SafeConfigParser()
    ConfigFile.read(ConfigFileName)
  else:
    print ("Config file not found.  Creating new one.")
    ConfigFile = SafeConfigParser()
    ConfigFile.read(ConfigFileName)
    ConfigFile.add_section('main')
    ConfigFile.add_section('pacdot')
    ConfigFile.add_section('crypto')

    
  print ("Time to save: ",AdjustedTime)
  print ("Pacdot score:      ",gv.PacDotScore)
  print ("Pacdot high score: ",gv.PacDotHighScore)
  print ("Crypto balance:    ",gv.CryptoBalance)

  ConfigFile.set('main',   'CurrentTime',     AdjustedTime)
  ConfigFile.set('pacdot', 'PacDotHighScore', str(gv.PacDotHighScore))
  ConfigFile.set('crypto', 'balance',         str(gv.CryptoBalance))


  print ("Writing configuration file")
  with open(ConfigFileName, 'w') as f:
    ConfigFile.write(f)
  print ("--------------------")



    
def LoadConfigData():
  
  global PacDotHighScore

  print ("--Load Config Data--")
  print ("PacDotHighScore Before Load: ",gv.PacDotHighScore)
    
  if (os.path.exists(ConfigFileName)):
    print ("Config file (",ConfigFileName,"): already exists")
    ConfigFile = SafeConfigParser()
    ConfigFile.read(ConfigFileName)

    #Get and set time    
    TheTime = ConfigFile.get("main","currenttime")
    print ("Setting time: ",TheTime)
    CMD = "sudo date --set " + TheTime
    #os.system(CMD)
   
    #Get high score data
    PacDotHighScore = ConfigFile.get("pacdot","pacdothighscore")
    print ("PacDotHighScore: ",gv.PacDotHighScore)

    #Get CryptoBalance
    gv.CryptoBalance = ConfigFile.get("crypto","balance")
    print ("CryptoBalance:   ",gv.CryptoBalance)

    
  else:
    print ("Config file not found! Running with default values.")

    
  print ("--------------------")
  print (" ")
  


 
  
    
  
  
  
  
def SetTimeHHMM():
  DigitsEntered = 0
  H1  = 0
  H2  = 0
  M1  = 0
  M2  = 0
  Key = -1

  CustomH = ([1,0,1,
              1,0,1,
              1,1,1,
              1,0,1,
              1,0,1])

  CustomM = ([1,0,1,
              1,1,1,
              1,1,1,
              1,0,1,
              1,0,1])

  QuestionMarkSprite = Sprite(
  3,
  5,
  0,
  0,
  0,
  [0,1,1,
   0,0,1,
   0,1,1,
   0,0,0,
   0,1,0]
  )

              
              
  CustomHSprite = Sprite(3,5,SDLowRedR,SDLowRedG,SDLowRedB,CustomH)
  CustomMSprite = Sprite(3,5,SDLowRedR,SDLowRedG,SDLowRedB,CustomM)
  AMSprite      = Sprite(5,5,SDLowGreenR,SDLowGreenG,SDLowGreenB,AlphaSpriteList[0].grid)
  PMSprite      = Sprite(5,5,SDLowGreenR,SDLowGreenG,SDLowGreenB,AlphaSpriteList[15].grid)
  AMPMSprite    = JoinSprite(QuestionMarkSprite,CustomMSprite,1)
  




 
  ScreenCap  = copy.deepcopy(unicorn.get_pixels())
  ScrollScreen('up',ScreenCap,gv.ScrollSleep)
  ShowScrollingBanner("set time: hours minutes",100,100,0,gv.ScrollSleep)
  ScrollScreen('down',ScreenCap,gv.ScrollSleep)

  
  HHSprite = TrimSprite(CustomHSprite)
  HHSprite = JoinSprite (HHSprite,TrimSprite(CustomHSprite),1)
  
  HHSprite.Display(1,1)
  #unicorn.show()
  #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
  
  #Get first hour digit
  while (Key != 0 and Key != 1):
    Key = PollKeyboardInt()
    time.sleep(0.15)
  H1 = Key
  
  #Convert user input H1 to a sprite
  #x = ord(H1) -48
  
  UserH1Sprite = Sprite(3,5,SDLowGreenR,SDLowGreenG,SDLowGreenB,DigitSpriteList[H1].grid)
  CustomHSprite.Erase(1,1)
  UserH1Sprite.Display(1,1)
  #unicorn.show()
  #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
  
  #Get second hour digit (special conditions to make sure we keep 12 hour time)
  Key = -1
  while ((H1 == 1 and (Key != 0 and Key != 1 and Key != 2))
     or (H1 == 0 and (Key == -1)) ):
    Key = PollKeyboardInt()
    time.sleep(0.15)
  H2 = Key
 
  #Convert user input H2 to a sprite
  UserH2Sprite = Sprite(3,5,SDLowGreenR,SDLowGreenG,SDLowGreenB,DigitSpriteList[H2].grid)
  CustomHSprite.Erase(5,1)
  UserH2Sprite.Display(5,1)
  #unicorn.show()
  #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
    
  #print ("HH: ",H1,H2)
  

  
  
  
  #Get minutes
  time.sleep(1)
  gv.TheMatrix.Clear()

  
  MMSprite = TrimSprite(CustomMSprite)
  MMSprite = JoinSprite (MMSprite,TrimSprite(CustomMSprite),1)
  
  MMSprite.Display(1,1)
  #unicorn.show()
  #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
  
  #Get first minute digit
  Key = -1
  while (Key < 0 or Key >= 6):
    Key = PollKeyboardInt()
    time.sleep(0.15)
  M1 = Key
  
  #Convert user input M1 to a sprite
  UserM1Sprite = Sprite(3,5,SDLowGreenR,SDLowGreenG,SDLowGreenB,DigitSpriteList[M1].grid)
  CustomMSprite.Erase(1,1)
  UserM1Sprite.Display(1,1)
  #unicorn.show()
  #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
  
  #Get second hour digit
  Key = -1
  while (Key == -1):
    Key = PollKeyboardInt()
    time.sleep(0.15)
  M2 = Key
 
  #Convert user input M2 to a sprite
  UserM2Sprite = Sprite(3,5,SDLowGreenR,SDLowGreenG,SDLowGreenB,DigitSpriteList[M2].grid)
  CustomMSprite.Erase(5,1)
  UserM2Sprite.Display(5,1)
  #unicorn.show()
  #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
    
  #print ("MM: ",M1,M2)
  
  time.sleep(1)
  gv.TheMatrix.Clear()

  # a.m / p.m.
  ShowScrollingBanner("AM or PM",100,100,0,gv.ScrollSleep * 0.65)
  AMPMSprite.Display(1,1)
  #unicorn.show()
  #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
  #Get A or P
  KeyChar = ''
  while (KeyChar == '' or (KeyChar != 'A' and KeyChar != 'a' and KeyChar != 'P' and KeyChar != 'p' )):
    KeyChar = PollKeyboardRegular()
    time.sleep(0.15)

  AMPMSprite.r = SDLowGreenR
  AMPMSprite.g = SDLowGreenG
  AMPMSprite.b = SDLowGreenB
  AMPMSprite.Display(1,1)
  #unicorn.show()
  #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
  
  QuestionMarkSprite.Erase(1,1)

  AMPM = ''
  if (KeyChar == 'a' or KeyChar == 'A'):
    AMSprite.Display(0,1)
    #unicorn.show()
    #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
    AMPM  = 'am'
    
  elif (KeyChar == 'p' or KeyChar == 'P'):
    PMSprite.Display(0,1)
    #unicorn.show()
    #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
    AMPM = 'pm'
    
  
  #print ("KeyChar ampm:",KeyChar, AMPM)    
  time.sleep(1)
 
  
  
  
  #set system time
  NewTime = str(H1) + str(H2) + ":" + str(M1) + str(M2) + AMPM
  CMD = "sudo date --set " + NewTime
  os.system(CMD)
  
  gv.TheMatrix.Clear()
  ScrollScreenShowClock('down',gv.ScrollSleep)         
  








def ShowScrollingBanner(TheMessage,r,g,b,ScrollSpeed):
  TheMessage = TheMessage.upper()
  TheBanner = CreateBannerSprite(TheMessage)
  TheBanner.r = r 
  TheBanner.g = g 
  TheBanner.b = b 
  TheBanner.ScrollAcrossScreen(gv.HatWidth-1,4,"left",ScrollSpeed)


def ShowScrollingBanner2(TheMessage,rgb,ScrollSpeed,v=5):
  r,g,b = rgb
  TheMessage = TheMessage.upper()
  TheBanner = CreateBannerSprite(TheMessage)
  TheBanner.r = r 
  TheBanner.g = g 
  TheBanner.b = b 
  TheBanner.ScrollAcrossScreen(gv.HatWidth-1,v,"left",ScrollSpeed)

def ShowFloatingBanner(TheMessage,rgb,ScrollSpeed,v=5):
  r,g,b = rgb
  TheMessage = TheMessage.upper()
  TheBanner = CreateBannerSprite(TheMessage)
  TheBanner.r = r 
  TheBanner.g = g 
  TheBanner.b = b 
  TheBanner.FloatAcrossScreen(gv.HatWidth-1,v,"left",ScrollSpeed)












  
def FlashDot(h,v,FlashSleep):
  r,g,b = getpixel(h,v)
  gv.TheMatrix.SetPixel(h,v,0,0,255)
  time.sleep(FlashSleep)
  #unicorn.show()
  #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
  gv.TheMatrix.SetPixel(h,v,r,g,b)
  time.sleep(FlashSleep)
  #unicorn.show()
  gv.TheMatrix.SetPixel(h,v,0,255,0)
  time.sleep(FlashSleep)
  #unicorn.show()
  gv.TheMatrix.SetPixel(h,v,r,g,b)
  time.sleep(FlashSleep)
  #unicorn.show()
  #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
  return;

def FlashDot2(h,v,FlashSleep):
  r,g,b = getpixel(h,v)
  gv.TheMatrix.SetPixel(h,v,100,100,0)
  gv.TheMatrix.SetPixel(h,v,200,200,0)
  gv.TheMatrix.SetPixel(h,v,255,255,255)
  time.sleep(FlashSleep)
  gv.TheMatrix.SetPixel(h,v,r,g,b)

  return;


  
def FlashDot3(h,v,r,g,b,FlashSleep):
 
    
  LowR = int(r * 0.75)
  LowG = int(g * 0.75)
  LowB = int(b * 0.75)
  HighR = int(r * 1.5)
  HighG = int(g * 1.5)
  HighB = int(b * 1.5)
  
  if (LowR < 0 ):
    LowR = 0
  if (LowG < 0 ):
    LowG = 0
  if (LowB < 0 ):
    LowBB = 0
  
  
  if (HighR > 255):
    HighR = 255
  if (HighG > 255):
    HighG = 255
  if (HighB > 255):
    HighB = 255
    
  gv.TheMatrix.SetPixel(h,v,HighR,HighG,HighB)
  #unicorn.show()
  #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
  time.sleep(FlashSleep)
  gv.TheMatrix.SetPixel(h,v,r,g,b)
  #unicorn.show()
  gv.TheMatrix.SetPixel(h,v,LowR,LowG,LowB)
  #unicorn.show()
  time.sleep(FlashSleep)
  #unicorn.show()
  gv.TheMatrix.SetPixel(h,v,HighR,HighG,HighB)
  #unicorn.show()
  time.sleep(FlashSleep)
  gv.TheMatrix.SetPixel(h,v,r,g,b)
  #unicorn.show()
  gv.TheMatrix.SetPixel(h,v,LowR,LowG,LowB)
  #unicorn.show()
  time.sleep(FlashSleep)
  #unicorn.show()
  #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
  
  
def FlashDot4(h,v,FlashSleep):
  r,g,b = getpixel(h,v)
  #gv.TheMatrix.SetPixel(h,v,0,0,100)
  #unicorn.show()
  #time.sleep(FlashSleep)
  #gv.TheMatrix.SetPixel(h,v,0,0,175)
  #unicorn.show()
  time.sleep(FlashSleep)
  gv.TheMatrix.SetPixel(h,v,0,0,255)
  #unicorn.show()
  time.sleep(FlashSleep)
  gv.TheMatrix.SetPixel(h,v,0,255,255)
  #unicorn.show()
  time.sleep(FlashSleep)
  gv.TheMatrix.SetPixel(h,v,255,255,255)
  #unicorn.show()
  #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
  time.sleep(FlashSleep)
  gv.TheMatrix.SetPixel(h,v,r,g,b)
  #unicorn.show()
  time.sleep(FlashSleep)
  return;
  

def FlashDot5(h,v,TimeSleep):
  #r,g,b = getpixel(h,v)
  
  #There is not get pixel function in rpi-rgb-led
  r,g,b = (255,255,255)

  setpixel(h,v,255,255,255)
  #unicorn.show()
  #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
  time.sleep(TimeSleep)
  setpixel(h,v,r,g,b)
  
  
  return;


def FlashDot6(h,v):
  r,g,b = getpixel(h,v)
  gv.TheMatrix.SetPixel(h,v,255,255,255)
  #unicorn.show()
  #gv.TheMatrix.SetPixel(h,v,r,g,b)
  return;


def FlashDot7(h,v):
  gv.TheMatrix.SetPixel(h,v,255,150,0)
  #unicorn.show()
  gv.TheMatrix.SetPixel(h,v,0,0,0)
  return;



  

  
def CalculateMovement(h,v,Direction):
  # I am not sure why this function returns the direction 
  #1N 2E 3S 4W
  if (Direction == 1):
    v = v -1
  if (Direction == 2):
    h = h + 1
  if (Direction == 3):
    v = v + 1
  if (Direction == 4):
    h = h -1
  return h,v,Direction;


def CalculateDotMovement(h,v,Direction):
  #1N 2E 3S 4W
  if (Direction == 1):
    v = v -1
  if (Direction == 2):
    h = h + 1
  if (Direction == 3):
    v = v + 1
  if (Direction == 4):
    h = h -1
  return h,v;


  

  
  
def ScanDot(h,v):
  BoundaryHit = CheckBoundary(h,v)
  if BoundaryHit == 1:
    item = "boundary"
  else:
    r,g,b = getpixel(h,v)
    #print ("rgb:",r,g,b," DotRGB:",DotR,DotG,DotB)
    #FlashDot(h,v,0)
 
  

    if r == DotR and g == DotG and b == DotB:
      item = "dot"
      #print ("Scanned dot:",h,v)
    elif r == PillR and g == PillG and b == PillB:
      item = "pill"
    elif r == Ghost1R and g == Ghost1G and b == Ghost1B:
      item = "ghost"
    elif r == Ghost2R and g == Ghost2G and b == Ghost2B:
      item = "ghost"
    elif r == Ghost3R and g == Ghost3G and b == Ghost3B:
      item = "ghost"
    elif r == Ghost4R and g == Ghost4G and b == Ghost4B:
      item = "ghost"
    elif r == PacR and g == PacG and b == PacB:
      item = "pacdot"
    elif r == BlueGhostR and g == BlueGhostG and b == BlueGhostB:
      item = "blueghost"
    elif r == WallR and g == WallG and b == WallB:
      item = "wall"
    elif ((r,g,b) == gv.SpriteFillerRGB or (r,g,b) == WallRGB):
      item = "wall"
    else: 
      item = "empty"
  

    if (gv.DotMatrix[h][v] == 1):
      #print ("ScanDot Override DOT hv:",h,v)
      item = "dot"

    if (gv.DotMatrix[h][v] == 2):
      #print ("ScanDot Override PILL hv:",h,v)
      item = "pill"


  return item;

def ScanBox(h,v,Direction):
  #pass in current h,v,direction
  #will examine multiple dots in front and to sides
  
  
  item = "NULL"
  ScanHit = "NULL"
  ScanH = 0
  ScanV = 0
  ScanDirection = 0
  
  #print ("--------")


  
  
  #Front
  ScanDirection = Direction
  ScanH, ScanV, ScanDirection = CalculateMovement(h,v,ScanDirection)
  item = ScanDot(ScanH,ScanV)
  if item == "dot":
    ScanHit = "frontdot"
  elif item == "ghost":  
    ScanHit = "frontghost"
  elif item == "blueghost":  
    ScanHit = "frontblueghost"
  elif item == "pill":
    ScanHit = "frontpill"
  elif item == "wall":
    ScanHit = "frontwall"

  #Left
  if ScanHit == "NULL":
    ScanDirection = TurnLeft(Direction)
    ScanH, ScanV, ScanDirection = CalculateMovement(h,v,ScanDirection)
    item = ScanDot(ScanH,ScanV)
    if item == "dot":
      ScanHit = "leftdot"
    elif item == "ghost":  
      ScanHit = "leftghost"
    elif item == "blueghost":  
      ScanHit = "leftblueghost"
    elif item == "pill":
      ScanHit = "leftpill"
    elif item == "wall":
      ScanHit = "leftwall"

  
      
 #Right
  if ScanHit == "NULL" or ScanHit == "leftwall":
    ScanDirection = TurnRight(Direction)
    ScanH, ScanV, ScanDirection = CalculateMovement(h,v,ScanDirection)
    item = ScanDot(ScanH,ScanV)
    if item == "dot":
      ScanHit  = "rightdot"
      print ("Rightdot")
    elif item == "ghost":  
      ScanHit  = "rightghost"
    elif item == "blueghost":  
      ScanHit  = "rightblueghost"
    elif item == "pill":
      ScanHit  = "rightpill"
    elif item == "wall":
      ScanHit  = "rightwall"

 
  

 
  
  if (ScanHit == "NULL"):
    ScanHit = "empty"
  #print ("ScanHit: ",ScanHit)
  return ScanHit;









  
#----------------------------------------------------------------------------
#--                                                                        --
#--                                                                        --
#--          RallyDot                                                      --
#--                                                                        --
#--                                                                        --
#----------------------------------------------------------------------------




# - the player car will not move, but the maze around him will
# - the playfield contains all objects, including cars walls enemies and bullets
# - we loop through the playfield, examining each object
    # - ignore empty
    # - ignore walls
    # - if player/enemy then give it a turn to use radar to find nearby items
        # - make a decision on what to to
        # - decisions are priority based
        # - shoot opponent
        # - run
        # - hide
    # - we still  use a clock/speed value to see if a player/enemy object is going to make a decision this turn
# - objects off screen will still move, but will not be visible
# - draw window function will be used to display the current visible sqare in the map (8x8)    




def ExaminePlayfield(RaceWorld):
  #The array is [V][H]
  print ("--Examine Playfield--")
  width  = RaceWorld.width
  height = RaceWorld.height
  h      = 0
  v      = 0
  Playfield = RaceWorld.Playfield
  
  #Iterate through playfield (left to right, top to bottom)
  for v in range (height):
    for h in range (width):
      print ("vh name: ",v,h,Playfield[v][h].name)

      
def TurnLeftOrRight8Way(direction):
  WhichWay = random.randint(1,4)
  #print ("WhichWay:",WhichWay)
  if (WhichWay == 1):
    #print ("turning W")
    direction = TurnLeft8Way(direction)
    direction = TurnLeft8Way(direction)
  elif (WhichWay == 2):
    #print ("turning NW")
    direction = TurnLeft8Way(direction)
  elif (WhichWay == 3):
    #print ("turning NE")
    direction = TurnRight8Way(direction)
  elif (WhichWay == 4):
    #print ("turning E")
    direction = TurnRight8Way(direction)
    direction = TurnRight8Way(direction)
    
  return direction;

      
def TurnLeftOrRightTwice8Way(direction):
  WhichWay = random.randint(1,2)
  #print ("WhichWay:",WhichWay)
  if (WhichWay == 1):
    direction = TurnLeft8Way(direction)
    direction = TurnLeft8Way(direction)
  elif (WhichWay == 2):
    direction = TurnRight8Way(direction)
    direction = TurnRight8Way(direction)
    
  return direction;


  
      
def ReverseDirection8Way(direction):
  if direction == 1:
    direction = 5
  elif direction == 2:
    direction = 6
  elif direction == 3:
    direction = 7
  elif direction == 4:
    direction = 8
  elif direction == 5:
    direction = 1
  elif direction == 6:
    direction = 2
  elif direction == 7:
    direction = 3
  elif direction == 8:
    direction = 4
  return direction;

  

def CalculateDotMovement8Way(h,v,Direction):
  #1N 2NE 3E 4SE 5S 6SW 7W 8NW
  # 8 1 2
  # 7 x 3
  # 6 5 4
  
  if (Direction == 1):
    v = v -1
  if (Direction == 2):
    h = h + 1
    v = v - 1
  if (Direction == 3):
    h = h + 1
  if (Direction == 4):
    h = h + 1
    v = v + 1
  if (Direction == 5):
    v = v + 1
  if (Direction == 6):
    h = h - 1
    v = v + 1
  if (Direction == 7):
    h = h - 1
  if (Direction == 8):
    h = h - 1
    v = v - 1
  return h,v;



def TurnRight8Way(direction):
  if direction == 1:
    direction = 2
  elif direction == 2:
    direction = 3
  elif direction == 3:
    direction = 4
  elif direction == 4:
    direction = 5
  elif direction == 5:
    direction = 6
  elif direction == 6:
    direction = 7
  elif direction == 7:
    direction = 8
  elif direction == 8:
    direction = 1
  #print "  new: ",direction
  return direction;
    

def TurnLeft8Way(direction):
  #print "ChangeDirection!"
  #print "  old: ",direction
  if direction == 1:
    direction = 8
  elif direction == 8:
    direction = 7
  elif direction == 7:
    direction = 6
  elif direction == 6:
    direction = 5
  elif direction == 5:
    direction = 4
  elif direction == 4:
    direction = 3
  elif direction == 3:
    direction = 2
  elif direction == 2:
    direction = 1
  #print ("  new: ",direction)
  return direction;



def ChanceOfTurning8Way(Direction,Chance):
  #print ("Chance of turning: ",Chance)
  if Chance > randint(1,100):
    if randint(0,1) == 0:
      Direction = TurnLeft8Way(Direction)
    else:
      Direction = TurnRight8Way(Direction)
  return Direction;


  


  
  
def IncreaseColor(Car):

  #Make player car more blue
  if (Car.name == "Player"):
    Car.b = Car.b + 20
    
    if (Car.b >= 255):
      Car.b = 255

  #Make enemy more red
  else:
    Car.r = Car.r + 50
    
    if (Car.r >= 255):
      Car.r = 255

  #print ("Carname rgb",Car.name,Car.r,Car.g,Car.b)      
      
def DecreaseColor(Car):
  #Make player car less blue
  if (Car.name == "Player"):
    Car.b = Car.b - 1

    if (Car.b <= 60):
      Car.b = 60
      
    
  #Make player car less blue
  else:
    Car.r = Car.r - 1

    if (Car.r <= 60):
      Car.r = 60

      
      


def ReverseDirection(direction):
  if direction == 1:
    direction = 3
  elif direction == 2:
    direction = 4
  elif direction == 3:
    direction = 1
  elif direction == 4:
    direction = 2
  return direction;
    

def TurnRight(direction):
  if direction == 1:
    direction = 2
  elif direction == 2:
    direction = 3
  elif direction == 3:
    direction = 4
  elif direction == 4:
    direction = 1
  #print "  new: ",direction
  return direction;
    

def TurnLeft(direction):
  #print "ChangeDirection!"
  #print "  old: ",direction
  if direction == 1:
    direction = 4
  elif direction == 2:
    direction = 1
  elif direction == 3:
    direction = 2
  elif direction == 4:
    direction = 3
  #print "  new: ",direction
  return direction;
    
def ChanceOfTurning(Direction,Chance):
  #print ("Chance of turning: ",Chance)
  if Chance > randint(1,100):
    if randint(0,1) == 0:
      Direction = TurnLeft(Direction)
    else:
      Direction = TurnRight(Direction)
  return Direction;





def TurnLeftOrRight(direction):
  WhichWay = random.randint(1,2)
  #print ("WhichWay:",WhichWay)
  if (WhichWay == 1):
    #print ("turning left")
    direction = TurnLeft(direction)
  else:
    #print ("turning right")
    direction = TurnRight(direction)
    
  return direction;






def CreateClockSprite(format):   
  #print ("CreateClockSprite")
  #Create the time as HHMMSS
  
  if (format == 12 or format == 2):  
    hhmmss = datetime.now().strftime('%I:%M:%S')
    hh,mm,ss = hhmmss.split(':')
  
  if format == 24:  
    hhmmss = datetime.now().strftime('%H:%M:%S')
    hh,mm,ss = hhmmss.split(':')
  
   

  
  #get hour digits
  h1 = int(hh[0])
  h2 = int(hh[1])
  #get minute digits
  m1 = int(mm[0])
  m2 = int(mm[1])


  #For 12 hour format, we don't want to display leading zero 
  #for tiny clock (2) format we only get hours
  if ((format == 12 or format == 2) and h1 == 0):
    ClockSprite = DigitSpriteList[h2]
  else:
    ClockSprite = JoinSprite(DigitSpriteList[h1], DigitSpriteList[h2], 1)
  
  if (format == 12 or format == 24):
    ClockSprite = JoinSprite(ClockSprite, ColonSprite, 0)
    ClockSprite = JoinSprite(ClockSprite, DigitSpriteList[m1], 0)
    ClockSprite = JoinSprite(ClockSprite, DigitSpriteList[m2], 1)
    

  ClockSprite.r = SDMedRedR
  ClockSprite.g = SDMedRedG
  ClockSprite.b = SDMedRedB
  
  
  #add variables to the object (python allows this, very cool!)
  ClockSprite.h = (gv.HatWidth - ClockSprite.width) // 2
  ClockSprite.v = -4
  ClockSprite.rgb = (SDMedGreenR,SDMedGreenG,SDMedGreenB)

  #used for displaying clock
  ClockSprite.StartTime = time.time()

  #used for scrolling clock
  ClockSprite.PauseStartTime = time.time()
  ClockSprite.IsScrolling     = 0
  ClockSprite.Delay           = 2
  ClockSprite.PausePositionV  = 1
  ClockSprite.PauseTimerOn    = 0

  
  ClockSprite.on = 1
  ClockSprite.DirectionIncrement = 1

  ClockSprite.name = 'Clock'
  
  return ClockSprite 




def GetEthereumBalance():

  #Use CoinGeckoAPI to check current Ethereum price in currency
  ETHPrice = CoinGeckoAPI().get_price(ids='ethereum', vs_currencies='cad')
  CurrencyPrice = float(('{}'.format(ETHPrice['ethereum']['cad'])))
  print ("Etherium price CDN: ", CurrencyPrice)
  
  #Get current balance
  url     = "https://mainnet.infura.io/v3/b426370b8d7d4847b57db1b1a8603938"
  data    = {'jsonrpc':'2.0', 'id':1, 'method':'eth_getBalance', 'params':['0x3D15798193ecdc14217F431FC341fA81C70AAd45', 'latest']}
  headers = {'Content-type': 'application/json'}
  r       = requests.post(url, data=json.dumps(data), headers=headers)
  r_dict  = json.loads(r.text)
  
  ETHWalletBalance = float(int(r_dict['result'],0) / 1000000000000000000.0)
  CashBalance      = str(ETHWalletBalance * CurrencyPrice)

  print ("Ethereum balance:   ",ETHWalletBalance)
  print ("Cash value:         ",CashBalance," CDN")
    
  return CashBalance, CurrencyPrice, ETHWalletBalance


def CreateCurrencySprite():   
  

  #Use CoinGeckoAPI to check current Ethereum price in currency
  print ("Get currency price")
  ETHPrice = CoinGeckoAPI().get_price(ids='ethereum', vs_currencies='cad')
  CurrencyPrice = float(('{}'.format(ETHPrice['ethereum']['cad'])))
  
  #Get current balance
  print ("Getting wallet balance")
  url     = "https://mainnet.infura.io/v3/b426370b8d7d4847b57db1b1a8603938"
  data    = {'jsonrpc':'2.0', 'id':1, 'method':'eth_getBalance', 'params':['0x3D15798193ecdc14217F431FC341fA81C70AAd45', 'latest']}
  headers = {'Content-type': 'application/json'}
  r       = requests.post(url, data=json.dumps(data), headers=headers)

  r_dict  = json.loads(r.text)
  
  
  AccountBalance = str(float(int(r_dict['result'],0) / 1000000000000000000.0) * CurrencyPrice)
  print ("Balance:",AccountBalance,"CDN")

   
  #get dollars
  d1 = int(AccountBalance[0])
  d2 = int(AccountBalance[1])
  d3 = int(AccountBalance[2])
  #get cents
  c1 = int(AccountBalance[4])
  c2 = int(AccountBalance[5])


  ClockSprite = DigitSpriteList[d1]  
  ClockSprite = JoinSprite(ClockSprite, DigitSpriteList[d2], 1)
  ClockSprite = JoinSprite(ClockSprite, DigitSpriteList[d3], 1)
  ClockSprite = JoinSprite(ClockSprite, DigitSpriteList[c1], 1)
    

  ClockSprite.r = SDMedRedR
  ClockSprite.g = SDMedRedG
  ClockSprite.b = SDMedRedB
  
  
  #add variables to the object (python allows this, very cool!)
  ClockSprite.h = (gv.HatWidth - ClockSprite.width) // 2
  ClockSprite.v = -4
  ClockSprite.rgb = (SDMedGreenR,SDMedGreenG,SDMedGreenB)
  ClockSprite.AccountBalance = AccountBalance[0:6]

  #used for displaying clock
  ClockSprite.StartTime = time.time()

  #used for scrolling clock
  ClockSprite.PauseStartTime = time.time()
  ClockSprite.IsScrolling     = 0
  ClockSprite.Delay           = 2
  ClockSprite.PausePositionV  = 1
  ClockSprite.PauseTimerOn    = 0

  
  ClockSprite.on = 1
  ClockSprite.DirectionIncrement = 1
  ClockSprite.name = 'Currency'

  
  return ClockSprite 



def CreateSecondsSprite():   
  
  hhmmss = datetime.now().strftime('%I:%M:%S')
  hh,mm,ss = hhmmss.split(':')
 
  #get seconds digits
  s1 = int(ss[0])
  s2 = int(ss[1])

  SecondsSprite = JoinSprite(DigitSpriteList[s1], DigitSpriteList[s2], 1)
  
  SecondsSprite.r = SDDarkOrangeR
  SecondsSprite.g = SDDarkOrangeG
  SecondsSprite.b = SDDarkOrangeB
  
  
  #add variables to the object (python allows this, very cool!)
  SecondsSprite.h = (gv.HatWidth - SecondsSprite.width) // 2
  SecondsSprite.v = 5
  SecondsSprite.rgb = (SDMedGreenR,SDMedGreenG,SDMedGreenB)
  
  return SecondsSprite 



def CreateDayOfWeekSprite():   
  
  weekdaynum = datetime.today().weekday()
  dow        = ""
 
  if (weekdaynum   == 0 ):
    dow = "MON"
  elif (weekdaynum == 1 ):
    dow = "TUE"
  elif (weekdaynum == 2 ):
    dow = "WED"
  elif (weekdaynum == 3 ):
    dow = "THU"
  elif (weekdaynum == 4 ):
    dow = "FRI"
  elif (weekdaynum == 5 ):
    dow = "SAT"
  elif (weekdaynum == 6 ):
    dow = "SUN"


  DowSprite = LeftTrimSprite(CreateBannerSprite(dow),1)  
  
  DowSprite.r = SDMedOrangeR
  DowSprite.g = SDMedOrangeG
  DowSprite.b = SDMedOrangeB
  
  
  #add variables to the object (python allows this, very cool!)
  DowSprite.h = ((gv.HatWidth - DowSprite.width) // 2) -1
  DowSprite.v = 5
  DowSprite.rgb = (SDMedGreenR,SDMedGreenG,SDMedGreenB)
  
  return DowSprite



def CreateMonthSprite():   
  
  ShortMonth = (datetime.now()).strftime('%b').upper()
  print ("Month:",ShortMonth)
  

  MonthSprite = LeftTrimSprite(CreateBannerSprite(ShortMonth),1)
  
  MonthSprite.r = SDMedBlueR
  MonthSprite.g = SDMedBlueG
  MonthSprite.b = SDMedBlueB
  
  
  #add variables to the object (python allows this, very cool!)
  MonthSprite.h = ((gv.HatWidth - MonthSprite.width) // 2) -1
  MonthSprite.v = 5
  MonthSprite.rgb = (SDMedGreenR,SDMedGreenG,SDMedGreenB)
  
  return MonthSprite



def CreateDayOfMonthSprite():   
  
  DayOfMonth = str((datetime.now()).day)
  print ("Month:",DayOfMonth)
  

  DayOfMonthSprite = LeftTrimSprite(CreateBannerSprite(DayOfMonth),1)
  
  DayOfMonthSprite.r = SDMedBlueR
  DayOfMonthSprite.g = SDMedBlueG
  DayOfMonthSprite.b = SDMedBlueB
  
  
  #add variables to the object (python allows this, very cool!)
  DayOfMonthSprite.h = ((gv.HatWidth - DayOfMonthSprite.width) // 2) -1
  DayOfMonthSprite.v = 5
  DayOfMonthSprite.rgb = (SDMedGreenR,SDMedGreenG,SDMedGreenB)
  
  return DayOfMonthSprite





def CreateShortMessageSprite(ShortMessage):
  if (ShortMessage == "you win"):
    ShortMessageSprite = Sprite(
      16,
      11,
      200,
      0,
      0,
      [0,1,0,1,0,0,1,1,0,0,1,0,0,1,0,0,
       0,1,0,1,0,1,0,0,1,0,1,0,0,1,0,0,
       0,0,1,0,0,1,0,0,1,0,1,0,0,1,0,0,
       0,0,1,0,0,1,0,0,1,0,1,0,0,1,0,0,
       0,0,1,0,0,0,1,1,0,0,0,1,1,0,0,0,
       0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
       0,1,0,0,0,1,0,1,1,1,0,1,0,0,1,0,
       0,1,0,1,0,1,0,0,1,0,0,1,1,0,1,0,  
       0,1,1,0,1,1,0,0,1,0,0,1,0,1,1,0,
       0,0,1,0,1,0,0,1,1,1,0,1,0,0,1,0,
       0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,  
       ]
    )
  elif (ShortMessage == "you die"):
    ShortMessageSprite = Sprite(
      16,
      11,
      200,
      0,
      0,
      [0,1,0,1,0,0,1,1,0,0,1,0,0,1,0,0,
       0,1,0,1,0,1,0,0,1,0,1,0,0,1,0,0,
       0,0,1,0,0,1,0,0,1,0,1,0,0,1,0,0,
       0,0,1,0,0,1,0,0,1,0,1,0,0,1,0,0,
       0,0,1,0,0,0,1,1,0,0,0,1,1,0,0,0,
       0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
       0,1,1,0,0,1,1,1,0,1,1,1,0,0,1,0,
       0,1,0,1,0,0,1,0,0,1,0,0,0,0,1,0,  
       0,1,0,1,0,0,1,0,0,1,1,1,0,0,1,0,
       0,1,0,1,0,0,1,0,0,1,0,0,0,0,0,0,
       0,1,1,0,0,1,1,1,0,1,1,1,0,0,1,0,  
       ]
    )
  elif (ShortMessage == "smile"):
    ShortMessageSprite = Sprite(
      12,
      10,
      200,
      200,
      0,
      [0,0,0,0,1,1,1,1,0,0,0,0,
       0,0,0,1,0,0,0,0,1,0,0,0,
       0,0,1,0,0,0,0,0,0,1,0,0,
       0,1,0,0,1,0,0,1,0,0,1,0,
       0,1,0,0,0,0,0,0,0,0,1,0,
       0,1,0,1,0,0,0,0,1,0,1,0,
       0,1,0,0,1,1,1,1,0,0,1,0,
       0,0,1,0,0,0,0,0,0,1,0,0,  
       0,0,0,1,0,0,0,0,1,0,0,0,
       0,0,0,0,1,1,1,1,0,0,0,0,
       ]
    )
  else: #(ShortMessage == "frown"):
    ShortMessageSprite = Sprite(
      12,
      10,
      200,
      200,
      0,
      [0,0,0,0,1,1,1,1,0,0,0,0,
       0,0,0,1,0,0,0,0,1,0,0,0,
       0,0,1,0,0,0,0,0,0,1,0,0,
       0,1,0,0,1,0,0,1,0,0,1,0,
       0,1,0,0,0,0,0,0,0,0,1,0,
       0,1,0,0,0,1,1,0,0,0,1,0,
       0,1,0,0,1,0,0,1,0,0,1,0,
       0,0,1,0,0,0,0,0,0,1,0,0,  
       0,0,0,1,0,0,0,0,1,0,0,0,
       0,0,0,0,1,1,1,1,0,0,0,0,
       ]
    )
    
  
  #add variables to the object (python allows this, very cool!)
  ShortMessageSprite.h = (gv.HatWidth - ShortMessageSprite.width) // 2
  ShortMessageSprite.v = 0 - ShortMessageSprite.height
  ShortMessageSprite.rgb = (ShortMessageSprite.r,ShortMessageSprite.g,ShortMessageSprite.b)
  ShortMessageSprite.StartTime = time.time()
  
  #used for scrolling clock
  ShortMessageSprite.PauseStartTime = time.time()
  ShortMessageSprite.IsScrolling     = 0
  ShortMessageSprite.Delay           = 1
  ShortMessageSprite.PausePositionV  = 2
  ShortMessageSprite.PauseTimerOn    = 0
  
  ShortMessageSprite.on = 0
  ShortMessageSprite.DirectionIncrement = 1

  
  return ShortMessageSprite


  
  
def CreateShortWordSprite(ShortWord):   

  ShortWord = ShortWord.upper()
  TheBanner = CreateBannerSprite(ShortWord)
      

  TheBanner.r = SDMedRedR
  TheBanner.g = SDMedRedG
  TheBanner.b = SDMedRedB
  
  
  #add variables to the object (python allows this, very cool!)
  TheBanner.h = (gv.HatWidth - TheBanner.width) // 2
  TheBanner.v = -4
  TheBanner.rgb = (SDMedGreenR,SDMedGreenG,SDMedGreenB)

  #used for displaying clock
  TheBanner.StartTime = time.time()

  #used for scrolling clock
  TheBanner.PauseStartTime = time.time()
  TheBanner.IsScrolling     = 0
  TheBanner.Delay           = 2
  TheBanner.PausePositionV  = 1
  TheBanner.PauseTimerOn    = 0
  
  TheBanner.on = 1
  TheBanner.DirectionIncrement = 1

  
  return TheBanner 

  
  


  

  
 
  
def CreateBannerSprite(TheMessage):
  #We need to dissect the message and build our banner sprite one letter at a time
  #We need to initialize the banner sprite object first, so we pick the first letter
  x = -1
  
  BannerSprite = Sprite(1,5,0,0,0,[0,0,0,0,0])
  
  #Iterate through the message, decoding each characater
  for i,c, in enumerate(TheMessage):
    x = ord(c) -65
    if (c == '?'):
      BannerSprite = JoinSprite(BannerSprite, QuestionMarkSprite,0)
    elif (c == '-'):
      BannerSprite = JoinSprite(BannerSprite, DashSprite,0)
    elif (c == '#'):
      BannerSprite = JoinSprite(BannerSprite, DashSprite,0)
    elif (c == '$'):
      BannerSprite = JoinSprite(BannerSprite, DollarSignSprite,0)
    elif (c == '.'):
      BannerSprite = JoinSprite(BannerSprite, PeriodSprite,0)
    elif (c == ':'):
      BannerSprite = JoinSprite(BannerSprite, ColonSprite,0)
    elif (c == '!'):
      BannerSprite = JoinSprite(BannerSprite, ExclamationSprite,0)
    elif (c == ' '):
      BannerSprite = JoinSprite(BannerSprite, SpaceSprite,0)
    elif (ord(c) >= 48 and ord(c)<= 57):
      BannerSprite = JoinSprite(BannerSprite, DigitSpriteList[int(c)],1)
    else:
      BannerSprite = JoinSprite(BannerSprite, TrimSprite(AlphaSpriteList[x]),1)
  return BannerSprite

  
    

  
  

def ShowLevelCount(LevelCount):
  global MainSleep
  gv.TheMatrix.Clear()
      
  SDColor = (random.randint (0,6) *4 + 1) 
  print ("LevelCountColor:",SDColor)
  
  r,g,b =  ColorList[SDColor]  
  max   = 50
  #sleep = 0.06 * gv.MainSleep
  
  #print ("sleep: ",sleep," gv.MainSleep: ",MainSleep)
  
  LevelSprite = Sprite(1,5,r,g,b,[0,0,0,0,0])
  
  if (LevelCount > 9):
    LevelString = str(LevelCount)
    LevelSprite1 = DigitSpriteList[int(LevelString[0])]
    LevelSprite2 = DigitSpriteList[int(LevelString[1])]
   
    
    for x in range(0,max,1):
      LevelSprite1.r = r + x*5
      LevelSprite1.g = g + x*5
      LevelSprite1.b = b + x*5
      LevelSprite2.r = r + x*5
      LevelSprite2.g = g + x*5
      LevelSprite2.b = b + x*5

      if(LevelSprite1.r > 255):
        LevelSprite1.r = 255
      if(LevelSprite1.g > 255):
        LevelSprite1.g = 255
      if(LevelSprite1.b > 255):
        LevelSprite1.b = 255
      if(LevelSprite2.r > 255):
        LevelSprite2.r = 255
      if(LevelSprite2.g > 255):
        LevelSprite2.g = 255
      if(LevelSprite2.b > 255):
        LevelSprite2.b = 255

      LevelSprite.Display((gv.HatWidth-6) // 2 ,(gv.HatHeight -5)//2)
      LevelSprite.Display((gv.HatWidth-10) // 2 ,(gv.HatHeight -5)//2)      
      #unicorn.show()
      #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
      #time.sleep(sleep)

    
    for x in range(0,max,1):
      LevelSprite1.r = r + max -x*3
      LevelSprite1.g = g + max -x*3
      LevelSprite1.b = b + max -x*3
      LevelSprite2.r = r + max -x*3
      LevelSprite2.g = g + max -x*3
      LevelSprite2.b = b + max -x*3

      if(LevelSprite1.r < r):
        LevelSprite1.r = r
      if(LevelSprite1.g < g):
        LevelSprite1.g = g
      if(LevelSprite1.b < b):
        LevelSprite1.b = b
      if(LevelSprite2.r < r):
        LevelSprite2.r = r
      if(LevelSprite2.g < g):
        LevelSprite2.g = g
      if(LevelSprite2.b < b):
        LevelSprite2.b = b

      LevelSprite1.Display(6,1)
      LevelSprite2.Display(10,1)
      #unicorn.show()
      #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)

      #time.sleep(sleep) 
     
      
  else:    
    LevelSprite = DigitSpriteList[LevelCount]

    for x in range(0,max,1):
      LevelSprite.r = r + x*3
      LevelSprite.g = g + x*3
      LevelSprite.b = b + x*3

      if(LevelSprite.r > 255):
        LevelSprite.r = 255
      if(LevelSprite.g > 255):
        LevelSprite.g = 255
      if(LevelSprite.b > 255):
        LevelSprite.b = 255

      LevelSprite.Display((gv.HatWidth-3) // 2 ,(gv.HatHeight -5)//2)
      #unicorn.show()
      #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
      #time.sleep(sleep) 
      
    for x in range(0,max,1):
      LevelSprite.r = r + max -x*3
      LevelSprite.g = g + max -x*3
      LevelSprite.b = b + max -x*3

      if(LevelSprite.r < r):
        LevelSprite.r = r
      if(LevelSprite.g < g):
        LevelSprite.g = g
      if(LevelSprite.b < b):
        LevelSprite.b = b
      LevelSprite.Display((gv.HatWidth-3) // 2 ,(gv.HatHeight -5)//2)
      #unicorn.show()
      #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
      #time.sleep(sleep)
      

  
  gv.TheMatrix.Clear()
  return
  







  

  


  
def ScreenWipe(Wipe, Speed):
  if Wipe == "RedCurtain":
    for x in range (gv.HatWidth):
      for y in range (gv.HatHeight):
        gv.TheMatrix.SetPixel(x,y,255,0,0)
        #unicorn.show()
        #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
        time.sleep(Speed)
    
#Primitive, single color



  



  
  
def MoveBigSprite(sprite,FlashSleep):
  for i in range (0,80):
    
    y,x = divmod(i,16)
    #print ("x,y,i",x,y,i)
    if (x >= 0 and x<= 2):
      BigSprite.grid[i] = DigitSpriteList[2].grid[x-(0*4)+(y*3)]
    if (x >= 4 and x<= 6):
      BigSprite.grid[i] = DigitSpriteList[3].grid[x-(1*4)+(y*3)]
    if (x >=8  and x<= 10):
      BigSprite.grid[i] = DigitSpriteList[0].grid[x-(2*4)+(y*3)]
    if (x >=12  and x<= 14):
      BigSprite.grid[i] = DigitSpriteList[7].grid[x-(3*4)+(y*3)]
    #"looping"
  BigSprite.Scroll(-16,0,"right",24,gv.FlashSleep)
  BigSprite.Scroll(9,0,"left",24,gv.FlashSleep)
    

  
def JoinSprite(Sprite1, Sprite2, Buffer):
  #This function takes two sprites, and joins them together horizontally
  #The color of the second sprite is used for the new sprite
  height = Sprite1.height
  width  = Sprite1.width + Buffer + Sprite2.width
  elements = height * width
  x = 0
  y = 0
  
 
  TempSprite = Sprite(
  width,
  height,
  Sprite2.r,
  Sprite2.g,
  Sprite2.b,
  [0]*elements
  )
  for i in range (0,elements):
    y,x = divmod(i,width)
    
    #copy elements of first sprite
    if (x >= 0 and x< Sprite1.width):
      TempSprite.grid[i] = Sprite1.grid[x + (y * Sprite1.width)]
    
    if (x >= (Sprite1.width + Buffer) and x< (Sprite1.width + Buffer + Sprite2.width)):
      TempSprite.grid[i] = Sprite2.grid[(x - (Sprite1.width + Buffer)) + (y * Sprite2.width)]

  
  return TempSprite    


def TrimSprite(Sprite1):
  height       = Sprite1.height
  width        = Sprite1.width
  newwidth     = 0
  elements     = height * width
  Empty        = 1
  Skipped      = 0
  EmptyColumns = []
  EmptyCount   = 0
  BufferX      = 0
  BufferColumn = [(0) for i in range(height)]
  
  i = 0
  x = 0
  y = 0

  
  for x in range (0,width):
    
    #Find empty columns, add them to a list
    Empty = 1  
    for y in range (0,height):
      i = x + (y * width)
      
      BufferColumn[y] = Sprite1.grid[i]
      if (Sprite1.grid[i] != 0):
        Empty = 0
    
    if (Empty == 0):
      newwidth =  newwidth + 1
    
    elif (Empty == 1):
      #print ("Found empty column: ",x)
      EmptyColumns.append(x)
      EmptyCount = EmptyCount +1

      
  BufferSprite = Sprite(
    newwidth,
    height,
    Sprite1.r,
    Sprite1.g,
    Sprite1.b,
    [0]*(newwidth*height)
    )
      
  #Now that we identified the empty columns, copy data and skip those columns
  for x in range (0,width):
    Skipped = 0
    
    for y in range (0,height):
      i = x + (y * width)
      b = BufferX + (y * newwidth)
      if (x in EmptyColumns):
        Skipped = 1
      else:
        BufferSprite.grid[b] = Sprite1.grid[i]
    
    
    #advance our Buffer column counter only if we skipped a column
    if (Skipped == 0):
      BufferX = BufferX + 1
    
    
  
  BufferSprite.width = newwidth
  
  
  
  #print (BufferSprite.grid)
  return BufferSprite



def LeftTrimSprite(Sprite1,Columns):
  height       = Sprite1.height
  width        = Sprite1.width
  newwidth     = 0
  elements     = height * width
  Empty        = 1
  Skipped      = 0
  EmptyColumns = []
  EmptyCount   = 0
  BufferX      = 0
  BufferColumn = [(0) for i in range(height)]
  
  i = 0
  x = 0
  y = 0

  
  for x in range (0,width):
    
    #Find empty columns, add them to a list
    Empty = 1  
    for y in range (0,height):
      i = x + (y * width)
      
      BufferColumn[y] = Sprite1.grid[i]
      if (Sprite1.grid[i] != 0):
        Empty = 0
    
    if (Empty == 0 or EmptyCount > Columns):
      newwidth =  newwidth + 1
    
    elif (Empty == 1):
      #print ("Found empty column: ",x)
      EmptyColumns.append(x)
      EmptyCount = EmptyCount +1

      
  BufferSprite = Sprite(
    newwidth,
    height,
    Sprite1.r,
    Sprite1.g,
    Sprite1.b,
    [0]*(newwidth*height)
    )
      
  #Now that we identified the empty columns, copy data and skip those columns
  for x in range (0,width):
    Skipped = 0
    
    for y in range (0,height):
      i = x + (y * width)
      b = BufferX + (y * newwidth)
      if (x in EmptyColumns):
        Skipped = 1
      else:
        BufferSprite.grid[b] = Sprite1.grid[i]
    
    
    #advance our Buffer column counter only if we skipped a column
    if (Skipped == 0):
      BufferX = BufferX + 1
    
    
  
  BufferSprite.width = newwidth
  
  
  
  #print (BufferSprite.grid)
  return BufferSprite
    
  
 
  




#------------------------------------------------------------------------------
# Keyboard Functions                                                         --
#------------------------------------------------------------------------------


import curses

def ProcessKeypress(Key):

  global MainSleep
  global ScrollSleep
  global NumDots

  # a = animation demo
  # h = set time - hours minutes
  # q = quit - go on to next game
  # i = show IP address
  # r = reboot
  # p or space = pause 5 seconds
  # c = analog clock for 1 hour
  # t = Clock Only mode
  # 1 - 8 Games
  # 8 = ShowDotZerkRobotTime
  # 0 = ?
  # m = Debug Playfield/Map
    
  if (Key == "p" or Key == " "):
    time.sleep(5)
  elif (Key == "q"):
    gv.TheMatrix.Clear()
    ShowScrollingBanner2("Quit!",(MedRed),gv.ScrollSleep)
  elif (Key == "r"):
    gv.TheMatrix.Clear()
    #ShowScrollingBanner("Reboot!",100,0,0,ScrollSleep * 0.55)
    os.execl(sys.executable, sys.executable, *sys.argv)
  elif (Key == "t"):

    ActivateClockMode(60)

  elif (Key == "c"):
    DrawTinyClock(60)
  elif (Key == "h"):
    SetTimeHHMM()
  elif (Key == "i"):
    ShowIPAddress()
  elif (Key == "a"):
    ShowAllAnimations(ScrollSleep * 0.5)


  elif (Key == "1"): 
    PlayPacDot(30)
  elif (Key == "2"):
    PlaySuperWorms()
  elif (Key == "3"):
    PlayWormDot()
  elif (Key == "4"):
    PlaySpaceDot()
  elif (Key == "5"):
    PlayDotZerk()
  elif (Key == "6"):
    PlayDotInvaders()
  elif (Key == "7"):
    gv.TheMatrix.Clear()
    PlayRallyDot()
  elif (Key == "8"):
    gv.TheMatrix.Clear()
    PlayOutbreak()


    
  elif (Key == "9"):
    gv.TheMatrix.Clear()
    ShowDotZerkRobotTime(0.03)
    ShowFrogTime(0.04)
  elif (Key == "0"):
    gv.TheMatrix.Clear()
    DrawSnake(random.randint(0,gv.HatWidth-1),random.randint(0,gv.HatWidth-1),255,0,0,random.randint(1,4),.5)
    DrawSnake(random.randint(0,gv.HatWidth-1),random.randint(0,gv.HatWidth-1),0,255,0,random.randint(1,4),.5)
    DrawSnake(random.randint(0,gv.HatWidth-1),random.randint(0,gv.HatWidth-1),0,0,255,random.randint(1,4),.5)
    DrawSnake(random.randint(0,gv.HatWidth-1),random.randint(0,gv.HatWidth-1),125,125,0,random.randint(1,4),.5)
    DrawSnake(random.randint(0,gv.HatWidth-1),random.randint(0,gv.HatWidth-1),0,125,125,random.randint(1,4),.5)
    DrawSnake(random.randint(0,gv.HatWidth-1),random.randint(0,gv.HatWidth-1),125,0,125,random.randint(1,4),.5)
  elif (Key == "+"):
    MainSleep = MainSleep -0.01
    ScrollSleep = ScrollSleep * 0.75
    if (MainSleep <= 0.01):
      MainSleep = 0.01

    #print("Game speeding up")
    #print("MainSleep: ",MainSleep, " ScrollSleep: ",ScrollSleep)
  elif (Key == "-"):
    MainSleep = MainSleep +0.01
    ScrollSleep = ScrollSleep / 0.75
    #print("Game slowing down ")
    #print("MainSleep: ",MainSleep, " ScrollSleep: ",ScrollSleep)



    
    
    


def GetKey(stdscr):
  ReturnChar = ""
  stdscr.nodelay(1) # doesn't keep waiting for a key press
  c = stdscr.getch()  
  
  #Look for specific characters
  if  (c == ord(" ") 
    or c == ord("+")
    or c == ord("-")
    or c == ord("a")
    or c == ord("b")
    or c == ord("c")
    or c == ord("d")
    or c == ord("h")
    or c == ord("i")
    or c == ord("p")
    or c == ord("q")
    or c == ord("r")
    or c == ord("t")
    or c == ord("n")
    or c == ord("m") ):
    ReturnChar = chr(c)       

  #Look for digits (ascii 48-57 == digits 0-9)
  elif (c >= 48 and c <= 57):
    print ("Digit detected")
    ReturnChar = chr(c)    

  return ReturnChar
 

  
  

def PollKeyboard():
  Key = ""
  curses.filter()
  stdscr = curses.initscr()
  curses.noecho()
  Key = curses.wrapper(GetKey)
  if (Key != ""):
    print ("----------------")
    print ("Key Pressed: ",Key)
    print ("----------------")
    #ProcessKeypress(Key)
    #SaveConfigData()
    
  
  return Key


  
def GetKeyInt(stdscr):
  ReturnInt = -1
  stdscr.nodelay(1) # doesn't keep waiting for a key press
  
  #gets ascii value
  c = stdscr.getch()  

  
  #Look for digits (ascii 48-57 == digits 0-9)
  if (c >= 48 and c <= 57):
    print ("Digit detected")
    ReturnInt = c - 48   

  return ReturnInt

  
  
def PollKeyboardInt():
  Key = -1
  stdscr = curses.initscr()
  curses.noecho()
  Key = curses.wrapper(GetKeyInt)
  if (Key != -1):
    print ("----------------")
    print ("Key Pressed: ",Key)
    print ("----------------")
    ProcessKeypress(Key)
  
  return Key


  

  
  
  
# This section deals with getting specific input from a question and does not
# trigger events  
  
def GetKeyRegular(stdscr):
  ReturnChar = ""
  stdscr.nodelay(1) # doesn't keep waiting for a key press
  c = stdscr.getch()  

  if (c >= 48 and c <= 150):
    ReturnChar = chr(c)    

  return ReturnChar
  
def PollKeyboardRegular():
  Key = ""
  stdscr = curses.initscr()
  curses.noecho()
  Key = curses.wrapper(GetKeyRegular)
  if (Key != ""):
    print ("----------------")
    print ("Key Pressed: ",Key)
    print ("----------------")
  
  return Key
  


def GetClockDot(time):
  #this is a list of hv coordinates around the outside of the unicorn hat
  #pass in a number from 1-60 to get the correct dot to display
  
  DotList = []
  DotList.append ([4,0]) #0 same as 60
  DotList.append ([4,0])
  DotList.append ([5,0])
  DotList.append ([6,0])
  DotList.append ([7,0])
  DotList.append ([7,1])
  DotList.append ([7,2])
  DotList.append ([7,3])
  DotList.append ([7,4])
  DotList.append ([7,5])
  DotList.append ([7,6])
  DotList.append ([7,7])
  DotList.append ([6,7])
  DotList.append ([5,7])
  DotList.append ([4,7])
  DotList.append ([3,7])
  DotList.append ([2,7])
  DotList.append ([1,7])
  DotList.append ([0,7])
  DotList.append ([0,6])
  DotList.append ([0,5])
  DotList.append ([0,4])
  DotList.append ([0,3])
  DotList.append ([0,2])
  DotList.append ([0,1])
  DotList.append ([0,0])
  DotList.append ([1,0])
  DotList.append ([2,0])
  DotList.append ([3,0])
  
  return DotList[time]







def DrawTinyClock(Minutes):
  print ("--DrawTinyClock--")
  print ("Minutes:",Minutes)
  gv.TheMatrix.Clear()
  MinDate = datetime.now()
  MaxDate = datetime.now() + timedelta(minutes=Minutes)
  now     = datetime.now()
  Quit    = 0
  

  while (now >= MinDate and now <= MaxDate and Quit == 0):
    print ("--DrawTinyClock--")
    gv.TheMatrix.Clear()
    ClockSprite = CreateClockSprite(2)
    ClockSprite.r = SDDarkRedR
    ClockSprite.g = SDDarkRedG
    ClockSprite.b = SDDarkRedB


    #Center the display
    h = 3 - (ClockSprite.width // 2)
    ClockSprite.Display(h,1)

    #break apart the time
    now = datetime.now()

    print ("Now:",now)
    print ("Min:",MinDate)
    print ("Max:",MaxDate)
    DrawClockMinutes()
    Quit = DrawClockSeconds()
    print("Quit:",Quit)
    now = datetime.now()

  gv.TheMatrix.Clear()
    
def DrawClockMinutes():

  #break apart the time
  now = datetime.now()
  mm  = now.minute
  print ("DrawClockMinutes minutes:",mm)  
  
  dots = int(28.0 // 60.0 * mm)

#  #Erase  
  for i in range(1,28):
    h,v = GetClockDot(i)
  gv.TheMatrix.SetPixel(h,v,0,0,0)
  #unicorn.show()
  #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)

  
  for i in range(1,dots+1):
    print ("Setting minute dot:",i)
    h,v = GetClockDot(i)
    gv.TheMatrix.SetPixel(h,v,SDDarkBlueR,SDDarkBlueG,SDDarkBlueB)
    #unicorn.show()
    #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
  
  
  
  
def DrawClockSeconds():
  #break apart the time
  now = datetime.now()
  ss  = now.second
  
  print ("--DrawClockSeconds seconds:",ss,"--")  

  r = 0
  g = 0
  b = 0
  
   
  h = 0
  v = 0
  x = -1
  y = -1
  
  
  gv.TheMatrix.SetPixel(3,0,0,0,0)


  for i in range(ss,61):
    
    #Erase dot 0/60
    DisplayDot =  int(28.0 // 60.0 * i)
    h,v = GetClockDot(DisplayDot)
    
    
    print ("Setting second dot:",i)
    #print ("xy hv:",x,y,h,v)
    if (x >= 0):
      #print ("writing old pixel")
      gv.TheMatrix.SetPixel(x,y,r,g,b)

    
    #capture previous pixel
    x,y = h,v
    
    r,g,b = getpixel(h,v)
    gv.TheMatrix.SetPixel(h,v,SDLowWhiteR,SDLowWhiteG,SDLowWhiteB)
    #unicorn.show()
    #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
    time.sleep(0.005)

    gv.TheMatrix.SetPixel(h,v,SDDarkPurpleR,SDDarkPurpleG,SDDarkPurpleB)
    #unicorn.show()
    #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
    
    #Check for keyboard input
    Key = PollKeyboard()
    if (Key == 'q'):
      return 1
    

    
    time.sleep(0.995)
    
  print ("--end seconds--")
  return 0
  

def GetDistanceBetweenDots(h1,v1,h2,v2):
  a = abs(h1 - h2)
  b = abs(v1 - v2)
  c = math.sqrt(a**2 + b**2)

  return c;  






#--------------------------------------
#  Transitions and Sequences         --
#--------------------------------------




def ScrollBigClock(direction,speed,ZoomFactor,RGB):    
  #Screen capture is a copy of the unicorn display Buffer, which in HD is a numby array
  #Capture the screen, then pass that to this function
  #this function will make a copy, chop up that copy and display the slices in the order to make
  #it look like the screen is scrolling up or down, left or right
  
  #For now, we scroll, replacing with empty screen.  Also, reverse.
 

  ScreenCap    = copy.deepcopy(gv.ScreenArray)
  OldScreenCap = copy.deepcopy(gv.ScreenArray)
  

  TheTime = CreateClockSprite(12)
  TheTime.h = (gv.HatWidth  //2) - (TheTime.width  * ZoomFactor // 2)
  TheTime.v = (gv.HatHeight //2) - (TheTime.height * ZoomFactor // 2)


  CopySpriteToBufferZoom(TheTime,TheTime.h,TheTime.v, ColorTuple=RGB,FillerTuple=(-1,-1,-1),ZoomFactor = ZoomFactor)
  InsertLine = gv.ScreenArray[0]
  
  print("InsertLine LEN:",len(InsertLine))
  print("ScreenCap  LEN:",len(ScreenCap[0]))
  print("ScreenArray  LEN:",len(gv.ScreenArray[0]))

  #Scroll up
  #Delete top row, insert blank on bottom, pushing remaining to the top
  if (direction == 'up'):
    
    #print ("Buffer",Buffer)

    for x in range (0,gv.HatHeight):
      InsertLine = gv.ScreenArray[x]
      ScreenCap = numpy.delete(ScreenCap,(0),axis=0)
      ScreenCap = numpy.insert(ScreenCap,gv.HatHeight-1,InsertLine,axis=0)
      setpixelsLED(ScreenCap)
      #unicorn.show()
      #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
      time.sleep(speed)

    
    

  Oldmm = 0
  done  = 0
  ShownOnce = 0
  
  while (1 == 1):
 
    #If the time has changed, draw a new time
    mm = datetime.now().strftime('%M')
    if (mm != Oldmm):
      #Erase old time
      Oldmm = mm
      ClearBigLED()

      TheTime = CreateClockSprite(12)
      TheTime.h = (gv.HatWidth //2 )  - (TheTime.width * ZoomFactor // 2)
      TheTime.v = (gv.HatHeight //2 ) - (TheTime.height * ZoomFactor // 2)

      #Display New Time
      CopySpriteToPixelsZoom(TheTime,TheTime.h,TheTime.v, ColorTuple=RGB,FillerTuple=(-1,-1,-1),ZoomFactor = ZoomFactor)

    Key = PollKeyboard()
    if (Key =='q'):
      for x in range (0,gv.HatHeight):
        InsertLine = OldScreenCap[x]
        ScreenCap = numpy.delete(ScreenCap,(0),axis=0)
        ScreenCap = numpy.insert(ScreenCap,gv.HatHeight-1,InsertLine,axis=0)
        setpixelsLED(ScreenCap)
        #unicorn.show()
        #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
        time.sleep(speed)
      return;

         
    time.sleep(1)








def ScrollScreen(direction,ScreenCap,speed):    
  #Screen capture is a copy of the unicorn display Buffer, which in HD is a numby array
  #Capture the screen, then pass that to this function
  #this function will make a copy, chop up that copy and display the slices in the order to make
  #it look like the screen is scrolling up or down, left or right
  
  #For now, we scroll, replacing with empty screen.  Also, reverse.
 
 
  EmptyCap   = [[(0,0,0) for i in range (0,gv.HatWidth)]]
  InsertLine = copy.deepcopy(EmptyCap)
  Buffer     = copy.deepcopy(EmptyCap)

  
  #Scroll up
  #Delete top row, insert blank on bottom, pushing remaining to the top
  if (direction == 'up'):
    Buffer = copy.deepcopy(ScreenCap)
    #print ("Buffer",Buffer)

    for x in range (0,gv.HatHeight):
      
      Buffer = numpy.delete(Buffer,(0),axis=1)
      Buffer = numpy.insert(Buffer,gv.HatHeight-1,InsertLine,axis=1)
      setpixelsLED(Buffer)


      #unicorn.show()
      #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
      #print(Buffer)
      time.sleep(speed)

  #Scroll down
  #Screen is blank, start adding lines from ScreenCap
  if (direction == 'down'):
    # Make an empty Buffer, axis must be 0 to match the EmptyBuffer layout [(0,0,0),(0,0,0),(0,0,0)...etc.]
    Buffer = [[(0,0,0) for i in range(gv.HatHeight)] for i in range(gv.HatWidth)]

    for x in range (0,gv.HatWidth):
      InsertLine = [()]
      #copy line from the ScreenCap into the Buffer
      #we do this one element at a time because I could not figure out how to slice the array properly
      for y in range (0,gv.HatWidth):
        InsertLine = numpy.append(InsertLine, ScreenCap[y][abs(gv.HatWidth-1 - x)])

      InsertLine = InsertLine.reshape(1,gv.HatWidth,3)
      Buffer = numpy.insert(Buffer,0,InsertLine,axis=1)
      setpixelsLED(Buffer)
      #unicorn.show()
      #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
      time.sleep(speed)


      
      

  #Scroll to RIGHT
  #Delete right row, insert blank on left, pushing remaining to the right
  if (direction == 'right'):
    Buffer = copy.deepcopy(ScreenCap)
    for x in range (0,gv.HatWidth):
      
      Buffer = numpy.delete(Buffer,(0),axis=0)
      Buffer = numpy.append(Buffer,EmptyCap,axis=0)
      setpixelsLED(Buffer)
      #unicorn.show()
      #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
      #time.sleep(speed)
  
  
  
  
  #Scroll to LEFT
  #Delete left row, insert blank on right, pushing remaining to the left
  if (direction == 'left'):
    # Make an empty Buffer
    for x in range (0,gv.HatWidth-1):
      Buffer = numpy.append(Buffer,EmptyCap,axis=0)

    for x in range (0,gv.HatWidth):
      Buffer = numpy.delete(Buffer,(-1),axis=0)
      
      #Copy each tuple to the line to be inserted (gotta be a better way!)
      for j in range (gv.HatWidth):
        InsertLine[0][j] = ScreenCap[abs(gv.HatWidth-x)][j]
      
      Buffer = numpy.insert(Buffer,0,InsertLine,axis=0)
      
      setpixelsLED(Buffer)
      #unicorn.show()
      #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
      time.sleep(speed)


      







def ZoomScreen(ScreenArray,ZoomStart,ZoomStop,ZoomSleep):    
  #Capture the screen, then pass that to this function
  #Loop through the zoom levels specified, calling the DisplayScreenCap function

 
  ZoomFActor = 0
    

  if (ZoomStart <= ZoomStop):
    for ZoomFactor in range (ZoomStart,ZoomStop):
      gv.TheMatrix.Clear()        
      DisplayScreenCap(ScreenArray,ZoomFactor)
      time.sleep(ZoomSleep)
        
  else:
    for ZoomFactor in reversed(range(ZoomStop, ZoomStart)):
      #clear the screen as we zoom to remove leftovers
      gv.TheMatrix.Clear()        
      DisplayScreenCap(ScreenArray,ZoomFactor )
      time.sleep(ZoomSleep)




  # for y in range (gv.HatWidth):
    # for x in range (gv.HatWidth):
      # r,g,b = ScreenCap[abs(15-x)][y]
      # gv.TheMatrix.SetPixel(x,y,r,g,b)





def DisplayScreenCap(ScreenCap,ZoomFactor = 0):
  #This function writes a Screen capture to the buffer using the specified zoom factor
  r = 0
  g = 0
  b = 0
  count    = 0
  H_modifier = 0
  V_modifier = 0
    
  HIndentFactor = 0    
  VIndentFactor = 0    


  if (ZoomFactor > 1):
    H_modifier = (1 / gv.HatWidth ) * ZoomFactor * 2  #BigLED is 2 times wider than tall. Hardcoding now, will fix later. 
    V_modifier = (1 / gv.HatHeight ) * ZoomFactor
    NewHeight = round(gv.HatHeight * V_modifier)
    NewWidth  = round(gv.HatWidth * H_modifier)


    HIndentFactor = (gv.HatWidth / 2)  - (NewWidth /2)
    VIndentFactor = (gv.HatHeight / 2) - (NewHeight /2)
  else:
    IndentFactor = 0



  for V in range(0,gv.HatHeight):
    for H in range (0,gv.HatWidth):
      r,g,b = ScreenCap[V][H]
      if (ZoomFactor > 0):
        gv.Canvas.SetPixel((H * H_modifier) + HIndentFactor ,(V * V_modifier) + VIndentFactor,r,g,b)

      else:
        gv.Canvas.SetPixel(H,V,r,g,b)
  
  gv.TheMatrix.SwapOnVSync(gv.Canvas)
        
  
  #unicorn.show()




  
    
def ScrollScreenScrollBanner(message,r,g,b,direction,speed):

  # this has been converted from an older way of scrolling.  
  # we might need to input multiple directions to give more flexibility
  
  
  ScreenCap  = copy.deepcopy(unicorn.get_pixels())
  ScrollScreen('up',ScreenCap,speed)

  af.ShowScrollingBanner(message,r,g,b,speed)

  TheTime.ScrollAcrossScreen(0,1,"right",speed)
  ScrollScreen('down',ScreenCap,speed)





def PointTowardsObject8Way(SourceH,SourceV,TargetH,TargetV):

  #   8 1 2
  #   7 . 3
  #   6 5 4

  #d = GetDistanceBetweenDots(SourceH, SourceV, TargetH, TargetV):
  
  #source is upper left of target
  if (SourceH < TargetH and SourceV < TargetV):
    direction = 4

  #source is directly above target
  elif (SourceH == TargetH and SourceV < TargetV):
    direction = 5

  #source is upper right of target
  elif (SourceH > TargetH and SourceV < TargetV):
    direction = 6

  #source is directly right of target
  elif (SourceH > TargetH and SourceV == TargetV):
    direction = 7

  #source is lower right of target
  elif (SourceH > TargetH and SourceV > TargetV):
    direction = 8

  #source is directly below target
  elif (SourceH == TargetH and SourceV > TargetV):
    direction = 1
    
  #source is lower left of target
  elif (SourceH < TargetH and SourceV > TargetV):
    direction = 2

  #source is directly left of target
  elif (SourceH < TargetH and SourceV == TargetV):
    direction = 3

  else: direction = random.randint(1,8)

  return direction;




def TurnTowardsShipWay(SourceShip, TargetShip):

#     1 
#   4   2
#     3

  #Source is to the left of target
  if (SourceShip.h < TargetCar.h):
    if (SourceShip.direction in (1,4)):
      SourceShip.direction =  TurnRight(SourceShip.direction)
    if (SourceShip.direction == 3):
      SourceShip.direction = TurnLeft(SourceShip.direction)
      
  if (SourceShip.h > TargetCar.h):
    if (SourceShip.direction in (1,2)):
      SourceShip.direction = TurnLeft(SourceShip.direction)
    if (SourceShip.direction in (3,12)):
      SourceShip.direction =  TurnRight(SourceShip.direction)


  if (SourceShip.v < TargetCar.v):
    if (SourceShip.direction in (1,4)):
      SourceShip.direction = TurnLeft(SourceShip.direction)
    if (SourceShip.direction == 2):
      SourceShip.direction =  TurnRight(SourceShip.direction)
      
  if (SourceShip.v > TargetCar.v):
    if (SourceShip.direction in (4,3)):
      SourceShip.direction =  TurnRight(SourceShip.direction)
    if (SourceShip.direction == 2):
      SourceShip.direction = TurnLeft(SourceShip.direction)

  SourceShip.scandirection = SourceShip.direction
  return;
  




def PointTowardsObjectH(Source, Target):

#     1 
#   4   2
#     3

  #Source is to the left of target
  if (Source.h < Target.h and Source.direction == 4) or (Source.h > Target.h and Source.direction == 2):
    Source.direction = ReverseDirection(Source.direction)

  return;
  






def ShowIPAddress():
  IPAddress = str(subprocess.check_output("hostname -I", shell=True)[:-1]);
  print ("-->",IPAddress,"<--")
  af.ShowScrollingBanner2(IPAddress,(af.HighGreen),gv.ScrollSleep )
  af.ShowScrollingBanner2(IPAddress,(af.HighGreen),gv.ScrollSleep )














def ShowGlowingText(
    h          = -1,
    v          = -1,
    Text       = 'Test',
    RGB        = (100,100,100),
    ShadowRGB  = (20,20,20),
    ZoomFactor = 2,
    GlowLevels = 200,
    DropShadow = True,
    CenterHoriz = False,
    CenterVert  = False,
    FadeLevels  = 0,
    FadeDelay   = 1
    
  ):


  r,g,b = RGB 
  r2 = 0
  g2 = 0
  b2 = 0
  Text      = Text.upper()
  TheBanner = CreateBannerSprite(Text)
  

  #Center if HV not specified
  if (CenterHoriz == True):
    h = (gv.HatWidth // 2)  - ((TheBanner.width * ZoomFactor) // 2) - ZoomFactor
  if (CenterVert  == True):
    v = (gv.HatHeight // 2) - ((TheBanner.height * ZoomFactor) // 2) - ZoomFactor

  #Draw Shadow Text
  if(DropShadow == True):
    CopySpriteToPixelsZoom(TheBanner,h-1,v+1,ShadowRGB,(0,0,0),ZoomFactor,Fill=False)

                                    
  if (GlowLevels > 0):
    for i in range (1,GlowLevels):
      r2 = math.ceil((r / GlowLevels) * i)
      g2 = math.ceil((g / GlowLevels) * i)
      b2 = math.ceil((b / GlowLevels) * i)
      CopySpriteToPixelsZoom(TheBanner,h,v,(r2,g2,b2),(0,0,0),ZoomFactor,Fill=False)

  #Draw text
  CopySpriteToPixelsZoom(TheBanner,h,v,(r,g,b),(0,0,0),ZoomFactor,Fill=False)


  #Fade away!
  if (FadeLevels > 0):
    time.sleep(FadeDelay)
    if(DropShadow == True):
      CopySpriteToPixelsZoom(TheBanner,h-1,v+1,(0,0,0),(0,0,0),ZoomFactor,Fill=False)

    for i in range (FadeLevels,0,-1):
      r2 = math.ceil((r / GlowLevels) * i)
      g2 = math.ceil((g / GlowLevels) * i)
      b2 = math.ceil((b / GlowLevels) * i)
      CopySpriteToPixelsZoom(TheBanner,h,v,(r2,g2,b2),(0,0,0),ZoomFactor,Fill=False)
    CopySpriteToPixelsZoom(TheBanner,h-1,v+1,(0,0,0),(0,0,0),ZoomFactor,Fill=False)





 
  return   






def CopySpriteToPixelsZoom(TheSprite,h,v, ColorTuple=(-1,-1,-1),FillerTuple=(-1,-1,-1),ZoomFactor = 1,Fill=True):
  #Copy a regular sprite to the LED and the ScreenArray buffer
  #Apply a ZoomFactor i.e  1 = normal / 2 = double in size / 3 = 3 times the size
  #print ("Copying sprite to playfield:",TheSprite.name, ObjectType, Filler)
  #if Fill = False, don't write anything for filler, that way we can leave existing lights on LED

  width   = TheSprite.width 
  height  = TheSprite.height

  
  
  if (ColorTuple == (-1,-1,-1)):
    r = TheSprite.r
    g = TheSprite.g
    b = TheSprite.b
  else:
    r,g,b   = ColorTuple
  
  if (FillerTuple == (-1,-1,-1)):
    fr = 0
    fg = 0
    fb = 0
  else:
    fr,fg,fb   = FillerTuple


  #Copy sprite to LED pixels
  for count in range (0,(TheSprite.width * TheSprite.height)):
    y,x = divmod(count,TheSprite.width)

    y = y * ZoomFactor
    x = x * ZoomFactor


    if (ZoomFactor >= 1):
      for zv in range (0,ZoomFactor):
        for zh in range (0,ZoomFactor):
          H = x+h+zh
          V = y+v+zv
         
          if(CheckBoundary(H,V) == 0):

            if TheSprite.grid[count] != 0:
              gv.Canvas.SetPixel(H,V,r,g,b)
              gv.ScreenArray[V][H]=(r,g,b)
            else:
              if (Fill == True):
                gv.Canvas.SetPixel(H,V,fr,fg,fb)
                gv.ScreenArray[V][H]=(fr,fg,fb)

  #draw the contents of the buffer to the LED matrix
  gv.TheMatrix.SwapOnVSync(gv.Canvas)
  



  return;





def CopySpriteToBufferZoom(TheSprite,h,v, ColorTuple=(-1,-1,-1),FillerTuple=(-1,-1,-1),ZoomFactor = 1,Fill=True):
  #Copy a regular sprite to the a buffer
  #Apply a ZoomFactor i.e  1 = normal / 2 = double in size / 3 = 3 times the size
  #print ("Copying sprite to playfield:",TheSprite.name, ObjectType, Filler)


  width   = TheSprite.width 
  height  = TheSprite.height
  
  if (ColorTuple == (-1,-1,-1)):
    r = TheSprite.r
    g = TheSprite.g
    b = TheSprite.b
  else:
    r,g,b   = ColorTuple

  if (FillerTuple == (-1,-1,-1)):
    fr = 0
    fg = 0
    fb = 0
  else:
    fr,fg,fb   = FillerTuple


  #Copy sprite to buffer 
  for count in range (0,(width * height)):
    y,x = divmod(count,width)

    y = y * ZoomFactor
    x = x * ZoomFactor

 
    if (ZoomFactor >= 1):
      for zv in range (0,ZoomFactor):
        for zh in range (0,ZoomFactor):
          H = x+h+zh
          V = y+v+zv
         
          if(CheckBoundary(H,V) == 0):

            if TheSprite.grid[count] != 0:
              gv.Canvas.SetPixel(H,V,r,g,b)
              gv.ScreenArray[V][H]=(r,g,b)
            else:
              if (Fill == True):
                gv.Canvas.SetPixel(H,V,fr,fg,fb)
                gv.ScreenArray[V][H]=(fr,fg,fb)


  
  return




  def CopySpriteToBuffer(self,h1,v1):
    #Does the same as Display, but does not call show(), allowing calling function to further modify the Buffer
    #before displaying
    x = 0,
    y = 0
    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
      #print("Count:",count,"xy",x,y)
      if self.grid[count] == 1:
        if (CheckBoundary(x+h1,y+v1) == 0):
          gv.TheMatrix.SetPixel(x+h1,y+v1,self.r,self.g,self.b)
      elif self.grid[count] == 0:
        if (CheckBoundary(x+h1,y+v1) == 0):
          gv.TheMatrix.SetPixel(x+h1,y+v1,0,0,0)
    #unicorn.show()



def DisplayScore(score,rgb):

  r,g,b = rgb

  ScoreSprite = CreateBannerSprite(str(score))
  ScoreH      = gv.HatWidth  - ScoreSprite.width
  ScoreV      = gv.HatHeight - ScoreSprite.height
  ScoreSprite.r = r
  ScoreSprite.g = g
  ScoreSprite.b = b
  ScoreSprite.DisplayIncludeBlack(ScoreH,ScoreV)



def DisplayLevel(level,rgb):

  r,g,b = rgb

  ScoreSprite = CreateBannerSprite(str(level))
  ScoreH      = gv.HatWidth  - 33
  ScoreV      = gv.HatHeight - ScoreSprite.height
  ScoreSprite.r = r
  ScoreSprite.g = g
  ScoreSprite.b = b
  ScoreSprite.DisplayIncludeBlack(ScoreH,ScoreV)








  

def DebugPlayfield(Playfield,width,height):
  #Show contents of playfield - in text window, for debugging purposes
    
  print ("Map width height:",width,height)

  
  print ("=======================================")

  for V in range(0,height):
    for H in range (0,width):
       
      name = Playfield[V][H].name
      #print ("Display: ",name,V,H)
      if (name == 'EmptyObject'):
        print ('--',end='')

      #draw border walls
      elif (V == 0 or V == height-1):
        print(' _',end='')
      
      #draw border walls
      elif (H == 0 or H == width-1):
        print(' |',end='')
        
      #draw interior
      elif (name == 'Wall'):
        print (' #',end='')

      elif (name == 'Ground'):
        print (' G',end='')

      #draw asteroid
      elif (name == 'Asteroid'):
        if (Playfield[V][H].alive == 1):
          print (' A',end='')
        else:
          print ('*a')
        
        FlashDot(H,V,0.01)


      #draw asteroid
      elif (name == 'UFO'):
        print (' U',end='')

      #draw asteroid
      elif (name == 'BomberShip'):
        print (' B',end='')

      #draw UFOMissile
      elif (name == 'UFOMissile'):
        print (' m',end='')

      #draw UFOMissile
      elif (name == 'PlayerMissile'):
        print (' p',end='')

      #draw UFOMissile
      elif (name == 'Explosion'):
        print (' E',end='')

      #draw HomingMissile
      elif (name == 'HomingMissile'):
        print (' H',end='')



      #draw interior
      elif (name == 'WallBreakable'):
        print (' o',end='')

      elif (Playfield[V][H].alive == 1):
        print (' ?',end='')
        #print ("Name?:",name," alive:",Playfield[V][H].alive)
      elif (Playfield[V][H].alive == 0):
        print (' !',end='')
        #print ("Name!:",name," alive:",Playfield[V][H].alive)
      else:
        print (' X',end='')
        #print ("NameX:",name," alive:",Playfield[V][H].alive)

    print('')
  print ("=============================================")
  time.sleep(1)

  return






def GetElapsedSeconds(starttime):
  elapsed_time = time.time() - starttime
  elapsed_hours   = elapsed_time / 3600
  elapsed_minutes = elapsed_time / 60
  elapsed_seconds = elapsed_time 
  #print ("StartTime:",starttime,"Seconds:",seconds)
  #print("Clock Timer: {:0>2}:{:0>2}:{:05.2f}".format(int(elapsed_hours),int(elapsed_minutes),elapsed_seconds),"Elapsed seconds:",elapsed_seconds, "Check seconds:",seconds)
  
  return elapsed_time



def CleanupDebris(StartH,EndH,StartV,EndV,Playfield):
  

  for V in range(StartV,EndV):
    for H in range (StartH,EndH):
      if ((Playfield[V][H].name  == 'EmptyObject') 
       or (Playfield[V][H].name  in ('Explosion','HomingMissile') and Playfield[V][H].alive == 0)):
        setpixel(H,V,0,0,0)
        Playfield[V][H] = gv.EmptyObject




def CenterSpriteOnShip(Sprite,Ship):
  Sprite.h = Ship.h - (Sprite.width // 2)
  Sprite.v = Ship.v - (Sprite.height // 2)




# def Displaybuffer(Buffer,h,v,ZoomFactor = 0):
  # #This function accepts a buffer, HV coordinates and zoomfactor
  
    
  # r = 0
  # g = 0
  # b = 0
  # count = 0
  # H_modifier = 0
  # V_modifier = 0
  
  # HIndentFactor = 0    
  # VIndentFactor = 0    

  # #make a canvas/buffer for display purposes
  # ZoomBuffer = TheMatrix.CreateFrameCanvas()
  # ZoomBuffer.Fill(0,0,0)


    # if (ZoomFactor > 1):
      # H_modifier = (1 / gv.HatWidth ) * ZoomFactor * 2  #BigLED is 2 times wider than tall. Hardcoding now, will fix later. 
      # V_modifier = (1 / gv.HatHeight ) * ZoomFactor
      # NewHeight = round(gv.HatHeight * V_modifier)
      # NewWidth  = round(gv.HatWidth * H_modifier)

      # HIndentFactor = (gv.HatWidth / 2)  - (NewWidth /2)
      # VIndentFactor = (gv.HatHeight / 2) - (NewHeight /2)
    # else:
      # IndentFactor = 0

    # #print("gv.HatWidth",gv.HatWidth," NewWidth",NewWidth," ZoomFactor:",ZoomFactor,"HV_modifier",HV_modifier, "IndentFactor:",IndentFactor)

    # for V in range(0,gv.HatHeight):
      # for H in range (0,gv.HatWidth):
        # #print ("DisplayWindow hv HV: ",h,v,H,V) 
        
        # r,g,b = Buffer[ 

        # else:
          # r = self.Playfield[v+V][h+H].r
          # g = self.Playfield[v+V][h+H].g
          # b = self.Playfield[v+V][h+H].b
          
        # #Our map is an array V of array H  [V][1,2,3,4...etc]
        # if (ZoomFactor > 0):
          # gv.TheMatrix.SetPixel((H * H_modifier) + HIndentFactor ,(V * V_modifier) + VIndentFactor,r,g,b)
        
    

        # else:
          # gv.TheMatrix.SetPixel(H,V,r,g,b)
    
    #unicorn.show()
    #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)



  # def DisplayWindowZoom(self,h,v,Z1=8,Z2=1,ZoomSleep=0.05):
    # #uses playfield to display items

    # if (Z1 <= Z2):
      # for Z in range (Z1,Z2):
        # gv.TheMatrix.Clear()
        # self.DisplayWindow(h,v,Z)
        # time.sleep(ZoomSleep)
        
    # else:
      # for Z in reversed(range(Z2,Z1)):
        # gv.TheMatrix.Clear()        
        # self.DisplayWindow(h,v,Z)
        # time.sleep(ZoomSleep)
        




#!/usr/bin/env python
#print("moves:",moves,end='\r', flush=True)
#notes: check all playfield[v][h] in all versions to make sure v comes first.  I found one where it was switched
#       and this may account for when the zombie dots don't die
# - ship objects that also have a sprite should have
#   their HV co-ordinates looked at.  We want to draw the sprite around the center of the sprite, not the corner
#   Look at SpaceDot homing missile for an example.
#------------------------------------------------------------------------------



#------------------------------------------------------------------------------
#                                                                            --
#      _    ____   ____    _    ____  _____    ____ _     ___   ____ _  __   --
#     / \  |  _ \ / ___|  / \  |  _ \| ____|  / ___| |   / _ \ / ___| |/ /   --
#    / _ \ | |_) | |     / _ \ | | | |  _|   | |   | |  | | | | |   | ' /    --
#   / ___ \|  _ <| |___ / ___ \| |_| | |___  | |___| |__| |_| | |___| . \    --
#  /_/   \_\_| \_\\____/_/   \_\____/|_____|  \____|_____\___/ \____|_|\_\   --
#                                                                            --
#                                                                            --
#  Main Programs                                                             --
#                                                                            --
#------------------------------------------------------------------------------



#------------------------------------------------------------------------------
#  Arcade Retro Clock RGB
#  
#  Copyright 2021 William McEvoy
#  Metropolis Dreamware Inc.
#  william.mcevoy@gmail.com
#
#  NOT FOR COMMERCIAL USE
#  If you want to use my code for commercial purposes, contact William McEvoy
#  and we can make a deal.
#
#
#------------------------------------------------------------------------------
#   Version: 0.1                                                             --
#   Date:    January 13, 2021                                                --
#   Reason:  Converting PacDot to run on 64x32 panel                         --
#------------------------------------------------------------------------------
#   Version: 0.2                                                             --
#   Date:    January 13, 2021                                                --
#   Reason:  Lots of cleanup                                                 --
#------------------------------------------------------------------------------



#NOTES

#Future Work
#revisit curses for reading keypress.  Only initialize once.


#running PacDot automatically as background task (non interactive)
# cd /etc
# sudo nano rc.local
# nohup sudo python /home/pi/Pimoroni/unicornhat/examples/PacDot.py 0.07 0.07 0.07 20 40 200 >/dev/null 2>&1 &

#running PacDot after auto-loggin in
#modify profile script to include call to bash file
#cd /etc
#sudo nano profile
#cd pi
#./go.sh





#------------------------------------------------------------------------------
# Initialization Section                                                     --
#------------------------------------------------------------------------------
from __future__ import print_function


#RGB Matrix
from rgbmatrix import graphics
from rgbmatrix import RGBMatrix, RGBMatrixOptions


import time
import GlobalVariables as gv


import sys
import random
import string
from datetime import datetime, timedelta
from random import randint
import argparse
import copy
import numpy
import math
import subprocess
import traceback
import os

#For displaying crypto currency
#from pycoingecko import CoinGeckoAPI
#price = CoinGeckoAPI().get_price(ids='bitcoin', vs_currencies='usd')


#For capturing keypresses
import curses


#to help with debugging
import inspect


#JSON
import requests
import simplejson as json



#To support remote displays
#from signalrcore.hub_connection_builder import HubConnectionBuilder
#import logging
#Kareem's display
#from pixel_sim_display import PixelSimDisplay



#Check for keyboard input
#c = stdscr.getch()
#  if c > 1:
#  time.sleep(5)



random.seed()
start_time = time.time()

#python debugger
import pdb


#------------------------------------------------------------------------------
# Variable Declaration Section                                               --
#------------------------------------------------------------------------------

parser = argparse.ArgumentParser()
parser.add_argument("MainSleep",  type=float, nargs='?',default=0.06)
parser.add_argument("FlashSleep", type=float, nargs='?',default=0.01)
parser.add_argument("ScrollSleep",type=float, nargs='?',default=0.02)

#parser.add_argument("MinDots",          type=int, nargs='?',default=1)
#parser.add_argument("MaxDots",          type=int, nargs='?',default=240)
#parser.add_argument("MaxMoves",         type=int, nargs='?',default=2000)
parser.add_argument("TinyClockStartHH", type=int, nargs='?',default=0)
parser.add_argument("TinyClockHours",   type=int, nargs='?',default=0)
parser.add_argument("CPUModifier",      type=float, nargs='?',default=1.0)  #used to compensate for CPU speeds (A+ vs Pi 3)
parser.add_argument("Gamma",            type=float, nargs='?',default=1.0)  #used to increase brightness of all colors for largers displays with dimmer LEDs

args = parser.parse_args()

gv.MainSleep        = args.MainSleep
gv.FlashSleep       = args.FlashSleep
gv.ScrollSleep      = args.ScrollSleep
gv.TinyClockStartHH = args.TinyClockStartHH
gv.TinyClockHours   = args.TinyClockHours
gv.CPUModifier      = args.CPUModifier
gv.Gamma            = args.Gamma



KeyboardSpeed  = 15


##########
## HD   ##
##########
#gv.MainSleep   = 0.001 * gv.CPUModifier
#gv.ScrollSleep = 0.005 * gv.CPUModifier
#gv.FlashSleep  = 0.001


#relic of PacDot initial game
NumDots = 2000
MaxMoves = 5000




#Common Functions
import CommonFunctions as cf


#----------------------
#-- Clock Variables  --
#----------------------


CheckTime        = 60
ClockOnDuration  = 3
ClockOffDuration = CheckTime - ClockOnDuration
ClockSlideSpeed  = 1 
CheckClockSpeed  = 500



#apply CPU modifier
#VirusTopSpeed     = VirusTopSpeed    * gv.CPUModifier
#VirusBottomSpeed  = VirusBottomSpeed * gv.CPUModifier


#----------------------------
#-- PacDot                 --
#----------------------------

#thise things are left over from before I made the PacDot function
#cleanup later I hope (likely too lazy, likkit bitch!)

PowerPills  = 25
moves       = 0
DotsEaten   = 0
Pacmoves    = 0
PowerPillActive = 0
PowerPillMoves  = 0
BlueGhostmoves = 250


# StartGhostSpeed1    = 3
# StartGhostSpeed2    = 3
# StartGhostSpeed3    = 4
# StartGhostSpeed4    = 5
# GhostSpeed1    = StartGhostSpeed1
# GhostSpeed2    = StartGhostSpeed2
# GhostSpeed3    = StartGhostSpeed3
# GhostSpeed4    = StartGhostSpeed4
# PacSpeed       = 2
# BlueGhostSpeed = 4


LevelCount     = 1
PacPoints      = 0


PacStuckMaxCount = 20
PacStuckCount    = 1
PacOldH          = 0
PacOldV          = 0

#Pac Scoring
DotPoints         = 1
BlueGhostPoints   = 20
PillPoints        = 5
PacDotScore       = 0



MaxMoves = 2000

#Timers




#----------------------------
#-- Dot Invaders           --
#----------------------------





#----------------------------
#-- Worms                  --
#----------------------------

GreenObstacleFadeValue = 10
GreenObstacleMinVisible = 45

#Be warned!  Green is used to indicate obstacles in Worms.  SuperWorms shares some of the same functions, so be 
#careful what colors you use for worms.  Do not use SDLowRed for example
  
    


WheelAnimatedSprite = cf.AnimatedSprite(8,8,cf.BlueR,cf.BlueG,cf.BlueB,5,[])
WheelAnimatedSprite.grid.append(
  [0,0,1,1,1,0,0,0,
   0,0,1,1,1,0,0,0,
   0,0,1,1,1,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0]
)

WheelAnimatedSprite.grid.append(
  [0,0,0,0,0,0,0,0,
   0,0,1,1,1,0,0,0,
   0,0,1,1,1,0,0,0,
   0,0,1,1,1,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0]
)


WheelAnimatedSprite.grid.append(
  [0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,1,1,1,0,0,0,
   0,0,1,1,1,0,0,0,
   0,0,1,1,1,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0]
)


WheelAnimatedSprite.grid.append(
  [0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,1,1,1,0,0,0,
   0,0,1,1,1,0,0,0,
   0,0,1,1,1,0,0,0]
)

WheelAnimatedSprite.grid.append(
  [0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,1,1,1,0,0,0,
   0,1,1,1,1,1,0,0]
)

WheelAnimatedSprite.grid.append(
  [0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,
   1,1,1,1,1,1,1,0]
)


TestAnimatedSprite = cf.AnimatedSprite(5,5,cf.GreenR,cf.GreenG,cf.GreenB,3,[])
TestAnimatedSprite.grid.append(
  [0,0,1,0,0,
   0,0,1,0,0,
   0,0,1,0,0,
   0,0,1,0,0,
   0,0,1,0,0]
)
TestAnimatedSprite.grid.append(
  [0,0,0,0,1,
   0,0,0,1,0,
   0,0,1,0,0,
   0,1,0,0,0,
   1,0,0,0,0]
)
TestAnimatedSprite.grid.append(
  [0,0,0,0,0,
   0,0,0,0,0,
   1,1,1,1,1,
   0,0,0,0,0,
   0,0,0,0,0]
)
TestAnimatedSprite.grid.append(
  [1,0,0,0,0,
   0,1,0,0,0,
   0,0,1,0,0,
   0,0,0,1,0,
   0,0,0,0,1]
)


PacDotAnimatedSprite = cf.AnimatedSprite(5,5,cf.YellowR,cf.YellowG,cf.YellowB,4,[])
PacDotAnimatedSprite.grid.append(
  [0,1,1,1,0,
   1,1,1,0,0,
   1,1,0,0,0,
   1,1,1,0,0,
   0,1,1,1,0]
)

PacDotAnimatedSprite.grid.append(
  [0,1,1,1,0,
   1,1,1,1,1,
   1,1,0,0,0,
   1,1,1,1,1,
   0,1,1,1,0]
)


PacDotAnimatedSprite.grid.append(
  [0,1,1,1,0,
   1,1,1,1,1,
   1,1,1,1,1,
   1,1,1,1,1,
   0,1,1,1,0]
)
PacDotAnimatedSprite.grid.append(
  [0,1,1,1,0,
   1,1,1,1,0,
   1,1,1,0,0,
   1,1,1,1,0,
   0,1,1,1,0]
)

PacDotAnimatedSprite.grid.append(
  [0,1,1,1,0,
   1,1,0,0,0,
   1,0,0,0,0,
   1,1,0,0,0,
   0,1,1,1,0]
)


# Make left and right facing pacmen
PacRightAnimatedSprite = copy.deepcopy(PacDotAnimatedSprite)
PacLeftAnimatedSprite  = copy.deepcopy(PacDotAnimatedSprite)
PacLeftAnimatedSprite.HorizontalFlip()






PacSprite = cf.Sprite(
  5,
  5,
  cf.YellowR,
  cf.YellowG,
  cf.YellowB,
  [0, 0,1,1,1,0,
   0, 1,1,1,0,0,
   0, 1,1,0,0,0,
   0, 1,1,1,0,0,
   0, 0,1,1,1,0]
)


RedGhostSprite = cf.Sprite(
  5,
  5,
  cf.RedR,
  cf.RedG,
  cf.RedB,
  [0,1,1,1,0,
   1,1,1,1,1,
   1,0,1,0,1,
   1,1,1,1,1,
   1,0,1,0,1]
)
    

OrangeGhostSprite = cf.Sprite(
  5,
  5,
  cf.OrangeR,
  cf.OrangeG,
  cf.OrangeB,
  [0,1,1,1,0,
   1,1,1,1,1,
   1,0,1,0,1,
   1,1,1,1,1,
   1,0,1,0,1]
)
    
BlueGhostSprite = cf.Sprite(
  5,
  5,
  cf.BlueR,
  cf.BlueG,
  cf.BlueB,
  [0,1,1,1,0,
   1,1,1,1,1,
   1,0,1,0,1,
   1,1,1,1,1,
   1,0,1,0,1]
)

PurpleGhostSprite = cf.Sprite(
  5,
  5,
  cf.PurpleR,
  cf.PurpleG,
  cf.PurpleB,
  [0,1,1,1,0,
   1,1,1,1,1,
   1,0,1,0,1,
   1,1,1,1,1,
   1,0,1,0,1]
)


ClockSpriteBackground = cf.Sprite(
  16,
  7,
  0,
  0,
  0,
  [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,  
   ]
)







IsaacSprite =([0,0,1,0,0,
               1,0,1,0,0,
               0,1,1,1,1,
               0,0,1,0,0,
               0,1,0,1,0,
               0,1,0,1,0])
 





#(h,v,name,width,height,frames,currentframe,framerate,grid):


FrogSprite = cf.ColorAnimatedSprite(h=0, v=0, name="Frog", width=9, height=8, frames=1, currentframe=0,framerate=1,grid=[])
FrogSprite.grid.append(
  [
   0, 0, 9, 9, 0, 0, 9, 9, 0,
   0, 0, 9, 9, 9, 9, 9, 9, 0,
   0, 9, 9, 0, 2, 9, 0, 2, 0,
   0, 9, 9, 9, 9, 9, 9, 9, 0,
   0, 9,17,17,17,17,17,17,17,
   0,13, 9,17,17,17,17,17, 0,
   0,13, 9, 9, 9, 9, 9, 0, 0,
   0,13,13,13,13,13,13, 0, 0,
   ]
)



RedGhostSprite = cf.Sprite(
  5,
  5,
  cf.RedR,
  cf.RedG,
  cf.RedB,
  [0,1,1,1,0,
   1,1,1,1,1,
   1,0,1,0,1,
   1,1,1,1,1,
   1,0,1,0,1]
)




  


ThreeGhostPacSprite = cf.ColorAnimatedSprite(h=0, v=0, name="ThreeGhost", width=26, height=5, frames=5, currentframe=0,framerate=1,grid=[])



ThreeGhostPacSprite.grid.append(
  [
   0, 0,33,33,33, 0, 0, 0,18,18,18, 0, 0, 0, 7, 7, 7, 0, 0, 0, 0,22,22,22, 0, 0,
   0,33,33,33,33,33, 0,18,18,18,18,18, 0, 7, 7, 7, 7, 7, 0, 0, 22,22,22, 0,0, 0,
   0,33, 1,33, 1,33, 0,18, 1,18, 1,18, 0, 7, 1, 7, 1, 7, 0, 0, 22,22, 0, 0,0, 0,
   0,33,33,33,33,33, 0,18,18,18,18,18, 0, 7, 7, 7, 7, 7, 0, 0, 22,22,22, 0,0, 0,
   0,33, 0,33, 0,33, 0,18, 0,18, 0,18, 0, 7, 0, 7, 0, 7, 0, 0, 0,22,22,22, 0, 0
  
   ]
)


ThreeGhostPacSprite.grid.append(
  [
     0,0,33,33,33, 0, 0, 0,18,18,18, 0, 0, 0, 7, 7, 7, 0, 0, 0, 0,22,22,22,0, 0,
    0,33,33,33,33,33, 0,18,18,18,18,18, 0, 7, 7, 7, 7, 7, 0, 0, 22,22,22,22,22, 0,
    0,33, 1,33, 1,33, 0,18, 1,18, 1,18, 0, 7, 1, 7, 1, 7, 0, 0, 22,22,22,0,0, 0,
    0,33,33,33,33,33, 0,18,18,18,18,18, 0, 7, 7, 7, 7, 7, 0, 0, 22,22,22,22,22, 0,
    0,33, 0,33, 0,33, 0,18, 0,18, 0,18, 0, 7, 0, 7, 0, 7, 0, 0, 0,22,22,22,0, 0
  
   ]
)



ThreeGhostPacSprite.grid.append(
  [
    0, 0,33,33,33, 0, 0, 0,18,18,18, 0, 0, 0, 7, 7, 7, 0, 0, 0, 0,23,23,23,0, 0,
    0,33,33,33,33,33, 0,18,18,18,18,18, 0, 7, 7, 7, 7, 7, 0, 0, 23,23,23,23,23, 0,
    0,33, 1,33, 1,33, 0,18, 1,18, 1,18, 0, 7, 1, 7, 1, 7, 0, 0, 23,23,23,23,23, 0,
    0,33,33,33,33,33, 0,18,18,18,18,18, 0, 7, 7, 7, 7, 7, 0, 0, 23,23,23,23,23, 0,
    0,33, 0,33, 0,33, 0,18, 0,18, 0,18, 0, 7, 0, 7, 0, 7, 0, 0, 0,23,23,23,0, 0
  
   ]
)



ThreeGhostPacSprite.grid.append(
  [
    0,0,33,33,33, 0, 0, 0,18,18,18, 0, 0, 0, 7, 7, 7, 0, 0, 0,  0,23,23,23,0, 0,
    0,33,33,33,33,33, 0,18,18,18,18,18, 0, 7, 7, 7, 7, 7, 0, 0, 23,23,23,23,0, 0,
    0,33, 1,33, 1,33, 0,18, 1,18, 1,18, 0, 7, 1, 7, 1, 7, 0, 0, 23,23,23,0,0, 0,
    0,33,33,33,33,33, 0,18,18,18,18,18, 0, 7, 7, 7, 7, 7, 0, 0, 23,23,23,23,0,  0,
    0,33, 0,33, 0,33, 0,18, 0,18, 0,18, 0, 7, 0, 7, 0, 7, 0, 0, 0,23,23,23,0, 0
  
   ]
)

 
ThreeGhostPacSprite.grid.append(
  [
     0,0,33,33,33, 0, 0, 0,18,18,18, 0, 0, 0, 7, 7, 7, 0, 0, 0, 0,23,23,23,0, 0,
    0,33,33,33,33,33, 0,18,18,18,18,18, 0, 7, 7, 7, 7, 7, 0, 0, 23,23,0,0,0, 0,
    0,33, 1,33, 1,33, 0,18, 1,18, 1,18, 0, 7, 1, 7, 1, 7, 0, 0, 23,23,0,0,0, 0,
    0,33,33,33,33,33, 0,18,18,18,18,18, 0, 7, 7, 7, 7, 7, 0, 0, 23,23,0,0,0, 0,
    0,33, 0,33, 0,33, 0,18, 0,18, 0,18, 0, 7, 0, 7, 0, 7, 0, 0, 0,23,23,23,0, 0
  
   ]
)




ThreeBlueGhostPacSprite = cf.ColorAnimatedSprite(h=0, v=0, name="ThreeGhost", width=26, height=5, frames=6, currentframe=0,framerate=1,grid=[])

ThreeBlueGhostPacSprite.grid.append(
  [
     0,0,14,14,14, 0, 0, 0,14,14,14, 0, 0, 0,14,14,14, 0, 0, 0, 0,23,23,23,0, 0,
    0,14,14,14,14,14, 0,14,14,14,14,14, 0,14,14,14,14,14, 0, 0, 0,0,23,23,23, 0,
    0,14, 2,14, 1,14, 0,14, 2,14, 2,14, 0,14, 2,14, 2,14, 0, 0, 0,0,0,23,23, 0,
    0,14,14,14,14,14, 0,14,14,14,14,14, 0,14,14,14,14,14, 0, 0, 0,0,23,23,23, 0,
    0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0, 0, 0,23,23,23,0, 0
  
   ]
)


ThreeBlueGhostPacSprite.grid.append(
  [
     0,0,14,14,14, 0, 0, 0,14,14,14, 0, 0, 0,14,14,14, 0, 0, 0, 0,23,23,23,0, 0,
    0,14,14,14,14,14, 0,14,14,14,14,14, 0,14,14,14,14,14, 0, 0, 23,23,23,23,23, 0,
    0,14, 2,14, 2,14, 0,14, 2,14, 2,14, 0,14, 2,14, 2,14, 0, 0, 0,0,0,23,23, 0,
    0,14,14,14,14,14, 0,14,14,14,14,14, 0,14,14,14,14,14, 0, 0, 23,23,23,23,23, 0,
    0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0, 0, 0,23,23,23,0, 0
  
   ]
)



ThreeBlueGhostPacSprite.grid.append(
  [
     0,0,14,14,14, 0, 0, 0,14,14,14, 0, 0, 0,14,14,14, 0, 0, 0, 0,23,23,23,0, 0,
    0,14,14,14,14,14, 0,14,14,14,14,14, 0,14,14,14,14,14, 0, 0, 23,23,23,23,23, 0,
    0,14, 2,14, 2,14, 0,14, 2,14, 2,14, 0,14, 2,14, 2,14, 0, 0, 23,23,23,23,23, 0,
    0,14,14,14,14,14, 0,14,14,14,14,14, 0,14,14,14,14,14, 0, 0, 23,23,23,23,23, 0,
    0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0, 0, 0,23,23,23,0, 0
  
   ]
)

ThreeBlueGhostPacSprite.grid.append(
  [
     0,0,14,14,14, 0, 0, 0,14,14,14, 0, 0, 0,14,14,14, 0, 0, 0, 0,23,23,23,0, 0,
    0,14,14,14,14,14, 0,14,14,14,14,14, 0,14,14,14,14,14, 0, 0, 0,23,23,23,23, 0,
    0,14, 2,14, 2,14, 0,14, 2,14, 2,14, 0,14, 2,14, 2,14, 0, 0, 0,0,23,23,23, 0,
    0,14,14,14,14,14, 0,14,14,14,14,14, 0,14,14,14,14,14, 0, 0, 0,23,23,23,23, 0,
    0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0, 0, 0,23,23,23,0, 0
  
   ]
)

 
ThreeBlueGhostPacSprite.grid.append(
  [
     0,0,14,14,14, 0, 0, 0,14,14,14, 0, 0, 0,14,14,14, 0, 0, 0, 0,23,23,23,0, 0,
    0,14,14,14,14,14, 0,14,14,14,14,14, 0,14,14,14,14,14, 0, 0, 0,0,0,23,23, 0,
    0,14, 2,14, 2,14, 0,14, 2,14, 2,14, 0,14, 2,14, 2,14, 0, 0, 0,0,0,0,23, 0,
    0,14,14,14,14,14, 0,14,14,14,14,14, 0,14,14,14,14,14, 0, 0, 0,0,0,23,23, 0,
    0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0, 0, 0,23,23,23,0, 0
  
   ]
)

ThreeBlueGhostPacSprite.grid.append(
  [
     0,0,14,14,14, 0, 0, 0,14,14,14, 0, 0, 0,14,14,14, 0, 0, 0, 0,23,23,23,0, 0,
    0,14,14,14,14,14, 0,14,14,14,14,14, 0,14,14,14,14,14, 0, 0, 0,0,0,23,23, 0,
    0,14, 2,14, 2,14, 0,14, 2,14, 2,14, 0,14, 2,14, 2,14, 0, 0, 0,0,0,0,23, 0,
    0,14,14,14,14,14, 0,14,14,14,14,14, 0,14,14,14,14,14, 0, 0, 0,0,0,23,23, 0,
    0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0, 0, 0,23,23,23,0,  0
  
   ]
)






ThreeGhostSprite = cf.ColorAnimatedSprite(h=0, v=0, name="ThreeGhost", width=19, height=5, frames=1, currentframe=0,framerate=1,grid=[])
ThreeGhostSprite.grid.append(
  [
   0, 0,33,33,33, 0, 0, 0,18,18,18, 0, 0, 0, 7, 7, 7, 0, 0, 
   0,33,33,33,33,33, 0,18,18,18,18,18, 0, 7, 7, 7, 7, 7, 0, 
   0,33, 1,33, 1,33, 0,18, 1,18, 1,18, 0, 7, 1, 7, 1, 7, 0, 
   0,33,33,33,33,33, 0,18,18,18,18,18, 0, 7, 7, 7, 7, 7, 0, 
   0,33, 0,33, 0,33, 0,18, 0,18, 0,18, 0, 7, 0, 7, 0, 7, 0 
  
   ]
)


ThreeBlueGhostSprite = cf.ColorAnimatedSprite(h=0, v=0, name="ThreeBlueGhost", width=19, height=5, frames=1, currentframe=0,framerate=1,grid=[])
ThreeBlueGhostSprite.grid.append(
  [
   0, 0,14,14,14, 0, 0, 0,14,14,14, 0, 0, 0,14,14,14, 0, 0, 
   0,14,14,14,14,14, 0,14,14,14,14,14, 0,14,14,14,14,14, 0, 
   0,14, 2,14, 2,14, 0,14, 2,14, 2,14, 0,14, 2,14, 2,14, 0, 
   0,14,14,14,14,14, 0,14,14,14,14,14, 0,14,14,14,14,14, 0, 
   0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0 
  
   ]
)



# # MAX
# # 39 40 41 42 43 44 45
# ColorList.append((255,  0,  0))  #MAX-RED
# ColorList.append((  0,255,  0))  #MAX-GREEN
# ColorList.append((  0,  0,255))  #MAX-BLUE
# ColorList.append((255,255,0  ))  #MAX-YELLOW
# ColorList.append((255,  0,255))  #MAX-PURPLE
# ColorList.append((  0,255,255))  #MAX-CYAN
# ColorList.append((255,255,255))  #MAX-WHITE


AsteroidExplosion = cf.ColorAnimatedSprite(
  h      = 0 , 
  v      = 0, 
  name   = 'Asteroid',
  width  = 3, 
  height = 3,
  frames = 5,
  currentframe = 0,
  framerate    = 10,
  grid=[]
)

AsteroidExplosion.grid.append(
  [0, 0, 0,
   0,45, 0,
   0, 0, 0
  ]
)

AsteroidExplosion.grid.append(
  [0,45, 0,
  45,45,45,
   0,45, 0
  ]
)
AsteroidExplosion.grid.append(
  [0,45, 0,
  45, 8,45,
   0,45, 0
  ]
)
AsteroidExplosion.grid.append(
  [0, 8, 0,
   8, 0, 8,
   0, 8, 0
  ]
)
AsteroidExplosion.grid.append(
  [0, 0, 0,
   0, 0, 0,
   0, 0, 0
  ]
)



AsteroidExplosion2 = cf.ColorAnimatedSprite(
  h      = 0 , 
  v      = 0, 
  name   = 'Asteroid',
  width  = 3, 
  height = 1,
  frames = 7,
  currentframe = 0,
  framerate    = 50,
  grid=[]
)

AsteroidExplosion2.grid.append(
  [
    0,45, 0
  ]
)

AsteroidExplosion2.grid.append(
  [
   45,20,45
  ]
)

AsteroidExplosion2.grid.append(
  [
   20,20,20
  ]
)

AsteroidExplosion2.grid.append(
  [
    8, 8, 8
  ]
)

AsteroidExplosion2.grid.append(
  [
    8, 6, 8
  ]
)

AsteroidExplosion2.grid.append(
  [
    6, 5, 6
  ]
)

AsteroidExplosion2.grid.append(
  [
    5, 5, 5
  ]
)




PlayerShipExplosion = cf.ColorAnimatedSprite(
  h=0, v=0, name="Explosion", width=5, height=5, 
  frames=14,
  currentframe=0,
  framerate=2,grid=[]
)
PlayerShipExplosion.grid.append(
  [0,0,0,0,0,
   0,0,0,0,0,
   0,0,4,0,0,
   0,0,0,0,0,
   0,0,0,0,0
   ]
)

PlayerShipExplosion.grid.append(
   [0,0,0,0,0,
    0, 0, 4, 0,0,
    0, 4,18, 4,0,
    0, 0, 4, 0,0,
    0,0,0,0,0
   ]
)
  
PlayerShipExplosion.grid.append(
   [ 0, 0, 4, 0, 0,
     0,18,18,18, 0,
     4,18,19,18, 4,
     0,18,18,18, 0,
     0, 0, 4, 0,0
   ]
)
PlayerShipExplosion.grid.append(
   [ 0,18,18,18, 0,
    18,19,19,19,18,
    18,18,20,19,18,
    18,19,19,19,18,
     0,18,18,18, 0
   ]
)
PlayerShipExplosion.grid.append(
   [ 0,19,19,19, 0,
    19,20,20,20,19,
    19,20,20,20,19,
    19,20,20,20,19,
     0,19,19,19, 0
   ]
)
PlayerShipExplosion.grid.append(
   [ 0,20,20,20, 0,
    20,20,20,20,20,
    20,20,20,20,20,
    20,20,20,20,20,
     0,20,20,20, 0
   ]


)
PlayerShipExplosion.grid.append(
   [00,20,20,20,00,
    20,20,20,20,20,
    20,20, 8,20,20,
    20,20,20,20,20,
    00,20,20,20,00
   ]
)
PlayerShipExplosion.grid.append(
   [ 0,20,20,20, 0,
    20,20, 8,20,20,
    20, 8, 7, 8,20,
    20,20, 8,20,20,
     0,20,20,20, 0
   ]
)  

PlayerShipExplosion.grid.append(
   [ 0,20, 8,20, 0,
    20, 8, 7, 8,20,
     8, 7, 6, 7, 8,
    20, 8, 7, 8,20,
     0,20, 8,20, 0
   ]
)
PlayerShipExplosion.grid.append(
   [ 0, 8, 7, 8, 0,
     8, 7, 6, 7, 8,
     7, 6, 5, 6, 7,
     8, 7, 6, 7, 8,
     0, 8, 7, 8, 0
   ]
)
PlayerShipExplosion.grid.append(
   [ 0, 7, 6, 7, 0,
     7, 6, 0, 6, 7,
     6, 5, 0, 5, 6,
     7, 6, 0, 6, 7,
     0, 7, 6, 7, 0
   ]
)
PlayerShipExplosion.grid.append(
   [ 0, 6, 5, 6, 0,
     6, 5, 0, 5, 6,
     5, 0, 0, 0, 5,
     6, 5, 0, 5, 6,
     0, 6, 5, 6, 0
   ]
)
PlayerShipExplosion.grid.append(
   [ 0, 5, 0, 5, 0,
     5, 0, 0, 0, 5,
     0, 0, 0, 0, 0,
     5, 0, 0, 0, 5,
     0, 5, 0, 5, 0
   ]
)  

PlayerShipExplosion.grid.append(
   [ 0, 0, 0, 0, 0,
     0, 0, 0, 0, 0,
     0, 0, 0, 0, 0,
     0, 0, 0, 0, 0,
     0, 0, 0, 0, 0
   ]
)  




BomberShipExplosion = cf.ColorAnimatedSprite(
  h = 0, 
  v = 0,
  name         = "Explosion", 
  width        = 5, 
  height       = 5, 
  frames       = 9,
  currentframe = 0,
  framerate    = 15, 
  grid         = []
)
BomberShipExplosion.grid.append(
   [ 0, 0, 0, 0, 0,
     0, 0,45, 0, 0,
     0,45,45,45, 0,
     0, 0,45, 0, 0,
     0, 0, 0, 0, 0
   ]
)

BomberShipExplosion.grid.append(
   [ 0, 0,45, 0, 0,
     0,45,45,45, 0,
    45,45,45,45,45,
     0,45,45,45, 0,
     0, 0,45, 0, 0
   ]
)

BomberShipExplosion.grid.append(
   [ 0, 0,42, 0, 0,
     0,45,42,45, 0,
    42,42,42,42,42,
     0,45,42,45, 0,
     0, 0,42, 0, 0
   ]
)


BomberShipExplosion.grid.append(
   [ 0, 0,42, 0, 0,
     0, 2,20, 2, 0,
    42,20,20,20,42,
     0, 2,20, 2, 0,
     0, 0,42, 0, 0
   ]
)


BomberShipExplosion.grid.append(
   [ 0, 0,20, 0, 0,
     0, 1,20, 1, 0,
    20,20,39,20,20,
     0, 1,20, 1, 0,
     0, 0,20, 0, 0
   ]
)

BomberShipExplosion.grid.append(
   [ 0, 0,39, 0, 0,
     0, 1,39, 1, 0,
    39,39,39,39,20,
     0, 1,39, 1, 0,
     0, 0,39, 0, 0
   ]
)

BomberShipExplosion.grid.append(
   [ 0, 0,39, 0, 0,
     0, 1, 8, 1, 0,
    39, 8, 6, 8,39,
     0, 1, 8, 1, 0,
     0, 0,39, 0, 0
   ]
)


BomberShipExplosion.grid.append(
   [ 0, 0, 0, 0, 0,
     0, 0, 5, 0, 0,
     0, 5, 5, 5, 0,
     0, 0, 5, 0, 0,
     0, 0, 0, 0, 0
   ]
)

BomberShipExplosion.grid.append(
   [ 0, 0, 0, 0, 0,
     0, 0, 0, 0, 0,
     0, 0, 0, 0, 0,
     0, 0, 0, 0, 0,
     0, 0, 0, 0, 0
   ]
)





SmallExplosion = cf.ColorAnimatedSprite(
  h=-1, v=-1, name="Explosion", width=3, height=3,
  frames=7,
  currentframe=0,
  framerate = 2,grid=[])
SmallExplosion.grid.append(
  [
   0, 0, 0,
   0,29, 0,
   0, 0, 0,
   
   ]
)

SmallExplosion.grid.append(
   [ 
     0,29, 0,
    29,30,29,
     0,29, 0, 
   
   ]
)
  
SmallExplosion.grid.append(
   [ 
      0,30, 0,
     30,31,30,
      0,30, 0,
     
   ]
)
SmallExplosion.grid.append(
   [
     0,31, 0,
    31,32,31,
     0,31, 0,
    
   ]
)

SmallExplosion.grid.append(
   [
     0,32, 0,
    32, 8,32,
     0,32, 0
   ]
)
   

SmallExplosion.grid.append(
   [
     0,20, 0,
    20, 0,20,
     0,20, 0,
    
   ]
)

   
SmallExplosion.grid.append(
   [
     0, 0, 0,
     0, 0, 0,
     0, 0, 0,
    
   ]
)



BigGroundExplosion = cf.ColorAnimatedSprite(
  h            = -1, #this is important, it is used to indicate if the explosion is brand new.  I think.
  v            = -1,  
  name         = "Explosion", 
  width        = 9, 
  height       = 3, 
  frames       = 6, 
  currentframe = 0,
  framerate    = 150,
  grid         = []
)


BigGroundExplosion.grid.append(
  [
  44, 0, 0, 0, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 4, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0, 0, 0, 0
   ]
)

BigGroundExplosion.grid.append(
  [
  44, 0, 0, 0, 0, 0, 0, 0, 0,
   0, 0, 0, 4, 4, 4, 0, 0, 0,
   0, 0, 0, 0, 0, 0, 0, 0, 0
   ]
)
BigGroundExplosion.grid.append(
  [
  44, 0, 0, 0, 4, 0, 0, 0, 0,
   0, 0, 4, 4, 4, 4, 4, 0, 0,
   0, 0, 0, 0, 4, 0, 0, 0, 0
   ]
)
BigGroundExplosion.grid.append(
  [
  44, 0, 0, 0, 4, 0, 0, 0, 0,
   0, 4, 4, 4, 4, 4, 4, 4, 0,
   0, 0, 0, 0, 4, 0, 0, 0, 0
   ]
)
BigGroundExplosion.grid.append(
  [
  44, 0, 0, 0, 4, 0, 0, 0, 0,
   4, 4, 4, 0, 0, 0, 4, 4, 4,
   0, 0, 0, 0, 4, 0, 0, 0, 0
   ]
)
BigGroundExplosion.grid.append(
  [
  44, 0, 0, 0, 0, 0, 0, 0, 0,
   4, 0, 0, 0, 0, 0, 0, 0, 4,
   0, 0, 0, 0, 0, 0, 0, 0, 0
   ]
)
BigGroundExplosion.grid.append(
  [
  44, 0, 0, 0, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0, 0, 0, 0
   ]
)





BigShipExplosion = cf.ColorAnimatedSprite(
  h = 0, 
  v = 0,
  name         = "Explosion", 
  width        = 8, 
  height       = 5, 
  frames       = 10,
  currentframe = 0,
  framerate    = 15, 
  grid         = []
)
BigShipExplosion.grid.append(
   [ 0, 0, 0, 0, 0, 0, 0, 0, 
     0, 0, 0, 5, 5, 0, 0, 0, 
     0, 0, 5, 5, 5, 5, 0, 0, 
     0, 0, 0, 5, 5, 0, 0, 0, 
     0, 0, 0, 0, 0, 0, 0, 0
   ]
)
BigShipExplosion.grid.append(
   [ 0, 0, 0, 0, 0, 0, 0, 0, 
     0, 0, 0, 5, 5, 0, 0, 0, 
     0, 0, 5, 5, 5, 5, 0, 0, 
     0, 0, 0, 5, 5, 0, 0, 0, 
     0, 0, 0, 0, 0, 0, 0, 0
   ]
)

BigShipExplosion.grid.append(
   [ 0, 0, 0, 5, 5, 0, 0, 0, 
     0, 0, 0, 7, 7, 0, 0, 0, 
     0, 5, 7, 7, 7, 7, 5, 0, 
     0, 0, 0, 7, 7, 0, 0, 0, 
     0, 0, 0, 5, 5, 0, 0, 0
   ]
)
BigShipExplosion.grid.append(
   [ 0, 0, 0, 5, 5, 0, 0, 0, 
     0, 0, 0, 7, 7, 0, 0, 0, 
     0, 5, 7, 7, 7, 7, 5, 0, 
     0, 0, 0, 7, 7, 0, 0, 0, 
     0, 0, 0, 5, 5, 0, 0, 0
   ]
)

BigShipExplosion.grid.append(
   [ 0, 0, 0, 8, 8, 0, 0, 0, 
     0, 0, 0,39,39, 0, 0, 0, 
     8, 8,39,39,39,39, 8, 8, 
     0, 0, 0,39,39, 0, 0, 0, 
     0, 0, 0, 8, 8, 0, 0, 0
   ]
)

BigShipExplosion.grid.append(
   [ 0, 0, 0,39,39, 0, 0, 0, 
     0, 0, 0,45,45, 0, 0, 0, 
    39,39,45,45,45,45,39,39, 
     0, 0, 0,45,45, 0, 0, 0, 
     0, 0, 0,39,39, 0, 0, 0
   ]
)


BigShipExplosion.grid.append(
   [ 0, 0, 0,45,45, 0, 0, 0, 
     0, 0,45,45,45,45, 0, 0, 
    45,45,45,45,45,45,45,45, 
     0, 0,45,45,45,45, 0, 0, 
     0, 0, 0,45,45, 0, 0, 0
   ]
)


BigShipExplosion.grid.append(
   [ 0, 0, 0, 8, 8, 0, 0, 0, 
     0, 0, 5, 5, 5, 5, 0, 0, 
     8, 8, 5, 5, 5, 5, 8, 8, 
     0, 0, 5, 5, 5, 5, 0, 0, 
     0, 0, 0, 8, 8, 0, 0, 0
   ]
)

BigShipExplosion.grid.append(
   [ 0, 0, 0, 8, 8, 0, 0, 0, 
     0, 0, 5, 5, 5, 5, 0, 0, 
     8, 8, 5, 5, 5, 5, 8, 8, 
     0, 0, 5, 5, 5, 5, 0, 0, 
     0, 0, 0, 8, 8, 0, 0, 0
   ]
)

BigShipExplosion.grid.append(
   [ 0, 0, 0, 0, 0, 0, 0, 0, 
     0, 0, 0, 0, 0, 0, 0, 0, 
     0, 0, 0, 0, 0, 0, 0, 0, 
     0, 0, 0, 0, 0, 0, 0, 0, 
     0, 0, 0, 0, 0, 0, 0, 0
   ]
)


DropShip = cf.ColorAnimatedSprite(h=0, v=0, name="DropShip", width=5, height=8, frames=2, currentframe=0,framerate=1,grid=[])
DropShip.grid.append(
  [
    0, 0, 0, 0, 0,
    0, 0,15, 0, 0,
    0, 0,15, 0, 0,
    0,14,15,14, 0,
    0,14, 7,14, 0,
    0, 0, 6, 0, 0,
    0, 0, 5, 0, 0,
    0, 0, 0, 0, 0,
  ]
)

DropShip.grid.append(
  [
    0, 0, 0, 0, 0,
    0, 0,15, 0, 0,
    0, 0,15, 0, 0,
    0,14,15,14, 0,
    0,14, 6,14, 0,
    0, 0, 5, 0, 0,
    0, 0, 5, 0, 0,
    0, 0, 0, 0, 0,
  ]
)



SpaceInvader = cf.ColorAnimatedSprite(h=0, v=0, name="SpaceInvader", width=13, height=8, frames=2, currentframe=0,framerate=1,grid=[])
SpaceInvader.grid.append(
  [
    0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0,
    0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 
    0, 0, 9, 9,11, 9, 9, 9,11, 9, 9, 0, 0,
    0, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 0,
    0, 9, 0, 9, 9, 9, 9, 9, 9, 9, 0, 9, 0,
    0, 9, 0, 9, 0, 0, 0, 0, 0, 9, 0, 9, 0,
    0, 0, 0, 0, 9, 0, 0, 0, 9, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
  ]
)
SpaceInvader.grid.append(
  [
    0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0,
    0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9, 0, 0,
    0, 0, 9, 9,11, 9, 9, 9,11, 9, 9, 0, 0,
    0, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 0,
    0, 9, 0, 9, 9, 9, 9, 9, 9, 9, 0, 9, 0,
    0, 9, 0, 9, 0, 0, 0, 0, 0, 9, 0, 9, 0,
    0, 0, 0, 9, 0, 0, 0, 0, 0, 9, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
  ]
)



TinyInvader = cf.ColorAnimatedSprite(h=0, v=0, name="TinyInvader", width=7, height=6, frames=4, currentframe=0,framerate=1,grid=[])
TinyInvader.grid.append(
  [
   0, 0, 0, 8, 0, 0, 0,
   0, 0, 9, 9, 9, 0, 0,
   0, 9,11, 9,11, 9, 0,
   0, 9, 9, 9, 9, 9, 0,
   0, 0, 9, 0, 9, 0, 0,
   0, 9, 0, 0, 0, 9, 0
  ]
)
TinyInvader.grid.append(
  [
   0, 0, 0, 8, 0, 0, 0, 
   0, 0, 9, 9, 9, 0, 0, 
   0, 9,11, 9,11, 9, 0, 
   0, 9, 9, 9, 9, 9, 0, 
   0, 0, 9, 0, 9, 0, 0, 
   0, 9, 0, 0, 0, 9, 0
  ]
)
TinyInvader.grid.append(
  [
   0, 0, 0,16, 0, 0, 0,
   0, 0, 9, 9, 9, 0, 0,
   0, 9,11, 9,11, 9, 0,
   0, 9, 9, 9, 9, 9, 0,
   0, 0, 9, 0, 9, 0, 0,
   0, 9, 0, 0, 0, 9, 0
  ]
)

TinyInvader.grid.append(
  [
   0, 0, 0,16, 0, 0, 0,
   0, 0, 9, 9, 9, 0, 0,
   0, 9,11, 9,11, 9, 0,
   0, 9, 9, 9, 9, 9, 0,
   0, 0, 9, 0, 9, 0, 0,
   0, 0, 9, 0, 9, 0, 0
  ]
)




SmallInvader = cf.ColorAnimatedSprite(h=0, v=0, name="SmallInvader", width=9, height=6, frames=2, currentframe=0,framerate=1,grid=[])
SmallInvader.grid.append(
  [
    0, 0, 0, 9, 9, 9, 0, 0, 0,
    0, 0, 9, 9, 9, 9, 9, 0, 0,
    0, 9,10,11, 9,11,10, 9, 0,
    0, 9, 9, 9, 9, 9, 9, 9, 0,
    0, 9, 0, 9, 0, 9, 0, 9, 0,
    0, 0, 9, 0, 9, 0, 9, 0, 0,
  ]
)
SmallInvader.grid.append(
  [
    0, 0, 0, 9, 9, 9, 0, 0, 0,
    0, 0, 9, 9, 9, 9, 9, 0, 0,
    0, 9,10,11, 9,11,10, 9, 0,
    0, 9, 9, 9, 9, 9, 9, 9, 0,
    0, 9, 0, 9, 0, 9, 0, 9, 0,
    0, 9, 0, 9, 0, 9, 0, 9, 0,
  ]
)



LittleShipFlying = cf.ColorAnimatedSprite(h=0, v=0, name="LittleShips", width=16, height=8, frames=2, currentframe=0,framerate=1,grid=[])

LittleShipFlying.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0, 0,15, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 5, 6, 7, 8, 5,14,14,14, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,15, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 5, 6, 7, 8, 5,14,14,14,
    0, 0, 0, 0, 0,15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 6, 7, 8, 5,14,14,14, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    
   ]
)

LittleShipFlying.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0, 0,15, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 5, 6, 7, 8, 5,14,14,14, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,15, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 5, 6, 7, 8, 5,14,14,14,
    0, 0, 0, 0, 0,15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 6, 7, 8, 5,14,14,14, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    
   ]
)


                  
BigShipFlying = cf.ColorAnimatedSprite(h=0, v=0, name="BigShipFlying", width=36, height=8, frames=6, currentframe=0,framerate=1,grid=[])

BigShipFlying.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,15,15,15,15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 5, 5, 5, 5,14,14,14,14,14,16,14,16,14,14,14,14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 5, 5, 5, 5, 6, 6, 7, 7, 8, 8,17,14,14, 9,14, 9,14,14,13,13,13,13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,15, 0, 0,
    0, 5, 5, 5, 5, 6, 6, 7, 7, 8, 8,17,14,14,14, 9,14, 9,13,13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,17,14,14,14,
    0, 0, 0, 0, 0, 0, 0, 5, 5, 5, 5, 1,14,13,13,13,13,13, 8, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 5,13,13,13,13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   ]
)

BigShipFlying.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,15,15,15,15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 5, 5, 5, 5,14,14,15,14,14,16,14,16,14,14,14,14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 5, 5, 5, 5, 6, 6, 7, 8, 8, 5,17,14,15, 9,14, 9,14,14,13,13,13,13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,15, 0, 0,
    0, 5, 5, 5, 5, 6, 6, 7, 8, 8, 5,17,14,15,14, 9,14, 9,13,13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5,14,14,14,
    0, 0, 0, 0, 0, 0, 0, 5, 5, 5, 5, 1,14,15,13,13,13,13, 0, 5, 5, 5, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 5,13,13,13,13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   ]
)

BigShipFlying.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,15,15,15,15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 5, 5, 5, 5,14,14,15,14,14,16,14,16,14,14,14,14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 5, 5, 5, 5, 6, 6, 7, 8, 8, 5,17,14,15, 9,14, 9,14,14,13,13,13,13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,15, 0, 0,
    0, 5, 5, 5, 5, 6, 6, 7, 8, 8, 5,17,14,15,14, 9,14, 9,13,13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,17,14,14,14,
    0, 0, 0, 0, 0, 0, 0, 5, 5, 5, 5, 1,14,15,13,13,13,13, 0, 0, 0, 0, 0, 5, 5, 5, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 5,13,13,13,13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   ]
)

BigShipFlying.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,15,15,15,15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 5, 5, 5, 5,14,14,15,14,14,16,14,16,14,14,14,14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 5, 5, 5, 5, 6, 6, 7, 8, 8, 5,17,14,15, 9,14, 9,14,14,13,13,13,13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,15, 0, 0,
    0, 5, 5, 5, 5, 6, 6, 7, 8, 8, 5,17,14,15,14, 9,14, 9,13,13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5,14,14,14,
    0, 0, 0, 0, 0, 0, 0, 5, 5, 5, 5, 1,14,15,13,13,13,13, 0, 0, 0, 0, 0, 0, 0, 0, 5, 5, 5, 7, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 5,13,13,13,13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   ]
)

BigShipFlying.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,15,15,15,15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 5, 5, 5, 5,14,14,15,14,14,16,14,16,14,14,14,14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 5, 5, 5, 5, 6, 6, 7, 8, 8, 5,17,14,15, 9,14, 9,14,14,13,13,13,13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,15, 0, 0,
    0, 5, 5, 5, 5, 6, 6, 7, 8, 8, 5,17,14,15,14, 9,14, 9,13,13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,17,14,14,14,
    0, 0, 0, 0, 0, 0, 0, 5, 5, 5, 5, 1,14,15,13,13,13,13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 5, 5, 7, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 5,13,13,13,13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   ]
)

BigShipFlying.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,15,15,15,15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 5, 5, 5, 5,14,14,15,14,14,16,14,16,14,14,14,14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 5, 5, 5, 5, 6, 6, 7, 8, 8, 5,17,14,15, 9,14, 9,14,14,13,13,13,13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,15, 0, 0,
    0, 5, 5, 5, 5, 6, 6, 7, 8, 8, 5,17,14,15,14, 9,14, 9,13,13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5,14,14,14,
    0, 0, 0, 0, 0, 0, 0, 5, 5, 5, 5, 1,14,15,13,13,13,13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 5, 5,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 5,13,13,13,13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   ]
)
 

#This will hold HH:MM
BigSprite = cf.Sprite(16,5,cf.GreenR,cf.GreenG,cf.GreenB,
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
)


#DotZerk Human Death
HumanExplosion = cf.ColorAnimatedSprite(h=0, v=0, name="HumanExplosion", width=3, height=3, frames=6, currentframe=0,framerate=1,grid=[])
HumanExplosion.grid.append(
  [
    0, 0, 0,
    0, 5, 0,
    0, 0, 0
  ]
)
HumanExplosion.grid.append(
  [
    0, 5, 0,
    5, 6, 5,
    0, 5, 0
  ]
)
HumanExplosion.grid.append(
  [
    0, 6, 0,
    6, 7, 6,
    0, 6, 0
  ]
)
HumanExplosion.grid.append(
  [
    0, 7, 0,
    7, 8, 7,
    0, 7, 0
  ]
)
HumanExplosion.grid.append(
  [
    0, 8, 0,
    8, 0, 8,
    0, 8, 0
  ]
)

HumanExplosion.grid.append(
  [
    0, 0, 0,
    0, 0, 0,
    0, 0, 0
  ]
)



#DotZerk Human Death
HumanExplosion2 = cf.ColorAnimatedSprite(h=0, v=0, name="HumanExplosion", width=3, height=3, frames=8, currentframe=0,framerate=1,grid=[])
HumanExplosion2.grid.append(
  [
    0, 0, 0,
    0, 5, 0,
    0, 0, 0
  ]
)
HumanExplosion2.grid.append(
  [
    0, 5, 0,
    5, 6, 5,
    0, 5, 0
  ]
)
HumanExplosion2.grid.append(
  [
    0, 6, 0,
    6, 7, 6,
    0, 6, 0
  ]
)
HumanExplosion2.grid.append(
  [
    0, 7, 0,
    7, 8, 7,
    0, 7, 0
  ]
)
HumanExplosion2.grid.append(
  [
    0, 8, 0,
    8,20, 8,
    0, 8, 0
  ]
)

HumanExplosion2.grid.append(
  [
    0,20, 0,
   20, 0,20,
    0,20, 0
  ]
)

HumanExplosion2.grid.append(
  [
    5, 0, 5,
    0, 0, 0,
    5, 0, 5
  ]
)

HumanExplosion2.grid.append(
  [
    0, 0, 0,
    0, 0, 0,
    0, 0, 0
  ]
)


DotZerkRobot = cf.ColorAnimatedSprite(h=0, v=0, name="Robot", width=10, height=8, frames=9, currentframe=0,framerate=1,grid=[])
DotZerkRobot.grid.append(
  [
    0, 0, 0, 6, 6, 6, 6, 0, 0, 0,
    0, 0, 6, 8, 1, 6, 6, 6, 0, 0,
    0, 6, 6, 6, 6, 6, 6, 6, 6, 0,
    0, 6, 0, 6, 6, 6, 6, 0, 6, 0,
    0, 6, 0, 6, 6, 6, 6, 0, 6, 0,
    0, 0, 0, 6, 6, 6, 6, 0, 0, 0,
    0, 0, 0, 6, 0, 0, 6, 0, 0, 0,
    0, 0, 6, 6, 0, 0, 6, 6, 0, 0

  ]
)
DotZerkRobot.grid.append(
  [
    0, 0, 0, 6, 6, 6, 6, 0, 0, 0,
    0, 0, 6, 1, 8, 6, 6, 6, 0, 0,
    0, 6, 6, 6, 6, 6, 6, 6, 6, 0,
    0, 6, 0, 6, 6, 6, 6, 0, 6, 0,
    0, 6, 0, 6, 6, 6, 6, 0, 6, 0,
    0, 0, 0, 6, 6, 6, 6, 0, 0, 0,
    0, 0, 0, 6, 0, 0, 6, 0, 0, 0,
    0, 0, 6, 6, 0, 0, 6, 6, 0, 0

  ]
)
DotZerkRobot.grid.append(
  [
    0, 0, 0, 6, 6, 6, 6, 0, 0, 0,
    0, 0, 6, 6, 1, 8, 6, 6, 0, 0,
    0, 6, 6, 6, 6, 6, 6, 6, 6, 0,
    0, 6, 0, 6, 6, 6, 6, 0, 6, 0,
    0, 6, 0, 6, 6, 6, 6, 0, 6, 0,
    0, 0, 0, 6, 6, 6, 6, 0, 0, 0,
    0, 0, 0, 6, 0, 0, 6, 0, 0, 0,
    0, 0, 6, 6, 0, 0, 6, 6, 0, 0

  ]
)
DotZerkRobot.grid.append(
  [
    0, 0, 0, 6, 6, 6, 6, 0, 0, 0,
    0, 0, 6, 6, 6, 1, 8, 6, 0, 0,
    0, 6, 6, 6, 6, 6, 6, 6, 6, 0,
    0, 6, 0, 6, 6, 6, 6, 0, 6, 0,
    0, 6, 0, 6, 6, 6, 6, 0, 6, 0,
    0, 0, 0, 6, 6, 6, 6, 0, 0, 0,
    0, 0, 0, 6, 0, 0, 6, 0, 0, 0,
    0, 0, 6, 6, 0, 0, 6, 6, 0, 0

  ]
)


DotZerkRobot.grid.append(
  [
    0, 0, 0, 6, 6, 6, 6, 0, 0, 0,
    0, 0, 6, 6, 6, 1, 8, 6, 0, 0,
    0, 6, 6, 6, 6, 6, 6, 6, 6, 0,
    0, 6, 0, 6, 6, 6, 6, 0, 6, 0,
    0, 6, 0, 6, 6, 6, 6, 0, 6, 0,
    0, 0, 0, 6, 6, 6, 6, 0, 0, 0,
    0, 0, 0, 6, 0, 0, 6, 0, 0, 0,
    0, 0, 6, 6, 0, 0, 6, 6, 0, 0

  ]
)

DotZerkRobot.grid.append(
  [
    0, 0, 0, 6, 6, 6, 6, 0, 0, 0,
    0, 0, 6, 6, 6, 8, 1, 6, 0, 0,
    0, 6, 6, 6, 6, 6, 6, 6, 6, 0,
    0, 6, 0, 6, 6, 6, 6, 0, 6, 0,
    0, 6, 0, 6, 6, 6, 6, 0, 6, 0,
    0, 0, 0, 6, 6, 6, 6, 0, 0, 0,
    0, 0, 0, 6, 0, 0, 6, 0, 0, 0,
    0, 0, 6, 6, 0, 0, 6, 6, 0, 0

  ]
)


DotZerkRobot.grid.append(
  [
    0, 0, 0, 6, 6, 6, 6, 0, 0, 0,
    0, 0, 6, 6, 8, 1, 6, 6, 0, 0,
    0, 6, 6, 6, 6, 6, 6, 6, 6, 0,
    0, 6, 0, 6, 6, 6, 6, 0, 6, 0,
    0, 6, 0, 6, 6, 6, 6, 0, 6, 0,
    0, 0, 0, 6, 6, 6, 6, 0, 0, 0,
    0, 0, 0, 6, 0, 0, 6, 0, 0, 0,
    0, 0, 6, 6, 0, 0, 6, 6, 0, 0

  ]
)


DotZerkRobot.grid.append(
  [
    0, 0, 0, 6, 6, 6, 6, 0, 0, 0,
    0, 0, 6, 8, 1, 6, 6, 6, 0, 0,
    0, 6, 6, 6, 6, 6, 6, 6, 6, 0,
    0, 6, 0, 6, 6, 6, 6, 0, 6, 0,
    0, 6, 0, 6, 6, 6, 6, 0, 6, 0,
    0, 0, 0, 6, 6, 6, 6, 0, 0, 0,
    0, 0, 0, 6, 0, 0, 6, 0, 0, 0,
    0, 0, 6, 6, 0, 0, 6, 6, 0, 0

  ]
)

DotZerkRobot.grid.append(
  [
    0, 0, 0, 6, 6, 6, 6, 0, 0, 0,
    0, 0, 6, 8, 1, 6, 6, 6, 0, 0,
    0, 6, 6, 6, 6, 6, 6, 6, 6, 0,
    0, 6, 0, 6, 6, 6, 6, 0, 6, 0,
    0, 6, 0, 6, 6, 6, 6, 0, 6, 0,
    0, 0, 0, 6, 6, 6, 6, 0, 0, 0,
    0, 0, 0, 6, 0, 0, 6, 0, 0, 0,
    0, 0, 6, 6, 0, 0, 6, 6, 0, 0,

  ]
)




DotZerkRobotWalking = cf.ColorAnimatedSprite(h=0, v=0, name="Robot", width=10, height=8, frames=2, currentframe=0,framerate=1,grid=[])
DotZerkRobotWalking.grid.append(
  [
    0, 0, 0, 6, 6, 6, 6, 0, 0, 0,
    0, 0, 6,14,14, 6, 6, 6, 0, 0,
    0, 6, 6, 6, 6, 6, 6, 6, 6, 0,
    0, 6, 0, 6, 6, 6, 6, 0, 6, 0,
    0, 6, 0, 6, 6, 6, 6, 0, 6, 0,
    0, 0, 0, 6, 6, 6, 6, 0, 0, 0,
    0, 0, 0, 6, 0, 0, 6, 0, 0, 0,
    0, 0, 6, 6, 0, 6, 6, 0, 0, 0,

  ]
)
DotZerkRobotWalking.grid.append(
  [
    0, 0, 0, 6, 6, 6, 6, 0, 0, 0,
    0, 0, 6,14,14, 6, 6, 6, 0, 0,
    0, 6, 6, 6, 6, 6, 6, 6, 6, 0,
    0, 6, 0, 6, 6, 6, 6, 0, 6, 0,
    0, 6, 0, 6, 6, 6, 6, 0, 6, 0,
    0, 0, 0, 0, 6, 6, 0, 0, 0, 0,
    0, 0, 0, 0, 6, 6, 0, 0, 0, 0,
    0, 0, 0, 6, 6, 6, 0, 0, 0, 0

  ]
)


DotZerkRobotWalkingSmall = cf.ColorAnimatedSprite(h=0, v=0, name="Robot", width=9, height=5, frames=4, currentframe=0,framerate=1,grid=[])
DotZerkRobotWalkingSmall.grid.append(
  [
   0, 0, 0,10,10,10,10, 0, 0,
   0, 0,10, 7, 7,10,10,10, 0,
   0, 0,10,10,10,10,10,10, 0,
   0, 0,10, 0, 0, 0, 0,10, 0,
   0, 10,10, 0, 0, 0,10,10, 0

  ]
)
DotZerkRobotWalkingSmall.grid.append(
  [
   0, 0, 0,10,10,10,10, 0, 0,
   0, 0,10, 7, 7,10,10,10, 0,
   0, 0,10,10,10,10,10,10, 0,
   0, 0, 0,10, 0, 0,10, 0, 0,
   0, 0,10,10, 0,10,10, 0, 0,

  ]
)

DotZerkRobotWalkingSmall.grid.append(
  [
   0, 0, 0,10,10,10,10, 0, 0,
   0, 0,10, 7, 7,10,10,10, 0,
   0, 0,10,10,10,10,10,10, 0,
   0, 0, 0, 0,10,10, 0, 0, 0,
   0, 0, 0,10,10,10, 0, 0, 0,

  ]
)
DotZerkRobotWalkingSmall.grid.append(
  [
   0, 0, 0,10,10,10,10, 0, 0,
   0, 0,10, 7, 7,10,10,10, 0,
   0, 0,10,10,10,10,10,10, 0,
   0, 0, 0,10, 0, 0,10, 0, 0,
   0, 0,10,10, 0,10,10, 0, 0,

  ]
)






ChickenRunning = cf.ColorAnimatedSprite(h=0, v=0, name="Chicken", width=8, height=8, frames=4, currentframe=0,framerate=1,grid=[])
ChickenRunning.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 5, 0, 0, 0, 0, 0,
    0,17, 2, 0, 0, 0, 0, 0,
    0, 0, 5, 2, 0, 2, 2, 0,
    0, 0, 0, 2, 2, 2, 0, 0,
    0, 0, 0, 0,22, 0, 0, 0,
    0, 0, 0,22, 0,21, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0

  ]
)

ChickenRunning.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 5, 0, 0, 0, 0, 0,
    0,17, 2, 0, 0, 0, 0, 0,
    0, 0, 5, 2, 0, 2, 2, 0,
    0, 0, 0, 2, 2, 2, 0, 0,
    0, 0, 0, 0,22, 0, 0, 0,
    0, 0, 0, 0,22, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0

  ]
)

ChickenRunning.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 5, 0, 0, 0, 0, 0,
    0,17, 2, 0, 0, 0, 0, 0,
    0, 0, 5, 2, 0, 2, 2, 0,
    0, 0, 0, 2, 2, 2, 0, 0,
    0, 0, 0, 0,22, 0, 0, 0,
    0, 0, 0,21, 0,22, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0

  ]
)


ChickenRunning.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 5, 0, 0, 0, 0, 0,
    0,17, 2, 0, 0, 0, 0, 0,
    0, 0, 5, 2, 0, 2, 2, 0,
    0, 0, 0, 2, 2, 2, 0, 0,
    0, 0, 0, 0,22, 0, 0, 0,
    0, 0, 0, 0,22, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0

  ]
)







WormChasingChicken = cf.ColorAnimatedSprite(h=0, v=0, name="Chicken", width=24, height=8, frames=4, currentframe=0,framerate=1,grid=[])
WormChasingChicken.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0,17, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 5, 2, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0,22, 0, 0, 0, 0, 0, 0, 0,17,17,17,17,17,17,17,17, 0, 0, 0, 0,
    0, 0, 0,22, 0,21, 0, 0, 0, 0, 0, 0,17,17,17,17,17,17,17,17, 0, 0, 0, 0,

  ]
)

WormChasingChicken.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0,17, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 5, 2, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,17,17, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0,22, 0, 0, 0, 0, 0, 0, 0, 0,17,17,17,17,17,17,17, 0, 0, 0, 0,
    0, 0, 0, 0,22, 0, 0, 0, 0, 0, 0, 0, 0,17,17,17, 0, 0,17,17, 0, 0, 0, 0,

  ]
)

WormChasingChicken.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0,17, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 5, 2, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0,17,17, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,17,17, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0,22, 0, 0, 0, 0, 0, 0, 0, 0, 0,17,17, 0, 0,17,17, 0, 0, 0, 0,
    0, 0, 0,21, 0,22, 0, 0, 0, 0, 0, 0, 0, 0,17,17, 0, 0,17,17, 0, 0, 0, 0

  ]
)


WormChasingChicken.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0,17, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 5, 2, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,17,17, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0,22, 0, 0, 0, 0, 0, 0, 0, 0,17,17,17,17,17,17,17, 0, 0, 0, 0,
    0, 0, 0, 0,22, 0, 0, 0, 0, 0, 0, 0, 0,17,17,17, 0, 0,17,17, 0, 0, 0, 0

  ]
)












ChickenChasingWorm = cf.ColorAnimatedSprite(h=0, v=0, name="Chicken", width=16, height=8, frames=4, currentframe=0,framerate=1,grid=[])
ChickenChasingWorm.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0,17, 2, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 2, 0, 2, 2, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,22, 0, 0, 0,
    5,17, 5,17,17, 0, 0, 0, 0, 0, 0,22, 0,21, 0, 0

  ]
)

ChickenChasingWorm.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0,17, 2, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 2, 0, 2, 2, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0,
    0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0,22, 0, 0, 0,
    0, 5,17, 0,17, 0, 0, 0, 0, 0, 0, 0,22, 0, 0, 0

  ]
)

ChickenChasingWorm.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0,17, 2, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 2, 0, 2, 2, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,22, 0, 0, 0,
    5,17, 5,17,17, 0, 0, 0, 0, 0, 0,21, 0,22, 0, 0

  ]
)


ChickenChasingWorm.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0,17, 2, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 2, 0, 2, 2, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0,
    0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0,22, 0, 0, 0,
    0, 5,17, 0,17, 0, 0, 0, 0, 0, 0, 0,22, 0, 0, 0

  ]
)




#----------------------------
#-- SpaceDot               --
#----------------------------

#Custom Colors because we will be running at full brightness
# Future work: convert to proper tuples.









  


PlayerShipR = cf.SDMedBlueR
PlayerShipG = cf.SDMedBlueG
PlayerShipB = cf.SDMedBlueB
PlayerMissileR = cf.SDMedWhiteR
PlayerMissileG = cf.SDMedWhiteG
PlayerMissileB = cf.SDMedWhiteB


#def __init__(h,v,r,g,b,direction,scandirection,speed,alive,lives,name,score,exploding):
#EmptyObject   = cf.Ship(-1,-1,0,0,0,0,1,0,0,0,'EmptyObject',0,0)

UFOMissile1   = cf.Ship(-1,-0,PlayerMissileR,PlayerMissileG,PlayerMissileB,3,3,gv.UFOMissileSpeed,0,0,'UFOMissile',0,0)
UFOMissile2   = cf.Ship(-1,-0,PlayerMissileR,PlayerMissileG,PlayerMissileB,3,3,gv.UFOMissileSpeed,0,0,'UFOMissile',0,0)
UFOMissile3   = cf.Ship(-1,-0,PlayerMissileR,PlayerMissileG,PlayerMissileB,3,3,gv.UFOMissileSpeed,0,0,'UFOMissile',0,0)
#PlayerMissile1 = cf.Ship(-0,-0,PlayerMissileR,PlayerMissileG,PlayerMissileB,1,1,5,0,0,'PlayerMissile', 0,0)
#PlayerMissile2 = cf.Ship(-0,-0,PlayerMissileR,PlayerMissileG,PlayerMissileB,1,1,5,0,0,'PlayerMissile', 0,0)



# BomberShip records the location and status
# BomberSprite is the color animated sprite of the ship

#(self,h,v,name,width,height,frames,currentframe,framerate,grid):
BomberSprite = cf.ColorAnimatedSprite(h=0, v=0, name="BomberShip", width=3, height=1, frames=4, currentframe=0,framerate=25,grid=[])
BomberSprite.grid.append(
  [ 9, 9, 9 ]
)
BomberSprite.grid.append(
  [ 9,10, 9 ]
)
BomberSprite.grid.append(
  [ 9,11, 9 ]
)
BomberSprite.grid.append(
  [ 9,10, 9 ]
)

BomberShip = cf.Ship(
  h=0,
  v=0,
  r=0,g=0,b=0,
  direction=2,scandirection=3,
  speed=gv.BomberShipSpeed,alive=0,lives=3,name="BomberShip",score=0,exploding=0
) 






#(self,h,v,name,width,height,frames,currentframe,framerate,grid):
SatelliteSprite = cf.ColorAnimatedSprite(
  h=-1, v=-1, name="HomingMissile", width=3, height=3, 
  frames       = 7,
  currentframe = 0,
  framerate    = gv.HomingMissileFrameRate,
  grid         = []
)
SatelliteSprite.grid.append(
  [ 0, 1, 0,
    1, 1, 1,
    0, 1, 0]
)

SatelliteSprite.grid.append(
  [ 0, 1, 0,
    1, 2, 1,
    0, 1, 0]
)
SatelliteSprite.grid.append(
  [ 0, 1, 0,
    1, 3, 1,
    0, 1, 0]
)
SatelliteSprite.grid.append(
  [ 0, 1, 0,
    1, 4, 1,
    0, 1, 0]
)

SatelliteSprite.grid.append(
  [ 0, 1, 0,
    1, 4, 1,
    0, 1, 0]
)

SatelliteSprite.grid.append(
  [ 0, 1, 0,
    1, 3, 1,
    0, 1, 0]
)

SatelliteSprite.grid.append(
  [ 0, 1, 0,
    1, 2, 1,
    0, 1, 0]
)






#(self,h,v,name,width,height,frames,currentframe,framerate,grid):
SatelliteSprite2 = cf.ColorAnimatedSprite(
  h=-1, v=-1, name="HomingMissile", width=3, height=3, 
  frames       = 7,
  currentframe = 0,
  framerate    = gv.HomingMissileFrameRate,
  grid         = []
)
SatelliteSprite2.grid.append(
  [ 0, 1, 0,
    1,13, 1,
    0, 1, 0]
)

SatelliteSprite2.grid.append(
  [ 0, 1, 0,
    1,14, 1,
    0, 1, 0]
)
SatelliteSprite2.grid.append(
  [ 0, 1, 0,
    1,15, 1,
    0, 1, 0]
)
SatelliteSprite2.grid.append(
  [ 0, 1, 0,
    1,16, 1,
    0, 1, 0]
)

SatelliteSprite2.grid.append(
  [ 0, 1, 0,
    1,16, 1,
    0, 1, 0]
)

SatelliteSprite2.grid.append(
  [ 0, 1, 0,
    1,15, 1,
    0, 1, 0]
)

SatelliteSprite2.grid.append(
  [ 0, 1, 0,
    1,14, 1,
    0, 1, 0]
)







#(self,h,v,name,width,height,frames,currentframe,framerate,grid):
SatelliteSprite3 = cf.ColorAnimatedSprite(
  h=-1, v=-1, name="HomingMissile", width=3, height=3, 
  frames       = 8,
  currentframe = 0,
  framerate    = gv.HomingMissileFrameRate,
  grid         = []
)
SatelliteSprite3.grid.append(
  [39,39, 0,
    0, 0, 0,
    0, 0, 0]
)

SatelliteSprite3.grid.append(
  [ 0,39,39,
    0, 0, 0,
    0, 0, 0]
)
SatelliteSprite3.grid.append(
  [ 0, 0,39,
    0, 0,39,
    0, 0, 0]
)
SatelliteSprite3.grid.append(
  [ 0, 0, 0,
    0, 0,39,
    0, 0,39]
)
SatelliteSprite3.grid.append(
  [ 0, 0, 0,
    0, 0, 0,
    0,39,39]
)
SatelliteSprite3.grid.append(
  [ 0, 0, 0,
    0, 0, 0,
   39,39, 0]
)
SatelliteSprite3.grid.append(
  [ 0, 0, 0,
   39, 0, 0,
   39, 0, 0]
)
SatelliteSprite3.grid.append(
  [39, 0, 0,
   39, 0, 0,
    0, 0, 0]
)



#(self,h,v,name,width,height,frames,currentframe,framerate,grid):
SatelliteSprite4 = cf.ColorAnimatedSprite(
  h=-1, v=-1, name="HomingMissile", width=3, height=3, 
  frames       = 8,
  currentframe = 0,
  framerate    = gv.HomingMissileFrameRate,
  grid         = []
)
SatelliteSprite4.grid.append(
  [40,40, 0,
    0, 0, 0,
    0, 0, 0]
)

SatelliteSprite4.grid.append(
  [ 0,40,40,
    0, 0, 0,
    0, 0, 0]
)
SatelliteSprite4.grid.append(
  [ 0, 0,40,
    0, 0,40,
    0, 0, 0]
)
SatelliteSprite4.grid.append(
  [ 0, 0, 0,
    0, 0,40,
    0, 0,40]
)
SatelliteSprite4.grid.append(
  [ 0, 0, 0,
    0, 0, 0,
    0,40,40]
)
SatelliteSprite4.grid.append(
  [ 0, 0, 0,
    0, 0, 0,
   40,40, 0]
)
SatelliteSprite4.grid.append(
  [ 0, 0, 0,
   40, 0, 0,
   40, 0, 0]
)
SatelliteSprite4.grid.append(
  [40, 0, 0,
   40, 0, 0,
    0, 0, 0]
)




#(self,h,v,name,width,height,frames,currentframe,framerate,grid):
SatelliteSprite5 = cf.ColorAnimatedSprite(
  h=-1, v=-1, name="HomingMissile", width=3, height=3, 
  frames       = 8,
  currentframe = 0,
  framerate    = gv.HomingMissileFrameRate,
  grid         = []
)
SatelliteSprite5.grid.append(
  [ 0,43,43,
    0, 0, 0,
    0, 0, 0]
)

SatelliteSprite5.grid.append(
  [43,43, 0,
    0, 0, 0,
    0, 0, 0]
)
SatelliteSprite5.grid.append(
  [43, 0, 0,
   43, 0, 0,
    0, 0, 0]
)
SatelliteSprite5.grid.append(
  [ 0, 0, 0,
   43, 0, 0,
   43, 0, 0]
)
SatelliteSprite5.grid.append(
  [ 0, 0, 0,
    0, 0, 0,
   43,43, 0]
)
SatelliteSprite5.grid.append(
  [ 0, 0, 0,
    0, 0, 0,
    0,43,43]
)
SatelliteSprite5.grid.append(
  [ 0, 0, 0,
    0, 0,43,
    0, 0,43]
)
SatelliteSprite5.grid.append(
  [ 0, 0,43,
    0, 0,43,
    0, 0, 0]
)



#(self,h,v,name,width,height,frames,currentframe,framerate,grid):
SatelliteSprite6 = cf.ColorAnimatedSprite(
  h=-1, v=-1, name="HomingMissile", width=3, height=3, 
  frames       = 8,
  currentframe = 0,
  framerate    = gv.HomingMissileFrameRate,
  grid         = []
)
SatelliteSprite6.grid.append(
  [42,20,20,
    0, 0,20,
    0, 0, 0]
)


SatelliteSprite6.grid.append(
  [20,20,20,
   42, 0, 0,
    0, 0, 0]
)

SatelliteSprite6.grid.append(
  [20,20, 0,
   20, 0, 0,
   42, 0, 0]
)

SatelliteSprite6.grid.append(
  [20, 0, 0,
   20, 0, 0,
   20,42, 0]
)


SatelliteSprite6.grid.append(
  [ 0, 0, 0,
   20, 0, 0,
   20,20,42]
)

SatelliteSprite6.grid.append(
  [ 0, 0, 0,
    0, 0,42,
   20,20,20]
)


SatelliteSprite6.grid.append(
  [ 0, 0,42,
    0, 0,20,
    0,20,20]
)



SatelliteSprite6.grid.append(
  [ 0,42,20,
    0, 0,20,
    0, 0,20]
)



#(self,h,v,name,width,height,frames,currentframe,framerate,grid):
SatelliteSprite7 = cf.ColorAnimatedSprite(
  h=-1, v=-1, name="HomingMissile", width=3, height=3, 
  frames       = 8,
  currentframe = 0,
  framerate    = gv.HomingMissileFrameRate,
  grid         = []
)
SatelliteSprite7.grid.append(
  [41,41,41,
    0, 0, 0,
    0, 0, 0]
)

SatelliteSprite7.grid.append(
  [41, 0,41,
    0,41, 0,
    0, 0, 0]
)

SatelliteSprite7.grid.append(
  [41, 0,41,
    0,41, 0,
    0,41, 0]
)


SatelliteSprite7.grid.append(
  [41, 0,41,
   41, 0,41,
   41,41,41]
)

SatelliteSprite7.grid.append(
  [ 0,41, 0,
    0,41, 0,
   41,41,41]
)

SatelliteSprite7.grid.append(
  [ 0, 0, 0,
    0,41, 0,
   41,41,41]
)

SatelliteSprite7.grid.append(
  [ 0, 0, 0,
    0, 0, 0,
   41,41,41]
)

SatelliteSprite7.grid.append(
  [ 0, 0, 0,
    0, 0, 0,
   41,41,41]
)


#(self,h,v,name,width,height,frames,currentframe,framerate,grid):
SmallUFOSprite = cf.ColorAnimatedSprite(
  h = -1,
  v = -1,
  name   = "HomingMissile", 
  width  = 3, 
  height = 3, 
  frames = 4, 
  currentframe = 0,
  framerate    = gv.UFOFrameRate,
  grid = []
)


SmallUFOSprite.grid.append(
  [ 4, 0, 0,
    0, 1, 0,
    0, 0, 4
    
  ]
)


SmallUFOSprite.grid.append(
  [ 0, 4, 0,
    0, 1, 0,
    0, 4, 0
    
  ]
)
SmallUFOSprite.grid.append(
  [ 0, 0, 4,
    0, 1, 0,
    4, 0, 0
    
  ]
)

SmallUFOSprite.grid.append(
  [ 0, 0, 0,
    4, 1, 4,
    0, 0, 0
    
  ]
)






#(self,h,v,name,width,height,frames,currentframe,framerate,grid):
SmallUFOSprite2 = cf.ColorAnimatedSprite(
  h = -1,
  v = -1,
  name   = "HomingMissile", 
  width  = 3, 
  height = 3, 
  frames = 2, 
  currentframe = 0,
  framerate    = gv.UFOFrameRate,
  grid = []
)


SmallUFOSprite2.grid.append(
  [14, 0,14,
    0,22, 0,
    0, 5, 0
    
  ]
)

SmallUFOSprite2.grid.append(
  [14, 0,14,
    0,22, 0,
    0, 8, 0
    
  ]
)





#(self,h,v,name,width,height,frames,currentframe,framerate,grid):
SmallUFOSprite3 = cf.ColorAnimatedSprite(
  h = -1,
  v = -1,
  name   = "HomingMissile", 
  width  = 3, 
  height = 3, 
  frames = 2, 
  currentframe = 0,
  framerate    = gv.UFOFrameRate,
  grid = []
)


SmallUFOSprite3.grid.append(
  [ 0,25, 0,
   25, 5,25,
    0, 8, 0
    
  ]
)

SmallUFOSprite3.grid.append(
  [ 0,25, 0,
   25, 8,25,
    0, 5, 0
    
  ]
)



#(self,h,v,name,width,height,frames,currentframe,framerate,grid):
SmallUFOSprite4 = cf.ColorAnimatedSprite(
  h = -1,
  v = -1,
  name   = "HomingMissile", 
  width  = 3, 
  height = 3, 
  frames = 4, 
  currentframe = 0,
  framerate    = gv.UFOFrameRate,
  grid = []
)


SmallUFOSprite4.grid.append(
  [ 0,25,37,
   25, 0,25,
    0,25, 0
    
  ]
)


SmallUFOSprite4.grid.append(
  [37,25, 0,
   25, 0,25,
    0,25, 0
    
  ]
)
SmallUFOSprite4.grid.append(
  [ 0,25, 0,
   25, 0,25,
   37,25, 0
    
  ]
)
SmallUFOSprite4.grid.append(
  [ 0,25, 0,
   25, 0,25,
    0,25,37
    
  ]
)






#(self,h,v,name,width,height,frames,currentframe,framerate,grid):
SmallUFOSprite5 = cf.ColorAnimatedSprite(
  h = -1,
  v = -1,
  name   = "HomingMissile", 
  width  = 3, 
  height = 3, 
  frames = 2, 
  currentframe = 0,
  framerate    = gv.UFOFrameRate,
  grid = []
)


SmallUFOSprite5.grid.append(
  [14, 0,14,
    0,22, 0,
    0,17, 0,
    0,17, 0
    
  ]
)

SmallUFOSprite5.grid.append(
  [14, 0,14,
    0,22, 0,
    0,22, 0,
    0,18, 0
    
  ]
)

SmallUFOSprite5.grid.append(
  [14, 0,14,
    0,17, 0,
    0,19, 0,
    0,20, 0
    
  ]
)





#(self,h,v,name,width,height,frames,currentframe,framerate,grid):
SmallUFOSprite6 = cf.ColorAnimatedSprite(
  h = -1,
  v = -1,
  name   = "HomingMissile", 
  width  = 3, 
  height = 3, 
  frames = 4, 
  currentframe = 0,
  framerate    = gv.UFOFrameRate,
  grid = []
)


SmallUFOSprite6.grid.append(
  [ 2, 0, 2,
    2, 5, 2,
    2, 0, 2
    
  ]
)


SmallUFOSprite6.grid.append(
  [ 2, 0, 2,
    2, 5, 2,
    2, 0, 2
    
  ]
)

SmallUFOSprite6.grid.append(
  [ 2, 0, 2,
    2,39, 2,
    2, 0, 2
    
  ]
)

SmallUFOSprite6.grid.append(
  [ 2, 0, 2,
    2,39, 2,
    2, 0, 2
    
  ]
)




#(self,h,v,name,width,height,frames,currentframe,framerate,grid):
SmallUFOSprite7 = cf.ColorAnimatedSprite(
  h = -1,
  v = -1,
  name   = "HomingMissile", 
  width  = 3, 
  height = 3, 
  frames = 4, 
  currentframe = 0,
  framerate    = gv.UFOFrameRate,
  grid = []
)


SmallUFOSprite7.grid.append(
  [ 2, 2, 2,
    2,25, 1,
    2, 1, 1
    
  ]
)

SmallUFOSprite7.grid.append(
  [ 2, 2, 2,
    2,25, 1,
    2, 1, 1
    
  ]
)

SmallUFOSprite7.grid.append(
  [ 2, 2, 2,
    2,43, 1,
    2, 1, 1
    
  ]
)

SmallUFOSprite7.grid.append(
  [ 2, 2, 2,
    2,43, 1,
    2, 1, 1
    
  ]
)


#(self,h,v,name,width,height,frames,currentframe,framerate,grid):
MediumUFOSprite = cf.ColorAnimatedSprite(
  h = -1,
  v = -1,
  name   = "HomingMissile", 
  width  = 4, 
  height = 4, 
  frames = 6, 
  currentframe = 0,
  framerate    = gv.UFOFrameRate,
  grid = []
)


MediumUFOSprite.grid.append(
  [ 4, 0, 0, 0,
    0, 1, 0, 0,
    0, 0, 1, 0,
    0, 0, 0, 4]
)

MediumUFOSprite.grid.append(
  [ 0, 4, 0, 0,
    0, 1, 0, 0,
    0, 0, 1, 0,
    0, 0, 4, 0]
)


MediumUFOSprite.grid.append(
  [ 0, 0, 4, 0,
    0, 0, 1, 0,
    0, 1, 0, 0,
    0, 4, 0, 0]
)

MediumUFOSprite.grid.append(
  [ 0, 0, 0, 4,
    0, 0, 1, 0,
    0, 1, 0, 0,
    4, 0, 0, 0]
)

MediumUFOSprite.grid.append(
  [ 0, 0, 0, 0,
    0, 0, 1, 4,
    4, 1, 0, 0,
    0, 0, 0, 0]
)

MediumUFOSprite.grid.append(
  [ 0, 0, 0, 0,
    4, 1, 0, 0,
    0, 0, 1, 4,
    0, 0, 0, 0]
)








#(self,h,v,name,width,height,frames,currentframe,framerate,grid):
MediumUFOSprite2 = cf.ColorAnimatedSprite(
  h = -1,
  v = -1,
  name   = "HomingMissile", 
  width  = 4, 
  height = 4, 
  frames = 8, 
  currentframe = 0,
  framerate    = gv.UFOFrameRate,
  grid = []
)


MediumUFOSprite2.grid.append(
  [ 0,28,25, 0,
   25, 9, 9,25,
   25, 9, 9,25,
    0,25,25, 0]
)


MediumUFOSprite2.grid.append(
  [ 0,25,28, 0,
   25, 9, 9,25,
   25, 9, 9,25,
    0,25,25, 0]
)

MediumUFOSprite2.grid.append(
  [ 0,25,25, 0,
   25, 9, 9,28,
   25, 9, 9,25,
    0,25,25, 0]
)

MediumUFOSprite2.grid.append(
  [ 0,25,25, 0,
   25, 9, 9,25,
   25, 9, 9,28,
    0,25,25, 0]
)

MediumUFOSprite2.grid.append(
  [ 0,25,25, 0,
   25, 0, 9,25,
   25, 0, 9,25,
    0,25,28, 0]
)

MediumUFOSprite2.grid.append(
  [ 0,25,25, 0,
   25, 9, 9,25,
   25, 9, 9,25,
    0,28,25, 0]
)

MediumUFOSprite2.grid.append(
  [ 0,25,25, 0,
   25, 9, 9,25,
   28, 9, 9,25,
    0,25,25, 0]
)
MediumUFOSprite2.grid.append(
  [ 0,25,25, 0,
   28, 9, 9,25,
   25, 9, 9,25,
    0,25,25, 0]
)









#(self,h,v,name,width,height,frames,currentframe,framerate,grid):
MediumUFOSprite3 = cf.ColorAnimatedSprite(
  h = -1,
  v = -1,
  name   = "HomingMissile", 
  width  = 4, 
  height = 4, 
  frames = 8, 
  currentframe = 0,
  framerate    = gv.UFOFrameRate,
  grid = []
)


MediumUFOSprite3.grid.append(
  [ 0, 9, 9, 0,
    9, 9, 9, 9,
    9, 9, 9, 9,
    0,10,10, 0]
)


MediumUFOSprite3.grid.append(
  [ 0, 9, 9, 0,
    9, 9, 9, 9,
    9,10,10, 9,
    0,11,11, 0]
)
MediumUFOSprite3.grid.append(
  [ 0, 9, 9, 0,
    9,10,10, 9,
    9,11,11, 9,
    0,12,12, 0]
)
MediumUFOSprite3.grid.append(
  [ 0,10,10, 0,
    9,11,11, 9,
    9,12,12, 9,
    0,11,11, 0]
)
MediumUFOSprite3.grid.append(
  [ 0,11,11, 0,
    9,12,12, 9,
    9,11,11, 9,
    0,10,10, 0]
)
MediumUFOSprite3.grid.append(
  [ 0,12,12, 0,
    9,11,11, 9,
    9,10,10, 9,
    0, 9, 9, 0]
)
MediumUFOSprite3.grid.append(
  [ 0,11,11, 0,
    9,10,10, 9,
    9, 9, 9, 9,
    0, 9, 9, 0]
)
MediumUFOSprite3.grid.append(
  [ 0,10,10, 0,
    9, 9, 9, 9,
    9, 9, 9, 9,
    0, 9, 9, 0]
)






#(self,h,v,name,width,height,frames,currentframe,framerate,grid):
MediumUFOSprite4 = cf.ColorAnimatedSprite(
  h = -1,
  v = -1,
  name   = "HomingMissile", 
  width  = 4, 
  height = 3, 
  frames = 6, 
  currentframe = 0,
  framerate    = gv.UFOFrameRate,
  grid = []
)


MediumUFOSprite4.grid.append(
  [31, 0, 0,31,
    0,32,32, 0,
    0, 0, 0, 0
  ]
)

MediumUFOSprite4.grid.append(
  [31, 0, 0,31,
    0,32,32, 0,
    0, 0, 0, 0
  ]
)
MediumUFOSprite4.grid.append(
  [31, 0, 0,31,
    0,32,32, 0,
    0, 0, 0, 0
  ]
)

MediumUFOSprite4.grid.append(
  [ 0, 0, 0, 0,
   31,32,32,31,
    0, 0, 0, 0
  ]
)

MediumUFOSprite4.grid.append(
  [ 0, 0, 0, 0,
    0,32,32, 0,
   31, 0, 0,31,
   ]
)

MediumUFOSprite4.grid.append(
  [ 0, 0, 0, 0,
    0,32,32, 0,
    0,31,31, 0 
   ]
)






#(self,h,v,name,width,height,frames,currentframe,framerate,grid):
LargeUFOSprite1 = cf.ColorAnimatedSprite(
  h = -1,
  v = -1,
  name   = "HomingMissile", 
  width  = 5, 
  height = 3, 
  frames = 6, 
  currentframe = 0,
  framerate    = gv.UFOFrameRate,
  grid = []
)


LargeUFOSprite1.grid.append(
  [ 
    0, 1, 1, 1, 0,
    1,13,39,13, 1,
    0, 1, 1, 1, 0,
  ]
)



LargeUFOSprite1.grid.append(
  [ 
    0, 1, 1, 1, 0,
    1,39,13,13, 1,
    0, 1, 1, 1, 0,
  ]
)
LargeUFOSprite1.grid.append(
  [ 
    0, 1, 1, 1, 0,
    1,39,13,13, 1,
    0, 1, 1, 1, 0,
  ]
)
LargeUFOSprite1.grid.append(
  [ 
    0, 1, 1, 1, 0,
    1,13,39,13, 1,
    0, 1, 1, 1, 0,
  ]
)


LargeUFOSprite1.grid.append(
  [ 
    0, 1, 1, 1, 0,
    1,13,13,39, 1,
    0, 1, 1, 1, 0,
  ]
)

LargeUFOSprite1.grid.append(
  [ 
    0, 1, 1, 1, 0,
    1,13,13,39, 1,
    0, 1, 1, 1, 0,
  ]
)



#(self,h,v,name,width,height,frames,currentframe,framerate,grid):
LargeUFOSprite2 = cf.ColorAnimatedSprite(
  h = -1,
  v = -1,
  name   = "HomingMissile", 
  width  = 5, 
  height = 5, 
  frames = 5, 
  currentframe = 0,
  framerate    = gv.UFOFrameRate,
  grid = []
)



LargeUFOSprite2.grid.append(
  [ 
    0, 0, 1, 0, 0,
    0, 1, 1, 1, 0,
   39,13,13,13,13,
    0, 1, 1, 1, 0,
    0, 0, 1, 0, 0 
  ]
)
LargeUFOSprite2.grid.append(
  [ 
    0, 0, 1, 0, 0,
    0, 1, 1, 1, 0,
   13,39,13,13,13,
    0, 1, 1, 1, 0,
    0, 0, 1, 0, 0 
  ]
)
LargeUFOSprite2.grid.append(
  [ 
    0, 0, 1, 0, 0,
    0, 1, 1, 1, 0,
   13,13,39,13,13,
    0, 1, 1, 1, 0,
    0, 0, 1, 0, 0 
  ]
)

LargeUFOSprite2.grid.append(
  [ 
    0, 0, 1, 0, 0,
    0, 1, 1, 1, 0,
   13,13,13,39,13,
    0, 1, 1, 1, 0,
    0, 0, 1, 0, 0 
  ]
)
LargeUFOSprite2.grid.append(
  [ 
    0, 0, 1, 0, 0,
    0, 1, 1, 1, 0,
   13,13,13,13,39,
    0, 1, 1, 1, 0,
    0, 0, 1, 0, 0 
  ]
)






#(self,h,v,name,width,height,frames,currentframe,framerate,grid):
LargeUFOSprite3 = cf.ColorAnimatedSprite(
  h = -1,
  v = -1,
  name   = "HomingMissile", 
  width  = 5, 
  height = 5, 
  frames = 4, 
  currentframe = 0,
  framerate    = gv.UFOFrameRate,
  grid = []
)






LargeUFOSprite3.grid.append(
  [ 
    1, 1, 1, 1, 0,
    1, 2, 2, 2, 2,
    1, 2,40,40, 2,
    1, 2, 9, 9, 2,
    0, 2, 2, 2, 2 
  ]
)

LargeUFOSprite3.grid.append(
  [ 
    1, 1, 1, 1, 0,
    1, 2, 2, 2, 2,
    1, 2, 9,40, 2,
    1, 2, 9,40, 2,
    0, 2, 2, 2, 2 
  ]
)
LargeUFOSprite3.grid.append(
  [ 
    1, 1, 1, 1, 0,
    1, 2, 2, 2, 2,
    1, 2, 9, 9, 2,
    1, 2,40,40, 2,
    0, 2, 2, 2, 2 
  ]
)
LargeUFOSprite3.grid.append(
  [ 
    1, 1, 1, 1, 0,
    1, 2, 2, 2, 2,
    1, 2,40, 9, 2,
    1, 2,40, 9, 2,
    0, 2, 2, 2, 2 
  ]
)



#(self,h,v,name,width,height,frames,currentframe,framerate,grid):
LargeUFOSprite4 = cf.ColorAnimatedSprite(
  h = -1,
  v = -1,
  name   = "HomingMissile", 
  width  = 5, 
  height = 5, 
  frames = 10, 
  currentframe = 0,
  framerate    = gv.UFOFrameRate,
  grid = []
)


LargeUFOSprite4.grid.append(
  [ 
    0, 1,16, 1, 0,
    1, 1,41, 1, 1,
   16,41,41,41,16,
    1, 1,41, 1, 1,
    0, 1,16, 1, 0 
  ]
)
LargeUFOSprite4.grid.append(
  [ 
    0, 1,41, 1, 0,
    1, 1,41, 1, 1,
   41,41,15,41,41,
    1, 1,41, 1, 1,
    0, 1,41, 1, 0 
  ]
)
LargeUFOSprite4.grid.append(
  [ 
    0, 1,16, 1, 0,
    1, 1,15, 1, 1,
   16,15,13,15,16,
    1, 1,15, 1, 1,
    0, 1,16, 1, 0 
  ]
)
LargeUFOSprite4.grid.append(
  [ 
    0, 1,15, 1, 0,
    1, 1,13, 1, 1,
   15,13,13,13,15,
    1, 1,13, 1, 1,
    0, 1,15, 1, 0 
  ]
)
LargeUFOSprite4.grid.append(
  [ 
    0, 1,13, 1, 0,
    1, 1,13, 1, 1,
   13,13,13,13,13,
    1, 1,13, 1, 1,
    0, 1,13, 1, 0 
  ]
)
LargeUFOSprite4.grid.append(
  [ 
    0, 1,13, 1, 0,
    1, 1,13, 1, 1,
   13,13,13,13,13,
    1, 1,13, 1, 1,
    0, 1,13, 1, 0 
  ]
)
LargeUFOSprite4.grid.append(
  [ 
    0, 1,13, 1, 0,
    1, 1,13, 1, 1,
   13,13,13,13,13,
    1, 1,13, 1, 1,
    0, 1,13, 1, 0 
  ]
)
LargeUFOSprite4.grid.append(
  [ 
    0, 1,13, 1, 0,
    1, 1,13, 1, 1,
   13,13,41,13,13,
    1, 1,13, 1, 1,
    0, 1,13, 1, 0 
  ]
)

LargeUFOSprite4.grid.append(
  [ 
    0, 1,13, 1, 0,
    1, 1,13, 1, 1,
   13,13,41,13,13,
    1, 1,13, 1, 1,
    0, 1,13, 1, 0 
  ]
)

LargeUFOSprite4.grid.append(
  [ 
    0, 1,13, 1, 0,
    1, 1,16, 1, 1,
   13,16,41,16,13,
    1, 1,16, 1, 1,
    0, 1,13, 1, 0 
  ]
)




#(self,h,v,name,width,height,frames,currentframe,framerate,grid):
LargeUFOSprite5 = cf.ColorAnimatedSprite(
  h = -4,
  v = -1,
  name   = "HomingMissile", 
  width  = 8, 
  height = 5, 
  frames = 4, 
  currentframe = 0,
  framerate    = gv.UFOFrameRate,
  grid = []
)


LargeUFOSprite5.grid.append(
  [ 
    0, 2, 0, 0, 0, 0, 2, 0,
    2, 0, 0, 2, 2, 0, 0, 2,
    2, 1, 1,39,39, 1, 1, 2,
    2, 0, 0, 2, 2, 0, 0, 2,
    0, 2, 0, 0, 0, 0, 2, 0
  ]
)
LargeUFOSprite5.grid.append(
  [ 
    0, 2, 0, 0, 0, 0, 2, 0,
    2, 0, 0, 2, 2, 0, 0, 2,
    2, 1, 1,39,39, 1, 1, 2,
    2, 0, 0, 2, 2, 0, 0, 2,
    0, 2, 0, 0, 0, 0, 2, 0
  ]
)

LargeUFOSprite5.grid.append(
  [ 
    0, 2, 0, 0, 0, 0, 2, 0,
    2, 0, 0, 2, 2, 0, 0, 2,
    2, 1, 1, 5, 5, 1, 1, 2,
    2, 0, 0, 2, 2, 0, 0, 2,
    0, 2, 0, 0, 0, 0, 2, 0
  ]
)
LargeUFOSprite5.grid.append(
  [ 
    0, 2, 0, 0, 0, 0, 2, 0,
    2, 0, 0, 2, 2, 0, 0, 2,
    2, 1, 1, 5, 5, 1, 1, 2,
    2, 0, 0, 2, 2, 0, 0, 2,
    0, 2, 0, 0, 0, 0, 2, 0
  ]
)




#(self,h,v,name,width,height,frames,currentframe,framerate,grid):
LargeUFOSprite6 = cf.ColorAnimatedSprite(
  h = -4,
  v = -1,
  name   = "HomingMissile", 
  width  = 8, 
  height = 4, 
  frames = 6, 
  currentframe = 0,
  framerate    = gv.UFOFrameRate,
  grid = []
)


LargeUFOSprite6.grid.append(
  [ 
    0, 0, 0, 9, 9, 0, 0, 0,
    0, 1, 1, 1, 1, 1, 1, 0,
   39, 5, 5,39, 5, 5,39, 5,
    0, 1, 1, 1, 1, 1, 1, 0

  ]
)

LargeUFOSprite6.grid.append(
  [ 
    0, 0, 0, 9, 9, 0, 0, 0,
    0, 1, 1, 1, 1, 1, 1, 0,
   39, 5, 5,39, 5, 5,39, 5,
    0, 1, 1, 1, 1, 1, 1, 0

  ]
)


LargeUFOSprite6.grid.append(
  [ 
    0, 0, 0,40,40, 0, 0, 0,
    0, 1, 1, 1, 1, 1, 1, 0,
    5,39, 5, 5,39, 5, 5,39,
    0, 1, 1, 1, 1, 1, 1, 0

  ]
)

LargeUFOSprite6.grid.append(
  [ 
    0, 0, 0,40,40, 0, 0, 0,
    0, 1, 1, 1, 1, 1, 1, 0,
    5,39, 5, 5,39, 5, 5,39,
    0, 1, 1, 1, 1, 1, 1, 0

  ]
)

LargeUFOSprite6.grid.append(
  [ 
    0, 0, 0, 9, 9, 0, 0, 0,
    0, 1, 1, 1, 1, 1, 1, 0,
    5, 5,39, 5, 5,39, 5, 5,
    0, 1, 1, 1, 1, 1, 1, 0

  ]
)

LargeUFOSprite6.grid.append(
  [ 
    0, 0, 0, 9, 9, 0, 0, 0,
    0, 1, 1, 1, 1, 1, 1, 0,
    5, 5,39, 5, 5,39, 5, 5,
    0, 1, 1, 1, 1, 1, 1, 0

  ]
)



#(self,h,v,name,width,height,frames,currentframe,framerate,grid):
WideUFOSprite1 = cf.ColorAnimatedSprite(
  h = -1,
  v = -1,
  name   = "HomingMissile", 
  width  = 8, 
  height = 1, 
  frames =18, 
  currentframe = 0,
  framerate    = gv.UFOFrameRate,
  grid = []
)

WideUFOSprite1.grid.append(
  [39, 0, 0, 0, 0, 0, 0, 0 ]
)

WideUFOSprite1.grid.append(
  [ 5,39, 0, 0, 0, 0, 0, 0 ]
)

WideUFOSprite1.grid.append(
  [ 5, 5,39, 0, 0, 0, 0, 0 ]
)
WideUFOSprite1.grid.append(
  [ 0, 5, 5,39, 0, 0, 0, 0 ]
)
WideUFOSprite1.grid.append(
  [ 0, 0, 5, 5,39, 0, 0, 0 ]
)
WideUFOSprite1.grid.append(
  [ 0, 0, 0, 5, 5,39, 0, 0 ]
)
WideUFOSprite1.grid.append(
  [ 0, 0, 0, 0, 5, 5,39, 0 ]
)
WideUFOSprite1.grid.append(
  [ 0, 0, 0, 0, 0, 5, 5,39 ]
)
WideUFOSprite1.grid.append(
  [ 0, 0, 0, 0, 0, 0, 5,39 ]
)
WideUFOSprite1.grid.append(
  [ 0, 0, 0, 0, 0, 0, 0,39 ]
)
WideUFOSprite1.grid.append(
  [ 0, 0, 0, 0, 0, 0,39, 5 ]
)
WideUFOSprite1.grid.append(
  [ 0, 0, 0, 0, 0,39, 5, 5 ]
)
WideUFOSprite1.grid.append(
  [ 0, 0, 0, 0,39, 5, 5, 0 ]
)
WideUFOSprite1.grid.append(
  [ 0, 0, 0,39, 5, 5, 0, 0 ]
)
WideUFOSprite1.grid.append(
  [ 0, 0,39, 5, 5, 0, 0, 0 ]
)
WideUFOSprite1.grid.append(
  [ 0,39, 5, 5, 0, 0, 0, 0 ]
)
WideUFOSprite1.grid.append(
  [39, 5, 5, 0, 0, 0, 0, 0 ]
)
WideUFOSprite1.grid.append(
  [39, 5, 0, 0, 0, 0, 0, 0 ]
)


#----------------------------
#-- DotZerk                --
#----------------------------




    
#------------------------------------------------------------------------------
# Functions                                                                  --
#------------------------------------------------------------------------------


def ProcessKeypress(Key):
  #I moved this back into the main program because it was getting awkward trying to start another game
  #from within CommonFunctions

  global MainSleep
  global ScrollSleep
  global NumDots

  # a = animation demo
  # b = Big Clock
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
    cf.ClearBigLED()
    Message = ("EXIT GAME")
    TheBanner = cf.CreateBannerSprite(Message)
    TheBanner.r = 200
    TheBanner.g = 0
    TheBanner.b = 0
    TheBanner.Display((gv.HatWidth / 2) - (TheBanner.width / 2) ,(gv.HatHeight / 2) -3)
    time.sleep(1)


  elif (Key == "r"):
    gv.TheMatrix.Clear
    #ShowScrollingBanner("Reboot!",100,0,0,ScrollSleep * 0.55)
    os.execl(sys.executable, sys.executable, *sys.argv)
  elif (Key == "t"):

    ActivateClockMode(60)

  elif (Key == "c"):
    cf.DrawTinyClock(60)
  elif (Key == "h"):
    SetTimeHHMM()
  elif (Key == "i"):
    ShowIPAddress()
  elif (Key == "a"):
    ShowAllAnimations(ScrollSleep * 0.5)
  elif (Key == "b"):
    ActivateBigClock()


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
    gv.TheMatrix.Clear
    PlayRallyDot()
  elif (Key == "8"):
    gv.TheMatrix.Clear
    PlayOutbreak()


    
  elif (Key == "9"):
    gv.TheMatrix.Clear
    ShowDotZerkRobotTime(0.03)
    ShowFrogTime(0.04)
  elif (Key == "0"):
    gv.TheMatrix.Clear
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







#Draws the dots on the screen  
def DrawDotMatrix(DotMatrix):
  #cf.ClearBigLED()      
  #print ("--Drawgv.DotMatrix--")
  NumDots = 0
  for h in range (0,gv.HatWidth):
    for v in range (0,gv.HatHeight):
      #print ("hv dot: ",h,v,DotMatrix[h][v])
      if (gv.DotMatrix[h][v] == 1):
        NumDots = NumDots + 1
        cf.setpixel(h,v,cf.DotR,cf.DotG,cf.DotB)

  #print ("Dots Found: ",NumDots)
  
  #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
  return NumDots;
  

def CountDotsRemaining(DotMatrix):
  NumDots = 0
  lasth   = 0
  lastv   = 0
  for h in range (0,gv.HatWidth):
    for v in range (0,gv.HatHeight):
      #print ("hv dot: ",h,v,DotMatrix[h][v])
      if (DotMatrix[h][v] == 1):
        NumDots = NumDots + 1
        lasth = h
        lastv = v
  if (NumDots == 1 ):
    cf.setpixel(lasth,lastv,cf.DotR,cf.DotG,cf.DotB)
    #FlashDot4(lasth,lastv,.01)
  return NumDots;



  
  
  
def DrawPowerPills(PowerPills):
  global DotMatrix
  global NumDots
  r = 0
  g = 0
  b = 0
  h = randint(0,gv.HatWidth-1)
  v = randint(0,gv.HatHeight-1)
  DotCount = 1
  while DotCount <= PowerPills:
   # print ("Green Pill: ",h," ",v)
    
    if (gv.DotMatrix[h][v] == 1):
      # 0/1/2  empty/dot/pill
      gv.DotMatrix[h][v] = 2
      #r,g,b = cf.getpixel(h,v)
      cf.setpixel(h,v,cf.PillR,cf.PillG,cf.PillB)
      DotCount = DotCount + 1  
      #NumDots = NumDots -1        
    
      #if we overwrite a dot, take one away from count
      #if (r == DotR and g == DotG and b == DotB ):
        #DotMatrix[h][v] = 0
        #NumDots = NumDots -1  
  

    h = randint(0,gv.HatWidth-1)
    v = randint(0,gv.HatHeight-1)
  return;

def DrawDots( NumDots ):
  #Keep track of the dots in a 2D array
  #DotMatrix = [[0 for x in range (gv.HatWidth)] for y in range (gv.HatWidth)] 
  #print("--DrawDots--")

  r = 0
  g = 0
  b = 0

  if (NumDots < 5 or NumDots > (gv.HatWidth * gv.HatHeight)):
    print ("ERROR - NumDots not valid: ",NumDots)
    NumDots = 1000
    
  global DotMatrix
  h = randint(0,gv.HatWidth-1)
  v = randint(0,gv.HatHeight-1)
  DotCount = 1
  Tries    = 0
  while (DotCount <= NumDots and Tries <= 10000):
    Tries = Tries + 1
    if (gv.DotMatrix[h][v] != 1):
      r,g,b = cf.getpixel(h,v)
      print (h,v,r,g,b)
      if (r == 0 and g == 0 and b == 0):
        gv.DotMatrix[h][v] = 1
        cf.FlashDot5(h,v,0.001)
        cf.setpixel(h,v,cf.DotR,cf.DotG,cf.DotB)  
        DotCount = DotCount + 1
    h = randint(0,gv.HatWidth-1)
    v = randint(0,gv.HatHeight-1)
  return gv.DotMatrix; 

 

def DrawMaze():
  cf.setpixel(41,1,cf.WallR,cf.WallG,cf.WallB)
  cf.setpixel(42,2,cf.WallR,cf.WallG,cf.WallB)
  cf.setpixel(43,3,cf.WallR,cf.WallG,cf.WallB)
  cf.setpixel(44,4,cf.WallR,cf.WallG,cf.WallB)
  cf.setpixel(45,5,cf.WallR,cf.WallG,cf.WallB)
  cf.setpixel(46,6,cf.WallR,cf.WallG,cf.WallB)
  cf.setpixel(47,7,cf.WallR,cf.WallG,cf.WallB)

  return; 

  
  
#Not sure why this returns h,v -- will be removed
def DrawGhost(h,v,r,g,b):
   global PowerPillActive
   if PowerPillActive == 1:
     cf.setpixel(h,v,cf.BlueGhostR,cf.BlueGhostG,cf.BlueGhostB)
   else:
     cf.setpixel(h,v,r,g,b)
   return h,v;


def DrawPacDot(h,v,r,g,b):
   cf.setpixel(h,v,r,g,b)
   #unicorn.show()
   return h,v;
 


  
def FollowScanner(h,v,Direction):
  ScanHit = cf.ScanBox(h,v,Direction)
  SanDirection = Direction
    
  ScanH = 0
  ScanV = 0

  #This is a waterfall list
  #top items get priority
  if ScanHit   == "leftblueghost":
    Direction  =  cf.TurnLeft(Direction)
  elif ScanHit == "rightblueghost":
    Direction  =   cf.TurnRight(Direction)
  elif ScanHit == "frontblueghost":
    Direction  =   Direction
  elif ScanHit == "leftpill":
    Direction  =  cf.TurnLeft(Direction)
  elif ScanHit == "frontpill":
    Direction  =  Direction
  elif ScanHit == "rightpill":
    Direction  =   cf.TurnRight(Direction)
  elif ScanHit == "leftdot":
    Direction  = cf.TurnLeft(Direction)
  elif ScanHit == "rightdot":
    print ("Turning for rightdot")
    Direction  =  cf.TurnRight(Direction)
  elif ScanHit == "frontdot":
    Direction  = Direction

  #More complex situations go here
  elif ScanHit == "frontghost":
    Direction  = cf.ReverseDirection(Direction)
  elif ScanHit == "frontwall":
    ScanDirection  = cf.TurnRight(Direction)
    ScanH, ScanV, ScanDirection = cf.CalculateMovement(h,v,ScanDirection)
    ScanHit = cf.ScanDot(ScanH,ScanV)

    if (ScanHit == "empty" or ScanHit == "pill" or ScanHit == "blueghost" or ScanHit == "dot"):
      Direction = ScanDirection
    else:
      ScanDirection  = cf.TurnLeft(Direction)
      ScanH, ScanV, ScanDirection = cf.CalculateMovement(h,v,ScanDirection)
      ScanHit = cf.ScanDot(ScanH,ScanV)
      if (ScanHit == "empty" or ScanHit == "pill" or ScanHit == "blueghost" or ScanHit == "dot"):
        Direction = ScanDirection
      else:
        Direction  = cf.ReverseDirection(Direction)
         

    

            
  
  
  return Direction;
  
  
  


# We need to move the ghost and leave behind the proper colored pixel
  
def MoveGhost(h,v,CurrentDirection,r,g,b):
  global DotMatrix
  item = "NULL"
  #print ("MoveGhost old:",h,v,CurrentDirection)
  
  newh, newv, CurrentDirection = cf.CalculateMovement(h,v,CurrentDirection)
  item = cf.ScanDot(newh,newv)

  #print ("MoveGhost New:",newh,newv,CurrentDirection, item)
  
  #ghosts avoid walls, pills, and other ghosts
  if item == "wall" or item == "pill" or item == "ghost":
    CurrentDirection = randint(1,4)
    newh = h
    newv = v     

  elif item == "empty" or item == "dot":
    cf.setpixel(newh,newv,r,g,b)
    #if where we were coming from is a dot, replace, otherwise put blank
    if (gv.DotMatrix[h][v]==1):
      cf.setpixel(h,v,cf.DotR,cf.DotG,cf.DotB)
    else:
      cf.setpixel(h,v,0,0,0)

  #if item is pacot, don't do anything just sit there
  elif item == "pacdot":
    newh = h
    newv = v     

  elif item == "boundary":    
    CurrentDirection = randint(1,4)
    newh = h
    newv = v     
 
  #unicorn.show()

  #print "After  HVD:",h,v,CurrentDirection
  return newh,newv,CurrentDirection;


def KillGhost(h,v):  
    global Ghost1Alive
    global Ghost1H
    global Ghost1V
    global Ghost2Alive
    global Ghost2H
    global Ghost2V
    global Ghost3Alive
    global Ghost3H
    global Ghost3V
    global Ghost4Alive
    global Ghost4H
    global Ghost4V
    if h == Ghost1H and v == Ghost1V:
      Ghost1Alive = 0
      #print ("Killing Ghost:",Ghost1Alive)
    if h == Ghost2H and v == Ghost2V:
      Ghost2Alive = 0
      #print ("Killing Ghost:",Ghost2Alive)
    if h == Ghost3H and v == Ghost3V:
      Ghost3Alive = 0
      #print ("Killing Ghost:",Ghost3Alive)
    if h == Ghost4H and v == Ghost4V:
      Ghost4Alive = 0
      #print ("Killing Ghost:",Ghost3Alive)







def FindClosestDot(PacDotH,PacDotV,DotMatrix):
  #We want the player car to journey towards the the powerpill or regular dots
  ClosestX     = gv.HatWidth // 2
  ClosestY     = gv.HatHeight // 2
  MinDistance  = 9999
  Distance     = 0
  for x in range(0,gv.HatWidth):
    for y in range(0,gv.HatHeight):
      #Look for alive dots
      #print("DotMatrix[x][y]",x,y,DotMatrix[x][y])
      if (DotMatrix[x][y] == 1):
        Distance = cf.GetDistanceBetweenDots(PacDotH,PacDotV,x,y)
        #print ("Distance: ",Distance, " MinDistance:",MinDistance, "xy:",x,y)
        if (Distance <= MinDistance):
          MinDistance = Distance
          ClosestX = x
          ClosestY = y
      elif (DotMatrix[x][y] == 2 and PowerPillActive == 0):
        Distance = cf.GetDistanceBetweenDots(PacDotH,PacDotV,x,y)
        MinDistance = Distance
        ClosestX = x
        ClosestY = y


    
  #FlashDot5(ClosestX,ClosestY,0.003)
  return ClosestX,ClosestY;


def MovePacDot(h,v,CurrentDirection,r,g,b,DotsEaten):
  global Pacmoves
  global PowerPillActive
  global Ghost1Alive
  global Ghost2Alive
  global Ghost3Alive
  global DotMatrix
  global PacDotScore
  global DotPoints
  global PillPoints
  global BlueGhosePoints
  global Ghost1Alive
  global Ghost2Alive
  global Ghost3Alive
  global Ghost4Alive
  global MovesSinceEatingGhost     
  
  
  Pacmoves = Pacmoves + 1
  item = "NULL"

  newh, newv, CurrentDirection = cf.CalculateMovement(h,v,CurrentDirection)
  item = cf.ScanDot(newh,newv)

  #print ("MovePacDot item:",item)
  if item == "dot":
    DotsEaten = DotsEaten + 1
    gv.MovesSinceSmartSeekFlip = 0
    gv.PacDotSmarkSeekMode = 1
    Pacmoves = 0
    PacDotScore = PacDotScore + DotPoints
    cf.setpixel(newh,newv,r,g,b)
    cf.setpixel(h,v,0,0,0)
    gv.DotMatrix[newh][newv] = 0
    
  elif item == "pill":
    Pacmoves = 0
    gv.MovesSinceSmartSeekFlip = 0
    gv.PacDotSmartSeekMode = 1
    PacDotScore = PacDotScore + PillPoints
    cf.setpixel(newh,newv,r,g,b)
    cf.setpixel(h,v,0,0,0)
    gv.DotMatrix[newh][newv] = 0
    PowerPillActive = 1
    
    if Ghost1Alive == 1: DrawGhost(Ghost1H,Ghost1V,cf.Ghost1R,cf.Ghost1G,cf.Ghost1B)
    if Ghost2Alive == 1: DrawGhost(Ghost2H,Ghost2V,cf.Ghost2R,cf.Ghost2G,cf.Ghost2B)
    if Ghost3Alive == 1: DrawGhost(Ghost3H,Ghost3V,cf.Ghost3R,cf.Ghost3G,cf.Ghost3B)
    if Ghost4Alive == 1: DrawGhost(Ghost4H,Ghost4V,cf.Ghost4R,cf.Ghost4G,cf.Ghost4B)
    

  #Pacman needs to leave walls alone
  elif item == "wall":
    Pacmoves = 0
    CurrentDirection = randint(1,4)
    newh = h
    newv = v     
    

    
    
  elif item == "blueghost":
    Pacmoves = 0
    MovesSinceSmartSeekFlip       = 0
    PacDotSmartSeekMode       = 1
    
    PacDotScore = PacDotScore + BlueGhostPoints
    cf.setpixel(newh,newv,r,g,b)
    cf.setpixel(h,v,0,0,0)
    gv.DotMatrix[newh][newv] = 0

    KillGhost(newh,newv)

    
  elif item == "ghost":
    if PowerPillActive == 1:
      KillGhost(newh, newv)
      MovesSinceSmartSeekFlip       = 0
      PacDotSmartSeekMode       = 1
    else:  
      CurrentDirection = cf.TurnLeftOrRight(CurrentDirection)
      #Ghosts scare pacdot, and he goes into dumb mode
      PacDotSmartSeekMode       = 0

    CurrentDirection = CurrentDirection
    newh = h
    newv = v

      
      
  elif item == "empty":
    cf.setpixel(newh,newv,r,g,b)
    cf.setpixel(h,v,0,0,0)
    gv.DotMatrix[newh][newv] = 0

  elif item == "boundary":    
    CurrentDirection = randint(1,4)
    newh = h
    newv = v     


  #print "After  HVD:",h,v,CurrentDirection
  return newh,newv,CurrentDirection,DotsEaten;


  
  
    
#--------------------------------------
#--            PING                  --
#--------------------------------------
    
  
def PlayPing():

  #Variables
  Player1H = 0
  Player1V = 2
  Player2H = 7
  Player2V = 2
  PingDotH = 3
  PingDotV = 4
  Player1Speed = 4
  Player2Speed = 4
  DotSpeed = 4
  

    
  #Define Characters
  Player1Sprite = cf.Sprite(1,2,WhiteLowR, WhiteLowG, WhiteLowB, [1,1])
  Player2Sprite = cf.Sprite(1,2,WhiteLowR, WhiteLowG, WhiteLowB, [1,1])
  DotSprite     = cf.Sprite(1,1,WhiteHighR, WhiteHighG, WhiteHighB, [1])

  #Title
  cf.ShowScrollingBanner("Ping",205,205,205,gv.ScrollSleep)
  

  Player1Sprite.Display(Player1H,Player1V)
  Player1Sprite.Display(Player2H, Player2V)
  DotSprite.Display(PingDotH,PingDotV)
  
  #Draw Playfield
  #unicorn.show()
  #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)


  
#--------------------------------------
#--          Light Dot               --
#--------------------------------------



def ScanWorms(h,v):
# I am keeping this simple for now, will remove color checking later
# border
# empty
# wall

  
  global GreenObstacleFadeValue
  global GreenObstacleMinVisible

  Item = ''
  OutOfBounds = cf.CheckBoundary(h,v)
  
  if (OutOfBounds == 1):
    Item = 'border'
  else:
    #FlashDot(h,v,0)
    r,g,b = cf.getpixel(h,v)  
    #print ("rgb scanned:",r,g,b)
    if (r == 0 and g == 0 and b == 0):
      Item = 'EmptyObject'
    
    #wormdot obstacles are green
    #Every time they are scanned, they grow dim and eventually disappear
    elif (r == 0 and g >= GreenObstacleMinVisible and b == 0):
      #print ("Green obstacle found g:,g")  
      g = g - GreenObstacleFadeValue
      if (g < GreenObstacleMinVisible):
        cf.setpixel(h,v,0,0,0)
        Item = 'EmptyObject'
      else:
        cf.setpixel(h,v,0,g,0)
        Item = 'obstacle'
    elif (r == cf.SDLowRedR and g == cf.SDLowRedG and b == cf.SDLowRedB):      
        #setpixel(h,v,0,0,0)
        Item = 'speeduppill'      
    else:
      Item = 'wall'
  #print("Scanned:",Item)
  return Item
    


#This function is for the game where worms hit obstacles
def MoveWorm(Dot):
  h = 0
  v = 0
  Dot.trail.append((Dot.h, Dot.v))

  ItemList = []

  #Scan all around, make decision, move
  ItemList = ScanSuperWormsDirection(Dot.h,Dot.v,Dot.direction)

  
  
  #print('DotName: ', Dot.name, 'hv',Dot.h,Dot.v, ' ', *ItemList, sep='|')
  
  #get possible items, then prioritize

  #The red dot must be hit head on
  #once this happens we erase it and increase the speed
  if (ItemList[3] == 'speeduppill'):
    h,v = cf.CalculateDotMovement(Dot.h,Dot.v,Dot.direction)
    Dot.speed = Dot.speed -1
    Dot.maxtrail = Dot.maxtrail + 1
    if (Dot.speed <= 3):
      Dot.speed = 3
    ItemList[3] = 'EmptyObject'
    #print ("Speed: ",Dot.speed)
    cf.setpixel(h,v,0,0,0)
  
 
  #Red on left
  if (ItemList[1] == 'speeduppill'):
    Dot.direction = cf.TurnLeft(Dot.direction)
    h,v = cf.CalculateDotMovement(Dot.h,Dot.v,Dot.direction)    
    Dot.speed = Dot.speed -1
    Dot.maxtrail = Dot.maxtrail + 1
    if (Dot.speed <= 1):
      Dot.speed = 1
    ItemList[1] = 'EmptyObject'
    #print ("Speed: ",Dot.speed)
    cf.setpixel(h,v,0,0,0)

  elif (ItemList[5] == 'speeduppill'):
    Dot.direction =  cf.TurnRight(Dot.direction)
    h,v = cf.CalculateDotMovement(Dot.h,Dot.v,Dot.direction)    
    Dot.maxtrail = Dot.maxtrail + 1
    Dot.speed = Dot.speed -1
    if (Dot.speed <= 1):
      Dot.speed = 1
    ItemList[5] = 'EmptyObject'
    #print ("Speed: ",Dot.speed)
    cf.setpixel(h,v,0,0,0)

  #empty = move forward
  elif (ItemList[3] == 'EmptyObject'):
    Dot.h, Dot.v = cf.CalculateDotMovement(Dot.h,Dot.v,Dot.direction)

  #This was an accident, but I like it
  #If the worm has a head on collision with the obstacle, it gets stuck and the obstacle
  #fades, almost as if the worm is ` it.  The worm ends up shorter though!  Weird.
  #print ('ItemList[3]:', ItemList[3])
  if ItemList[3]  == 'obstacle':
    #print ("Obstacle hit!  Draining our power!")
    r,g,b = cf.getpixel(h,v)
    if (g > 45):
      r,g,b = FadePixel(r,g,b,1)
      cf.setpixel(h,v,r,g,b)
      
      #I have decided to try moving away from green dot
      Dot.direction = cf.TurnLeftOrRight(Dot.direction)
      Dot.h, Dot.v = cf.CalculateDotMovement(Dot.h,Dot.v,Dot.direction)    
      Dot.speed = Dot.speed +1


    
    
  #if heading to boundary or wall
  elif (ItemList[3] == 'wall' or ItemList[3] == 'border' or ItemList[3] == 'obstacle'):
    if (ItemList[1] == 'EmptyObject' and ItemList[5] == 'EmptyObject'):
      #print ("both empty picking random direction")
      Dot.direction = cf.TurnLeftOrRight(Dot.direction)
      Dot.h, Dot.v = cf.CalculateDotMovement(Dot.h,Dot.v,Dot.direction)
    elif (ItemList[1] == 'EmptyObject' and ItemList[5] != 'EmptyObject'):
      #print ("left empty turning left")
      Dot.direction = cf.TurnLeft(Dot.direction)
      Dot.h, Dot.v = cf.CalculateDotMovement(Dot.h,Dot.v,Dot.direction)
    elif (ItemList[5] == 'EmptyObject' and ItemList[1] != 'EmptyObject'):
      #print ("left empty turning right")
      Dot.direction =  cf.TurnRight(Dot.direction)
      Dot.h, Dot.v = cf.CalculateDotMovement(Dot.h,Dot.v,Dot.direction)
    
    
    else:
      #print ("you died")
      ReverseOrDie(Dot)
      #Dot.alive = 0
      #Dot.trail.append((Dot.h, Dot.v))
      #Dot.EraseTrail('forward','flash')
  
  return Dot



  
  
def ScanSuperWorms(h,v):
# I am keeping this simple for now, will remove color checking later
# border
# empty
# wall

  
  global GreenObstacleFadeValue
  global GreenObstacleMinVisible

  Item = ''
  OutOfBounds = cf.CheckBoundary(h,v)
  
  if (OutOfBounds == 1):
    Item = 'border'
  else:
    #FlashDot(h,v,0)
    r,g,b = cf.getpixel(h,v)  
    #print ("rgb scanned:",r,g,b)
    if (r == 0 and g == 0 and b == 0):
      Item = 'EmptyObject'
    
    else:
      Item = 'wall'
  
  return Item
    
    
def ScanSuperWormsDirection(h,v,direction):
  ScanDirection = 0
  ScanH         = 0
  ScanV         = 0
  Item          = ''
  ItemList      = ['NULL']
  
  # We will scan 7 spots around the dot
  #  LF FF FR
  #  LL    RR 
  #  BL    BR
  #
  #  2  3  4
  #  1     5
  #  7     6
  
  #Scanning Probe
  #Turn left move one + SCAN
  #Turn Right move one + SCAN
  #Turn Right Move one + SCAN 
  #Move one + SCAN 
  #Turn Right Move one + SCAN 
  
  
  #LL 1
  ScanDirection = cf.TurnLeft(direction)
  ScanH, ScanV = cf.CalculateDotMovement(h,v,ScanDirection)
  Item = ScanSuperWorms(ScanH,ScanV)
  ItemList.append(Item)
  
  #LF 2
  ScanDirection =  cf.TurnRight(ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSuperWorms(ScanH,ScanV)
  ItemList.append(Item)
  
  #FF 3
  ScanDirection =  cf.TurnRight(ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSuperWorms(ScanH,ScanV)
  ItemList.append(Item)
  
  #FR 4
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSuperWorms(ScanH,ScanV)
  ItemList.append(Item)
  
  #RR 5
  ScanDirection =  cf.TurnRight(ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSuperWorms(ScanH,ScanV)
  ItemList.append(Item)

  #BR 6
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSuperWorms(ScanH,ScanV)
  ItemList.append(Item)


  #BL 7
  ScanDirection =  cf.TurnRight(ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSuperWorms(ScanH,ScanV)
  ItemList.append(Item)
  return ItemList;


def FadePixel(r,g,b,fadeval):
  newr = r - fadeval
  newg = g - fadeval
  newb = b - fadeval
  
  if (newr < 0):
    newr = 0
  if (newg < 0):
    newg = 0
  if (newb < 0):
    newb = 0

  return r,g,b;
  

#This one is for the game where there are NOT obstacles, just long worms  
def MoveSuperWorm(Dot):
  h = 0
  v = 0
  Dot.trail.append((Dot.h, Dot.v))
  Dot.score = Dot.score + 1
  ItemList = []

  #Scan all around, make decision, move
  ItemList = ScanSuperWormsDirection(Dot.h,Dot.v,Dot.direction)


  #  2  3  4
  #  1     5
  #  7     6

  # If there way is clear, but another worm is in 6 or 7, cut them off
  if (ItemList[2] == 'EmptyObject' and
      ItemList[3] == 'EmptyObject' and
      ItemList[4] == 'EmptyObject'):


    if (ItemList[1] == 'EmptyObject' and ItemList[7] == 'wall'):
      #print ("sharp turn to left")
      Dot.direction = cf.TurnLeft(Dot.direction)
      Dot.h, Dot.v = cf.CalculateDotMovement(Dot.h,Dot.v,Dot.direction)

    elif (ItemList[5] == 'EmptyObject' and ItemList[6] == 'wall'):
      #print ("sharp turn to right")
      Dot.direction = cf.TurnRight(Dot.direction)
      Dot.h, Dot.v = cf.CalculateDotMovement(Dot.h,Dot.v,Dot.direction)
    else:
      #print ("keep moving forward no sharp turns")
      Dot.h, Dot.v = cf.CalculateDotMovement(Dot.h,Dot.v,Dot.direction)
      
  #if heading to boundary or wall
  elif (ItemList[3] == 'wall' or ItemList[3] == 'border' or ItemList[3] == 'obstacle'):
    if (ItemList[1] == 'EmptyObject' and ItemList[5] == 'EmptyObject'):
      #print ("both empty picking random direction")
      Dot.direction = cf.TurnLeftOrRight(Dot.direction)
      Dot.h, Dot.v = cf.CalculateDotMovement(Dot.h,Dot.v,Dot.direction)
    elif (ItemList[1] == 'EmptyObject' and ItemList[5] != 'EmptyObject'):
      #print ("left empty turning left")
      Dot.direction = cf.TurnLeft(Dot.direction)
      Dot.h, Dot.v = cf.CalculateDotMovement(Dot.h,Dot.v,Dot.direction)
    elif (ItemList[5] == 'EmptyObject' and ItemList[1] != 'EmptyObject'):
      #print ("left empty turning right")
      Dot.direction =  cf.TurnRight(Dot.direction)
      Dot.h, Dot.v = cf.CalculateDotMovement(Dot.h,Dot.v,Dot.direction)
    else:
      ReverseOrDie(Dot)
    

  
  elif (ItemList[3] == 'EmptyObject'):
    #print ("keep moving forward")
    Dot.h, Dot.v = cf.CalculateDotMovement(Dot.h,Dot.v,Dot.direction)

  else:
    print ("you died")
    ReverseOrDie(Dot)
      #Dot.alive = 0
      #Dot.trail.append((Dot.h, Dot.v))
      #Dot.EraseTrail('forward','flash')
  
    #If dead, erase.  This is only for display purposes.  Other logic will
    #handle the death of the superworm
    if (Dot.alive == 0):
      Dot.Kill()
  return Dot

  

  


def ReverseOrDie(WormDot):

  #We need to tell what direction the trail is facing  
  h,v   = WormDot.trail[0] #the very back of the trail
  h1,v1 = WormDot.trail[1]
  NewDirection = 0
  if (v1 < v):
    NewDirection = 3
  elif (v1 > v):
    NewDirection = 1
  elif (h1 < h):
    NewDirection = 2
  elif (h1 > h):
    NewDirection = 4

  #Scan behind of the superworm
  ItemList     = ScanSuperWormsDirection(h,v,NewDirection)

  #print (ItemList)
  if (ItemList[3] == 'EmptyObject'):
    WormDot.ReverseWorm()
    print ("** Full Reverse! **")
    #cf.ShowScreenArray()    
  else:
    print ("** worm death imminent ** ")
    WormDot.Kill()

  return    

  
  



def CreateSuperWormMap(MapLevel):
  
  
  print ("CreateSuperWorm Map: ",MapLevel)

  #Create maze 0
  SuperWormMap = []
  SuperWormMap.append(cf.Maze(
    h      = 0,
    v      = 0,
    width  = 64, 
    height = 32
    )
  )
  SuperWormMap[0].ColorList = {
    ' ' : (0,0,0),
    'O' : cf.WallRGB,
    '-' : (0,50,0),
    '|' : cf.WallRGB
  }


  SuperWormMap[0].TypeList = {
    ' ' : 'EmptyObject',
    'O' : 'wall',
    '-' : 'wall',
    '|' : 'wall'

  }



  SuperWormMap[0].map= (
    #0.........1.........2.........3.........4.........5.........6...64    
    "                ------------------------------------------------", #0  
    "                -                                              -",
    "                -                                              -",
    "                -                                              -",
    "                -                                              -",
    "                -                                              -",
    "                -                                              -",
    "                -                                              -",
    "                -                                              -",
    "                -                                              -",
    "                -                                              -", #10
    "                -                                              -",
    "                -                                              -",
    "                -                                              -",
    "                -                                              -",
    "                -                                              -",
    "                -                                              -",
    "                -                                              -",
    "                -                                              -",
    "                -                                              -",
    "                -                                              -", #20
    "                -                                              -",
    "                -                                              -",
    "                -                                              -",
    "                -                                              -",
    "                -                                              -",
    "                -------------------------------------------------",
    "                                                                 ",
    "                                                                 ",
    "                                                                 ",
    "                                                                 ", #30
    "                                                                 ",
    "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO" #32
  )

  #Create maze 1
  SuperWormMap.append(cf.Maze(
    h      = 0,
    v      = 0,
    width  = 64, 
    height = 32
    )
  )
  SuperWormMap[1].ColorList = {
    ' ' : (0,0,0),
    'O' : (0,0,95),
    '-' : (0,50,10),
    '|' : cf.WallRGB,
    '.' : (90,90,90),
    'o' : (220,0,0),
    'x' : ( 0, 0,40)
  }


  SuperWormMap[1].TypeList = {
    ' ' : 'EmptyObject',
    'O' : 'wall',
    '-' : 'wall',
    '|' : 'wall',
    '.' : 'wall',
    'x' : 'wall'

  }



  SuperWormMap[1].map= (
    #0.........1.........2.........3.........4.........5.........6...64    
    "                ------------------------------------------------", #0  
    "                -                                              -",
    "                -                                              -",
    "                -                                              -",
    "                -                                              -",
    "                -              OOOOOOOOOOOOOOOOOOO             -",
    "                -              Oxx...xxxxxxx...xxO             -",
    "                -              Oxx.o.xxxxxxx.o.xxO             -",
    "                -              Oxx...xxxxxxx...xxO             -",
    "                -              OOOOOOOOxxxOOOOOOOO             -",
    "                -                     OOOOO                    -", #10
    "                -                                              -",
    "                -                                              -",
    "                -                     OOOOO                    -",
    "                -                     OxxxO                    -",
    "                -                     OOOOO                    -",
    "                -                                              -",
    "                -                                              -",
    "                -                                              -",
    "                -                   OOOOOOOO                   -",
    "                -              OOOOO........OOOOOO             -", #20
    "                -              O.................O             -",
    "                -              O..OOOOOOOOOOOOO..O             -",
    "                -              OOO             OOO             -",
    "                -                                              -",
    "                -                                              -",
    "                ------------------------------------------------",
    "                                                                ",
    "                                                                ",
    "                                                                ",
    "                                                                ", #30
    "                                                                ",
    "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO" #32
  )



  #Create maze 2
  SuperWormMap.append(cf.Maze(
    h      = 0,
    v      = 0,
    width  = 64, 
    height = 32
    )
  )
  SuperWormMap[2].ColorList = {
    ' ' : (0,0,0),
    'O' : (0,0,55),
    '-' : (0,0,50),
    '|' : cf.WallRGB,
    '.' : ( 50,  0,  0),
    'o' : (200,  0,  0),
    'x' : (100,  0,  0),
    '#' : (220,  0,  0),
  }


  SuperWormMap[2].TypeList = {
    ' ' : 'EmptyObject',
    'O' : 'wall',
    '-' : 'wall',
    '|' : 'wall',
    '.' : 'wall',
    'x' : 'wall',
    '#' : 'wall'

  }



  SuperWormMap[2].map= (
    #0.........1.........2.........3.........4.........5.........6...64    
    "                ------------------------------------------------", #0  
    "                -                                              -",
    "                -                                              -",
    "                -                                              -",
    "                -                     xx                       -",
    "                -                    x##x                      -",
    "                -             xxxxxxxxxxxxxxxxxx               -",
    "                -              x..............x                -",
    "                -              x..............x                -",
    "                -             xxxxxxxxxxxxxxxxxx               -",
    "                -              x..x        x..x                -", #10
    "                -              x..x        x..x                -",
    "                -              x..x        x..x                -",
    "                -              xxxx        xxxx                -",
    "                -              x..x        x..x                -",
    "                -              x..x        x..x                -",
    "                -              x..x        x..x                -",
    "                -              x..x        x..x                -",
    "                -              x...x      x...x                -",
    "                -              xxxxxx    xxxxxx                -",
    "                -                                              -", #20
    "                -                                              -",
    "                -                                              -",
    "                -                                              -",
    "                -                                              -",
    "                -                                              -",
    "                ------------------------------------------------",
    "                                                                ",
    "                                                                ",
    "                                                                ",
    "                                                                ", #30
    "                                                                ",
    "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO" #32
  )
  

#Create maze 3
  SuperWormMap.append(cf.Maze(
    h      = 0,
    v      = 0,
    width  = 64, 
    height = 32
    )
  )
  SuperWormMap[3].ColorList = {
    ' ' : (0,0,0),
    'O' : (0,0,55),
    '-' : (70,0, 0),
    '|' : cf.WallRGB,
    '.' : ( 50,  0,  0),
    'o' : (200,  0,  0),
    'x' : (100,  0,  0),
    '#' : (200,  0,  0),
    'X' : (  0,  0,220)
  }


  SuperWormMap[3].TypeList = {
    ' ' : 'EmptyObject',
    'O' : 'wall',
    '-' : 'wall',
    '|' : 'wall',
    '.' : 'wall',
    'x' : 'wall',
    '#' : 'wall',
    'X' : 'wall'

  }



  SuperWormMap[3].map= (
    #0........1.........2.........3.........4.........5.........6...64    
    "                    ----------------------------------------    ", #0  
    "                   -                                        -   ",
    "                  -                                          -  ",
    "                 -                                            - ",
    "                -                     xx                       -",
    "                -                    xXXx                      -",
    "                -             xxxxxxxxxxxxxxxxxx               -",
    "                -              x..............x                -",
    "                -              x..............x                -",
    "                -             xxxxxxxxxxxxxxxxxx               -",
    "                -              x..x        x..x                -", #10
    "                -              x..x        x..x                -",
    "                -              x..x        x..x                -",
    "                -              xxxx        xxxx                -",
    "                -              x..x        x..x                -",
    "                -              x..x        x..x                -",
    "                -              x..x        x..x                -",
    "                -              x..x        x..x                -",
    "                -              x...x      x...x                -",
    "                -              xxxxxx    xxxxxx                -",
    "                -                                              -", #20
    "                -                                              -",
    "                -                                              -",
    "                 -                                            - ",
    "                  -                                          -  ",
    "                   -                                        -   ",
    "                    ----------------------------------------    ",
    "                                                                ",
    "                                                                ",
    "                                                                ",
    "                                                                ", #30
    "                                                                ",
    "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO" #32
  )
  


#Create maze 4
  SuperWormMap.append(cf.Maze(
    h      = 0,
    v      = 0,
    width  = 64, 
    height = 32
    )
  )
  SuperWormMap[4].ColorList = {
    ' ' : (0,0,0),
    'O' : (0,0,55),
    '-' : (0,0,50),
    '|' : cf.WallRGB,
    '.' : ( 60, 35,  0),
    ',' : ( 25, 15,  0),
    'x' : (100,  0,  0),
    '#' : (200,  0,  0),
    'X' : (  0,  0,220),
    'p' : (cf.MedPink),
    'c' : (cf.MedCyan),
    'o' : (cf.MedOrange),
    'b' : (cf.MedBlue),
    'g' : (cf.MedGreen),
    'y' : (cf.MedYellow)
  }


  SuperWormMap[4].TypeList = {
    ' ' : 'EmptyObject',
    'O' : 'wall',
    '-' : 'wall',
    '|' : 'wall',
    '.' : 'wall',
    ',' : 'wall',
    'x' : 'wall',
    '#' : 'wall',
    'X' : 'wall',
    'p' : 'wall',
    'c' : 'wall',
    'o' : 'wall',
    'b' : 'wall',
    'g' : 'wall',
    'y' : 'wall'

  }



  SuperWormMap[4].map= (
    #0.........1.........2.........3.........4.........5.........6...64    
    "                ------------------------------------------------", #0  
    "                -                                              -",
    "                -                       ,                      -",
    "                -                     . , .                    -",
    "                -                 ...,.,.., . ,                -",
    "                -               . .,. . ., .,. .               -",
    "                -             yp ., .,. . . .,. yp             -",
    "                -             yppp ,,..,.,.,. yyyp             -",
    "                -             ypppcc. . , . ggyyyp             -",
    "                -             ypppccco,.,,bgggyyyp             -",
    "                -             ypppcccooobbbgggyyyp             -", #10
    "                -             ypppcccooobbbgggyyyp             -",
    "                -             ypppcccooobbbgggyyyp             -",
    "                -             ypppcccooobbbgggyyyp             -",
    "                -             ypppcccooobbbgggyyyp             -",
    "                -             ypppcccooobbbgggyyyp             -",
    "                -             ypppcccooobbbgggyyyp             -",
    "                -             ypppcccooobbbgggyyyp             -",
    "                -               ppcccooobbbgggyy               -",
    "                -                  ccooobbbgg                  -",
    "                -                     oobb                     -", #20
    "                -                                              -",
    "                -                                              -",
    "                -                                              -",
    "                -                                              -",
    "                -                                              -",
    "                ------------------------------------------------",
    "                                                                ",
    "                                                                ",
    "                                                                ",
    "                                                                ", #30
    "                                                                ",
    "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO" #32
  )
  
#Create maze 5
  SuperWormMap.append(cf.Maze(
    h      = 0,
    v      = 0,
    width  = 64, 
    height = 32
    )
  )
  SuperWormMap[5].ColorList = {
    ' ' : (0,0,0),
    '`' : (0,0,0),
    'O' : (0,0,55),
    '-' : (30,0,75),
    '|' : cf.WallRGB,
    '.' : ( 60, 35,  0),
    ',' : ( 25, 15,  0),
    'x' : (100,  0,  0),
    '#' : (200,  0,  0),
    'X' : (  0,  0,220),
    'p' : (cf.MedPink),
    'c' : (cf.MedCyan),
    'o' : (cf.MedOrange),
    'b' : (cf.MedBlue),
    'g' : (cf.MedGreen),
    'y' : (cf.MedYellow)
  }


  SuperWormMap[5].TypeList = {
    ' ' : 'EmptyObject',
    '`' : 'wall',
    'O' : 'wall',
    '-' : 'wall',
    '|' : 'wall',
    '.' : 'wall',
    ',' : 'wall',
    'x' : 'wall',
    '#' : 'wall',
    'X' : 'wall',
    'p' : 'wall',
    'c' : 'wall',
    'o' : 'wall',
    'b' : 'wall',
    'g' : 'wall',
    'y' : 'wall'

  }




  SuperWormMap[5].map= (
    #0.........1.........2.........3.........4.........5.........6...64    
    "                ```````````````-------------------``````````````", #0  
    "                ``````````````-ooooooooooooooooooo-`````````````",
    "                ``````````````-o---------------- o-`````````````",
    "                ``````````````-o-               -o-`````````````",
    "                ``````````````-o-               -o-`````````````",
    "                `-------------o-                 -o------------`",
    "                -ooooooooooooo-                   -oooooooooooo-",
    "                -o------------                     -----------o-",
    "                -o-                                          -o-",
    "                -o-                                          -o-",
    "                -o-                                          -o-", #10
    "                -o-                                          -o-",
    "                -o-                                          -o-",
    "                -o-                                          -o-",
    "                -o-                                          -o-",
    "                -o-                                          -o-",
    "                -o-                                          -o-",
    "                -o-                                          -o-",
    "                -o-                                          -o-",
    "                -o------------                     -----------o-",
    "                -ooooooooooooo-                   -oooooooooooo-", #20
    "                `-------------o-                 -o------------ ",
    "                ``````````````-o-               -o-`````````````",
    "                ``````````````-o-               -o-`````````````",
    "                ``````````````-o-----------------o-`````````````",
    "                ``````````````-ooooooooooooooooooo-`````````````",
    "                ```````````````-------------------``````````````",
    "                                                                ",
    "                                                                ",
    "                                                                ",
    "                                                                ", #30
    "                                                                ",
    "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO" #32
  )


  # SuperWormMap[4].map= (
    # #0.........1.........2.........3.........4.........5.........6...64    
    # "                ------------------------------------------------", #0  
    # "                -                                              -",
    # "                -                                              -",
    # "                -                                              -",
    # "                -                                              -",
    # "                -                                              -",
    # "                -                                              -",
    # "                -                                              -",
    # "                -                                              -",
    # "                -                                              -",
    # "                -                                              -", #10
    # "                -                                              -",
    # "                -                                              -",
    # "                -                                              -",
    # "                -                                              -",
    # "                -                                              -",
    # "                -                                              -",
    # "                -                                              -",
    # "                -                                              -",
    # "                -                                              -",
    # "                -                                              -", #20
    # "                -                                              -",
    # "                -                                              -",
    # "                -                                              -",
    # "                -                                              -",
    # "                -                                              -",
    # "                ------------------------------------------------",
    # "                                                                ",
    # "                                                                ",
    # "                                                                ",
    # "                                                                ", #30
    # "                                                                ",
    # "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO" #32
  # )


  
  SuperWormMap[MapLevel].LoadMap()


  return



  
def PlaySuperWorms():
  
  

  #Local variables
  moves      = 0
  Finished   = 'N'
  LevelCount = 0
  HighScore  = 0
  SuperWormMapCount = 5

  maxtrail     = gv.StartMaxTrail
  SpeedUpSpeed = gv.SpeedUpSpeed
  
  
  OriginalSleep = gv.MainSleep * 5
  SleepTime     = gv.SuperWormSleep


  #Clock and date sprites
  ClockSprite   = cf.CreateClockSprite(12)
  #ClockH        = gv.HatWidth  // 2 - (ClockSprite.width // 2)
  #ClockV        = gv.HatHeight // 2 - (ClockSprite.height // 2)

  DayOfWeekSprite     = cf.CreateDayOfWeekSprite()
  MonthSprite         = cf.CreateMonthSprite()
  DayOfMonthSprite    = cf.CreateDayOfMonthSprite()
  CurrencySprite      = CreateCurrencySprite()

  
  
  
  



  #Make an array of worms
  SuperWorms = []
  for i in range(0,gv.SuperWormCount):
    print ("Making worm:",i)
    r,g,b = cf.BrightColorList[random.randint(1,27)]
    direction  = random.randint(1,4)
    startspeed = random.randint(gv.StartSpeedHigh,gv.StartSpeedLow)
    alive      = 1
    name       = 'Superworm - ' + str(i)
    
    SpotFound = False
    h          = random.randint(30,63)
    v          = random.randint(0,31)

    while (SpotFound == False):
      if (cf.IsSpotEmpty(h,v) == True):
        SuperWorms.append(cf.Dot(h,v,r,g,b,direction,startspeed,alive,name,(0,0),0, gv.StartMaxTrail,gv.EraseSpeed,(r,g,b)))
        SpotFound = True
      else:
        h  = random.randint(30,63)
        v  = random.randint(0,31)


    

      
  #Title
  gv.TheMatrix.Clear()
  cf.ClearBuffers()


  #Draw the Big text
  #Clear only the LED matrix
  #Draw the next size down
  #When at the final zoom level
  #  - clear the LED Matrix
  #  - clear all buffers (canvas and ScreenArray[V][H])
  #  - draw the text at desired last zoom level
  #  - draw the rest of the text, at this point it is all written to ArrayBuffer
  #  - clear the LED Matrix
  #  - clear all buffers (canvas and ScreenArray[V][H])
  #Call the ZoomScreen function to redraw the display using ScreenArray[V][H] which at this point
  #contains the values last written to the screen.


  cf.ShowGlowingText(CenterHoriz = True,h = -8,v = 0,   Text = 'TRON', RGB = cf.HighBlue, ShadowRGB = cf.ShadowBlue, ZoomFactor = 8,GlowLevels=0,DropShadow=False)
  gv.TheMatrix.Clear()
  cf.ShowGlowingText(CenterHoriz = True,h = -8,v = 0,   Text = 'TRON', RGB = cf.HighBlue, ShadowRGB = cf.ShadowBlue, ZoomFactor = 7,GlowLevels=0,DropShadow=False)
  gv.TheMatrix.Clear()
  cf.ShowGlowingText(CenterHoriz = True,h = -8,v = 0,   Text = 'TRON', RGB = cf.HighBlue, ShadowRGB = cf.ShadowBlue, ZoomFactor = 6,GlowLevels=0,DropShadow=False)
  gv.TheMatrix.Clear()
  cf.ShowGlowingText(CenterHoriz = True,h = -8,v = 0,   Text = 'TRON', RGB = cf.HighBlue, ShadowRGB = cf.ShadowBlue, ZoomFactor = 5,GlowLevels=0,DropShadow=False)
  gv.TheMatrix.Clear()
  cf.ShowGlowingText(CenterHoriz = True,h = -8,v = 0,   Text = 'TRON', RGB = cf.HighBlue, ShadowRGB = cf.ShadowBlue, ZoomFactor = 4,GlowLevels=0,DropShadow=False)
  gv.TheMatrix.Clear()
  cf.ShowGlowingText(CenterHoriz = True,h = -8,v = 0,   Text = 'TRON', RGB = cf.HighBlue, ShadowRGB = cf.ShadowBlue, ZoomFactor = 3,GlowLevels=0,DropShadow=False)

  gv.TheMatrix.Clear()
  cf.ClearBuffers()
  cf.ShowGlowingText(CenterHoriz = True,h = 0 ,v = 0,   Text = 'TRON',       RGB = cf.HighBlue,   ShadowRGB = cf.ShadowBlue,   ZoomFactor = 2,GlowLevels=50, DropShadow=True)
  cf.ShowGlowingText(CenterHoriz = True,h = 0 ,v = 16,  Text = 'LIGHT CYCLE',RGB = cf.HighRed,    ShadowRGB = cf.ShadowRed,    ZoomFactor = 1,GlowLevels=200,DropShadow=True)
  cf.ShowGlowingText(CenterHoriz = True,h = 0 ,v = 26,  Text = 'BY DATAGOD', RGB = cf.HighGreen,  ShadowRGB = cf.ShadowGreen,  ZoomFactor = 1,GlowLevels=200,DropShadow=True)
  time.sleep(1)
  cf.EraseMessageArea(LinesFromBottom=6)
  Message = cf.TronGetRandomMessage(MessageType = 'CHALLENGE')
  cf.ShowScrollingBanner2(Message,(200,50,0),0.015,26)

  gv.TheMatrix.Clear()
  gv.Canvas.Clear()
  cf.ZoomScreen(gv.ScreenArray,32,256,0,Fade=True)
  gv.TheMatrix.Clear()



  
  while (LevelCount < gv.SuperWormLevels):
    print ("Drawing Snake")
    #DrawSnake(0,0,(cf.MedOrange),3,1)
    #cf.ShowLevelCount(LevelCount)
    
    
    LevelCount = LevelCount + 1
    cf.ClearBigLED()
    CreateSuperWormMap(random.randint(0,SuperWormMapCount-1))
    
    cf.EraseMessageArea(LinesFromBottom=5)
    cf.DisplayScoreMessage(Message="Level " + str(LevelCount),RGB=cf.HighOrange,FillerRGB=(0,0,0))
    time.sleep(1)
    cf.EraseMessageArea(LinesFromBottom=5)
    cf.DisplayScoreMessage(h=30,Message=str(LevelCount),RGB=cf.HighOrange,FillerRGB=(0,0,0))

    #Show Custom Sprite
    cf.CopySpriteToPixelsZoom(ClockSprite,      gv.ClockH,      gv.ClockV,      gv.ClockRGB,       gv.SpriteFillerRGB,1)
    cf.CopySpriteToPixelsZoom(DayOfWeekSprite,  gv.DayOfWeekH,  gv.DayOfWeekV,  gv.DayOfWeekRGB,   gv.SpriteFillerRGB,1)
    cf.CopySpriteToPixelsZoom(MonthSprite,      gv.MonthH,      gv.MonthV,      gv.MonthRGB,       gv.SpriteFillerRGB,1)
    cf.CopySpriteToPixelsZoom(DayOfMonthSprite, gv.DayOfMonthH, gv.DayOfMonthV, gv.DayOfMonthRGB , gv.SpriteFillerRGB,1)
    cf.CopySpriteToPixelsZoom(CurrencySprite,   gv.CurrencyH,   gv.CurrencyV,   gv.CurrencyRGB,    gv.SpriteFillerRGB,1)

   

    
    #Reset Variables between rounds
    for i in range(0,gv.SuperWormCount):
      print ("Resetting worm:",i)
      SuperWorms[i].score = 0
      SuperWorms[i].SetStartingPoint()
      SuperWorms[i].direction = (random.randint(1,4))
      SuperWorms[i].alive     = 1
      SuperWorms[i].maxtrail  = gv.StartMaxTrail
      SuperWorms[i].trail     = [(SuperWorms[i].h, SuperWorms[i].v)]
      
    
    LevelFinished = 'N'
    SleepTime = gv.SuperWormSleep
    


    while (LevelFinished == 'N'):
      
      
      #Check for keyboard input
      m,r = divmod(moves,KeyboardSpeed)
      if (r == 0):
        Key = cf.PollKeyboard()
        ProcessKeypress(Key)
        if (Key == 'q'):
          LevelCount    = gv.SuperWormLevels + 1
          LevelFinished = 'Y'
          return
        if (Key == 'n'):
          CreateSuperWormMap(random.randint(0,SuperWormMapCount-1))
      #Show clock
      m,r = divmod(moves,CheckClockSpeed)
      if (r == 0):
        CheckClockTimer(ClockSprite)
        cf.CopySpriteToPixelsZoom(ClockSprite,      gv.ClockH,      gv.ClockV,      gv.ClockRGB,       gv.SpriteFillerRGB,1)
        cf.CopySpriteToPixelsZoom(DayOfWeekSprite,  gv.DayOfWeekH,  gv.DayOfWeekV,  gv.DayOfWeekRGB,   gv.SpriteFillerRGB,1)
        cf.CopySpriteToPixelsZoom(MonthSprite,      gv.MonthH,      gv.MonthV,      gv.MonthRGB,       gv.SpriteFillerRGB,1)
        cf.CopySpriteToPixelsZoom(DayOfMonthSprite, gv.DayOfMonthH, gv.DayOfMonthV, gv.DayOfMonthRGB,  gv.SpriteFillerRGB,1)
    
      m,r = divmod(moves,gv.CheckCurrencySpeed)
      if (r == 0):  
        CurrencySprite = CreateCurrencySprite()
        cf.CopySpriteToPixelsZoom(CurrencySprite,   gv.CurrencyH,   gv.CurrencyV,   gv.CurrencyRGB,    gv.SpriteFillerRGB,1)




      #Display dots if they are alive
      #Do other stuff too
      WormsAlive = 0
      Score = 0
      ScoreRGB = (0,0,0)

      for i in range(0,gv.SuperWormCount):

        if (SuperWorms[i].alive == 1):
          SuperWorms[i].Display()
          SuperWorms[i].TrimTrail()
          WormsAlive = WormsAlive + 1
          if (Score < SuperWorms[i].score):
            Score = SuperWorms[i].score
            ScoreRGB = SuperWorms[i].r,SuperWorms[i].g,SuperWorms[i].b


          #Increase speed if necessary
          m,r = divmod(moves,gv.IncreaseTrailLengthSpeed)
          if (r == 0):
            SuperWorms[i].IncreaseMaxTrailLength(1)


          #Move worm if it is their time
          m,r = divmod(moves,SuperWorms[i].speed)
          if (r == 0):
            MoveSuperWorm(SuperWorms[i])
            #check for head on collisions
            #if the head of the superworm hits another head, reverse or die
            for sw in range (0,gv.SuperWormCount):
              if (SuperWorms[sw].alive and i != sw and SuperWorms[i].h == SuperWorms[sw].h  and SuperWorms[i].v == SuperWorms[sw].v):
                SuperWorms[i].Kill()
                SuperWorms[sw].Kill()
                print ("Head on collision.  Both worms died")
                WormsAlive = WormsAlive - 2
                break;



        else:
          r = random.randint(0,gv.ResurrectionChance)
          if (r == 1):
            SuperWorms[i].Resurrect()
        
        

      print ("WormsAlive:",WormsAlive," ",end="\r")




      #Calculate Movement / Display Score
      moves = moves +1

      #don't print the screen every move, otherwise it slows game down
      #this is a good spot for implementing multithreading
      if (random.randint(1,10) == 1):
        cf.DisplayScore(Score,ScoreRGB)

      

      LevelFinished = 'Y'

      for i in range(0,gv.SuperWormCount):
        if (SuperWorms[i].alive == 1):
          LevelFinished = 'N'


      # if(Worm1Dot.alive == 0 and Worm2Dot.alive == 0 and Worm3Dot.alive == 0 and Worm4Dot.alive == 0 and Worm5Dot.alive == 0):
        # LevelFinished = 'Y'
      
      #print ("Alive:",Worm1Dot.alive,Worm2Dot.alive,Worm3Dot.alive)
    

      #Increase speed
      m,r = divmod(moves,SpeedUpSpeed)
      if (r == 0):
        SleepTime = SleepTime * 0.95
        if (SleepTime < gv.MinSleepTime):
          SleepTime = gv.MinSleepTime
      
      if (SleepTime >= gv.MinSleepTime):
        time.sleep(SleepTime)

    #get a random message to show at bottom of screen
    Message = cf.TronGetRandomMessage()
    cf.EraseMessageArea(LinesFromBottom=5)
    cf.DisplayScoreMessage(Message=Message ,RGB=cf.HighOrange,FillerRGB=(20,0,0))
    time.sleep(1.5)
    cf.ZoomScreen(gv.ScreenArray,32,256,0,Fade=True)

  cf.ShowGlowingText(CenterHoriz=True,h=0,v=0 ,Text= 'END',  RGB= cf.HighRed,ShadowRGB= cf.ShadowRed,ZoomFactor= 2,GlowLevels=55, DropShadow=False)
  cf.ShowGlowingText(CenterHoriz=True,h=0,v=11,Text= 'OF',   RGB= cf.HighRed,ShadowRGB= cf.ShadowRed,ZoomFactor= 2,GlowLevels=55, DropShadow=False)
  cf.ShowGlowingText(CenterHoriz=True,h=0,v=22,Text= 'LINE', RGB= cf.HighRed,ShadowRGB= cf.ShadowRed,ZoomFactor= 2,GlowLevels=55, DropShadow=False)
  time.sleep(1)
  cf.ZoomScreen(gv.ScreenArray,32,256,0,Fade=True)



  #Determine winner
  LongestTrail     = 1
  WinningSuperWorm = 0
  for i in range (0,gv.SuperWormCount):
    if (LongestTrail < len(SuperWorms[i].trail)):
      LongestTrail     = len(SuperWorms[i].trail)
      WinningSuperWorm = i
  print ("Winner: SuperWorm",i," score:",LongestTrail)
  #SuperWorms[WinningSuperWorm].score = SuperWorms[WinningSuperWorm].score + LongestTrail

  FinalScore  = str(LongestTrail)
  FinalWinner = SuperWorms[WinningSuperWorm].name
  Finalr      = SuperWorms[WinningSuperWorm].r
  Finalg      = SuperWorms[WinningSuperWorm].g
  Finalb      = SuperWorms[WinningSuperWorm].b 
  FinalRGB    = (Finalr,Finalg,Finalb)
  
  gv.TheMatrix.Clear()
  cf.ClearBuffers()
  cf.ShowGlowingText(CenterHoriz=True,h=0,v=1 ,Text= 'GAME',       RGB= cf.HighRed,    ShadowRGB= cf.ShadowRed,    ZoomFactor= 2,GlowLevels=150, DropShadow=True)
  cf.ShowGlowingText(CenterHoriz=True,h=0,v=12,Text= 'OVER',       RGB= cf.HighRed,    ShadowRGB= cf.ShadowRed,    ZoomFactor= 2,GlowLevels=150, DropShadow=True)
  cf.ShowGlowingText(CenterHoriz=True,h=0,v=26,Text= FinalScore,   RGB= FinalRGB,      ShadowRGB= (15,15,15),      ZoomFactor= 1,GlowLevels=150, FadeLevels=150,DropShadow=True)
  ThreeGhostSprite.ScrollAcrossScreen(0,26,'right',gv.ScrollSleep)

  gv.TheMatrix.Clear()
  gv.Canvas.Clear()
  cf.ZoomScreen(gv.ScreenArray,32,256,0,Fade=True)






  return;



#--------------------------------------
#  WormDOt                           --
#--------------------------------------

def TrimTrail(Dot):
  if (len(Dot.trail) > Dot.maxtrail):
    h,v = Dot.trail[0]
    cf.setpixel(h,v,0,0,0)
    del Dot.trail[0]

def PlaceGreenObstacle():
  finished = 'N'
  h = 1
  v = 0

  h = random.randint(0,gv.HatWidth-1)
  v = random.randint(0,gv.HatWidth-1)

  while (finished == 'N'):
    h = random.randint(0,gv.HatWidth-1)
    v = random.randint(0,gv.HatWidth-1)
    while ((h == 1  and v == 0)
        or (h == 0  and v == 1)
        or (h == 15 and v == 1)
        or (h == 0  and v == 14)
        or (h == 15 and v == 14)
        or (h == 1  and v == 15)
        or (h == 14  and v == 15)
        or (h == 14  and v == 0)):
        
        # actually, I will allow it for now
        #or (v == 1) # I decided to not let any obstacles on these rows, to increase play time
        #or (v == 6)
        #or (h == 1)
        #or (h == 6)):
      h = random.randint(0,gv.HatWidth-1)
      v = random.randint(0,gv.HatWidth-1)
    r,g,b = cf.getpixel(h,v)
    #print ("got pixel rgb hv",r,g,b,h,v)
    
    #The color of green is very important as it denotes an obstacle
    #The scanner will fade the obstacle until it disappears
    if (r == 0 and g == 0 and b == 0):
      
      #Once in a while, we will make the obstacle permanent (white dot)
      if (random.randint(1,3) == 1):
        cf.setpixel(h,v,0,125,125)
      else:
        cf.setpixel(h,v,0,75,0)
  
      finished = 'Y'
    
    #Sometimes it takes too long to find a empty spot and the program
    #seems to hang. We now have a 1 in 20 chance of exiting
    if (random.randint(1,20) == 1):
      finished = 'Y'

        
      
      

def PlaceSpeedupPill():
  finished = 'N'
  while (finished == 'N'):
    h = random.randint(0,gv.HatWidth-1)
    v = random.randint(0,gv.HatWidth-1)
    r,g,b = cf.getpixel(h,v)
    if (r == 0 and g == 0 and b == 0):
      cf.setpixel(h,v,cf.SDLowRedR,cf.SDLowRedG,cf.SDLowRedB)
      finished = 'Y'

    
    
def PlayWormDot():
  
  #Local variables
  moves       = 0
  Finished    = 'N'
  LevelCount  = 3
  Worm1h      = 0
  Worm1v      = 0
  Worm2h      = 0
  Worm2v      = 0
  Worm3h      = 0
  Worm3v      = 0
  SleepTime   = gv.MainSleep / 8
  
  #How often to obstacles appear?
  ObstacleTrigger = 150
  SpeedupTrigger  = 75
  SpeedupMultiplier = 0.75
  
  
  
  #def __init__(self,h,v,r,g,b,direction,speed,alive,name,trail,score,maxtrail,erasespeed):
  Worm1Dot = cf.Dot(Worm1h,Worm1v,cf.SDLowBlueR,cf.SDLowBlueG,cf.SDLowBlueB,(random.randint(1,5)),1,1,'Blue',(Worm1h, Worm1v), 0, 1,0.03)
  Worm2Dot = cf.Dot(Worm2h,Worm2v,cf.SDLowPurpleR,cf.SDLowPurpleG,cf.SDLowPurpleB,(random.randint(1,5)),1,1,'Purple',(Worm2h,Worm2v),0, 1,0.03)
  Worm3Dot = cf.Dot(Worm3h,Worm3v,cf.SDDarkOrangeR,cf.SDDarkOrangeG,cf.SDDarkOrangeB,(random.randint(1,5)),1,1,'Orange',(Worm3h,Worm3v),0, 1,0.03)
 
  
  #Title
  cf.ClearBigLED()
  cf.ShowScrollingBanner2("Worms",(cf.MedOrange),gv.ScrollSleep)
    

  
  while (LevelCount > 0):
    #print ("show worms")
    cf.ClearBigLED()
    #Display animation and clock every 30 seconds

    #print ("Show level")
    cf.ShowLevelCount(LevelCount)
    LevelCount = LevelCount - 1
    cf.ClearBigLED()
    #print ("===============================")
  
    #Reset Variables between rounds
    Worm1Dot.speed = 1 * gv.CPUModifier
    Worm2Dot.speed = 1 * gv.CPUModifier
    Worm3Dot.speed = 1 * gv.CPUModifier
    Worm1Dot.maxtrail = 0
    Worm2Dot.maxtrail = 0
    Worm3Dot.maxtrail = 0
    Worm1Dots = 0
    Worm2Dots = 0
    Worm3Dots = 0
    LevelFinished = 'N'
    moves     = 0

    #Place obstacles
    PlaceGreenObstacle()
    PlaceGreenObstacle()
    PlaceGreenObstacle()
    PlaceGreenObstacle()
    PlaceGreenObstacle()
    PlaceGreenObstacle()
    
    
    #Increase length of trail
    Worm1Dot.maxtrail = Worm1Dot.maxtrail + 1
    Worm2Dot.maxtrail = Worm2Dot.maxtrail + 1
    Worm3Dot.maxtrail = Worm3Dot.maxtrail + 1
    
    #Set random starting points
    Worm1h = random.randint(1,6)
    Worm1v = random.randint(1,6)
    Worm2h = random.randint(1,6)
    Worm2v = random.randint(1,6)
    Worm3h = random.randint(1,6)
    Worm3v = random.randint(1,6)
    while (Worm2h == Worm1h and Worm2v == Worm1v):
      Worm2h = random.randint(1,6)
      Worm2v = random.randint(1,6)
    while ((Worm3h == Worm2h and Worm3v == Worm2v) or (Worm3h == Worm1h and Worm3v == Worm1v)):
      Worm3h = random.randint(1,6)
      Worm3v = random.randint(1,6)
      
         
      
    Worm1Dot.h         = Worm1h
    Worm1Dot.v         = Worm1v
    Worm1Dot.direction = (random.randint(1,4))
    Worm1Dot.alive     = 1
    Worm1Dot.trail     = [(Worm1h, Worm1v)]
    
    Worm2Dot.h         = Worm2h
    Worm2Dot.v         = Worm2v
    Worm2Dot.direction = (random.randint(1,4))
    Worm2Dot.alive     = 1
    Worm2Dot.trail     = [(Worm2h, Worm2v)]
    

    Worm3Dot.h         = Worm3h
    Worm3Dot.v         = Worm3v
    Worm3Dot.direction = (random.randint(1,4))
    Worm3Dot.alive     = 1
    Worm3Dot.trail     = [(Worm3h, Worm3v)]

    while (LevelFinished == 'N'):
      
      #reset variables
      #Display animation and clock every X seconds
      if (CheckElapsedTime(CheckTime) == 1):
        ScrollScreenShowChickenWormTime('up',gv.ScrollSleep)


      
      
      #print ("direction:",Worm1Dot.direction,Worm2Dot.direction,Worm3Dot.direction)
      #Display dots if they are alive
      if (Worm1Dot.alive == 1):
        Worm1Dot.Display()
      if (Worm2Dot.alive == 1):
        Worm2Dot.Display()
      if (Worm3Dot.alive == 1):
        Worm3Dot.Display()
      #unicorn.show()
      #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
    

      #Calculate Movement
      moves = moves +1

      #Check for keyboard input
      m,r = divmod(moves,KeyboardSpeed)
      if (r == 0):
        Key = cf.PollKeyboard()
        ProcessKeypress(Key)

        if (Key == 'q'):
          LevelFinished = 'Y'
          LevelCount = 0
          return
      
      #PlaceObstacle and Increase Speed of the game
      m,r = divmod(moves,ObstacleTrigger)
      if (r==0):
        PlaceGreenObstacle()
        #This isn't used anymore since I went to HD
        #SleepTime = SleepTime * SpeedupMultiplier

      #PlaceSpeedupPill
      m,r = divmod(moves,SpeedupTrigger)
      if (r==0):
        PlaceSpeedupPill()
        
        
      if (Worm1Dot.alive == 1):
        m,r = divmod(moves,Worm1Dot.speed)
        if (r == 0):
          MoveWorm(Worm1Dot)
          Worm1Dot.score = Worm1Dot.score + 1
          #check for head on collisions
          if ((Worm1Dot.h == Worm2Dot.h and Worm1Dot.v == Worm2Dot.v and Worm2Dot.alive == 1) or (Worm1Dot.h == Worm3Dot.h and Worm1Dot.v == Worm3Dot.v and Worm3Dot.alive == 1)):
            #Worm1Dot.alive = 0
            #Worm1Dot.EraseTrail()
            Worm1Dot.maxtrail - 1
            if (Worm1Dot.maxtrail <= 0):
              Worm1Dot.maxtrail = 1
            Worm1Dot.speed = Worm1Dot.speed + 2

      if (Worm2Dot.alive == 1):
        m,r = divmod(moves,Worm2Dot.speed)
        if (r == 0):
          #Worm2Dot.trail.append((Worm2Dot.h, Worm2Dot.v))
          MoveWorm(Worm2Dot)
          Worm2Dot.score = Worm2Dot.score + 1
          #check for head on collisions
          if ((Worm2Dot.h == Worm3Dot.h and Worm2Dot.v == Worm3Dot.v and Worm3Dot.alive == 1) or (Worm2Dot.h == Worm1Dot.h and Worm2Dot.v == Worm1Dot.v and Worm1Dot.alive == 1)):
            #Worm2Dot.alive = 0
            #Worm2Dot.EraseTrail()
            Worm2Dot.maxtrail - 1
            if (Worm2Dot.maxtrail <= 0):
              Worm1Dot.maxtrail = 1
            Worm2Dot.speed = Worm2Dot.speed + 2

      if (Worm3Dot.alive == 1):
        m,r = divmod(moves,Worm3Dot.speed)
        if (r == 0):
          #Worm3Dot.trail.append((Worm3Dot.h, Worm3Dot.v))
          MoveWorm(Worm3Dot)
          Worm3Dot.score = Worm3Dot.score + 1
          #check for head on collisions
          if ((Worm3Dot.h == Worm2Dot.h and Worm3Dot.v == Worm2Dot.v and Worm2Dot.alive == 1) or (Worm3Dot.h == Worm1Dot.h and Worm3Dot.v == Worm1Dot.v and Worm1Dot.alive == 1)):
            #Worm3Dot.alive = 0
            #Worm3Dot.EraseTrail()
            Worm3Dot.maxtrail - 1
            if (Worm3Dot.maxtrail <= 0):
              Worm1Dot.maxtrail = 1
            Worm3Dot.speed = Worm3Dot.speed + 2
      
      #Trim length of Tails
      TrimTrail(Worm1Dot)
      TrimTrail(Worm2Dot)
      TrimTrail(Worm3Dot)
      
      
      if(Worm1Dot.alive == 0 and Worm2Dot.alive == 0 and Worm3Dot.alive == 0):
        LevelFinished = 'Y'
      
      #print ("Alive:",Worm1Dot.alive,Worm2Dot.alive,Worm3Dot.alive)
    
      PlayersAlive = Worm1Dot.alive + Worm2Dot.alive + Worm3Dot.alive
      # if (PlayersAlive == 2):
        # SleepTime = (SleepTime )
      # elif (PlayersAlive == 1):
        # SleepTime = (SleepTime )
      #time.sleep(SleepTime)
    
    
  
  #Calculate Game score
  FinalWinner = ''
  FinalScore  = 0
  Finalr      = 0
  Finalg      = 0
  Finalb      = 0
  if (Worm1Dot.score > Worm2Dot.score and Worm1Dot.score >= Worm3Dot.score):
    FinalScore  = Worm1Dot.score
    FinalWinner = Worm1Dot.name
    Finalr      = Worm1Dot.r
    Finalg      = Worm1Dot.g
    Finalb      = Worm1Dot.b
  elif (Worm2Dot.score >= Worm1Dot.score and Worm2Dot.score >= Worm3Dot.score):
    FinalScore  = Worm2Dot.score
    FinalWinner = Worm2Dot.name
    Finalr      = Worm2Dot.r
    Finalg      = Worm2Dot.g
    Finalb      = Worm2Dot.b
  else:
    FinalScore = Worm3Dot.score
    FinalWinner = Worm3Dot.name
    Finalr      = Worm3Dot.r
    Finalg      = Worm3Dot.g
    Finalb      = Worm3Dot.b

  cf.ClearBigLED()
  ScrollString = FinalWinner + ' ' + str(FinalScore)
  
  cf.ShowScrollingBanner(ScrollString,Finalr,Finalg,Finalb,gv.ScrollSleep)
  cf.ShowScrollingBanner("GAME OVER",cf.SDMedPinkR,cf.SDMedPinkG,cf.SDMedPinkB,gv.ScrollSleep)












#--------------------------------------
#  SpaceDot       PlaySpaceDot       -- 
#--------------------------------------


#We need an 16 x 16 grid to represent the playfield
#each ship, each missile, each bunker will be an object that
#is located on the playfield.  That way we can scan the individual 
#objects and not have to rely on the pixel colors to determine what is what







#Make a bomber rock
BomberRock = cf.Ship(-1,-1,200,0,0,3,3,15,0,1,'BomberRock', 0,0)
BomberRock.alive = 0
BomberRock.speed = gv.BomberRockSpeed
BomberRock.exploding = 0


#Make UFOMissile 
UFOMissile1.Explosion = copy.deepcopy(AsteroidExplosion)
UFOMissile2.Explosion = copy.deepcopy(AsteroidExplosion)
UFOMissile3.Explosion = copy.deepcopy(AsteroidExplosion)



#Make an array of PlayerMissiles
PlayerMissiles = []
for i in range(0,gv.PlayerMissiles):
  print ("Making PlayerMissile:",i)
  r,g,b = (200,200,200)
  PlayerMissiles.append(cf.Ship(-1,-1,PlayerMissileR,PlayerMissileG,PlayerMissileB,1,1,5,0,1,'PlayerMissile', 0,0))
  PlayerMissiles[i].alive = 0
  PlayerMissiles[i].exploding = 0
  PlayerMissiles[i].Explosion = copy.deepcopy(SmallExplosion)
  PlayerMissiles[i].Explosion.alive = 0
  PlayerMissiles[i].Explosion.exploding = 0
  PlayerMissiles[i].speed = gv.PlayerMissileSpeed
  PlayerMissiles[i].h = -1
  PlayerMissiles[i].v = -1





#Custom Sprite List
HomingMissileSpriteList = []
#HomingMissileSpriteList.append(FrogSprite)
#HomingMissileSpriteList.append(DropShip)
#HomingMissileSpriteList.append(SpaceInvader)

#ChickenRunning.framerate = 25

#HomingMissileSpriteList.append(ChickenRunning) #chicken needs work
HomingMissileSpriteList.append(SatelliteSprite)
HomingMissileSpriteList.append(SatelliteSprite2)
HomingMissileSpriteList.append(SatelliteSprite3)
HomingMissileSpriteList.append(SatelliteSprite4)
HomingMissileSpriteList.append(SatelliteSprite5)
HomingMissileSpriteList.append(SatelliteSprite6)
HomingMissileSpriteList.append(SatelliteSprite7)
HomingMissileSpriteList.append(SmallUFOSprite)
HomingMissileSpriteList.append(SmallUFOSprite2)
HomingMissileSpriteList.append(SmallUFOSprite3)
HomingMissileSpriteList.append(SmallUFOSprite4)
HomingMissileSpriteList.append(SmallUFOSprite5)
HomingMissileSpriteList.append(SmallUFOSprite6)
HomingMissileSpriteList.append(SmallUFOSprite7)
HomingMissileSpriteList.append(MediumUFOSprite)
HomingMissileSpriteList.append(MediumUFOSprite2)
HomingMissileSpriteList.append(MediumUFOSprite3)
HomingMissileSpriteList.append(MediumUFOSprite4)
HomingMissileSpriteList.append(LargeUFOSprite1)
HomingMissileSpriteList.append(LargeUFOSprite2)
HomingMissileSpriteList.append(LargeUFOSprite3)
HomingMissileSpriteList.append(LargeUFOSprite4)
HomingMissileSpriteList.append(LargeUFOSprite5)
HomingMissileSpriteList.append(LargeUFOSprite6)
HomingMissileSpriteList.append(WideUFOSprite1)
gv.HomingMissileSprites = len(HomingMissileSpriteList)



HomingMissileSprite   = HomingMissileSpriteList[random.randint(0,gv.HomingMissileSprites -1 )]
HomingMissileSprite.h = -1
HomingMissileSprite.v = -1
HomingMissileSprite.direction     = 5
HomingMissileSprite.scandirection = 3
HomingMissileSprite.speed = gv.HomingMissileInitialSpeed
HomingMissileSprite.alive = 0
HomingMissileSprite.lives = gv.HomingMissileLives
HomingMissileSprite.name  = "HomingMissile"
HomingMissileSprite.score = 0
HomingMissileSprite.exploding = 0




def CheckBoundarySpaceDot(h,v):
  BoundaryHit = 0
  if (v < gv.SpaceDotMinV or v > gv.SpaceDotMaxV  or h < gv.SpaceDotMinH or h > gv.SpaceDotMaxH):
    BoundaryHit = 1
  return BoundaryHit;




  
def ScanSpaceDot(h,v):

  Item = ''
  OutOfBounds = CheckBoundarySpaceDot(h,v)
  
  #top of the playfield is ok, lets asteroids fall
  

  if (OutOfBounds == 1 and v < 0):
    Item = 'aboveborder'
    #print ("Border found HV: ",h,v)
  elif (OutOfBounds == 1 and v >= 0):
    Item = 'border'

  else:

    try:
      Item = gv.Playfield[v][h].name
      
      
    except:
      print ('Playfield error h,v:',h,v)
      print(gv.Playfield[v][h])
      cf.FlashDot(h,v,3)
    
  return Item
  

def ScanAroundShip(h,v,direction):
  ScanDirection = 0
  ScanH         = 0
  ScanV         = 0
  Item          = ''
  ItemList      = ['NULL']
  
  #  8 1 2
  #  7   3  
  #  6 5 4  

  #
  
  
  #1
  ScanDirection = direction
  ScanH, ScanV = cf.CalculateDotMovement(h,v,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)
  #2
  ScanDirection =  cf.TurnRight(ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)
  #3
  ScanDirection =  cf.TurnRight(ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)

  #4
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)

  #5
  ScanDirection =  cf.TurnRight(ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)

  #6
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)

  #7
  ScanDirection =  cf.TurnRight(ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)

  #8
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)

  return ItemList

  
def ScanShip(h,v,direction):
  ScanDirection = 0
  ScanH         = 0
  ScanV         = 0
  Item          = ''
  ItemList      = ['NULL']

  
  # We will scan 5 spots around the dot
  # and 6 more in front
  
  # Note: we now have grass, so the scan distance is 1 level shorter
  #       It will be complicated to remove slot 7 
  #       (because of the use of slots 11,12,13, so I will instead populate it
  #       with a copy of slot 6.
  #       
  #       Upgraded to 64x32 display
  #       
  #  33 33 33
  #     32
  #     31
  #     30
  #     29
  #     28
  #     27
  #     26
  #     25 
  #     24
  #     23
  #  20 21 22
  #     19
  #     18
  #     17
  #     16
  #     15
  #     14
  #  11 12 13
  #    10
  #     9
  #     8
  #     7
  #     6
  #  2  3  4
  #  1     5
  #
  
  #Scanning Probe
  #Turn left move one + SCAN
  #Turn Right move one + SCAN
  #Turn Right Move one + SCAN 
  #Move one + SCAN 
  #Turn Right Move one + SCAN 
  
  
  #LL 1
  ScanDirection = cf.TurnLeft(direction)
  ScanH, ScanV = cf.CalculateDotMovement(h,v,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)
  
  #LF 2
  ScanDirection =  cf.TurnRight(ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)
  
  #FF 3
  ScanDirection =  cf.TurnRight(ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)
  
  #FR 4
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)
  
  #RR 5
  ScanDirection =  cf.TurnRight(ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)

  #F1 6
  ScanDirection = cf.ReverseDirection(ScanDirection)
  ScanH, ScanV  = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  ScanDirection = cf.TurnLeft(ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  ScanDirection =  cf.TurnRight(ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)

  #F2 7
  # This slot has become redundant due to a shorter playfield.
  #ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)
  
  #F3 8
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)
  
  #F4 9
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)

  #F5 10
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)

  #F6 11
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  ScanDirection = cf.TurnLeft(ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)

  #F7 12
  ScanDirection = cf.ReverseDirection(ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)

  #F8 13
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)

  #14 -- new additions since moving to larger grid
  ScanDirection = cf.ReverseDirection(ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  ScanDirection =  cf.TurnRight(ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)

  #15
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)

  #16
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)

  #17
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)

  #18
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)

  #19
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)
  
  #20
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  ScanDirection = cf.TurnLeft(ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)

  #21
  ScanDirection = cf.ReverseDirection(ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)
  

  #22
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)


  #23
  ScanDirection = cf.ReverseDirection(ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  ScanDirection =  cf.TurnRight(ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)

  #24
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)

  #25
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)
  #26
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)
  #27
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)
  #28
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)
  #29
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)
  #30
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)
  #31
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)
  #32
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)
  

  #33
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  ScanDirection = cf.TurnLeft(ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)

  #34
  ScanDirection = cf.ReverseDirection(ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)
  

  #35
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)


  return ItemList;


def ScanBomberShip(BomberShip):
  ScanDirection = BomberShip.direction
  ScanH         = BomberShip.h
  ScanV         = BomberShip.v
  Item          = ''
  ItemList      = ['NULL']
  i             = 0

  
  # We will scan  around the dot
  # and  more in front
  
  # Note: we now have grass, so the scan distance is 1 level shorter
  #       It will be complicated to remove slot 7 
  #       (because of the use of slots 11,12,13, so I will instead populate it
  #       with a copy of slot 6.
  #       
  
  #
  #          
  #      
  #  1  .  .  .  3
  #  x  x  2  x  x
  #        4
  #        5
  #        6
  #        7
  #        8
  #        9
  #        10
  #        11
  #        12
  #        ..
  #        ..
  #        25  
  
  
  #1
  ScanH = ScanH-1
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)
  
  #2
  ScanH, ScanV = ScanH +2, ScanV + 1
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)
  
  #3
  ScanH, ScanV = ScanH + 2, ScanV -1
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)
  
  #4 - 25
  for i in range(i,20):
    ScanH, ScanV = ScanH -2, ScanV + 2
    Item = ScanSpaceDot(ScanH,ScanV)
    ItemList.append(Item)
  

  return ItemList;


  
  
def HitBomber(BomberShip):
  h = BomberShip.h
  v = BomberShip.v
  if (BomberShip.lives > 0):
    BomberShip.lives = BomberShip.lives - 1
    gv.SpaceDotScore = gv.SpaceDotScore + gv.BomberHitPoints
  else:
    #BomberShip.alive = 0
    #gv.SpaceDotScore = gv.SpaceDotScore + gv.BomberPoints
    #PlayerShipExplosion.Animate(h-2,v-2,'forward',0.025)
    BomberShip.exploding = 1
    BomberShip.alive     = 0
    BomberShip.Explosion.h = h
    BomberShip.Explosion.v = v

    gv.SpaceDotScore = gv.SpaceDotScore + gv.BomberPoints

    #Erase playfield (ship is 3 dots across)
    if (h > 0 and h <= gv.HatWidth-1):
      gv.Playfield[v][h] = gv.EmptyObject
    if (h+1 > 0 and h+1 <= gv.HatWidth-1):
      gv.Playfield[v][h+1] = gv.EmptyObject
    if (h+2 > 0 and h+2 <= gv.HatWidth-1):
      gv.Playfield[v][h+2] = gv.EmptyObject
    BomberShip.Erase()

def HitHomingMissile(HomingMissileShip,HomingMissileSprite):
  h = HomingMissileShip.h
  v = HomingMissileShip.v
  if (HomingMissileShip.lives > 0):
    HomingMissileShip.lives = HomingMissileShip.lives - 1
    gv.SpaceDotScore = gv.SpaceDotScore + gv.HomingMissilePoints

  if (HomingMissileShip.lives == 0):
    HomingMissileShip.exploding = 1
    HomingMissileShip.alive     = 0
    #print ("blowing up homing missile")
    #cf.FlashDot(h,v,1)
    HomingMissileSprite.h = h
    HomingMissileSprite.v = v
    gv.Playfield     = HomingMissileSprite.EraseSpriteFromPlayfield(gv.Playfield)
    gv.SpaceDotScore = gv.SpaceDotScore + gv.HomingMissilePoints



def HitPlayerShip(PlayerShip):
  if (PlayerShip.lives > 0):
    PlayerShip.lives = PlayerShip.lives - 1

  if (PlayerShip.lives == 0):
    PlayerShip.exploding = 1
    PlayerShip.alive     = 0
    #Playfield[Playership.v][Playership.h] = gv.EmptyObject()
    


def HitGround(Ground):
  h = Ground.h
  v = Ground.v

  #The ground is messed up.  Missiles hit it and the ground objects are getting overwritten with gv.EmptyObject
  #because of this I am  just going to change the color of the ground but leave the pieces alive
  Ground.alive   = 1

  #if (Ground.lives > 0):
  #  Ground.lives = Ground.lives - 1
  Ground.r = Ground.r +25
  Ground.g = Ground.g +5
  Ground.b = Ground.b = 0

  if (Ground.r >= 255):
    Ground.r = 255
  if (Ground.g >= 255):
    Ground.g = 0


    
  gv.Playfield[v][h].r = Ground.r
  gv.Playfield[v][h].g = Ground.g
  gv.Playfield[v][h].b = Ground.b

  print("Ground hit hv:",Ground.h,Ground.v," rgb",Ground.r,Ground.g,Ground.b,' lives:',Ground.lives)

  #calculate score
  gv.SpaceDotScore = gv.SpaceDotScore - gv.AsteroidLandedPoints



  return  


  
def AdjustSpeed(Ship,setting,amount):
  #print ("AS - BEFORE Ship.name Ship.speed setting amount",Ship.name, Ship.speed, setting,amount)
  if (setting == 'slow'):
    Ship.speed = Ship.speed + amount
  else:
    Ship.speed = Ship.speed - amount
  
  if (Ship.speed <= gv.PlayerShipMinSpeed):
    Ship.speed = gv.PlayerShipMinSpeed
  elif (Ship.speed >= 50):
    Ship.speed = 50   
  #print ("AS - AFTER Ship.name Ship.speed setting amount",Ship.name, Ship.speed, setting,amount)
  


 
def ShowExplosion(Explosion):

  h = Explosion.h 
  v = Explosion.v 
  #print("boom:",Explosion.currentframe,Explosion.name)
  
  Explosion.Display(h,v)
  #Explosion.currentframe = Explosion.currentframe + 1
  

def PointTowardsNearestAsteroid(Ship,Asteroids):
  h = Ship.h
  v = Ship.v
  nearest  = 0
  distance = 0
  shortest = gv.HatWidth

  for i in range (0,len(Asteroids)):
    if (Asteroids[i].alive == 1 and Asteroids[i].v > 0):
      distance = abs(h - Asteroids[i].h)
      if distance < shortest:
        shortest = distance
        nearest  = i

  if (nearest > 0):
    #print ("Nearst asteroid found.  Turning towards:",Wave.Asteroids[nearest].h)
    cf.PointTowardsObjectH(Ship,Asteroids[nearest])

  return

  
  
      
      

  
def MovePlayerShip(Ship, HomingMissileShip, Asteroids):
  #print ("moveship Direction HV:",Ship.name,Ship.direction,Ship.h,Ship.v)
  
  EnemyTargets = ['UFO','Asteroid','UFOMissile','BomberShip','HomingMissile','BomberRock']
  EnemyToFollow = ['UFO','BomberShip','HomingMissile']

  #Player ships always points up, enemy ships point down
  h = Ship.h
  v = Ship.v
  ItemList = []
  #Scan all around, make decision, move
  ItemList = ScanShip(Ship.h,Ship.v,Ship.scandirection)
  
  #these are special radar points to the left or right, above the player ship
  ItemsOnLeft  = [ItemList[11],ItemList[20],ItemList[33]]
  ItemsOnRight = [ItemList[13],ItemList[22],ItemList[35]]

  #Priority
  # 1 Evade close objects
  # 2 Blast far objects

  #If Enemy is detected, fire missile!
  if ( any(item in EnemyTargets for item in ItemList)):

    for i in range(0,gv.PlayerMissiles):
      if (PlayerMissiles[i].alive == 0 and PlayerMissiles[i].exploding == 0):
        #print ("MPS - UFO/Bomber/asteroid Detected PlayerMissile1.alive:",PlayerMissiles[i].alive)
        PlayerMissiles[i].h = h
        PlayerMissiles[i].v = v
        PlayerMissiles[i].alive = 1
        #PlayerMissiles[i].lives = 1
        PlayerMissiles[i].exploding = 0
        break  


  #Homing missile must be destroyed!  Follow and intercept
  if (HomingMissileShip.alive == 1 and HomingMissileShip.v <= gv.SpaceDotMaxV -4):
    cf.PointTowardsObjectH(Ship,HomingMissileShip)
    AdjustSpeed(Ship,'fast',5)

  else:

    #Follow UFO
    #slow down if ahead of UFO, speed up if behind
    if ( any(item in EnemyToFollow for item in ItemsOnLeft)):
      
      #We are looking at the playfield to find the UFO or Bombership's direction
      #Look at top of screen
      if (gv.Playfield[0][h-1].name in EnemyToFollow):
        Ship.direction = gv.Playfield[0][h-1].direction

      #Look at middle of screen (according to scan area)
      elif (gv.Playfield[gv.HatHeight-1][h-1].name in EnemyToFollow):
        Ship.direction = gv.Playfield[gv.HatHeight-1][h-1].direction
      
      #print ("MPS - ENEMY TO LEFT Enemy.name HV direction",Playfield[h-1][0].name,Playfield[h-1][0].h,Playfield[h-1][0].v, Playfield[h-1][0].direction)
      if (gv.Playfield[0][h-1].direction == 4 or
        gv.Playfield[gv.HatHeight-1][h-1].direction == 4):
        AdjustSpeed(Ship,'fast',5)

      elif (gv.Playfield[0][h-1].direction == 2 or
            gv.Playfield[gv.HatHeight-1][h-1].direction == 2):
        AdjustSpeed(Ship,'slow',1)
      
    elif ( any(item in EnemyToFollow for item in ItemsOnRight)):
   
      #We are looking at the playfield to find the UFO or Bombership's direction
      #Look at top of screen
      if (gv.Playfield[0][h+1].name in EnemyToFollow):
        Ship.direction = gv.Playfield[0][h+1].direction

      #Look at middle of screen (according to scan area)
      elif (gv.Playfield[gv.HatHeight-1][h+1].name in EnemyToFollow):
        Ship.direction = gv.Playfield[gv.HatHeight-1][h+1].direction

      #print ("MPS - ENEMY TO RIGHT Enemy.name HV direction",Playfield[0][h+1].name,Playfield[0][h+1].h,Playfield[0][h+1].v, Playfield[0][h+1].direction)
      if (gv.Playfield[0][h+1].direction == 2 or
          gv.Playfield[gv.HatHeight-1][h+1].direction == 2):
        #print ("MPS - adjusting speed fast 3")
        AdjustSpeed(Ship,'fast',4)
      elif (gv.Playfield[0][h+1].direction == 4 or
            gv.Playfield[gv.HatHeight-1][h+1].direction == 4):
        #print ("MPS - adjusting speed slow 1")
        AdjustSpeed(Ship,'slow',1)

    #point towards asteroids
    else:
      m,r = divmod(moves,gv.PlanetSurfaceSleep)  
      if (r == 0):
        PointTowardsNearestAsteroid(Ship,Asteroids)

      
  #print("MPS - 1Ship.direction: ",Ship.direction)
    
  
  #if heading to boundary or wall Reverse direction
  #print("checking border")
  if ((Ship.direction == 4 and ItemList[1] == 'border') or
      (Ship.direction == 2 and ItemList[5] == 'border')):
    Ship.direction = cf.ReverseDirection(Ship.direction)
    #print ("MPS - border detected, reversing direction")
    AdjustSpeed(Ship,'slow',1)
    #print("MPS - 2Ship.direction: ",Ship.direction)
  
  #Evade close objects
  # - if object in path of travel, reverse direction
  elif ((Ship.direction == 4 and (ItemList[1] != 'EmptyObject' or ItemList[2] != 'EmptyObject')) or
        (Ship.direction == 2 and (ItemList[5] != 'EmptyObject' or ItemList[4] != 'EmptyObject'))):      
    Ship.direction = cf.ReverseDirection(Ship.direction)
    #print("MPS - object in path, reversed direction")
    #print("MPS - 3Ship.direction: ",Ship.direction)
    

  # - speed up and move if object is directly above
  elif ((Ship.direction == 4 and (ItemList[3] != 'EmptyObject' and ItemList[1] == 'EmptyObject')) or
        (Ship.direction == 2 and (ItemList[3] != 'EmptyObject' and ItemList[5] == 'EmptyObject'))):
    AdjustSpeed(Ship,'fast',8)
    Ship.h, Ship.v =  cf.CalculateDotMovement(Ship.h,Ship.v,Ship.direction)
    #print("MPS - speeding up to avoid collision")
    #print("MPS - 4Ship.direction: ",Ship.direction)

  # - travelling left, move if empty
  # - travelling right, move if empty
  # - randomly switch directions
  elif ((ItemList[1] == 'EmptyObject' and Ship.direction == 4) or 
        (ItemList[5] == 'EmptyObject' and Ship.direction == 2 )):
    if ((random.randint(0,gv.HatWidth-1) <= 2) and Ship.h != 0 and Ship.h != gv.HatWidth-1):
      Ship.direction = cf.ReverseDirection(Ship.direction)
    Ship.h, Ship.v =  cf.CalculateDotMovement(Ship.h,Ship.v,Ship.direction)
    #print("MPS - Travelling, move if empty")
    #print("MPS - 5Ship.direction: ",Ship.direction)


  #if nothing nearby, and near the middle, stop moving
  if (all('EmptyObject' == Item for Item in ItemList)
      and Ship.h >= 6 and Ship.h <= 11):
    if (random.randint (0,2) == 1):
      #print ("MPS - Staying in the middle")
      Ship.h = h
      Ship.v = v
    
  #print("MPS - 6Ship.direction: ",Ship.direction)

  #print("MPS - OldHV: ",h,v, " NewHV: ",Ship.h,Ship.v, "direction: ",Ship.direction)
  if (Ship.h >= gv.SpaceDotMaxH):
    Ship.h = gv.SpaceDotMaxH
  if (Ship.v >= gv.SpaceDotMaxV):
    Ship.v = gv.SpaceDotMaxV
  gv.Playfield[Ship.v][Ship.h]= Ship
  Ship.Display()
  
  if ((h != Ship.h or v != Ship.v) or
     (Ship.alive == 0)):
    gv.Playfield[v][h] = Empty
    cf.setpixel(h,v,0,0,0)
    #print ("MPS - Erasing Player")
  #unicorn.show()

  #print ("Ship hv direction speed:",Ship.h,Ship.v,Ship.direction,Ship.speed)

  return 

  
def MoveEnemyShip(Ship):
  #print ("MES - moveship Direction HV:",Ship.name,Ship.direction,Ship.h,Ship.v)
  
  #Player ships always points up, enemy ships point down
  h = Ship.h
  v = Ship.v
  ItemList = []
  #Scan all around, make decision, move
  ItemList = ScanShip(Ship.h,Ship.v,Ship.scandirection)
  #print("MES - ItemList: ",ItemList)    
  #get possible items, then prioritize

  #Priority
  # 1 Shoot Player
  

  #If player is detected, fire missile!
  if ("Player1" in ItemList):
    if (UFOMissile1.alive == 0 and UFOMissile1.exploding == 0):
      UFOMissile1.h = h
      UFOMissile1.v = v
      UFOMissile1.alive = 1
    elif (UFOMissile2.alive == 0 and UFOMissile2.exploding == 0):
      UFOMissile2.h = h
      UFOMissile2.v = v
      UFOMissile2.alive = 1
    elif (UFOMissile3.alive == 0 and UFOMissile3.exploding == 0):
      UFOMissile3.h = h
      UFOMissile3.v = v
      UFOMissile3.alive = 1
    

  
  #UFO goes from one side to the other
  #print("checking border")
  if ((Ship.direction == 2 and ItemList[1] == 'border') or
      (Ship.direction == 4 and ItemList[5] == 'border')):
    #Ship.alive = 0
    Ship.v = Ship.v + 1
    if (Ship.v > gv.SpaceDotMaxV-3):
      Ship.v = gv.SpaceDotMaxV-3
    Ship.direction = cf.ReverseDirection(Ship.direction)
    Ship.h, Ship.v =  cf.CalculateDotMovement(Ship.h,Ship.v,Ship.direction)
    if (Ship.h == gv.SpaceDotMaxH-2):
      Ship.h = gv.SpaceDotMaxH-1
    elif (Ship.h == 1):
      Ship.h == 0
    
    #print ("MES - hit border, died")
  

  # - travelling left, move if empty
  # - travelling right, move if empty
  elif ((ItemList[5] == 'EmptyObject' and Ship.direction == 4) or 
        (ItemList[1] == 'EmptyObject' and Ship.direction == 2 )):
    Ship.h, Ship.v =  cf.CalculateDotMovement(Ship.h,Ship.v,Ship.direction)
    #print("MES - Travelling, move if empty")
      
      
  #print("OldHV: ",h,v, " NewHV: ",Ship.h,Ship.v)
  gv.Playfield[Ship.v][Ship.h]= Ship
  Ship.Display()
  
  if ((h != Ship.h or v != Ship.v) or
     (Ship.alive == 0)):
    gv.Playfield[v][h] = Empty
    cf.setpixel(h,v,0,0,0)
    #print ("MES - Erasing UFO")
  #unicorn.show()

  return 
  

#Enemy ship is the UFO
def MoveBomberShip(BomberShip,BomberSprite):
  #print ("MBS - Name Direction HV:",BomberShip.name,Ship.direction,Ship.h,Ship.v)
  
  #Player ships always points up, enemy ships point down
  h = BomberShip.h
  v = BomberShip.v
  ItemList = []
  #Scan all around, make decision, move
  ItemList = ScanBomberShip(BomberShip)
  
  #Priority
  # 1 Shoot Player
  
  #Bomber needs to be allowed to go off the screen
  
  
  #Bomber goes from one side to the other
  #print("checking border")
  if ((BomberShip.direction == 2 and ItemList[1] == 'border' and BomberShip.h > gv.SpaceDotMinH+1)):
    BomberShip.v = BomberShip.v + 1
    BomberShip.direction = cf.ReverseDirection(BomberShip.direction)
  elif ((BomberShip.direction == 4 and ItemList[3] == 'border' and BomberShip.h < gv.SpaceDotMaxH-2)):
    BomberShip.v = BomberShip.v + 1
    BomberShip.direction = cf.ReverseDirection(BomberShip.direction)

  BomberShip.h, BomberShip.v =  cf.CalculateDotMovement(BomberShip.h,BomberShip.v,BomberShip.direction)
  
  # - travelling left, move if empty
  # - travelling right, move if empty
  if ((ItemList[3] == 'EmptyObject' and BomberShip.direction == 4) or 
     (ItemList[1] == 'EmptyObject' and BomberShip.direction == 2 )):
    BomberShip.h, BomberShip.v =  cf.CalculateDotMovement(BomberShip.h,BomberShip.v,BomberShip.direction)
    #print("MES - Travelling, move if empty")

  return 


def MoveHomingMissile(HomingMissileShip,HomingMissileSprite,PlayerShip):
  #Scan all around, make decision, move
  distance = 0
  ItemList = []
  h        = HomingMissileShip.h
  v        = HomingMissileShip.v
  OldH     = HomingMissileShip.h
  OldV     = HomingMissileShip.v
  HomingMissileShip.direction = cf.PointTowardsObject8Way(h,v,PlayerShip.h,PlayerShip.v)
  ItemList = ScanAroundShip(h,v,HomingMissileShip.direction)
  
  


  # - travelling left, move if empty
  # - travelling right, move if empty

  #print(ItemList)
  #only move if a spot is empty
  if (ItemList[1] == 'EmptyObject' or ItemList[1] == 'HomingMissile'):
    #print("spot empty, moving homingmissile")

    #Calculate new position
    h, v = cf.CalculateDotMovement8Way(h,v,HomingMissileShip.direction)

    #we want to slow down the vertical descent
    if (random.randint(1,gv.HomingMissileDescentChance) == gv.HomingMissileDescentChance):
      HomingMissileShip.h = h
      HomingMissileShip.v = OldV
    else:
      HomingMissileShip.h = h  
      HomingMissileShip.v = v

    #don't go down too far
    if HomingMissileShip.v > gv.SpaceDotMaxV -1:
      HomingMissileShip.v = HomingMissileShip.v -1

  #print (ItemList)
  distance = cf.GetDistanceBetweenDots(HomingMissileShip.h,HomingMissileShip.v,PlayerShip.h,PlayerShip.v)
  #print("Player 1 detected distance: ",distance)
  if(distance <= 4):
    HitPlayerShip(PlayerShip)  
    HomingMissileShip.exploding = 1
    #HomingMissileShip.alive     = 0
    #PlayerShip.Alive            = 0
    PlayerShip.Exploding        = 1

  HomingMissileSprite.h = HomingMissileShip.h
  HomingMissileSprite.v = HomingMissileShip.v

  return 
  

  
  

def MoveMissile(Missile):
  #player and UFO shots, even asteroids are treated as "missiles"
  #they move in a straight line and blow up when they hit something
  global Empty
  
  
  #Record the current coordinates
  h = Missile.h
  v = Missile.v

  
  RegularTargets = ['Player1','UFO','UFOMissile','Asteroid','Wall','BomberRock']
  
  #Missiles simply drop to bottom and kablamo!
  #FF (one square in front of missile direction of travel)
  ScanH, ScanV = cf.CalculateDotMovement(h,v,Missile.scandirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  
  

  #Priority
  # 1 Hit target
  # 2 See if we are hit by enemy missle
  # 3 Move forward




  if(ScanV == gv.GroundV):
    print ('missile at ground.  name:',Missile.name,' item:',Item,ScanH,ScanV)
    #cf.FlashDot(ScanH,ScanV,0.05)
  
  #BomberShip is special
  if (Item == 'BomberShip' and Missile.name != 'BomberRock'):
    #print ("MM - Playfield - BEFORE Bomberhit",Playfield[ScanV][ScanH].name)
    HitBomber(gv.Playfield[ScanV][ScanH])  
    #print ("MM - Playfield - AFTER Bomberhit",Playfield[ScanV][ScanH].name)
    Missile.h = ScanH
    Missile.v = ScanV
    #Playfield[Missile.h][Missile.v] = Missile
    Missile.Display()
    Missile.exploding = 1
    Missile.alive = 0
    

  #HomingMissile is special
  elif (Item == 'HomingMissile' and Missile.name != 'Asteroid'):
    HitHomingMissile(gv.Playfield[ScanV][ScanH],HomingMissileSprite)  
    Missile.h = ScanH
    Missile.v = ScanV
    Missile.Display()
    Missile.exploding = 1
    Missile.alive = 0



  #Playership is special
  elif (Item == 'Player1'):
    HitPlayerShip(gv.Playfield[ScanV][ScanH])  
    Missile.h = ScanH
    Missile.v = ScanV
    Missile.Display()
    Missile.exploding = 1
    Missile.alive = 0


  elif(Item == 'Asteroid' and Missile.name != 'Asteroid'):
    print('Adding points:',gv.SpaceDotScore,gv.AsteroidPoints)
    gv.SpaceDotScore = gv.SpaceDotScore + gv.AsteroidPoints


  #Ground is special too.  See the pattern yet?
  if (Item == 'Ground'):
    #print ("item is the ground")
    HitGround(gv.Playfield[ScanV][ScanH])  
    Missile.h = -1
    Missile.v = -1
    Missile.exploding = 1
    #Missile.alive = 0
    if(Missile.name == 'Asteroid' or Missile.name == 'UFOMissile'):
      Missile.Explosion.h = ScanH
      Missile.Explosion.v = ScanV
    else:
      #center the big explosion
      Missile.Explosion.h = ScanH - (Missile.Explosion.width / 2) + 1
      Missile.Explosion.v = ScanV - 2

    gv.Playfield[v][h] = gv.EmptyObject
    #Missile.Display()
    Missile.Explosion.DisplayAnimated()
    cf.setpixel(h,v,0,0,0)
    return

  #See if other target ship is hit
  #try not to let asteroids blow each other up
  elif (Item  in RegularTargets and Missile.name != gv.Playfield[ScanV][ScanH].name):
    #target hit, kill target

    gv.Playfield[ScanV][ScanH].alive = 0
    gv.Playfield[ScanV][ScanH].lives = gv.Playfield[ScanV][ScanH].lives -1
    gv.Playfield[ScanV][ScanH]= Empty
    cf.setpixel(ScanH,ScanV,0,0,0)
    cf.setpixel(h,v,0,0,0)

    Missile.h = ScanH
    Missile.v = ScanV
    #Playfield[Missile.h][Missile.v] = Missile
    Missile.Display()
    Missile.exploding = 1
    Missile.alive = 0
    Missile.lives = Missile.lives - 1
  
#  elif (Item  == 'PlayerMissile'):
#    #We are hit
#    Missile.Alive = 0
#    Missile.exploding = 1
#    Playfield[ScanV][ScanH].alive = 0
#    Playfield[ScanV][ScanH]= Empty
#    Missile.Erase()
#    print ("MM - We have been  hit!")
  
  #Player missiles fire off into space
  #Enemy missiles explode on ground
  
  elif (Item == 'aboveborder' and Missile.name == 'Asteroid'):
    #print ("asteroid above border")
    Missile.h = ScanH
    Missile.v = ScanV
    gv.Playfield[Missile.v][Missile.h] = Missile
    

  elif (Item == 'aboveborder' and Missile.name == 'PlayerMissile'):
    #print ("MM - Missile hit border")
    Missile.alive  = 0
    Missile.lives  = Missile.lives - 1
    Missile.exploding = 0
    Missile.Erase()
  elif (Item == 'border' and (Missile.name == 'UFOMissile' or Missile.name == 'Asteroid' or Missile.name == 'BomberRock')
                         and not(Missile.name == 'Asteroid' and Missile.v <= 0)):


    #print ("MM - Missile hit border")
    Missile.alive = 0
    Missile.lives = Missile.lives - 1
    Missile.exploding = 1
    Missile.Erase()
    #print ("MM - UFO hit border HV:",Missile.h,Missile.v)
    
  #empty = move forward
  elif (Item == 'EmptyObject' and Missile.alive == 1):
    Missile.h = ScanH
    Missile.v = ScanV
    gv.Playfield[Missile.v][Missile.h] = Missile
    Missile.Display()
    #print ("MM - empty, moving forward")
    


  if ((h != Missile.h or v != Missile.v) or (Missile.alive == 0)):
    
    if (gv.Playfield[v][h].name != 'Ground'):
      gv.Playfield[v][h] = Empty
      cf.setpixel(h,v,0,0,0)
  
  return 










def RedrawGround(TheGround):
  GroundCount = 0
  for i in range (gv.SpaceDotMinH,gv.SpaceDotMaxH):
    gv.Playfield[gv.GroundV][i] = TheGround[GroundCount]
    gv.Playfield[gv.GroundV][i].Display()
    GroundCount = GroundCount + 1
  return








  
def PlaySpaceDot():
  
  
  cf.ClearBigLED()
  gv.SpaceDotScore = 0
  
  #Local variables
  moves       = 0
  Finished    = 'N'
  LevelCount  = 3
  Playerh     = 0
  Playerv     = 0
  SleepTime   = gv.MainSleep / 4
  ChanceOfUFO = 200
  

  #Timers / Clock display
  ClockSprite = cf.CreateClockSprite(12)
  #lockH        = gv.HatWidth  // 2 - (ClockSprite.width // 2)
  #lockV        = gv.HatHeight // 2 - (ClockSprite.height // 2)
  start_time    = time.time()
  DayOfWeekSprite     = cf.CreateDayOfWeekSprite()
  MonthSprite         = cf.CreateMonthSprite()
  DayOfMonthSprite    = cf.CreateDayOfMonthSprite()
  CurrencySprite      = CreateCurrencySprite()

  



  #define objects
  #def __init__(self,h,v,r,g,b,direction,scandirection,speed,alive,lifes,name,score,exploding):
  PlayerShip = cf.Ship(3 + gv.SpaceDotMinH,gv.SpaceDotMaxV - 2,PlayerShipR,PlayerShipG,PlayerShipB,4,1,gv.PlayerShipSpeed,1,3,'Player1', 0,0)
  PlayerShip.lives = gv.PlayerShipLives
  

  EnemyShip  = cf.Ship(gv.SpaceDotMinH,0,cf.SDMedPurpleR,cf.SDMedPurpleG,cf.SDMedPurpleB,4,3,gv.UFOShipSpeed,0,3,'UFO', 0,0)
  Empty      = cf.Ship(-1,-1,0,0,0,0,1,0,0,0,'EmptyObject',0,0)
   
  BomberShip.h = -2 + gv.SpaceDotMinH
  BomberShip.v =  gv.SpaceDotMinV
  BomberShip.alive = 0
  #HomingMissileShip.h =  gv.SpaceDotMinH + (int(gv.SpaceDotMinH / 2))
  #HomingMissileShip.v =  gv.SpaceDotMinV
  
  HomingMissileShip    = cf.Ship(gv.SpaceDotMinH,gv.SpaceDotMaxV - 1,PlayerShipR,PlayerShipG,PlayerShipB,4,1,8,1,3,'HomingMissile', 0,0)
  HomingMissileSprite  = HomingMissileSpriteList[random.randint(0,gv.HomingMissileSprites -1 )]

  #Explosion Sprites
  PlayerShip.Explosion = copy.deepcopy(PlayerShipExplosion)  
  BomberShip.Explosion = copy.deepcopy(BomberShipExplosion)  

  BomberShip.Explosion.framerate = 10
  BomberRock.Explosion           = copy.deepcopy(PlayerShipExplosion)  
  BomberRock.Explosion.framerate = 2
  BomberRock.Explosion.h         = -1
  BomberRock.Explosion.v         = -1

  #HomingMissileShipExplosion    = copy.deepcopy(PlayerShipExplosion)  
  HomingMissileShipExplosion    = copy.deepcopy(BigShipExplosion)  

  cf.CenterSpriteOnShip(HomingMissileShipExplosion,HomingMissileShip)
  #HomingMissileShipExplosion.h  = -1
  #HomingMissileShipExplosion.v  = -1
  HomingOldH = -1
  HomingOldV = -1
  #PlayerMissile1Explosion = copy.deepcopy(SmallExplosion)
  #PlayerMissile2Explosion = copy.deepcopy(SmallExplosion)




  #Tracking moves between waves
  MovesSinceWaveStop  = 0
  WaveAlive           = 1
  AsteroidsAlive      = 0

  #Make wave of asteroids
  Wave = cf.AsteroidWave(gv.AsteroidsInWaveMin)
  







  #Reset Playfield
  for x in range (0,gv.HatWidth):
    for y in range (0,gv.HatHeight):
      #print ("XY",x,y)
      gv.Playfield[y][x] = Empty
               
  gv.Playfield[PlayerShip.v][PlayerShip.h] = PlayerShip




  #Title
  #cf.ShowScrollingBanner2("SpaceDot",(cf.MedOrange),gv.ScrollSleep)

  #Animation Sequence
  #ShowBigShipTime(gv.ScrollSleep)  

  gv.TheMatrix.Clear()
  cf.ClearBuffers()
  




  #Title
  gv.TheMatrix.Clear()
  cf.ClearBuffers()


  #Draw the Big text
  #Clear only the LED matrix
  #Draw the next size down
  #When at the final zoom level
  #  - clear the LED Matrix
  #  - clear all buffers (canvas and ScreenArray[V][H])
  #  - draw the text at desired last zoom level
  #  - draw the rest of the text, at this point it is all written to ArrayBuffer
  #  - clear the LED Matrix
  #  - clear all buffers (canvas and ScreenArray[V][H])
  #Call the ZoomScreen function to redraw the display using ScreenArray[V][H] which at this point
  #contains the values last written to the screen.


  cf.ShowGlowingText(CenterHoriz = True,h = -8,v = 0,   Text = 'ASTRO', RGB = cf.MedGreen,  ShadowRGB = cf.ShadowGreen, ZoomFactor = 8,GlowLevels=0,DropShadow=False)
  gv.TheMatrix.Clear()
  cf.ShowGlowingText(CenterHoriz = True,h = -8,v = 0,   Text = 'ASTRO', RGB = cf.MedGreen, ShadowRGB = cf.ShadowGreen, ZoomFactor = 7,GlowLevels=0,DropShadow=False)
  gv.TheMatrix.Clear()
  cf.ShowGlowingText(CenterHoriz = True,h = -8,v = 0,   Text = 'ASTRO', RGB = cf.MedGreen, ShadowRGB = cf.ShadowGreen, ZoomFactor = 6,GlowLevels=0,DropShadow=False)
  gv.TheMatrix.Clear()
  cf.ShowGlowingText(CenterHoriz = True,h = -8,v = 0,   Text = 'ASTRO', RGB = cf.MedGreen, ShadowRGB = cf.ShadowGreen, ZoomFactor = 5,GlowLevels=0,DropShadow=False)
  gv.TheMatrix.Clear()
  cf.ShowGlowingText(CenterHoriz = True,h = -8,v = 0,   Text = 'ASTRO', RGB = cf.MedGreen, ShadowRGB = cf.ShadowGreen, ZoomFactor = 4,GlowLevels=0,DropShadow=False)
  gv.TheMatrix.Clear()
  cf.ShowGlowingText(CenterHoriz = True,h = -8,v = 0,   Text = 'ASTRO', RGB = cf.MedGreen, ShadowRGB = cf.ShadowGreen, ZoomFactor = 3,GlowLevels=0,DropShadow=False)

  gv.TheMatrix.Clear()
  cf.ClearBuffers()
  cf.ShowGlowingText(CenterHoriz = True,h = -8,v = 0,   Text = 'ASTRO',      RGB = cf.HighGreen,  ShadowRGB = cf.ShadowGreen,  ZoomFactor = 2,GlowLevels=200,DropShadow=False)
  cf.ShowGlowingText(CenterHoriz = True,h = 0 ,v = 12,  Text = 'SMASH!',     RGB = (255,0,0),     ShadowRGB = cf.ShadowRed,    ZoomFactor = 2,GlowLevels=50,DropShadow=True)
  cf.ShowGlowingText(CenterHoriz = True,h = 0 ,v = 26,  Text = 'BY DATAGOD', RGB = cf.HighBlue,   ShadowRGB = cf.ShadowBlue,   ZoomFactor = 1,GlowLevels=200,DropShadow=True)
  time.sleep(1)
  gv.TheMatrix.Clear()
  gv.Canvas.Clear()
  cf.ZoomScreen(gv.ScreenArray,32,128,0)
  cf.ZoomScreen(gv.ScreenArray,128,1,0,Fade=True)
  



  #Show clock
  CheckClockTimer(ClockSprite)
  cf.CopySpriteToPixelsZoom(ClockSprite,      gv.ClockH,      gv.ClockV,      gv.ClockRGB,       gv.SpriteFillerRGB,1)
  cf.CopySpriteToPixelsZoom(DayOfWeekSprite,  gv.DayOfWeekH,  gv.DayOfWeekV,  gv.DayOfWeekRGB,   gv.SpriteFillerRGB,1)
  cf.CopySpriteToPixelsZoom(MonthSprite,      gv.MonthH,      gv.MonthV,      gv.MonthRGB,       gv.SpriteFillerRGB,1)
  cf.CopySpriteToPixelsZoom(DayOfMonthSprite, gv.DayOfMonthH, gv.DayOfMonthV, gv.DayOfMonthRGB,  gv.SpriteFillerRGB,1)
  cf.CopySpriteToPixelsZoom(CurrencySprite,   gv.CurrencyH,   gv.CurrencyV,   gv.CurrencyRGB,    gv.SpriteFillerRGB,1)



  
  

  while (LevelCount > 0):
    #print ("show playership")
    
    #print ("Show level")

    #cf.ShowLevelCount(LevelCount)
    LevelCount = LevelCount - 1
    
    
    #Reset Variables between rounds
    LevelFinished        = 'N'
    moves                = 1
    PlayerShip.alive     = 1
    PlayerShip.exploding = 0
    PlayerShip.speed     = gv.PlayerShipSpeed
    PlayerShip.h         = random.randint (gv.SpaceDotMinH,gv.SpaceDotMaxH)
    PlayerShip.Explosion.alive = 0

    if (random.randint(0,2) == 1):
      PlayerShip.direction = 2
    else:
      PlayerShip.direction = 4
    EnemyShip.alive   = 0
    UFOMissile1.alive = 0
    UFOMissile2.alive = 0
    UFOMissile3.alive = 0
    UFOMissile1.h     = -1
    UFOMissile2.v     = -1
    UFOMissile2.h     = -1
    UFOMissile2.v     = -1
    UFOMissile3.h     = -1
    UFOMissile3.v     = -1


    EnemyShip.speed   = random.randint (gv.UFOShipMinSpeed,gv.UFOShipMaxSpeed)
    
    #Reset colors
    UFOMissile1.r = PlayerMissileR
    UFOMissile1.g = PlayerMissileG
    UFOMissile1.b = PlayerMissileB
    UFOMissile2.r = PlayerMissileR
    UFOMissile2.g = PlayerMissileG
    UFOMissile2.b = PlayerMissileB
    UFOMissile3.r = PlayerMissileR
    UFOMissile3.g = PlayerMissileG
    UFOMissile3.b = PlayerMissileB
    BomberShip.alive = 0
    BomberShip.lives = 3
    HomingMissileShip.alive = 0
    HomingMissileShip.lives = gv.HomingMissileLives
    

    #Make a wave of asteroids
    
    Wave = cf.AsteroidWave(gv.AsteroidsInWaveMin)
    Wave.CreateAsteroidWave()
    cf.DisplayLevel(Wave.WaveCount,cf.MedBlue)
    

    
    #Reset Playfield
    for x in range (0,gv.HatWidth):
      for y in range (0,gv.HatHeight):
        #print ("XY",x,y)
        gv.Playfield[y][x] = Empty
                 
    gv.Playfield[PlayerShip.v][PlayerShip.h] = PlayerShip

    #Create the ground
    color = random.randint(1,7) * 4 + 1
    r,g,b = cf.ColorList[color]    
    TheGround   = []    
    GroundCount = 0
    for i in range (gv.SpaceDotMinH,gv.SpaceDotMaxH):
      TheGround.append(cf.Ship(i,gv.GroundV,r,g,b,0,0,0,1,gv.SpaceDotGroundLives,'Ground', 0,0))
      gv.Playfield[gv.GroundV][i] = TheGround[GroundCount]
      gv.Playfield[gv.GroundV][i].Display()
      cf.FlashDot2(i,gv.GroundV,0.04)
      #print("Ground:",i,gv.GroundV)
      GroundCount = GroundCount + 1





    
    # Main timing loop
    while (LevelFinished == 'N' and PlayerShip.alive == 1):
      moves = moves + 1

      
      #Draw bottom background
      m,r = divmod(moves,gv.PlanetSurfaceSleep)  
      if (r == 0):
        RedrawGround(TheGround)

      #Cleanup debris (leftover pixels from explosions)
      m,r = divmod(moves,gv.DebrisCleanupSleep)
      if (r == 0):
        cf.CleanupDebris(gv.SpaceDotMinH,gv.SpaceDotMaxH,gv.SpaceDotMinV,gv.SpaceDotMaxV,gv.Playfield)

     

      #Check for keyboard input
      m,r = divmod(moves,KeyboardSpeed)
      if (r == 0):
        Key = cf.PollKeyboard()
        ProcessKeypress(Key)
        if (Key == 'Q' or Key == 'q'):
          LevelCount = 0
          return
        elif (Key == 'd'):
          cf.DebugPlayfield(gv.Playfield,gv.HatWidth,gv.HatHeight)
          for i in range (0,gv.PlayerMissiles):
            print("Name HV Alive Exploding Speed:",PlayerMissiles[i].name,PlayerMissiles[i].h,PlayerMissiles[i].v,PlayerMissiles[i].alive,PlayerMissiles[i].exploding,PlayerMissiles[i].speed)
          time.sleep(2)

        elif (Key == 'n'):
          gv.Playfield            = HomingMissileSprite.EraseSpriteFromPlayfield(gv.Playfield)
          HomingMissileShip.h     = 32
          HomingMissileShip.v     = 0
          HomingMissileShip.lives = 10
          HomingMissileShip.alive = 1
          HomingMissileSprite.v   = 0
          HomingMissileSprite     = HomingMissileSpriteList[random.randint(0,gv.HomingMissileSprites -1 )]

      
#      print ("=================================================")
#      for H in range(0,gv.HatWidth-1):
#        for V in range (0,gv.HatWidth-1):
#          if (Playfield[v][h].name != 'EmptyObject'):
#            print ("Playfield: HV Name",H,V,Playfield[v][h].name)
#      print ("=================================================")
      


      m,r = divmod(moves,CheckClockSpeed)
      if (r == 0):  
        #CheckClockTimer(ClockSprite)
        TheTime = cf.CreateClockSprite(12)

        #Show Custom sprites
        cf.CopySpriteToPixelsZoom(ClockSprite,      gv.ClockH,      gv.ClockV,      gv.ClockRGB,       gv.SpriteFillerRGB,1)
        cf.CopySpriteToPixelsZoom(DayOfWeekSprite,  gv.DayOfWeekH,  gv.DayOfWeekV,  gv.DayOfWeekRGB,   gv.SpriteFillerRGB,1)
        cf.CopySpriteToPixelsZoom(MonthSprite,      gv.MonthH,      gv.MonthV,      gv.MonthRGB,       gv.SpriteFillerRGB,1)
        cf.CopySpriteToPixelsZoom(DayOfMonthSprite, gv.DayOfMonthH, gv.DayOfMonthV, gv.DayOfMonthRGB,  gv.SpriteFillerRGB,1)
 
  
      m,r = divmod(moves,gv.CheckCurrencySpeed)
      if (r == 0):  
        CurrencySprite = CreateCurrencySprite()
      m,r = divmod(moves,gv.DisplayCurrencySpeed)
      if (r == 0):  
        cf.CopySpriteToPixelsZoom(CurrencySprite,   gv.CurrencyH,   gv.CurrencyV,   gv.CurrencyRGB,    gv.SpriteFillerRGB,1)





      
      if (PlayerShip.alive == 1):
        #print ("M - Playership HV speed alive exploding direction: ",PlayerShip.h, PlayerShip.v,PlayerShip.speed, PlayerShip.alive, PlayerShip.exploding, PlayerShip.direction)
        #print ("M - moves: ", moves)        
        m,r = divmod(moves,PlayerShip.speed)
        if (r == 0):
          MovePlayerShip(PlayerShip,HomingMissileShip,Wave.Asteroids)
          i = random.randint(0,2)
          if (i >= 0):
            AdjustSpeed(PlayerShip,'fast',1)
            
      
      if (EnemyShip.alive == 1):
        m,r = divmod(moves,EnemyShip.speed)
        if (r == 0):
          MoveEnemyShip(EnemyShip)
          


      #print ("M - Bombership Alive Lives HV:",BomberShip.alive, BomberShip.lives,BomberShip.h,BomberShip.v)
      if (BomberShip.alive == 1):
        m,r = divmod(moves,BomberShip.speed)
        if (r == 0):
          if (BomberShip.v == gv.SpaceDotMaxV):
            BomberShip.v = 0
          BomberOldH = BomberShip.h
          BomberOldV = BomberShip.v
          MoveBomberShip(BomberShip,BomberSprite)
          gv.Playfield = BomberSprite.EraseSpriteFromPlayfield(gv.Playfield)
          gv.Playfield = BomberSprite.CopyAnimatedSpriteToPlayfield(gv.Playfield,BomberShip)

          
        cf.CenterSpriteOnShip(BomberSprite,BomberShip) 
        BomberSprite.DisplayAnimated()





          
      #print ("M - Homingship Alive Lives HV:",HomingShip.alive, HomingShip.lives,HomingShip.h,HomingShip.v)
      if (HomingMissileShip.alive == 1):
        m,r = divmod(moves,HomingMissileShip.speed)
        if (r == 0):
            
          #cf.CenterSpriteOnShip(HomingMissileSprite,HomingMissileShip)
          #HomingOldH = HomingMissileShip.h
          #HomingOldV = HomingMissileShip.v

          #Need to erase old position, and draw new position to playfield
          #HomingMissileSprite.h = HomingOldH
          #HomingMissileSprite.v = HomingOldV
        
          gv.Playfield = HomingMissileSprite.EraseSpriteFromPlayfield(gv.Playfield)
          MoveHomingMissile(HomingMissileShip,HomingMissileSprite,PlayerShip)
          cf.CenterSpriteOnShip(HomingMissileSprite,HomingMissileShip)
          gv.Playfield = HomingMissileSprite.CopyAnimatedSpriteToPlayfield(gv.Playfield,HomingMissileShip)
          
          

        #even if we don't move, we still animate the sprite
        if(HomingMissileShip.alive == 1):
          HomingMissileSprite.DisplayAnimated(HomingMissileSprite.h,HomingMissileSprite.v)
        

          
      if (UFOMissile1.alive == 1 and UFOMissile1.exploding == 0):
        m,r = divmod(moves,UFOMissile1.speed)
        if (r == 0):
          MoveMissile(UFOMissile1)

      if (UFOMissile2.alive == 1 and UFOMissile2.exploding == 0):
        m,r = divmod(moves,UFOMissile2.speed)
        if (r == 0):
          MoveMissile(UFOMissile2)

      if (UFOMissile3.alive == 1 and UFOMissile3.exploding == 0):
        m,r = divmod(moves,UFOMissile3.speed)
        if (r == 0):
          MoveMissile(UFOMissile3)

          

      #Check all player missiles
      for i in range (0,gv.PlayerMissiles):
        #print ("Checking player missile:",i)

        #check for buggy missiles that have gone out of range
        #this check should be removed once we determine why someitmes missile.h = 24
        if(PlayerMissiles[i].h < gv.SpaceDotMinH and PlayerMissiles[i].h >= 0):
          PlayerMissiles[i].alive = 0
          PlayerMissiles[i].exploding = 0

        if (PlayerMissiles[i].alive == 1 and PlayerMissiles[i].exploding == 0):
          m,r = divmod(moves,PlayerMissiles[i].speed)
          if (r == 0):
            MoveMissile(PlayerMissiles[i])
        if (PlayerMissiles[i].v <= -1):
          PlayerMissiles[i].alive = 0
          PlayerMissiles[i].exploding = 0
         
      



      #Spawn asteroids or move asteroids (asteroids are treated as missiles)
      if (Wave.Alive  == True):
        #print("moves:",moves,end='\r', flush=True)
        m,r = divmod(moves,gv.WaveDropSpeed)
        if (r == 0):
          Wave.UpdateCounts()
          Wave.DropAsteroids((random.randint(gv.AsteroidsToDropMin,gv.AsteroidsToDropMax)),gv.Playfield)

          
        #Move asteroids that are alive
        for i in range (0,Wave.AsteroidCount): 

          #if asteroid is alive move it
          if (Wave.Asteroids[i].alive == 1):
            #print ("Asteroid alive moves speed hv:",moves,Wave.Asteroids[i].speed, Wave.Asteroids[i].h,Wave.Asteroids[i].v)

            m,r = divmod(moves,Wave.Asteroids[i].speed)
            if (r == 0):
              #print("Moving alive asteroid:",Wave.Asteroids[i].h,Wave.Asteroids[i].v)
              MoveMissile(Wave.Asteroids[i])
              Wave.Asteroids[i].Display()


            
        

        

        
            
          

      #Spawn enemy ship UFO
      m,r = divmod(moves,ChanceOfUFO)
      if (r == 0 and EnemyShip.alive == 0):
        #print ("Spawning UFO")
        EnemyShip.alive = 1
        EnemyShip.direction = cf.ReverseDirection(EnemyShip.direction)
        if (EnemyShip.direction == 2):
          EnemyShip.h = gv.SpaceDotMinH
          EnemyShip.v = gv.SpaceDotMinV
          #EnemyShip.v = random.randint(0,4)
        else:
          EnemyShip.h = gv.SpaceDotMaxH
          EnemyShip.v = gv.SpaceDotMinV
        EnemyShip.Display()


        

      #Spawn BomberShip
      if (Wave.WaveCount >= gv.MinBomberWave):

        m,r = divmod(moves,gv.ChanceOfBomberShip)
        if (r == 0 and BomberShip.alive == 0):
          #print ("Spawning BomberShip")
          BomberShip.alive = 1
          BomberShip.lives = 3 #(takes 3 hits to die)
          BomberShip.direction = cf.ReverseDirection(BomberShip.direction)
          if (BomberShip.direction == 2):
            BomberShip.h = gv.SpaceDotMinH-2
            BomberShip.v = gv.SpaceDotMinV
            gv.Playfield[gv.SpaceDotMinV][gv.SpaceDotMinH] = BomberShip
          else:
            BomberShip.h = gv.HatWidth
            BomberShip.v = 0
            gv.Playfield[gv.SpaceDotMinV][gv.SpaceDotMaxH] = BomberShip

        #Bombership drops a red asteroid (#4)
        if (BomberShip.h >= gv.SpaceDotMinH +3 and BomberShip.h <= gv.SpaceDotMaxH -3 and BomberRock.alive == 0 and BomberShip.lives <=2 and BomberShip.alive == 1):
          BomberRock.alive = 1
          BomberRock.speed = gv.BomberRockSpeed
          BomberRock.h     = BomberShip.h 
          BomberRock.v     = BomberShip.v +1
          


        
      #move BomberRock
      if (BomberRock.alive == 1 and BomberRock.exploding == 0):
        m,r = divmod(moves,BomberRock.speed)
        if (r == 0):
          MoveMissile(BomberRock)


      
        
          
      #Spawn Homing missile
      if (Wave.WaveCount >= gv.MinHomingMissileWave):
        m,r = divmod(moves,gv.ChanceOfHomingMissile)
        if (r == 0 and HomingMissileShip.alive == 0):

          HomingMissileSprite   = HomingMissileSpriteList[random.randint(0,gv.HomingMissileSprites -1)]
          HomingMissileShip.alive = 1
          HomingMissileShip.lives = gv.HomingMissileLives
          MissileSpawned = False
          while (MissileSpawned == False):
            h = random.randint(gv.SpaceDotMinH,gv.SpaceDotMaxH)
            v = gv.SpaceDotMinV 
            if (gv.Playfield[v][h].name == 'EmptyObject'):
              HomingMissileShip.h = h
              HomingMissileShip.v = v
              gv.Playfield[v][h] = HomingMissileShip
              HomingMissileShip.speed = gv.HomingMissileInitialSpeed
              MissileSpawned = True
              cf.CenterSpriteOnShip(HomingMissileSprite,HomingMissileShip)
        

      
          
      


     
      #-----------------------------
      # Check for exploding objects
      #-----------------------------

      #player missiles
      for i in range (0,gv.PlayerMissiles):
        if (PlayerMissiles[i].exploding == 1):
          #print("------> PlayerMissile1.exploding: ",PlayerMissile1.exploding)
          PlayerMissiles[i].Explosion.h = PlayerMissiles[i].h
          PlayerMissiles[i].Explosion.v = PlayerMissiles[i].v
          PlayerMissiles[i].Explosion.DisplayAnimated()
          
        #Kill missile after explosion animation is complete
        if (PlayerMissiles[i].Explosion.currentframe >= PlayerMissiles[i].Explosion.frames-1):
          #print ("killing missile")
          PlayerMissiles[i].Explosion.currentframe = 0
          PlayerMissiles[i].Explosion.exploding    = 0
          PlayerMissiles[i].Explosion.alive        = 0
          
          PlayerMissiles[i].exploding = 0
          PlayerMissiles[i].alive = 0
          
        
      #Asteroids
      for i in range(0,Wave.AsteroidCount):
        if (Wave.Asteroids[i].exploding == 1 ):
          if (Wave.Asteroids[i].Explosion.h == -1):
            Wave.Asteroids[i].Explosion.h    = Wave.Asteroids[i].h-1
            Wave.Asteroids[i].Explosion.v    = Wave.Asteroids[i].v-1
          Wave.Asteroids[i].Explosion.DisplayAnimated()
         
        #Kill asteroids after explosion animation is complete 
        #AND replace the ground object on the playfield
        if (Wave.Asteroids[i].Explosion.currentframe >= Wave.Asteroids[i].Explosion.frames-1):

          Wave.Asteroids[i].Explosion.h            = -1
          Wave.Asteroids[i].Explosion.v            = -1
          Wave.Asteroids[i].Explosion.currentframe = 0
          Wave.Asteroids[i].Explosion.exploding    = 0
          Wave.Asteroids[i].Explosion.alive        = 0
          Wave.Asteroids[i].alive = 0
          Wave.Asteroids[i].exploding = 0

          Wave.Asteroids[i].h                      = -1
          Wave.Asteroids[i].v                      = -1
          gv.Playfield[Wave.Asteroids[i].v][Wave.Asteroids[i].h] = TheGround[i]

#handle points somewhere else.


      #BomberRock
      if (BomberRock.exploding == 1 ):

        if (BomberRock.Explosion.h == -1):
          BomberRock.Explosion.h = BomberRock.h -2
          BomberRock.Explosion.v = BomberRock.v -2

        BomberRock.Explosion.DisplayAnimated()

        if (BomberRock.Explosion.currentframe >= BomberRock.Explosion.frames-1):
          BomberRock.Explosion.h            = -1
          BomberRock.Explosion.v            = -1
          BomberRock.Explosion.currentframe = 0
          BomberRock.Explosion.exploding    = 0
          BomberRock.Explosion.alive        = 0
          BomberRock.exploding              = 0
          BomberRock.alive                  = 0
          BomberRock.h                      = -1
          BomberRock.v                      = -1
          RedrawGround(TheGround)
          #compute score
          gv.SpaceDotScore = gv.SpaceDotScore + gv.AsteroidPoints
        


              
      #BomberShip
      if (BomberShip.exploding == 1):
        BomberShip.Explosion.DisplayAnimated()

        #Kill bombership after explosion animation is complete
        if (BomberShip.Explosion.currentframe >= BomberShip.Explosion.frames-1):
          BomberShip.Explosion.currentframe = 0
          BomberShip.Explosion.exploding    = 0
          BomberShip.Explosion.alive        = 0
          BomberShip.exploding              = 0
          BomberShip.alive                  = 0
          RedrawGround(TheGround)
          #compute score
          gv.SpaceDotScore = gv.SpaceDotScore + gv.BomberPoints


      #HomingMissileShip
      if (HomingMissileShip.exploding == 1):
        if (HomingMissileShipExplosion.h == -1):
          cf.CenterSpriteOnShip(HomingMissileShipExplosion,HomingMissileShip)
        HomingMissileShipExplosion.DisplayAnimated()

        #Kill homing missile after explosion animation is complete
        if (HomingMissileShipExplosion.currentframe >= HomingMissileShipExplosion.frames-1):
          HomingMissileShipExplosion.currentframe = 0
          HomingMissileShipExplosion.exploding    = 0
          HomingMissileShipExplosion.alive        = 0
          HomingMissileShip.exploding             = 0
          HomingMissileShip.alive                 = 0
          HomingMissileShipExplosion.h = HomingMissileShip.h
          HomingMissileShipExplosion.v = HomingMissileShip.v
          gv.Playfield = HomingMissileShipExplosion.EraseSpriteFromPlayfield(gv.Playfield)
          gv.Playfield = HomingMissileSprite.EraseSpriteFromPlayfield(gv.Playfield)
          HomingMissileShipExplosion.h = -1 
          HomingMissileShipExplosion.v = -1 
          RedrawGround(TheGround)
          #compute score
          gv.SpaceDotScore = gv.SpaceDotScore + gv.HomingMissilePoints

      #PlayerShip
      if (PlayerShip.exploding == 1):
        PlayerShip.Explosion.h = PlayerShip.h
        PlayerShip.Explosion.v = PlayerShip.v
        PlayerShip.Explosion.DisplayAnimated()

        #Kill PlayerShip after explosion animation is complete
        if (PlayerShip.Explosion.currentframe >= PlayerShipExplosion.frames-1):
          PlayerShip.Explosion.currentframe = 0
          PlayerShip.Explosion.exploding    = 0
          PlayerShip.Explosion.alive        = 0
          PlayerShip.exploding              = 0
          PlayerShip.alive                  = 0
          PlayerShip.Explosion.h            = -1
          PlayerShip.Explosion.v            = -1



      #UFO Missiles need to be optimized into an array like we did with asteroids
      if (UFOMissile1.exploding == 1 ):
        if (UFOMissile1.Explosion.h == -1):
          UFOMissile1.Explosion.h = UFOMissile1.h
          UFOMissile1.Explosion.v = UFOMissile1.v
        UFOMissile1.Explosion.DisplayAnimated()


        #Kill UFOMissile after explosion animation is complete
        if (UFOMissile1.Explosion.currentframe >= UFOMissile1.Explosion.frames-1):
          UFOMissile1.Explosion.currentframe = 0
          UFOMissile1.Explosion.exploding    = 0
          UFOMissile1.Explosion.alive        = 0
          UFOMissile1.exploding              = 0
          UFOMissile1.alive                  = 0
          UFOMissile1.Explosion.h            = -1
          UFOMissile1.Explosion.v            = -1
          RedrawGround(TheGround)
          #compute score
          gv.SpaceDotScore = gv.SpaceDotScore + gv.AsteroidPoints

       



      #UFO Missiles need to be optimized into an array like we did with asteroids
      if (UFOMissile2.exploding == 1 ):
        if (UFOMissile2.Explosion.h == -1):
          UFOMissile2.Explosion.h = UFOMissile2.h
          UFOMissile2.Explosion.v = UFOMissile2.v
        UFOMissile2.Explosion.DisplayAnimated()

        #Kill missile after explosion animation is complete
        if (UFOMissile2.Explosion.currentframe >= UFOMissile2.Explosion.frames-1):
          UFOMissile2.Explosion.currentframe = 0
          UFOMissile2.Explosion.exploding    = 0
          UFOMissile2.Explosion.alive        = 0
          UFOMissile2.exploding              = 0
          UFOMissile2.alive                  = 0
          UFOMissile2.Explosion.h            = -1
          UFOMissile2.Explosion.v            = -1
          RedrawGround(TheGround)
          #compute score
          gv.SpaceDotScore = gv.SpaceDotScore + gv.AsteroidPoints

      #UFO Missiles need to be optimized into an array like we did with asteroids
      if (UFOMissile3.exploding == 1 ):
        if (UFOMissile3.Explosion.h == -1):
          UFOMissile3.Explosion.h = UFOMissile3.h
          UFOMissile3.Explosion.v = UFOMissile3.v
        UFOMissile3.Explosion.DisplayAnimated()

        #Kill missile after explosion animation is complete
        if (UFOMissile3.Explosion.currentframe >= UFOMissile3.Explosion.frames-1):
          UFOMissile3.Explosion.currentframe = 0
          UFOMissile3.Explosion.exploding    = 0
          UFOMissile3.Explosion.alive        = 0
          UFOMissile3.exploding              = 0
          UFOMissile3.alive                  = 0
          UFOMissile3.Explosion.h            = -1
          UFOMissile3.Explosion.v            = -1
          RedrawGround(TheGround)
          #compute score
          gv.SpaceDotScore = gv.SpaceDotScore + gv.AsteroidPoints





      #if (PlayerShip.alive == 0):
      #  PlayerShipExplosion.Animate(PlayerShip.h-2,PlayerShip.v-2,'forward',0.025)
        
      #Display animation and clock every X seconds
      #if (CheckElapsedTime(CheckTime) == 1):
      #  ScrollScreenShowLittleShipTime(gv.ScrollSleep)         
  
     
      #-------------------------------------
      # Display Score
      #-------------------------------------
      cf.DisplayScore(gv.SpaceDotScore,cf.MedGreen)


     
      #-------------------------------------
      # End of Wave 
      #-------------------------------------
      
      #check for time between armadas
      if (Wave.Alive == False):
        MovesSinceWaveStop = MovesSinceWaveStop + 1
        
        #print("Moves since wave stop:",MovesSinceWaveStop)
        if (MovesSinceWaveStop > gv.MovesBetweenWaves):
          print("--End of Wave--")
          MovesSinceWaveStop = 0
          Wave.Alive  = True


          gv.PlayerMissiles = gv.PlayerMissiles + 1
          if (gv.PlayerMissiles >= gv.MaxPlayerMissiles):
            gv.PlayerMissiles = gv.MaxPlayerMissiles
          PlayerMissiles.append(cf.Ship(-0,-0,PlayerMissileR,PlayerMissileG,PlayerMissileB,1,1,5,0,1,'PlayerMissile', 0,0))
          PlayerMissiles[-1].alive     = 0
          PlayerMissiles[-1].exploding = 0
          PlayerMissiles[-1].Explosion = copy.deepcopy(SmallExplosion)

          #increase speed of all missiles
          gv.PlayerMissileSpeed = gv.PlayerMissileSpeed -1
          if(gv.PlayerMissileSpeed <= gv.PlayerMissileMinSpeed):
            gv.PlayerMissileSpeed = gv.PlayerMissileMinSpeed

          for i in range(0,gv.PlayerMissiles):
            PlayerMissiles[i].speed = gv.PlayerMissileSpeed

          #increase speed of player ship
          gv.PlayerShipSpeed = gv.PlayerShipSpeed -5
          gv.PlayerShipMinSpeed = gv.PlayerShipMinSpeed -5
          if(gv.PlayerShipMinSpeed <= gv.PlayerShipAbsoluteMinSpeed):
            gv.PlayerShipMinSpeed = gv.PlayerShipAbsoluteMinSpeed

          if(gv.PlayerShipSpeed <= gv.PlayerShipAbsoluteMinSpeed):
            gv.PlayerShipSpeed = gv.PlayerShipAbsoluteMinSpeed

          PlayerShip.speed = gv.PlayerShipSpeed



          #adjust speeds, lower number is faster
          gv.AsteroidMinSpeed = gv.AsteroidMinSpeed - 1
          if(gv.AsteroidMinSpeed < gv.WaveMinSpeed):
            gv.AsteroidMinSpeed = gv.WaveMinSpeed
          
          gv.AsteroidMaxSpeed = gv.AsteroidMaxSpeed - 1
          if(gv.AsteroidMaxSpeed < gv.WaveMinSpeed + gv.WaveSpeedRange ):
            gv.AsteroidMaxSpeed = gv.WaveMinSpeed + gv.WaveSpeedRange

          cf.DisplayLevel(Wave.WaveCount,cf.MedBlue)


          #launch next wave of asteroids, maybe show some fancy graphics here
          Wave.AsteroidCount = Wave.AsteroidCount + 1
          Wave.WaveCount     = Wave.WaveCount + 1

          if(Wave.AsteroidCount  >= gv.AsteroidsInWaveMax):
            Wave.AsteroidCount    = gv.AsteroidsInWaveMax

          Wave.CreateAsteroidWave()

          Wave.Alive        = True
          
          print ("Wave:",Wave.WaveCount,"Asteroids in wave:",Wave.AsteroidCount)
          print("----")
          

        
      #time.sleep(gv.MainSleep / 25)
      
      












#--------------------------------------
#--         Dot Invaders             --
#--------------------------------------


def PutArmadaOnPlayfield(Armada,ArmadaHeight,ArmadaWidth,Playfield):
  #we need to examine the armada, and see which ones are visible and should be put on the playfield

  for x in range (ArmadaWidth):
    for y in range (ArmadaHeight):
      if(Armada[y][x].alive == 1):
        #print ("PAPF - Armada[x][y] HV:",x,y,Armada[x][y].h,Armada[x][y].v)
        #print ("placing on field:",Armada[x][y].name)
        Playfield[Armada[y][x].v][Armada[y][x].h] = Armada[y][x]

def DisplayPlayfield(Playfield):
  for x in range (gv.HatWidth):
    for y in range (gv.HatHeight):
      if (Playfield[y][x].name != 'EmptyObject'):
        #print("Playfield: ",Playfield[x][y].name)
        Playfield[y][x].Display()
        if (Playfield[y][x].name == 'UFO'):
          cf.FlashDot2(x,y,0.0001)
        
        
        
        
def CreateSpecialArmada(ShowTime=True):
    #Does the same as Display, but does not call show(), allowing calling function to further modify the Buffer
    #before displaying
    x = 0,
    y = 0

    
    # Random medium brightness color
    #7 11 15 19 23 27 32

    
    color = random.randint(1,7) * 4 + 3
    r,g,b = cf.ColorList[color]
    
    
    #Show time or word
    if ((random.randint(1,2) == 1) or ShowTime == True):
      TheTime = cf.CreateClockSprite(12)
    else:
      WordList=("PAC","MAN","1943","USA","CAN","AUS","NZ","UK","XX","RAS","PIE","PI",
                "IOI",":O:","8:8","123","777","42","888")
      TheMessage = WordList[random.randint(1,len(WordList)-1)]
      print ("Armada Message:",TheMessage)
      TheTime = cf.CreateBannerSprite(TheMessage)
      print ("Armada launched!")
    
    #if the HH has double digits, sprite is too wide.  Trim the left empty columns.
    if (TheTime.width >= 14):
      TheTime = cf.LeftTrimSprite(TheTime,1)
    Armada = [[ cf.Ship(1,1,r,g,b,2,3,50,1,1,'UFO', 0,0) for y in range(TheTime.height)] for x in range(TheTime.width)]
    ArmadaHeight = TheTime.height
    ArmadaWidth  = TheTime.width
    
    for count in range (0,(TheTime.width * TheTime.height)):
      y,x = divmod(count,TheTime.width)
      #print("Count:",count,"xy",x,y)
      if TheTime.grid[count] == 1:
        Armada[x][y].alive = 1
      else:
        Armada[x][y].alive = 0
    #unicorn.show()
    return Armada,ArmadaHeight,ArmadaWidth;



        
def DotInvadersCheckBoundarySpaceDot(h,v):
  BoundaryHit = 0
  if (v < 0 or v > gv.HatHeight-1 or h < 0 or h > gv.HatWidth-1):
    BoundaryHit = 1
  return BoundaryHit;



def DotInvadersExplodeMissile(Ship,Playfield,increment):
  Ship.r = Ship.r + increment
  Ship.g = 0 #Ship.g + increment
  Ship.b = 0 #Ship.b + increment

  #After explosion, reset colors
  if (Ship.r >= 255 or Ship.g >= 255 or Ship.b >= 255):
    if (Ship.name == 'PlayerMissile'):
      Ship.r = PlayerMissileR
      Ship.g = PlayerMissileG
      Ship.b = PlayerMissileB
    elif (Ship.name == 'Asteroid'):
      Ship.r = cf.SDDarkOrangeR
      Ship.g = cf.SDDarkOrangeG
      Ship.b = cf.SDDarkOrangeB
    elif (Ship.name == 'UFOMissile'):
      Ship.r = PlayerMissileR
      Ship.g = PlayerMissileG
      Ship.b = PlayerMissileB
    elif (Ship.name == 'UFO'):
      Ship.r = cf.SDDarkPurpleR
      Ship.g = cf.SDDarkPurpleG
      Ship.b = cf.SDDarkPurpleB

    Ship.exploding = 0
    Ship.alive     = 0
    #print ("Ship Exploded")
    Ship.Erase()
    Playfield[Ship.v][Ship.h].alive = 0
    Playfield[Ship.v][Ship.h] = Empty

  if (Ship.exploding == 1):
    cf.setpixel(Ship.h,Ship.v,255,255,255)
    cf.setpixel(Ship.h,Ship.v,Ship.r,Ship.g,Ship.b)
    #print("EM - Ship.exploding: ",Ship.exploding)
    #print("EM - After: ",Ship.name, "HV",Ship.h,Ship.v," rgb",Ship.r,Ship.g,Ship.b)
  
  



def MoveArmada(Armada,ArmadaHeight,ArmadaWidth,Playfield):
  #every ship in the armada will look in the directon they are travelling
  #if a wall is found, drop down a level and reverse direction
  #if you hit the ground, game over

  ScanH = 0
  ScanV = 0
  direction = 0
  x = 0
  y = 0
  #print ("MA - moving armada")
  BorderDetected = 0
  LowestV = 0


#  print ("=====***************************************************================")
#  for x in range(ArmadaWidth-1,-1,-1):
#    for y in range (ArmadaHeight-1,-1,-1):
#      h = Armada[x][y].h
#      v = Armada[x][y].v
#      cf.FlashDot(h,v,0.005)
#      print ("XY hv Alive Armada.Name Playfield.Name",x,y,h,v,Armada[x][y].alive,Armada[x][y].name,Playfield[v][h].name)
#  print ("=====***************************************************================")



  
  #Check for border
  for x in range(ArmadaWidth-1,-1,-1):
    for y in range (ArmadaHeight-1,-1,-1):
      if (Armada[x][y].alive == 1):
        #print ("MA - Calculating Armada[x][y].hv: ",x,y,Armada[x][y].h,Armada[x][y].v)
        h = Armada[x][y].h
        v = Armada[x][y].v
        direction = Armada[x][y].direction
        ScanH,ScanV = cf.CalculateDotMovement(h,v,direction)
        
        #we just want to know the lowest armada ship, for firing missiles
        if (LowestV < v):
          LowestV = v
        #if (DotInvadersCheckBoundarySpaceDot(ScanH, ScanV) == 0):
        #FlashDot(h,v,0.005)
          
        #print ("MA - checking xy ScanH ScanV: ",x,y,ScanH,ScanV)
        if (DotInvadersCheckBoundarySpaceDot(ScanH, ScanV) == 1):
          BorderDetected = 1
          #print ("MA - border detected - inner break")
          break
      if (DotInvadersCheckBoundarySpaceDot(ScanH, ScanV) == 1):
        BorderDetected = 1
        #print ("MA - border detected - outer break")
        break
  
  #Move
  if (BorderDetected == 1):
    direction = cf.ReverseDirection(direction)
  
  if (direction == 2):
    for x in range(ArmadaWidth-1,-1,-1):
      for y in range (ArmadaHeight-1,-1,-1):
        if (Armada[x][y].alive == 1):

          OldH = Armada[x][y].h
          OldV = Armada[x][y].v
          #print ("MA  - OldH OldV direction",OldH,OldV,direction)
          
          NewH, NewV = cf.CalculateDotMovement(OldH,OldV,direction)
          if(BorderDetected == 1):
            NewH = OldH
            NewV = NewV + 1
          Armada[x][y].h = NewH
          Armada[x][y].v = NewV

          cf.setpixel(OldH,OldV,0,0,0)
          Armada[x][y].Display()
          Armada[x][y].direction = direction
          Playfield[OldH][OldV] = Empty
          #print ("NewH NewV",NewH,NewV)
          if (NewV <= 15):
            Playfield[NewH][NewV] = Armada[x][y]
          else:
            print ("Game Over")
          
  else:
    for x in range(ArmadaWidth):
      for y in range (ArmadaHeight-1,-1,-1):
        if (Armada[x][y].alive == 1):
  
          OldH = Armada[x][y].h
          OldV = Armada[x][y].v
          #print ("MA  - OldH OldV direction",OldH,OldV,direction)
          
          NewH, NewV = cf.CalculateDotMovement(OldH,OldV,direction)
          if(BorderDetected == 1):
            NewH = OldH
#            NewV = NewV + 1
            NewV = NewV 
          Armada[x][y].h = NewH
          Armada[x][y].v = NewV

          cf.setpixel(OldH,OldV,0,0,0)
          Armada[x][y].Display()
          Armada[x][y].direction = direction
          Playfield[OldH][OldV] = Empty
          Playfield[NewH][NewV] = Armada[x][y]
          
          
  #Count Armada alive
  ArmadaCount = 0
  for x in range (ArmadaWidth):
    for y in range (ArmadaHeight):
      if (Armada[x][y].alive == 1):
        ArmadaCount = ArmadaCount + 1
  

  #Drop missiles
  h,v = NewH, NewV
  if (UFOMissile1.alive == 0 and UFOMissile1.exploding == 0):
    UFOMissile1.h = h
    UFOMissile1.v = LowestV
    UFOMissile1.alive = 1
  elif (UFOMissile2.alive == 0 and UFOMissile2.exploding == 0 and ArmadaCount > 1):
    UFOMissile2.h = h
    UFOMissile2.v = LowestV
    UFOMissile2.alive = 1

      
def DotInvadersMoveMissile(Missile,Ship,Playfield):
  global Empty
  #print ("MM - MoveMissile:",Missile.name)
  
  #Record the current coordinates
  h = Missile.h
  v = Missile.v

  
  #Missiles simply drop to bottom and kablamo!
  #FF (one square in front of missile direction of travel)
  ScanH, ScanV = cf.CalculateDotMovement(Missile.h,Missile.v,Missile.scandirection)
  Item = DotInvadersScanSpaceDot(ScanH,ScanV)
  
  #print("Item: ",Item)
  
  #Priority
  # 1 Hit target
  # 2 See if we are hit by enemy missle
  # 3 Move forward
  

  #See if other target ship is hit
  if (Item  == 'Player1' or Item == 'UFO' or Item == 'UFOMissile' or Item == 'Bunker'):
    #target hit, kill target
    #print ("DIMM - Item Name", Item, Playfield[ScanV][ScanH].name)
    Playfield[ScanV][ScanH].alive = 0
    Playfield[ScanV][ScanH]= Empty
    cf.setpixel(ScanH,ScanV,0,0,0)
    cf.setpixel(h,v,0,0,255)
    if (Item == 'EnemyShip'):
      Ship.score = Ship.score + random.randint(1,11)
    else:
      Ship.score = Ship.score + 1


    Missile.h = ScanH
    Missile.v = ScanV
    #Playfield[Missile.h][Missile.v] = Missile
    Missile.Display()
    Missile.exploding = 1
    Missile.alive = 0
    

  
  #Player missiles fire off into space
  #Enemy missiles explode on ground
  elif (Item == 'border' and Missile.name == 'PlayerMissile'):
    #print ("MM - Missile hit border")
    Missile.alive  = 0
    Missile.exploding = 0
    Missile.Erase()
  elif (Item == 'border' and (Missile.name == 'UFOMissile' or Missile.name == 'Asteroid')):
    #print ("MM - Missile hit border")
    Missile.alive  = 0
    Missile.exploding = 1
    Missile.Erase()
    #print ("MM - UFO hit border HV:",Missile.h,Missile.v)
    
  #empty = move forward
  elif (Item == 'EmptyObject' and Missile.alive == 1):
    Missile.h = ScanH
    Missile.v = ScanV
    Playfield[Missile.h][Missile.v] = Missile
    Missile.Display()
    #print ("MM - empty, moving forward")
    

  if ((h != Missile.h or v != Missile.v) or
     (Missile.alive == 0)):
    Playfield[v][h] = Empty
    cf.setpixel(h,v,0,0,0)
    #print ("MM - Erasing Missile")
  #unicorn.show()
  #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
  
  return 
    
def DotInvadersScanSpaceDot(h,v,Playfield):
# border
# empty
# wall

  #print ("SSD - HV:",h,v)
  Item = ''
  OutOfBounds = DotInvadersCheckBoundarySpaceDot(h,v)
  
  if (OutOfBounds == 1):
    Item = 'border'
#    print ("Border found HV: ",h,v)
  else:
    #FlashDot(h,v,0.01)
    Item = Playfield[v][h].name
  return Item


        
def DotInvaderScanShip(h,v,direction,Playfield):
  ScanDirection = 0
  ScanH         = 0
  ScanV         = 0
  Item          = ''
  ItemList      = ['NULL']

  
  # We will scan 5 spots around the dot
  # and 8 more in front
  
  #    21
  #    20
  #    19
  #    18
  #    17
  #    16
  #    15
  #    14
  # 11 12 13
  #    10
  #     9
  #     8
  #     7
  #     6
  #  2  3  4
  #  1     5
  #
  
  
  #LL 1
  ScanDirection = cf.TurnLeft(direction)
  ScanH, ScanV = cf.CalculateDotMovement(h,v,ScanDirection)
  Item = DotInvadersScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)
  #print ("DISS1 - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #LF 2
  ScanDirection =  cf.TurnRight(ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotInvadersScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)
  #print ("DISS2 - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #FF 3
  ScanDirection =  cf.TurnRight(ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotInvadersScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)
  #print ("DISS3 - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #FR 4
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotInvadersScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)
  #print ("DISS4 - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #RR 5
  ScanDirection =  cf.TurnRight(ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotInvadersScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)
  #print ("DISS5 - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)

  #F1 6
  ScanDirection = cf.ReverseDirection(ScanDirection)
  ScanH, ScanV  = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  ScanDirection = cf.TurnLeft(ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  ScanDirection =  cf.TurnRight(ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotInvadersScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)
  #print ("DISS6 - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)

  #F2 7
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotInvadersScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)
  #print ("DISS7 - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #F3 8
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotInvadersScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)
  #print ("DISS8 - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #F4 9
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotInvadersScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)
  #print ("DISS9 - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)

  #F5 10
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotInvadersScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)
  #print ("DISS10 - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)

  #F6 11
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  ScanDirection = cf.TurnLeft(ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotInvadersScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)
  #print ("DISS11 - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)

  #F7 12
  ScanDirection = cf.ReverseDirection(ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotInvadersScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)
  #print ("DISS12 - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)

  #F8 13
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotInvadersScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)
  #print ("DISS13 - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)

  
  #14 -- new additions since moving to larger grid
  ScanDirection = cf.ReverseDirection(ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  ScanDirection =  cf.TurnRight(ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)

  #15
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)

  #16
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)

  #17
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)

  #18
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)

  #19
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)
  
  #20
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV)
  ItemList.append(Item)
  return ItemList;

  
  
  
  return ItemList;


def DotInvaderMovePlayerShip(Ship,Playfield):
  #print ("DIMPS - moveship HV Direction:",Ship.h,Ship.v,Ship.direction)
  
  #Player ships always points up, enemy ships point down
  h = Ship.h
  v = Ship.v
  ItemList = []
  #Scan all around, make decision, move
  ItemList = DotInvaderScanShip(Ship.h,Ship.v,Ship.scandirection,Playfield)
  
  #print("MPS - ItemList",ItemList)
  #print("MPS - Ship.name HV",Ship.name,Ship.h,Ship.v)
  #get possible items, then prioritize

  #Priority
  # 1 Evade close objects
  # 2 Blast far objects

  #If UFO is detected, fire missile!
  if ("UFO" in ItemList or "UFOMissile" in ItemList ):
    if (ItemList[3] != "Bunker" and ItemList[6] != "Bunker"):

      if (PlayerMissile1.alive == 0 and PlayerMissile1.exploding == 0):
        #print ("MPS - UFO/Bomber/aseroid Detected PlayerMissile1.alive:",PlayerMissile1.alive)
        PlayerMissile1.h = h
        PlayerMissile1.v = v
        PlayerMissile1.alive = 1
        PlayerMissile1.exploding = 0
        Ship.score = Ship.score + 1
          
  #    elif (PlayerMissile2.alive == 0 and PlayerMissile2.exploding == 0):
  #      #print ("MPS - UFO or asteroid Detected PlayerMissile1.alive:",PlayerMissile1.alive)
  #      PlayerMissile2.h = h
  #      PlayerMissile2.v = v
  #      PlayerMissile2.alive = 1
  #      PlayerMissile2.exploding = 0

  #Follow UFO
  #slow down if ahead of UFO, speed up if behind
  if (ItemList[11] == 'UFO' or ItemList[11] == 'BomberShip'):
    #print ("****************************")
    #print ("****************************")
    #print ("****************************")
    Ship.direction = Playfield[h-1][0].direction
    #print ("MPS - ENEMY TO LEFT Enemy.name HV direction speed",Playfield[h-1][0].name,Playfield[h-1][0].h,Playfield[h-1][0].v, Playfield[h-1][0].direction,Playfield[h-1][0].speed)
    if (Playfield[h-1][0].direction == 4):
      AdjustSpeed(Ship,'fast',5)
    elif (Playfield[h-1][0].direction == 2):
      AdjustSpeed(Ship,'slow',1)
    
  elif (ItemList[13] == 'UFO' or ItemList[13] == 'BomberShip'):

    #for x in range (0,gv.HatWidth):
      #for y in range (0,gv.HatWidth):
        #print("Playfield[x][y].name HV speed direction: ",x,y,Playfield[x][y].name,Playfield[x][y].h,Playfield[x][y].v,Playfield[x][y].speed,Playfield[x][y].direction)


    Ship.direction = Playfield[0][h+1].direction
    #print ("MPS - ENEMY TO RIGHT Enemy.name HV direction",Playfield[0][h+1].name,Playfield[0][h+1].h,Playfield[0][h+1].v, Playfield[0][h+1].direction)
    if (Playfield[0][h+1].direction == 2):
      #print ("MPS - adjusting speed fast 3")
      AdjustSpeed(Ship,'fast',4)
    elif (Playfield[0][h+1].direction == 4):
      #print ("MPS - adjusting speed slow 1")
      AdjustSpeed(Ship,'slow',1)
  
    
     
  
  #if heading to boundary or wall Reverse direction
  #print("checking border")
  if ((Ship.direction == 4 and ItemList[1] == 'border') or
      (Ship.direction == 2 and ItemList[5] == 'border')):
    Ship.direction = cf.ReverseDirection(Ship.direction)
    #print ("MPS - border detected, reversing direction")
    AdjustSpeed(Ship,'slow',1)
    #print("MPS - 2Ship.direction: ",Ship.direction)
  
  #Evade close objects
  # - if object in path of travel, reverse direction
  elif ((Ship.direction == 4 and ((ItemList[1] != 'EmptyObject' and ItemList[1] != 'Bunker') or (ItemList[2] != 'EmptyObject'and ItemList[2] != 'Bunker'))) or
        (Ship.direction == 2 and ((ItemList[5] != 'EmptyObject' and ItemList[5] != 'Bunker') or (ItemList[4] != 'EmptyObject' and ItemList[4] != 'Bunker')))):      
    Ship.direction = cf.ReverseDirection(Ship.direction)
    #print("MPS - object in path, reversed direction")
    #print("MPS - 3Ship.direction: ",Ship.direction)
    

  # - speed up and move if object is directly above
  elif ((Ship.direction == 4 and (ItemList[3] != 'EmptyObject' and ItemList[1] == 'EmptyObject')) or
        (Ship.direction == 2 and (ItemList[3] != 'EmptyObject' and ItemList[5] == 'EmptyObject'))):
    AdjustSpeed(Ship,'fast',8)
    Ship.h, Ship.v =  cf.CalculateDotMovement(Ship.h,Ship.v,Ship.direction)

  # - travelling left, move if empty
  # - travelling right, move if empty
  # - randomly switch directions
  elif ((ItemList[1] == 'EmptyObject' and Ship.direction == 4) or 
        (ItemList[5] == 'EmptyObject' and Ship.direction == 2 )):
    if ((random.randint(0,gv.HatWidth-1) == 1) and Ship.h != 0 and Ship.h != 15):
      Ship.direction = cf.ReverseDirection(Ship.direction)
    Ship.h, Ship.v =  cf.CalculateDotMovement(Ship.h,Ship.v,Ship.direction)
    #print("MPS - Travelling, move if empty")


  #if nothing nearby, and near the middle, stop moving
  if (ItemList[1]  == 'EmptyObject' and
      ItemList[2]  == 'EmptyObject' and
      ItemList[3]  == 'EmptyObject' and
      ItemList[4]  == 'EmptyObject' and
      ItemList[5]  == 'EmptyObject' and
      ItemList[6]  == 'EmptyObject' and
      ItemList[7]  == 'EmptyObject' and
      ItemList[8]  == 'EmptyObject' and
      ItemList[9]  == 'EmptyObject' and
      ItemList[10] == 'EmptyObject' and
      ItemList[12] == 'EmptyObject' and Ship.h >= 3 and Ship.h <= 4):
    if (random.randint (0,5) != 1):
      #print ("MPS - Staying in the middle")
      Ship.h = h
      Ship.v = v
    
  #print("MPS - 6Ship.direction: ",Ship.direction)

  #print("MPS - OldHV: ",h,v, " NewHV: ",Ship.h,Ship.v, "direction: ",Ship.direction)
  Playfield[Ship.v][Ship.h]= Ship
  Ship.Display()
  
  if ((h != Ship.h or v != Ship.v) or
     (Ship.alive == 0)):
    Playfield[v][h] = Empty
    cf.setpixel(h,v,0,0,0)
    #print ("MPS - Erasing Player")
  #unicorn.show()
  #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)

  #print("MPS - 7Ship.direction: ",Ship.direction)

  return 
        

def ShowFireworks(FireWorksExplosion,count,speed):
  x = 0
  h = 0
  v = 0
  for x in range(1,count):
    h = random.randint(2,12)
    v = random.randint(0,7)
    FireWorksExplosion.Animate(h,v,'forward',speed)        


        
          
def PlayDotInvaders():
  
  #Local variables
  moves       = 0
  Finished    = 'N'
  LevelCount  = 1
  Playerh     = 0
  Playerv     = 0
  SleepTime   = gv.MainSleep / 4
  ChanceOfEnemyShip = 800

  #define sprite objects
  #def __init__(self,h,v,r,g,b,direction,scandirection,speed,alive,lives,name,score,exploding):
  BunkerDot1  = cf.Ship( 2,14,cf.SDLowGreenR,cf.SDLowGreenG,cf.SDLowGreenB,1,1,999,1,5,'Bunker', 0,0)
  BunkerDot2  = cf.Ship( 3,14,cf.SDLowGreenR,cf.SDLowGreenG,cf.SDLowGreenB,1,1,999,1,5,'Bunker', 0,0)
  BunkerDot3  = cf.Ship( 7,14,cf.SDLowGreenR,cf.SDLowGreenG,cf.SDLowGreenB,1,1,999,1,5,'Bunker', 0,0)
  BunkerDot4  = cf.Ship( 8,14,cf.SDLowGreenR,cf.SDLowGreenG,cf.SDLowGreenB,1,1,999,1,5,'Bunker', 0,0)
  BunkerDot5  = cf.Ship(12,14,cf.SDLowGreenR,cf.SDLowGreenG,cf.SDLowGreenB,1,1,999,1,5,'Bunker', 0,0)
  BunkerDot6  = cf.Ship(13,14,cf.SDLowGreenR,cf.SDLowGreenG,cf.SDLowGreenB,1,1,999,1,5,'Bunker', 0,0)
  BunkerDot7  = cf.Ship( 2,13,cf.SDLowGreenR,cf.SDLowGreenG,cf.SDLowGreenB,1,1,999,1,5,'Bunker', 0,0)
  BunkerDot8  = cf.Ship( 3,13,cf.SDLowGreenR,cf.SDLowGreenG,cf.SDLowGreenB,1,1,999,1,5,'Bunker', 0,0)
  BunkerDot9  = cf.Ship( 7,13,cf.SDLowGreenR,cf.SDLowGreenG,cf.SDLowGreenB,1,1,999,1,5,'Bunker', 0,0)
  BunkerDot10 = cf.Ship( 8,13,cf.SDLowGreenR,cf.SDLowGreenG,cf.SDLowGreenB,1,1,999,1,5,'Bunker', 0,0)
  BunkerDot11 = cf.Ship(12,13,cf.SDLowGreenR,cf.SDLowGreenG,cf.SDLowGreenB,1,1,999,1,5,'Bunker', 0,0)
  BunkerDot12 = cf.Ship(13,13,cf.SDLowGreenR,cf.SDLowGreenG,cf.SDLowGreenB,1,1,999,1,5,'Bunker', 0,0)
  PlayerShip  = cf.Ship( 7,15,PlayerShipR,PlayerShipG,PlayerShipB,4,1,10,1,5,'Player1', 0,0)
  EnemyShip   = cf.Ship(14,0,cf.SDLowPurpleR,cf.SDLowPurpleG,cf.SDLowPurpleB,4,3,50,0,3,'UFO', 0,0)
  cf.Ship(15,0,cf.SDLowPurpleR,cf.SDLowPurpleG,cf.SDLowPurpleB,4,3,50,0,3,'UFO', 0,0)
  Empty      = cf.Ship(-1,-1,0,0,0,0,1,0,0,0,'EmptyObject',0,0)


  # Create armada of ships
  #Armada = [[Ship(1,1,cf.SDDarkGreenR,cf.SDDarkGreenG,cf.SDDarkGreenB,2,3,50,1,1,'UFO', 0,0) for y in range(ArmadaHeight)] for x in range(ArmadaWidth)]

  
  #Create playfield
  gv.Playfield = ([[]])
  gv.Playfield = [[0 for i in range(gv.HatWidth)] for i in range(gv.HatWidth)]
 
  #CreateExplosionSprites
  FireworksExplosion  = copy.deepcopy(PlayerShipExplosion)  
  BomberShipExplosion = copy.deepcopy(PlayerShipExplosion)  
  
  #Title
  cf.ClearBigLED()
  cf.ShowScrollingBanner2("DotInvader",(cf.MedGreen),gv.ScrollSleep)
  #ShowSpaceInvaderTime(gv.ScrollSleep)
  TinyInvader.ScrollAcrossScreen(0,5,'left',gv.ScrollSleep)

  FirstTime = True

  #Main Game Loop
  while (Finished == 'N'):

    #First time through, always show the time
    Armada, ArmadaHeight, ArmadaWidth = CreateSpecialArmada(FirstTime)
    FirstTime = False

    # Set initial starting positions
    for x in range (ArmadaWidth):
      for y in range(ArmadaHeight):
        Armada[x][y].h = x + ((gv.HatWidth // 2) - (ArmadaWidth //2))
        Armada[x][y].v = y + 1
        #Armada[x][y].alive = 1
    ArmadaSpeed = 125
    ArmadaAlive = 1

    
    
    cf.ClearBigLED()
    LevelCount = LevelCount + 1
    #ShowLevelCount(LevelCount)
    

    
    #Reset Variables between rounds
    LevelFinished     = 'N'
    moves             = 1
    PlayerShip.alive  = 1
    PlayerShip.speed  = gv.PlayerShipSpeed
    PlayerShip.h      = gv.HatWidth // 2
    PlayerShip.v      = gv.HatHeight
    PlayerMissile1.speed = 2
    if (random.randint(0,2) == 1):
      PlayerShip.direction = 2
    else:
      PlayerShip.direction = 4
    EnemyShip.alive   = 0
    UFOMissile1.alive = 0
    UFOMissile2.alive = 0
    EnemyShip.speed   = random.randint (15,50)
    
    #Speed up last life for player
    if (PlayerShip.lives == 1):
      PlayerShip.speed = 1

    
    #Reset colors
    UFOMissile1.r = PlayerMissileR
    UFOMissile1.g = PlayerMissileG
    UFOMissile1.b = PlayerMissileB
    UFOMissile2.r = PlayerMissileR
    UFOMissile2.g = PlayerMissileG
    UFOMissile2.b = PlayerMissileB
    PlayerMissile1.r     = PlayerMissileR
    PlayerMissile1.g     = PlayerMissileG
    PlayerMissile1.b     = PlayerMissileB
    PlayerMissile1.alive = 0

    #ShowDropShip(PlayerShip.h,PlayerShip.v,'dropoff',gv.ScrollSleep * 0.25)

    #Reset Playfield
    for x in range (0,gv.HatWidth):
      for y in range (0,gv.HatWidth):
        #print ("XY",x,y)
        Playfield[x][y] = Empty



    #Put items on Playfield
    Playfield[PlayerShip.h][PlayerShip.v] = PlayerShip
    PutArmadaOnPlayfield(Armada,ArmadaHeight,ArmadaWidth,Playfield)
    DisplayPlayfield(Playfield)

        
    
    #Draw Bunkers
    Playfield[BunkerDot1.h][BunkerDot1.v] = BunkerDot1
    Playfield[BunkerDot2.h][BunkerDot2.v] = BunkerDot1
    Playfield[BunkerDot3.h][BunkerDot3.v] = BunkerDot1
    Playfield[BunkerDot4.h][BunkerDot4.v] = BunkerDot1
    Playfield[BunkerDot5.h][BunkerDot5.v] = BunkerDot1
    Playfield[BunkerDot6.h][BunkerDot6.v] = BunkerDot1
    Playfield[BunkerDot7.h][BunkerDot7.v] = BunkerDot1
    Playfield[BunkerDot8.h][BunkerDot8.v] = BunkerDot1
    Playfield[BunkerDot9.h][BunkerDot9.v] = BunkerDot1
    Playfield[BunkerDot10.h][BunkerDot10.v] = BunkerDot1
    Playfield[BunkerDot11.h][BunkerDot11.v] = BunkerDot1
    Playfield[BunkerDot12.h][BunkerDot12.v] = BunkerDot1
    
    BunkerDot1.alive = 1
    BunkerDot2.alive = 1
    BunkerDot3.alive = 1
    BunkerDot4.alive = 1
    BunkerDot5.alive = 1
    BunkerDot6.alive = 1
    BunkerDot7.alive = 1
    BunkerDot8.alive = 1
    BunkerDot9.alive = 1
    BunkerDot10.alive = 1
    BunkerDot11.alive = 1
    BunkerDot12.alive = 1

    BunkerDot1.Flash()
    BunkerDot1.Display()
    BunkerDot2.Flash()
    BunkerDot2.Display()
    BunkerDot3.Flash()
    BunkerDot3.Display()
    BunkerDot4.Flash()
    BunkerDot4.Display()
    BunkerDot5.Flash()
    BunkerDot5.Display()
    BunkerDot6.Flash()
    BunkerDot6.Display()
    BunkerDot7.Flash()
    BunkerDot7.Display()
    BunkerDot8.Flash()
    BunkerDot8.Display()
    BunkerDot9.Flash()
    BunkerDot9.Display()
    BunkerDot10.Flash()
    BunkerDot10.Display()
    BunkerDot11.Flash()
    BunkerDot11.Display()
    BunkerDot12.Flash()
    BunkerDot12.Display()
  

    
    # Main timing loop
    while (LevelFinished == 'N' and PlayerShip.alive == 1):
      moves = moves + 1

      #Check for keyboard input
      m,r = divmod(moves,KeyboardSpeed)
      if (r == 0):
        Key = cf.PollKeyboard()
        ProcessKeypress(Key)
        if (Key == 'q'):
          LevelFinished = 'Y'
          Finished      = 'Y'
          PlayerShip.alive   = 0
          return

        
      
#      print ("=================================================")
#      for H in range(0,gv.HatWidth-1):
#        for V in range (0,gv.HatWidth-1):
#          if (Playfield[v][h].name != 'EmptyObject'):
#            print ("Playfield: HV Name Alive",H,V,Playfield[v][h].name,Playfield[v][h].alive)
#      print ("=================================================")
      

      
      #Spawn EnemyShip
      m,r = divmod(moves,ChanceOfEnemyShip)
      if (r == 0 and EnemyShip.alive == 0):
        #print ("Spawning UFO")
        EnemyShip.alive = 1
        EnemyShip.direction = cf.ReverseDirection(EnemyShip.direction)
        if (EnemyShip.direction == 2):
          EnemyShip.h = 0
          EnemyShip.v = 0
          #EnemyShip.v = random.randint(0,4)
        else:
          EnemyShip.h = gv.HatWidth-1
          EnemyShip.v = 0
        EnemyShip.Display()
      
      
      
      if (PlayerShip.alive == 1):
        #print ("M - Playership HV speed alive exploding direction: ",PlayerShip.h, PlayerShip.v,PlayerShip.speed, PlayerShip.alive, PlayerShip.exploding, PlayerShip.direction)
        m,r = divmod(moves,PlayerShip.speed)
        if (r == 0):
          DotInvaderMovePlayerShip(PlayerShip,gv.Playfield)
          i = random.randint(0,5)
          if (i >= 0):
            AdjustSpeed(PlayerShip,'fast',1)
          #print ("M - Player moved?")
          
            
      
      if (EnemyShip.alive == 1):
        m,r = divmod(moves,EnemyShip.speed)
        if (r == 0):
          if ((EnemyShip.h == 0  and EnemyShip.direction == 4)
            or EnemyShip.h == gv.HatWidth-1 and EnemyShip.direction == 2):
            EnemyShip.alive = 0
            Playfield[EnemyShip.h][EnemyShip.v] = Empty
            cf.setpixel(EnemyShip.h,EnemyShip.v,0,0,0)
          else:
            MoveEnemyShip(EnemyShip,Playfield)
        
          

      if (ArmadaAlive == 1):
        m,r = divmod(moves,ArmadaSpeed)
        if (r == 0):
          MoveArmada(Armada,ArmadaHeight,ArmadaWidth,Playfield)
        
          
          
      if (UFOMissile1.alive == 1 and UFOMissile1.exploding == 0):
        m,r = divmod(moves,UFOMissile1.speed)
        if (r == 0):
          DotInvadersMoveMissile(UFOMissile1,PlayerShip.gv.Playfield)

      if (UFOMissile2.alive == 1 and UFOMissile2.exploding == 0):
        m,r = divmod(moves,UFOMissile2.speed)
        if (r == 0):
          DotInvadersMoveMissile(UFOMissile2,PlayerShip.gv.Playfield)

      if (UFOMissile3.alive == 1 and UFOMissile3.exploding == 0):
        m,r = divmod(moves,UFOMissile3.speed)
        if (r == 0):
          DotInvadersMoveMissile(UFOMissile3,PlayerShip.gv.Playfield)

          
      if (PlayerMissile1.alive == 1 and PlayerMissile1.exploding == 0):
        m,r = divmod(moves,PlayerMissile1.speed)
        if (r == 0):
          DotInvadersMoveMissile(PlayerMissile1,PlayerShip.gv.Playfield)

#      if (PlayerMissile2.alive == 1 and PlayerMissile2.exploding == 0):
#        m,r = divmod(moves,PlayerMissile2.speed)
#        if (r == 0):
#          DotInvadersMoveMissile(PlayerMissile2,PlayerShip.gv.Playfield)

          
 
      
          
          

        

      #Check for exploding objects
      if (PlayerMissile1.exploding == 1):
        #print("------> PlayerMissile1.exploding: ",PlayerMissile1.exploding)
        DotInvadersExplodeMissile(PlayerMissile1,Playfield,10)

#      if (PlayerMissile2.exploding == 1 ):
#        #print("------> PlayerMissile2.exploding: ",PlayerMissile2.exploding)
#        DotInvadersExplodeMissile(PlayerMissile2,Playfield,20)


      if (UFOMissile1.exploding == 1 ):
        #print("------> UFOMissile1.exploding: ",UFOMissile1.exploding)
        DotInvadersExplodeMissile(UFOMissile1,Playfield,10)

      if (UFOMissile2.exploding == 1 ):
        #print("------> UFOMissile2.exploding: ",UFOMissile2.exploding)
        DotInvadersExplodeMissile(UFOMissile2,Playfield,10)

        
      #Display animation and clock every X seconds
      #if (CheckElapsedTime(CheckTime) == 1):
      #  ScrollScreenShowLittleShipTime('up',gv.ScrollSleep)         
     
      #=================================
      #= End of level conditions       =
      #=================================
     
      #Count armada UFOs alive
      #See how low down Armada is
      ArmadaCount = 0
      ArmadaLevel = 0
      for x in range (ArmadaWidth):
        for y in range (ArmadaHeight):
          if (Armada[x][y].alive == 1):
            ArmadaCount = ArmadaCount + 1
            if (Armada[x][y].v > ArmadaLevel):
              ArmadaLevel = Armada[x][y].v
      #print ("M - Armada AliveCount ArmadaLevel: ",ArmadaCount,ArmadaLevel)
      ArmadaSpeed = ArmadaCount * 10 + 5
        

      if (ArmadaCount == 0):
        LevelFinished = 'Y'
        #print ("M - Level:", LevelCount)
        cf.setpixel(PlayerMissile1.h,PlayerMissile1.v,0,0,0)
        cf.setpixel(UFOMissile1.h,UFOMissile1.v,0,0,0)
        cf.setpixel(UFOMissile2.h,UFOMissile2.v,0,0,0)

        FireworksExplosion.Animate(EnemyShip.h,EnemyShip.v,'forward',0.001)        
        FireworksExplosion.Animate(PlayerMissile1.h,PlayerMissile1.v,'forward',0.001)        
        FireworksExplosion.Animate(PlayerMissile2.h,PlayerMissile2.v,'forward',0.001)        
        FireworksExplosion.Animate(UFOMissile1.h,UFOMissile1.v,'forward',0.001)        
        FireworksExplosion.Animate(UFOMissile2.h,UFOMissile2.v,'forward',0.001)        
        FireworksExplosion.Animate(EnemyShip.h,EnemyShip.v,'forward',0.001)        
        
        
        ShowFireworks(FireworksExplosion,(random.randint(1,5)),0.003)
        ShowDropShip(PlayerShip.h,PlayerShip.v,'pickup',gv.ScrollSleep * 0.001)

      
      if (ArmadaLevel == gv.HatHeight-1):
        PlayerShip.alive = 0
        LevelFinished = 'Y'

      
        if (PlayerShip.lives <=0):
          Finished = 'Y'


        else:
          PlayerShip.alive = 1
        PlayerShipExplosion.Animate(PlayerShip.h-2,PlayerShip.v-2,'forward',0.025)

      #Display animation and clock every X seconds
      if (CheckElapsedTime(CheckTime) == 1):
        ScrollScreenShowClock('up',gv.ScrollSleep)         



        
      #time.sleep(MainSleep / 5)
  print ("M - The end?")    
  cf.ClearBigLED()
  
  ScoreString = str(PlayerShip.score) 
  cf.ShowScrollingBanner("Score",cf.SDLowGreenR,cf.SDLowGreenG,cf.SDLowGreenB,gv.ScrollSleep)
  cf.ShowScrollingBanner(ScoreString,cf.SDLowYellowR,cf.SDLowYellowG,cf.SDLowYellowB,(gv.ScrollSleep * 2))
  cf.ShowScrollingBanner("GAME OVER",cf.SDMedRedR,cf.SDMedRedG,cf.SDMedRedR,gv.ScrollSleep)




      







      
      
      
      
      
      
      
      
      
      
      


#------------------------------------------------------------------------------
# D o t Z e r k                                                              --
#------------------------------------------------------------------------------

# PlayDotZerk

# Notes
#
# Due to the unforseen complexity of navigating the maps, we are going to force
# doors to be in fixed positions
# We should make the doors be meta objects, and not items on the playfield
# It is very difficult to treat them as special wall objects

#Variables
ExitingRoom   = 0
RobotsAlive   = 0
HumanMissileR = cf.SDMedWhiteR
HumanMissileG = cf.SDMedWhiteG
HumanMissileB = cf.SDMedWhiteB
RobotMissileR = 200
RobotMissileG = 0
RobotMissileB = 250
DotZerkScore  = 0

#Hold speeds in a list, acting like gears
Gear = []
Gear.append(95)
Gear.append(85)
Gear.append(75)
Gear.append(65)
Gear.append(55)
Gear.append(45)
Gear.append(35)
Gear.append(25)
Gear.append(15)
global CurrentGear
global MaxGear
MaxGear     = 8
CurrentGear = 1

#Track previous human direction so we can close the door in a new room
DirectionOfTravel = 2



#define sprite objects
#def __init__(self,h,v,r,g,b,direction,scandirection,speed,alive,lives,name,score,exploding):
Human         = cf.Ship(1,3,cf.SDMedGreenR,cf.SDMedGreenG,cf.SDMedGreenB,2,2,10,1,10,'Human', 0,0)
HumanMissile1 = cf.Ship(-1,-1,HumanMissileR,HumanMissileG,HumanMissileB,1,1,4,0,0,'HumanMissile', 0,0)
HumanMissile2 = cf.Ship(-1,-1,HumanMissileR,HumanMissileG,HumanMissileB,1,1,4,0,0,'HumanMissile', 0,0)

Robot1 = cf.Ship(3,7,cf.SDLowRedR,cf.SDLowRedG,cf.SDLowRedB,4,1,10,0,3,'Robot', 0,0)
Robot2 = cf.Ship(3,7,cf.SDLowRedR,cf.SDLowRedG,cf.SDLowRedB,4,1,10,0,3,'Robot', 0,0)
Robot3 = cf.Ship(3,7,cf.SDLowRedR,cf.SDLowRedG,cf.SDLowRedB,4,1,10,0,3,'Robot', 0,0)
Robot4 = cf.Ship(3,7,cf.SDLowRedR,cf.SDLowRedG,cf.SDLowRedB,4,1,10,0,3,'Robot', 0,0)
RobotBob = cf.Ship(3,7,cf.SDMedYellowR,cf.SDMedYellowG,cf.SDMedYellowB,4,1,10,0,3,'Robot', 0,0)
Empty    = cf.Ship(-1,-1,0,0,0,0,1,0,0,0,'EmptyObject',0,0)



Robot1Missile   = cf.Ship(-5,-1,RobotMissileR,RobotMissileG,RobotMissileB,0,0,15,0,0,'RobotMissile',0,0)
Robot2Missile   = cf.Ship(-5,-1,RobotMissileR,RobotMissileG,RobotMissileB,0,0,15,0,0,'RobotMissile',0,0)
Robot3Missile   = cf.Ship(-5,-1,RobotMissileR,RobotMissileG,RobotMissileB,0,0,15,0,0,'RobotMissile',0,0)
Robot4Missile   = cf.Ship(-5,-1,RobotMissileR,RobotMissileG,RobotMissileB,0,0,15,0,0,'RobotMissile',0,0)
RobotBobMissile   = cf.Ship(-5,-1,RobotMissileR,RobotMissileG,RobotMissileB,0,0,15,0,0,'RobotMissile',0,0)

#(h,v,alive,locked,name):
Door1 = cf.Door(7,0,0,0,'Door')
Door2 = cf.Door(15,7,0,0,'Door')
Door3 = cf.Door(7,15,0,0,'Door')
Door4 = cf.Door(0,7,0,0,'Door')


#(self,name,width,height,Map,Playfield):
MazeWorld = cf.World(name='Maze',width=48,height=64,Map=[[]],Playfield=[[]],CurrentRoomH = 0,CurrentRoomV=3,DisplayH=0,DisplayV=48)
MazeWorld.CurrentRoomH = 0
MazeWorld.CurrentRoomV = 3




MazeWorld.Map[0]  = ([14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14, 14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14, 14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,])    
MazeWorld.Map[1]  = ([14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14,])
MazeWorld.Map[2]  = ([14, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0, 0, 0, 0,25, 0, 0, 0, 0,25, 0, 0, 0, 0,14, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0,14,])
MazeWorld.Map[3]  = ([14, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0, 0, 0, 0,25, 0, 0, 0, 0,25, 0, 0, 0, 0,14, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0,14,])
MazeWorld.Map[4]  = ([14, 0, 0,25,25,25,25, 0, 0, 0, 0,25, 0, 0, 0,14, 14, 0, 0, 0, 0,25, 0, 0, 0, 0,25, 0, 0, 0, 0,14, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0,14,])
MazeWorld.Map[5]  = ([14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0, 0,14, 14, 0, 0,25,25,25, 0, 0, 0, 0,25,25,25, 0, 0,14, 14, 0,25,25,25,25,25, 0, 0, 0,25, 0, 0, 0, 0,14,])
MazeWorld.Map[6]  = ([14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0, 0,14, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0, 0, 0, 0, 0,25, 0, 0, 0,25, 0, 0, 0, 0,14,])
MazeWorld.Map[7]  = ([14, 0, 0,25,25,25,25,25,25, 0, 0,25, 0, 0, 0,21, 21, 0, 0,25,25,25,25, 0, 0,25,25,25,25, 0, 0,21, 21, 0, 0, 0, 0, 0,25, 0, 0, 0,25, 0, 0, 0, 0,14,])
MazeWorld.Map[8]  = ([14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0, 0,14, 14, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0,14, 14, 0, 0, 0, 0, 0,25, 0, 0, 0,25, 0, 0, 0, 0,14,])
MazeWorld.Map[9]  = ([14, 0, 0, 0, 0,25, 0, 0, 0, 0, 0,25, 0, 0, 0,14, 14, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0,14, 14, 0, 0, 0, 0, 0,25, 0, 0, 0,25, 0, 0, 0, 0,14,])
MazeWorld.Map[10] = ([14, 0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0,14, 14, 0, 0, 0, 0, 0,25, 0, 0, 0,25, 0, 0, 0, 0,14,])
MazeWorld.Map[11] = ([14, 0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0,14, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14,])
MazeWorld.Map[12] = ([14, 0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0, 0,25, 0, 0, 0,25,25, 0, 0, 0,25, 0, 0,14, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14,])
MazeWorld.Map[13] = ([14, 0, 0, 0, 0,25,25,25,25,25,25,25, 0, 0, 0,14, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0, 0,25,25,25,25,25,25,25,25,25,25, 0, 0,14,])
MazeWorld.Map[14] = ([14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14,])
MazeWorld.Map[15] = ([14,14,14,14,14,14,14,21,14,14,14,14,14,14,14,14, 14,14,14,14,14,14,14,21,14,14,14,14,14,14,14,14, 14,14,14,14,14,14,14,21,14,14,14,14,14,14,14,14,])

MazeWorld.Map[16] = ([14,14,14,14,14,14,14,21,14,14,14,14,14,14,14,14, 14,14,14,14,14,14,14,21,14,14,14,14,14,14,14,14, 14,14,14,14,14,14,14,21,14,14,14,14,14,14,14,14,])    
MazeWorld.Map[17] = ([14, 0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14,])
MazeWorld.Map[18] = ([14, 0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14,])
MazeWorld.Map[19] = ([14, 0, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0,14, 14, 0, 0,25,25,25,25, 0, 0,25,25,25,25, 0, 0,14, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14,])
MazeWorld.Map[20] = ([14, 0, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0,14, 14, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0,14, 14, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0,14,])
MazeWorld.Map[21] = ([14, 0, 0, 0, 0, 0,25, 0, 0, 0,25, 0, 0, 0, 0,14, 14, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0,14, 14, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0,14,])
MazeWorld.Map[22] = ([14, 0, 0, 0, 0, 0,25,25,25,25,25, 0, 0, 0, 0,14, 14, 0, 0, 0, 0, 0,25,25,25,25, 0, 0, 0, 0, 0,14, 14, 0, 0,25,25,25,25,25,25,25,25,25,25, 0, 0,14,])
MazeWorld.Map[23] = ([14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,21, 21, 0, 0, 0, 0, 0,25,26,26,25, 0, 0, 0, 0, 0,21, 21, 0, 0, 0, 0, 0,25, 0,25, 0, 0, 0, 0, 0, 0,14,])
MazeWorld.Map[24] = ([14, 0,25,25,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0, 0, 0, 0, 0,25,26,26,25, 0, 0, 0, 0, 0,14, 14, 0, 0, 0, 0, 0,25, 0,25, 0, 0, 0, 0, 0, 0,14,])
MazeWorld.Map[25] = ([14, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0, 0,25, 0, 0,25,25,25,25, 0, 0,25, 0, 0,14, 14, 0, 0, 0, 0, 0,25, 0,25, 0, 0, 0, 0, 0, 0,14,])
MazeWorld.Map[26] = ([14, 0, 0, 0,25, 0, 0, 0, 0,25,25,25,25, 0, 0,14, 14, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0,14, 14, 0, 0, 0, 0, 0,25, 0,25, 0, 0, 0, 0, 0, 0,14,])
MazeWorld.Map[27] = ([14, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0,14, 14, 0, 0, 0, 0, 0,25, 0,25, 0, 0, 0, 0, 0, 0,14,])
MazeWorld.Map[28] = ([14, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0, 0,25,25,25,25, 0, 0,25,25,25,25, 0, 0,14, 14, 0, 0, 0, 0, 0,25, 0,25, 0, 0, 0, 0, 0, 0,14,])
MazeWorld.Map[29] = ([14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14,])
MazeWorld.Map[30] = ([14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14,])
MazeWorld.Map[31] = ([14,14,14,14,14,14,14,21,14,14,14,14,14,14,14,14, 14,14,14,14,14,14,14,21,14,14,14,14,14,14,14,14, 14,14,14,14,14,14,14,21,14,14,14,14,14,14,14,14,])

MazeWorld.Map[32] = ([14,14,14,14,14,14,14,21,14,14,14,14,14,14,14,14, 14,14,14,14,14,14,14,21,14,14,14,14,14,14,14,14, 14,14,14,14,14,14,14,21,14,14,14,14,14,14,14,14,])    
MazeWorld.Map[33] = ([14, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14,])
MazeWorld.Map[34] = ([14, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0, 0, 0, 0, 0, 0, 0, 0,25,25,25,25, 0, 0,14, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14,])
MazeWorld.Map[35] = ([14, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0,14, 14, 0, 0, 0,25,25,25,25,25,25,25,25, 0, 0, 0,14,])
MazeWorld.Map[36] = ([14, 0, 0,25,25,25,25,25, 0, 0,25,25,25, 0, 0,14, 14, 0, 0,25,25,25,25, 0, 0, 0, 0, 0,25, 0, 0,14, 14, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14,])
MazeWorld.Map[37] = ([14, 0, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0,14, 14, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0,14, 14, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14,])
MazeWorld.Map[38] = ([14, 0, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0,14, 14, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0,14, 14, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14,])
MazeWorld.Map[39] = ([14, 0, 0,25,25, 0, 0, 0, 0, 0,25, 0, 0, 0, 0,21, 21, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,21, 21, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14,])
MazeWorld.Map[40] = ([14, 0, 0,25,25, 0, 0, 0, 0, 0,25, 0, 0, 0, 0,14, 14, 0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0, 0, 0,25, 0, 0,25,25,25, 0, 0, 0, 0, 0,14,])
MazeWorld.Map[41] = ([14, 0, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0,14, 14, 0, 0, 0, 0,25, 0, 0, 0, 0,25, 0, 0, 0, 0,14, 14, 0, 0, 0,25, 0, 0, 0, 0,25, 0, 0, 0, 0, 0,14,])
MazeWorld.Map[42] = ([14, 0, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0,14, 14, 0, 0, 0, 0,25, 0, 0, 0, 0,25, 0, 0, 0, 0,14, 14, 0, 0, 0,25, 0, 0, 0, 0,25, 0, 0, 0, 0, 0,14,])
MazeWorld.Map[43] = ([14, 0, 0,25,25,25,25,25, 0, 0,25,25,25, 0, 0,14, 14, 0, 0, 0, 0,25,25,25,25, 0,25, 0, 0, 0, 0,14, 14, 0, 0, 0,25, 0, 0, 0, 0,25, 0, 0, 0, 0, 0,14,])
MazeWorld.Map[44] = ([14, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0,25,25,25,25, 0,14, 14, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0,14,])
MazeWorld.Map[45] = ([14, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0,14,])
MazeWorld.Map[46] = ([14, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0,14,])
MazeWorld.Map[47] = ([14,14,14,14,14,14,14,21,14,14,14,14,14,14,14,14, 14,14,14,14,14,14,14,21,14,14,14,14,14,14,14,14, 14,14,14,14,14,14,14,21,14,14,14,14,14,14,14,14,])

MazeWorld.Map[48] = ([14,14,14,14,14,14,14,21,14,14,14,14,14,14,14,14, 14,14,14,14,14,14,14,21,14,14,14,14,14,14,14,14, 14,14,14,14,14,14,14,21,14,14,14,14,14,14,14,14,])    
MazeWorld.Map[49] = ([14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14,])
MazeWorld.Map[50] = ([14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0, 0, 0,25, 0, 0, 0, 0, 0, 0,25, 0, 0, 0,14,])
MazeWorld.Map[51] = ([14, 0, 0,25, 0, 0,25, 0, 0,25,25,25,25, 0, 0,14, 14, 0, 0,25,25,25,25,25,25,25,25,25,25, 0, 0,14, 14, 0, 0,25, 0, 0,25, 0, 0,25, 0, 0,25, 0, 0,14,])
MazeWorld.Map[52] = ([14, 0, 0,25, 0, 0,25, 0, 0,25, 0, 0,25, 0, 0,14, 14, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0,25, 0, 0,25, 0, 0, 0, 0,25, 0, 0,25, 0,14,])
MazeWorld.Map[53] = ([14, 0, 0,25, 0, 0,25, 0, 0,25, 0, 0,25, 0, 0,14, 14, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0, 0, 0,25, 0, 0, 0, 0, 0, 0,25, 0, 0, 0,14,])
MazeWorld.Map[54] = ([14, 0, 0,25,25,25,25, 0, 0,25, 0, 0,25, 0, 0,14, 14, 0, 0,25,25,25,25,25,25,25,25,25,25, 0, 0,14, 14, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0,14,])
MazeWorld.Map[55] = ([14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,21, 21, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0,21, 21, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14,])
MazeWorld.Map[56] = ([14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0,14, 14, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0,14,])
MazeWorld.Map[57] = ([14, 0, 0,25,25,25,25, 0, 0,25, 0, 0,25, 0, 0,14, 14, 0, 0,25,25,25,25,25,25,25,25,25,25, 0, 0,14, 14, 0, 0, 0,25, 0, 0, 0, 0, 0, 0,25, 0, 0, 0,14,])
MazeWorld.Map[58] = ([14, 0, 0,25, 0, 0,25, 0, 0,25, 0, 0,25, 0, 0,14, 14, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0,25, 0, 0,25, 0, 0, 0, 0,25, 0, 0,25, 0,14,])
MazeWorld.Map[59] = ([14, 0, 0,25, 0, 0,25, 0, 0,25, 0, 0,25, 0, 0,14, 14, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0, 0,25, 0, 0,25, 0, 0,25, 0, 0,25, 0, 0,14,])
MazeWorld.Map[60] = ([14, 0, 0,25, 0, 0,25, 0, 0,25,25,25,25, 0, 0,14, 14, 0, 0,25,25,25,25,25,25,25,25,25,25, 0, 0,14, 14, 0, 0, 0,25, 0, 0, 0, 0, 0, 0,25, 0, 0, 0,14,])
MazeWorld.Map[61] = ([14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14,])
MazeWorld.Map[62] = ([14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,14,])
MazeWorld.Map[63] = ([14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14, 14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14, 14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,])
  


def DeactivateMissiles():

  #Remove missiles from playfield
  Robot1Missile.alive     = 0
  Robot1Missile.exploding = 0
  Robot2Missile.alive     = 0
  Robot2Missile.exploding = 0
  Robot3Missile.alive     = 0
  Robot3Missile.exploding = 0
  Robot4Missile.alive     = 0
  Robot4Missile.exploding = 0


  RobotBobMissile.alive     = 0
  RobotBobMissile.exploding = 0
  
  HumanMissile1.alive     = 0
  HumanMissile2.exploding = 0

  MazeWorld.Playfield[Robot1Missile.h][Robot1Missile.v] = Empty
  MazeWorld.Playfield[Robot2Missile.h][Robot2Missile.v] = Empty
  MazeWorld.Playfield[Robot3Missile.h][Robot3Missile.v] = Empty
  MazeWorld.Playfield[Robot4Missile.h][Robot4Missile.v] = Empty
  MazeWorld.Playfield[RobotBobMissile.h][RobotBobMissile.v] = Empty
  MazeWorld.Playfield[HumanMissile1.h][HumanMissile1.v] = Empty
  MazeWorld.Playfield[HumanMissile2.h][HumanMissile2.v] = Empty
  
  
def DotZerkAdjustSpeed(Human,ShiftDirection):
  global CurrentGear
  global MaxGear
  #print ("DZAS - BEFORE CurrentGear CurrentSpeed ShiftDirection",CurrentGear,Human.speed, ShiftDirection)
   
  if (ShiftDirection == 'down'):
    CurrentGear = CurrentGear -1
  else:
    CurrentGear = CurrentGear +1
  
  if (CurrentGear >= MaxGear):
    CurrentGear = MaxGear
  elif (CurrentGear <= 0):
    CurrentGear = 0 
    
  Human.speed = Gear[CurrentGear]
  #print ("DZAS - AFTER CurrentGear CurrentSpeed ",CurrentGear,Human.speed)

  
def DotZerkDisplayDoors():
  Door1.Display()
  Door2.Display()
  Door3.Display()
  Door4.Display()
  

def DotZerkLockDoors():
  global DirectionOfTravel
  Door1.locked = 0
  Door2.locked = 0
  Door3.locked = 0
  Door4.locked = 0
  
  
  #print ("DZLD - Direction of Travel:",DirectionOfTravel)
  if (DirectionOfTravel == 1):
    #Lock the door
    Door3.locked = 1
    #print ("DZLD - Locking bottom door")
  elif (DirectionOfTravel == 2):
    Door4.locked = 1
    #print ("DZLD - Locking left door")
  elif (DirectionOfTravel == 3):
    #Lock the door
    Door1.locked = 1
    #print ("DZLD - Locking top door")
  elif (DirectionOfTravel == 4):
    Door2.locked = 1
    #print ("DZLD - Locking right door")
  
  DotZerkDisplayDoors()
  
  
  
def DotZerkResetPlayfield(ShowFlash):
  print ("DZRP - Emptying playfield")
  for x in range (0,gv.HatWidth):
    for y in range (0,gv.HatWidth):
      #print ("XY",x,y)
      MazeWorld.Playfield[x][y] = Empty
      
  #Put items on Playfield
  MazeWorld.CopyMapToPlayfield()
  MazeWorld.Playfield[Human.h][Human.v] = Human
  PlaceRobotOnPlayfield(Robot1)
  #PlaceRobotOnPlayfield(Robot2)
  #PlaceRobotOnPlayfield(Robot3)
  #PlaceRobotOnPlayfield(Robot4)
  
  DeactivateMissiles()
  MazeWorld.DisplayPlayfield(ShowFlash)
  #print ("DZRP - Displayed Playfield")
  DotZerkLockDoors()

  MazeWorld.Playfield[7][0] = Door1
  MazeWorld.Playfield[15][7] = Door2
  MazeWorld.Playfield[7][15] = Door3
  MazeWorld.Playfield[0][7] = Door4

  
def PlaceRobotOnPlayfield(Robot):
  h = random.randint(1,gv.HatWidth-1)
  v = random.randint(1,gv.HatWidth-1)
  #print ("PROP - HV",h,v)
  while (MazeWorld.Playfield[v][h].name != 'EmptyObject'):
    #print ("PROP - Looking:",MazeWorld.Playfield[v][h].name)
    h = random.randint(1,gv.HatWidth-1)
    v = random.randint(1,gv.HatWidth-1)
    #print ("PROP - HV",h,v)

  Robot.h = h
  Robot.v = v
  Robot.alive = 1
  MazeWorld.Playfield[v][h] = Robot
  #print ("PROP - Robot placed HV",h,v)
  

def CheckMazeBoundary():
  #Cant find the bug, putting in a work around for now
  #change hard coded values to calculated, based on size of map
  #cant do it now, late for work!
  if (MazeWorld.CurrentRoomH < 0):
    MazeWorld.CurrentRoomH = 0
    #For some reason, the current room is getting into the negatives
    print ("**************************************************************")
    print ("** Negative Room Number detected!! Resetting to a positive **")
    print ("**************************************************************")
  if (MazeWorld.CurrentRoomH > 2):
    MazeWorld.CurrentRoomH = 2
    #For some reason, the current room is getting into the negatives
    print ("**************************************************************")
    print ("** Negative Room Number detected!! Resetting to a positive **")
    print ("**************************************************************")
  if (MazeWorld.CurrentRoomV < 0):
    MazeWorld.CurrentRoomV = 0
    #For some reason, the current room is getting into the negatives
    print ("**************************************************************")
    print ("** Negative Room Number detected!! Resetting to a positive **")
    print ("**************************************************************")
  if (MazeWorld.CurrentRoomV > 3):
    MazeWorld.CurrentRoomV = 3
    #For some reason, the current room is getting into the negatives
    print ("**************************************************************")
    print ("** Negative Room Number detected!! Resetting to a positive **")
    print ("**************************************************************")

    
  
def DotZerkExitRoom(DoorDirection):
  global DotZerkScore
  cf.ClearBigLED()
  #Scroll Right
  #print ("DZER - DoorDirection:",DoorDirection)

  #Increase score
  DotZerkScore = DotZerkScore + 5
  DeactivateMissiles()
  print ("DZER - CurrentRoomH CurrentRoomV",MazeWorld.CurrentRoomH, MazeWorld.CurrentRoomV)
  
 
  

  
  if (DoorDirection == 1):
    MazeWorld.CurrentRoomV = MazeWorld.CurrentRoomV - 1
    CheckMazeBoundary()
    
    ScrollH = MazeWorld.CurrentRoomH *16
    ScrollV = MazeWorld.CurrentRoomV *16
        
    #We display the window gv.HatWidth times, moving it one column every time
    #this gives a neat scrolling effect
    for x in range (ScrollV*gv.HatWidth,ScrollV-1,-1):
      #print ("DZER X:",x)
      #print ("DZER calling DisplayWindow ScrollH x:",ScrollH,x)
      MazeWorld.DisplayWindow(ScrollH,x)
      #unicorn.show()
      #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
      #time.sleep(0.1)
     
    #Move human to other side of the playfield
    Human.v = 14
    
  

  


  if (DoorDirection == 3):
    MazeWorld.CurrentRoomV = MazeWorld.CurrentRoomV + 1
    CheckMazeBoundary()

    ScrollH = MazeWorld.CurrentRoomH *gv.HatWidth
    ScrollV = MazeWorld.CurrentRoomV *gv.HatWidth
        
    #We display the window gv.HatWidth times, moving it one column every time
    #this gives a neat scrolling effect
    for x in range (ScrollV-gv.HatWidth,ScrollV+1):
      #print ("DZER X:",x)
      #print ("DZER calling DisplayWindow ScrollH x:",ScrollH,x)
      MazeWorld.DisplayWindow(ScrollH,x)
      #unicorn.show()
      #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
      #time.sleep(0.01)
    
    #Move human to other side of the playfield
    Human.v = 1
    


  if (DoorDirection == 2):
    MazeWorld.CurrentRoomH = MazeWorld.CurrentRoomH + 1
    CheckMazeBoundary()

    ScrollH = MazeWorld.CurrentRoomH *gv.HatWidth
    ScrollV = MazeWorld.CurrentRoomV *gv.HatWidth
        
    #We display the window 8 times, moving it one column every time
    #this gives a neat scrolling effect
    for x in range (ScrollH-gv.HatWidth,ScrollH+1):
      #print ("DZER X:",x)
      #print ("DZER calling DisplayWindow x ScrollV:",x,ScrollV)
      MazeWorld.DisplayWindow(x,ScrollV)
      #unicorn.show()
      #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
      #time.sleep(0.1)
    
    #Move human to other side of the playfield
    Human.h = 1

    
  
  elif (DoorDirection == 4):
    MazeWorld.CurrentRoomH = MazeWorld.CurrentRoomH -1
    CheckMazeBoundary()
    ScrollH = MazeWorld.CurrentRoomH *gv.HatWidth
    ScrollV = MazeWorld.CurrentRoomV *gv.HatWidth
    #print("DZER - ScrollHV",ScrollH,ScrollV)
    for x in range (ScrollH*gv.HatWidth,ScrollH-1,-1):
      #print ("DZER X:",x)
      #print ("DZER calling DisplayWindow x ScrollV:",x,ScrollV)
      MazeWorld.DisplayWindow(x,ScrollV)
      #unicorn.show()
      #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
      #time.sleep(0.1)

    #Move human to other side of the playfield
    Human.h = 6

      
  
  DotZerkResetPlayfield(0)
  


def DotZerkExplodeMissile(Ship,Playfield,increment):
  
  Ship.r = Ship.r + increment
  Ship.g = 0 #Ship.g + increment
  Ship.b = 0 #Ship.b + increment

  #After explosion, reset colors
  if (Ship.r >= 400 or Ship.g >= 400 or Ship.b >= 400):
    if (Ship.name == 'HumanMissile'):
      Ship.r = HumanMissileR
      Ship.g = HumanMissileG
      Ship.b = HumanMissileB
    elif (Ship.name == 'RobotMissile'):
      Ship.r = RobotMissileR
      Ship.g = RobotMissileG
      Ship.b = RobotMissileB

    Ship.exploding = 0
    Ship.alive     = 0
    #print ("+++++++++++++++++++++++++++++++++++++")
    #print ("Missile Exploded")
    #print ("+++++++++++++++++++++++++++++++++++++")
    Ship.Erase()
    Playfield[Ship.v][Ship.h].alive = 0
    Playfield[Ship.v][Ship.h] = Empty
    
      

  if (Ship.exploding == 1):
    r = Ship.r
    g = Ship.g
    b = Ship.b
    if (r > 255):
      r = 255
    if (g > 255):
      g = 255
    if (b > 255):
      b = 255
    cf.setpixel(Ship.h,Ship.v,r,g,b)
#  #print("DZEM - Ship.exploding: ",Ship.exploding)
#  print("DZEM - After: ",Ship.name, "HV",Ship.h,Ship.v," rgb",Ship.r,Ship.g,Ship.b)
  

def DotZerkExplodeRobot(Robot,Playfield,increment):
  global RobotsAlive
  global DotZerkScore
  
  Robot.r = Robot.r + increment
  Robot.g = Robot.g + increment
  Robot.b = 0 #Robot.b + increment

  #After explosion, reset colors
  if (Robot.r >= 400 or Robot.g >= 400 or Robot.b >= 400):
    Robot.r = cf.SDLowRedR
    Robot.g = cf.SDLowRedR
    Robot.b = cf.SDLowRedR

    Robot.exploding = 0
    Robot.alive     = 0
    #print ("+++++++++++++++++++++++++++++++++++++")
    #print ("ROBOT Exploded")
    #print ("+++++++++++++++++++++++++++++++++++++")
    Robot.Erase()
    Playfield[Robot.h][Robot.v].alive = 0
    Playfield[Robot.h][Robot.v] = Empty

    RobotsAlive = RobotsAlive -1
    if (RobotsAlive < 0):
      RobotsAlive = 0

    DotZerkScore = DotZerkScore + 5


  if (Robot.exploding == 1):
    r = Robot.r
    g = Robot.g
    b = Robot.b
    if (r > 255):
      r = 255
    if (g > 255):
      g = 255
    if (b > 255):
      b = 255
    cf.setpixel(Robot.h,Robot.v,r,g,b)  



def PrintDoorStatus():
  print ("=====THE DOORS===============================")
  print ("Door1 alive locked:",Door1.alive,Door1.locked)
  print ("Door2 alive locked:",Door2.alive,Door2.locked)
  print ("Door3 alive locked:",Door3.alive,Door3.locked)
  print ("Door4 alive locked:",Door4.alive,Door4.locked)
  print ("=============================================")


def DotZerkScanDot(h,v,Playfield):
# border
# empty
# wall

  #print ("DZSD - HV:",h,v)
  Item = 'Wall'
  OutOfBounds = cf.CheckBoundary(h,v)
  #print ("DZSD - OutOfBounds:",OutOfBounds)
  
  if (OutOfBounds == 1):
    Item = 'border'
    #print ("DZSD - Border found HV: ",h,v)
  else:
    #FlashDot(h,v,0.005)
    #print ("DZSD - Not out of bounds")

    #Doors need to be unlocked to be visible
    #print ("DZSD - Name Scanned:",Playfield[v][h].name)
    
    if (h == 7 and v == 0):
      #print ("DZSD - Top door being examined")    
      if (Door1.alive == 1 and Door1.locked == 0):
        Item = 'Door'
    elif (h == 15 and v == 7):
      #print ("DZSD - right door being examined")    
      if (Door2.alive == 1 and Door2.locked == 0):
        Item = 'Door'
    elif (h == 7 and v == 15):
      #print ("DZSD - Bottom door being examined")    
      if (Door3.alive == 1 and Door3.locked == 0):
        Item = 'Door'
    elif (h == 0 and v == 7):
      #print ("DZSD - left door being examined")    
      if (Door4.alive == 1 and Door4.locked == 0):
        Item = 'Door'
    else:
      #print ("DZSD - Not a door...then what is it? ",Playfield[v][h].name)
      Item = Playfield[v][h].name
      
      
  if (Item == ''):
    print ('REeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee!')
    print ('REeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee!')
    print ('REeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee!')
    print ('REeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee!')
    print ('REeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee!')
    #time.sleep(5)  
  return Item


def DotZerkScanHuman(h,v,direction,Playfield):

  #Scans cannot go through walls.  If a wall is encountered (forward) than all subsequent items will be the wall
  

  ScanDirection = direction
  ScanH         = 0
  ScanV         = 0
  Item          = ''
  ItemList      = ['NULL']
  WallHit       = 0

  

#          16
#          15
#          14
#          13
#          12
#          11
#          10                             
#           9                             
#           8                             
#           7                            
#           6                              
#        2  3   4                            
#        1      5
                                           

  #print("--------------------------------------------")     
  #print("DZSH - hv direction",h,v,direction)
  
  #1
  ScanDirection = cf.TurnLeft(ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(h,v,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV)
  ItemList.append(Item)
  #print ("DZSH1 - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #2
  ScanDirection =  cf.TurnRight(ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV)
  ItemList.append(Item)
  #print ("DZSH2 - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #3
  ScanDirection =  cf.TurnRight(ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV)
  if (Item == 'Wall' or WallHit == 1):
    ItemList.append('Wall')
    WallHit = 1
  else:
    ItemList.append(Item)
  #print ("DZSH3 - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #4
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV)
  ItemList.append(Item)
  #print ("DZSH - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #5
  ScanDirection =  cf.TurnRight(ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV)
  ItemList.append(Item)
  #print ("DZSH - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)

  #6
  ScanDirection =  cf.TurnRight(ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  ScanDirection =  cf.TurnRight(ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV)
  if (Item == 'Wall' or WallHit == 1):
    ItemList.append('Wall')
    WallHit = 1
  else:
    ItemList.append(Item)
  #print ("DZSH - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)

  #7
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV)
  if (Item == 'Wall' or WallHit == 1):
    ItemList.append('Wall')
    WallHit = 1
  else:
    ItemList.append(Item)
  #print ("DZSH - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)

  #8
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV)
  if (Item == 'Wall' or WallHit == 1):
    ItemList.append('Wall')
    WallHit = 1
  else:
    ItemList.append(Item)
  #print ("DZSH - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #9
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV)
  if (Item == 'Wall' or WallHit == 1):
    ItemList.append('Wall')
    WallHit = 1
  else:
    ItemList.append(Item)
  #print ("DZSH - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #10
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV)
  if (Item == 'Wall' or WallHit == 1):
    ItemList.append('Wall')
    WallHit = 1
  else:
    ItemList.append(Item)
  #print ("DZSH - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #11
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV)
  if (Item == 'Wall' or WallHit == 1):
    ItemList.append('Wall')
    WallHit = 1
  else:
    ItemList.append(Item)
  #print ("DZSH - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #12
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV)
  if (Item == 'Wall' or WallHit == 1):
    ItemList.append('Wall')
    WallHit = 1
  else:
    ItemList.append(Item)
  #print ("DZSH - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  

  #13
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV)
  if (Item == 'Wall' or WallHit == 1):
    ItemList.append('Wall')
    WallHit = 1
  else:
    ItemList.append(Item)
  #print ("DZSH - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)

  
  #14
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV)
  if (Item == 'Wall' or WallHit == 1):
    ItemList.append('Wall')
    WallHit = 1
  else:
    ItemList.append(Item)
  #print ("DZSH - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)

  
  
  #15
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV)
  if (Item == 'Wall' or WallHit == 1):
    ItemList.append('Wall')
    WallHit = 1
  else:
    ItemList.append(Item)
  #print ("DZSH - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)

  
  
  #16
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV)
  if (Item == 'Wall' or WallHit == 1):
    ItemList.append('Wall')
    WallHit = 1
  else:
    ItemList.append(Item)
  #print ("DZSH - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)

  
  return ItemList;



def DotZerkScanStraightLine(h,v,direction,Playfield):
  ScanDirection = direction
  ScanH         = 0
  ScanV         = 0
  Item          = ''
  ItemList      = ['NULL']
  WallHit       = 0

#          12
#          11
#          10
#           9
#           8
#           7
#           6
#           5                             
#           4                             
#           3                             
#           2                            
#           1                              
                                           

  #print ("")
  #print("== DZ Scan Straight Line")     
  #print("DZSSL - hv direction",h,v,direction)
  
  #1
  ScanH, ScanV = cf.CalculateDotMovement(h,v,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV)
  if (Item == 'Wall' or WallHit == 1):
    ItemList.append('Wall')
    WallHit = 1
  else:
    ItemList.append(Item)
  #print ("DZSSL - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #2
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV)
  if (Item == 'Wall' or WallHit == 1):
    ItemList.append('Wall')
    WallHit = 1
  else:
    ItemList.append(Item)
  #print ("DZSSL - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #3
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV)
  if (Item == 'Wall' or WallHit == 1):
    ItemList.append('Wall')
    WallHit = 1
  else:
    ItemList.append(Item)
  #print ("DZSSL - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #4
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV)
  if (Item == 'Wall' or WallHit == 1):
    ItemList.append('Wall')
    WallHit = 1
  else:
    ItemList.append(Item)
  #print ("DZSH - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #5
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV)
  if (Item == 'Wall' or WallHit == 1):
    ItemList.append('Wall')
    WallHit = 1
  else:
    ItemList.append(Item)
  #print ("DZSH - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)

  #6
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV)
  if (Item == 'Wall' or WallHit == 1):
    ItemList.append('Wall')
    WallHit = 1
  else:
    ItemList.append(Item)
  #print ("DZSH - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)

  #7
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV)
  if (Item == 'Wall' or WallHit == 1):
    ItemList.append('Wall')
    WallHit = 1
  else:
    ItemList.append(Item)

  #print ("DZSH - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)

  #87
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV)
  if (Item == 'Wall' or WallHit == 1):
    ItemList.append('Wall')
    WallHit = 1
  else:
    ItemList.append(Item)
  #print ("DZSH - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  #8
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV)
  if (Item == 'Wall' or WallHit == 1):
    ItemList.append('Wall')
    WallHit = 1
  else:
    ItemList.append(Item)
  #print ("DZSH - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)

  #10
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV)
  if (Item == 'Wall' or WallHit == 1):
    ItemList.append('Wall')
    WallHit = 1
  else:
    ItemList.append(Item)
  #print ("DZSH - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)

  #11
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV)
  if (Item == 'Wall' or WallHit == 1):
    ItemList.append('Wall')
    WallHit = 1
  else:
    ItemList.append(Item)
  #print ("DZSH - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)

  #12
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV)
  if (Item == 'Wall' or WallHit == 1):
    ItemList.append('Wall')
    WallHit = 1
  else:
    ItemList.append(Item)
  #print ("DZSH - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  return ItemList;



  

  
def DotZerkScanRobot(h,v,direction,Playfield):
  ScanDirection = direction
  ScanH         = 0
  ScanV         = 0
  Item          = ''
  ItemList      = ['NULL']
#          12
#          11
#          10                             
#           9                             
#           8                             
#           7                            
#           6                              
#        2  3   4                            
#        1      5
                                           

  #print("--------------------------------------------")     
  #print("DZSH - hv direction",h,v,direction)
  
  #1
  ScanDirection = cf.TurnLeft(ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(h,v,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV)
  ItemList.append(Item)
#  #print ("DZSR1 - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #2
  ScanDirection =  cf.TurnRight(ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV)
  ItemList.append(Item)
#  print ("DZSR2 - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #3
  ScanDirection =  cf.TurnRight(ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV)
  ItemList.append(Item)
#  print ("DZSR3 - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #4
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV)
  ItemList.append(Item)
#  print ("DZSR - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #5
  ScanDirection =  cf.TurnRight(ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV)
  ItemList.append(Item)
#  print ("DZSR - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)

  #6
  ScanDirection =  cf.TurnRight(ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  ScanDirection =  cf.TurnRight(ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV)
  ItemList.append(Item)
#  print ("DZSR - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)

  #7
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV)
  ItemList.append(Item)
#  print ("DZSR - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)

  #8
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV)
  ItemList.append(Item)
#  print ("DZSR - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #9
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV)
  ItemList.append(Item)
#  print ("DZSR - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #10
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV)
  ItemList.append(Item)
#  print ("DZSR - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #11
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV)
  ItemList.append(Item)
#  print ("DZSR - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #12
  ScanH, ScanV = cf.CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV)
  ItemList.append(Item)
#  print ("DZSR - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  
  return ItemList;


  

  
  

      
def DotZerkMoveMissile(Missile,Ship,Playfield):

  #The ship being passed in is the object that launched the missile
  
  global Empty
  #print ("DZMM - MoveMissile:",Missile.name)
  
  #Record the current coordinates
  h = Missile.h
  v = Missile.v

#  if (Ship.name != "Human"):
#    cf.FlashDot(h,v,0.01)
  
  #FF (one square in front of missile direction of travel)
  ScanH, ScanV = cf.CalculateDotMovement(Missile.h,Missile.v,Missile.scandirection)
  Item = DotZerkScanDot(ScanH,ScanV)
  
  #print("DZMM Item: ",Item)
  
  #Priority
  # 1 Hit target
  # 2 See if we are hit by enemy missle
  # 3 Move forward

  #print ("DZMM - Item Name", Item)

  
  #Don't blow up yourself
  if (Item == Ship.name):
    #print ("DZMM - Abort missile!  Don't hit your own launch vehicle")
    Missile.exploding = 1
    Missile.alive = 0

    
  
  #See if other target ship is hit
  elif (Item  == 'Human' or Item == 'Robot' or Item == 'RobotMissile' or Item == "HumanMissile" ):
    #target hit, kill target
    #print ("*********************************")
    #print ("DZMM - Target Hit!")
    #print ("DZMM - Item Name", Item)
    Playfield[ScanV][ScanH].alive = 0
    Playfield[ScanV][ScanH].exploding = 1
    Playfield[ScanV][ScanH]= Empty
    cf.setpixel(ScanH,ScanV,0,0,0)
      
      
    #print ("*********************************")
    Missile.h = ScanH
    Missile.v = ScanV
    Missile.Display()
    Missile.exploding = 1
    Missile.alive = 0
    
  
  
  
  #Missiles explode on walls
  elif (Item == 'border' or Item == 'Wall' or Item == 'Door'):
    #print ("DZMM - Missile hit border/wall/door")
    Missile.alive  = 0
    Missile.exploding = 1
    Missile.Erase()
    
  #empty = move forward
  elif (Item == 'EmptyObject' and Missile.alive == 1):
    Missile.h = ScanH
    Missile.v = ScanV
    Playfield[ScanV][ScanH] = Missile
    Missile.Display()
    #print ("DZMM - empty, moving forward")
    
  #Keep missiles away from outer walls
  if (Missile.h == 15):
    Missile.h = 14
  if (Missile.h == 0):
    Missile.h = 1
  if (Missile.v == 15):
    Missile.v = 14
  if (Missile.v == 0):
    Missile.v = 1
    
    
  #Erase missile's old position
  if ((h != Missile.h or v != Missile.v) or
     (Missile.alive == 0)):
    if (Playfield[v][h].name != 'Wall' and Playfield[v][h].name != 'Door'):
      Playfield[v][h] = Empty
      cf.setpixel(h,v,0,0,0)
      #print ("DZMM - Erasing Missile")
  #unicorn.show()
  
  #Display Ship to avoid strange flicker when the objects are too close to each other
  Ship.Display()
  
  return 

  
def DotZerkMoveRobot(Robot,Human,RadarChance, Playfield):
  #print ("DZMR - Name Direction HV:",Robot.name,Robot.direction,Robot.h,Robot.v)
  
  h = Robot.h
  v = Robot.v
  direction = Robot.scandirection
  ItemList = []
  HumanDetected = 0
 
  
  
  #Scan all around, make decision, move
  ItemList = DotZerkScanRobot(Robot.h,Robot.v,direction,Playfield)
  #print("DZMR - ItemList: ",ItemList)    
  #get possible items, then prioritize

  #Priority
  # 1 Shoot Player
  

  #If player is detected, fire missile!
  if ("Human" in ItemList):
    if (Robot1Missile.alive == 0 and Robot1Missile.exploding == 0):
      #print ("############################################")
      #print ("DZMR - Firing missile1 at human")
      Robot1Missile.h, Robot1Missile.v = h,v
      Robot1Missile.direction     = direction
      Robot1Missile.scandirection = direction
      Robot1Missile.alive = 1
      direction = cf.ReverseDirection(direction)
      #Robot.direction     = cf.ReverseDirection(Robot.direction)
      #Robot.scandirection = cf.ReverseDirection(Robot.scandirection)
      #print ("DZMR - robot missile HV",Robot1Missile.h,Robot1Missile.v)
      #print ("############################################")

    
    #We don't want both missiles firing at the same time, so we use elif
    elif (Robot2Missile.alive == 0 and Robot2Missile.exploding == 0):
      #print ("############################################")
      #print ("DZMR - Firing missile2 at human")
      Robot2Missile.h, Robot2Missile.v = h,v
      Robot2Missile.direction     = direction
      Robot2Missile.scandirection = direction
      Robot2Missile.alive = 1
      #Robot.direction     = cf.ReverseDirection(Robot.direction)
      #Robot.scandirection = cf.ReverseDirection(Robot.scandirection)
      #print ("DZMR - robot missile HV",Robot2Missile.h,Robot2Missile.v)
      #print ("############################################")

    elif (Robot3Missile.alive == 0 and Robot3Missile.exploding == 0):
      #print ("############################################")
      #print ("DZMR - Firing missile3 at human")
      Robot3Missile.h, Robot3Missile.v = h,v
      Robot3Missile.direction     = direction
      Robot3Missile.scandirection = direction
      Robot3Missile.alive = 1
      direction = cf.ReverseDirection(direction)
      #Robot.direction     = cf.ReverseDirection(Robot.direction)
      #Robot.scandirection = cf.ReverseDirection(Robot.scandirection)
      #print ("DZMR - robot missile HV",Robot3Missile.h,Robot2Missile.v)
      #print ("############################################")


    elif (Robot4Missile.alive == 0 and Robot4Missile.exploding == 0):
      #print ("############################################")
      #print ("DZMR - Firing missile4 at human")
      Robot4Missile.h, Robot4Missile.v = h,v
      Robot4Missile.direction     = direction
      Robot4Missile.scandirection = direction
      Robot4Missile.alive = 1
      direction = cf.ReverseDirection(direction)
      #Robot.direction     = cf.ReverseDirection(Robot.direction)
      #Robot.scandirection = cf.ReverseDirection(Robot.scandirection)
      #print ("DZMR - robot missile HV",Robot3Missile.h,Robot2Missile.v)
      #print ("############################################")

      
    
  if ((ItemList[1] == 'border' or ItemList[1] == 'Wall' or ItemList[1] == 'Door' or ItemList[1] == 'Robot')
  and (ItemList[3] == 'border' or ItemList[3] == 'Wall' or ItemList[3] == 'Door' or ItemList[3] == 'Robot')
  and (ItemList[5] == 'border' or ItemList[5] == 'Wall' or ItemList[5] == 'Door' or ItemList[1] == 'Robot')):
    #print ("Reversing direction")
    direction = cf.ReverseDirection(direction)
    
  #Left Corner
  elif ((ItemList[3] == 'border' or ItemList[3] == 'Wall' or ItemList[3] == 'Door')
    and (ItemList[1] == 'border' or ItemList[1] == 'Wall' or ItemList[1] == 'Door')
    and (ItemList[5] == 'EmptyObject')):
    #print ("Turn right")
    direction =  cf.TurnRight(direction)

  #Right Corner
  elif ((ItemList[3] == 'border' or ItemList[3] == 'Wall' or ItemList[3] == 'Door')
    and (ItemList[5] == 'border' or ItemList[5] == 'Wall' or ItemList[5] == 'Door')
    and (ItemList[1] == 'EmptyObject')):
    #print ("Turn left")
    direction = cf.TurnLeft(direction)
    
  
  #middle of wall
  elif ((ItemList[1] == 'EmptyObject')
    and (ItemList[3] == 'border' or ItemList[3] == 'Wall' or ItemList[3] == 'Door')
    and (ItemList[5] == 'EmptyObject')):
    
    #print ("Turn left or right")
    direction = cf.TurnLeftOrRight(direction)

  
  #elif (ItemList[5] == 'EmptyObject'):
    #print("Go straigt")
  
  #elif (ItemList[1] == 'EmptyObject' and ItemList[5] == 'Wall'):
    #print ("go straight")

    
  #else:
    #print ("keep on truckin forward")

    

  #determine new path
  #check the radar -- if RadarChance happens, it will modify Robot.direction to point towards human
  HumanDetected = CheckRobotRadar(Robot,Human,RadarChance)
  if (HumanDetected == 1):
    direction = Robot.direction
  else:
    Robot.direction  = direction
    Robot.scandirection = direction      

  Robot.h, Robot.v =  cf.CalculateDotMovement(h,v,direction)
   
  
  
  #Prevent Robot from going into the walls
  if (Robot.h >= 15):
    Robot.h = 14
  if (Robot.v >= 15):
    Robot.v = 14
  if (Robot.h <= 0):
    Robot.h = 1
  if (Robot.v <= 0):
    Robot.v = 1

  
    
  #print("DZMR - OldHV: ",h,v, " NewHV: ",Robot.h,Robot.v, "direction: ",Robot.direction)
  Playfield[Robot.h][Robot.v]= Robot
  Robot.Display()
  
  #Robot has moved or died
  if ((h != Robot.h or v != Robot.v) or (Robot.alive == 0)):
    if (Playfield[v][h].name != 'Wall' and Playfield[v][h].name != 'Door' ):
      Playfield[v][h] = Empty
      cf.setpixel(h,v,0,0,0)
    #print ("DZMR - Erasing Robot")
  #unicorn.show()

  
  return 

  




def DotZerkMoveHuman(Human,Playfield):
  global ExitingRoom
  global RobotsAlive
  global CurrentGear
  
  #print ("")
  #print ("== DZ Move Human ==")
  #print ("DZMH - MoveHuman HV Direction:",Human.h,Human.v,Human.direction)
  #print ("DZMH - RobotsAlive:",RobotsAlive)
  h = Human.h
  v = Human.v
  oldh  = h
  oldv  = v
  ScanH = 0
  ScanV = 0
  direction = Human.scandirection
  ItemList = []

  #PrintDoorStatus()
  
  #Scan left, right, behind looking for robots only
  #print("DZMH - Scan Right")
  direction =  cf.TurnRight(direction)
  ItemList = DotZerkScanStraightLine(h,v,direction,Playfield)
  #print (ItemList)
  if ("Robot" in ItemList or "RobotMissile" in ItemList):
    print ("Robot to the right HumanMissile2.alive:",HumanMissile2.alive,HumanMissile2.exploding)
    if (HumanMissile2.alive == 0 and HumanMissile2.exploding == 0):
      HumanMissile2.h, HumanMissile2.v = cf.CalculateDotMovement(h,v,direction)
      HumanMissile2.alive              = 1
      HumanMissile2.scandirection      = direction
      HumanMissile2.direction          = direction
      HumanMissile2.exploding          = 0
      #print("DZMH - FireMissile2 alive scandirection exploding",HumanMissile2.alive,HumanMissile2.scandirection,HumanMissile2.exploding)
      DotZerkAdjustSpeed(Human,'up')
  
  #we don't want the human to shoot, turn around, then do this scan and shoot again.
  #Reverse shots only work with Missile1
  #print("DZMH - Scan behind")
  direction =  cf.TurnRight(direction)
  ItemList = DotZerkScanStraightLine(h,v,direction,Playfield)
  #print (ItemList)
  if ("Robot" in ItemList or "RobotMissile" in ItemList):
    print ("Robot behind us HumanMissile2.alive exploding:",HumanMissile1.alive,HumanMissile1.exploding)
    if (HumanMissile1.alive == 0 and HumanMissile1.exploding == 0):
      HumanMissile1.h, HumanMissile1.v = cf.CalculateDotMovement(h,v,direction)
      HumanMissile1.alive              = 1
      HumanMissile1.scandirection      = direction
      HumanMissile1.direction          = direction
      HumanMissile1.exploding          = 0
      #print("DZMH - FireMissile1 alive scandirection exploding",HumanMissile1.alive,HumanMissile1.scandirection,HumanMissile1.exploding)
      DotZerkAdjustSpeed(Human,'up')

  #print("DZMH - Scan Left")
  direction =  cf.TurnRight(direction)
  ItemList = DotZerkScanStraightLine(h,v,direction,Playfield)
  print (ItemList)
  if ("Robot" in ItemList or "RobotMissile" in ItemList):
    print ("Robot to the left HumanMissile2.alive:",HumanMissile2.alive,HumanMissile2.exploding)
    if (HumanMissile2.alive == 0 and HumanMissile2.exploding == 0):
      HumanMissile2.h, HumanMissile2.v = cf.CalculateDotMovement(h,v,direction)
      HumanMissile2.alive              = 1
      HumanMissile2.scandirection      = direction
      HumanMissile2.direction          = direction
      HumanMissile2.exploding          = 0
      #print("DZMH - FireMissile2 alive scandirection exploding",HumanMissile2.alive,HumanMissile2.scandirection,HumanMissile2.exploding)
      DotZerkAdjustSpeed(Human,'up')
      
  #Back to original direction (we did a 360)      
  #print("DZMH - Scan in front")
  direction =  cf.TurnRight(direction)

  #Scan all around, make decision, move
  ItemList = DotZerkScanHuman(h,v,direction,Playfield)
  
  #print("DZMH - ItemList",ItemList)
  #print("DZMH - Human.name HV",Human.name,Human.h,Human.v)
  #get possible items, then prioritize

  #Priority
  # 1 Evade close objects
  # 2 Blast far objects
  # 3 Follow right hand rule (or left hand rule, possibly different per room?)

  #Prevent collision of Robot and Human
  if (ItemList[3] == 'Robot'):
    #print ("DZMH - Robot detected immediately in front of human")
    ScanH,ScanV = cf.CalculateDotMovement(h,v,direction)
    Playfield[ScanV][ScanH].alive = 0
    Playfield[ScanV][ScanH].exploding = 1
  
  
  #If Robot is detected, fire missile!
  #and reverse direction
  if ("Robot" in ItemList or "RobotMissile" in ItemList):
    if (HumanMissile1.alive == 0 and HumanMissile1.exploding == 0):
      print ("***********************************")
      print ("DZMH - Robot/RobotMissile Detected ")
      print ("***********************************")
      HumanMissile1.h, HumanMissile1.v = cf.CalculateDotMovement(h,v,direction)
#      HumanMissile1.h, HumanMissile1.v = h,v
      HumanMissile1.alive = 1
      HumanMissile1.scandirection = direction
      HumanMissile1.exploding = 0
      direction = cf.ReverseDirection(direction)
      #print ("DZMH - Launching missile HV",HumanMissile1.h,HumanMissile1.v)
      #print ("DZMH - missile direction",HumanMissile1.direction)
      DotZerkAdjustSpeed(Human,'up')
      DotZerkAdjustSpeed(Human,'up')
      DotZerkAdjustSpeed(Human,'up')

  
  #Behave differently if all robots are dead
  if (RobotsAlive == 0):
    #print ("DZMH - Robots dead")
    if ((ItemList[1] == 'border' or ItemList[1] == 'Wall' or ItemList[1] == 'RobotMissile' or ItemList[1] == 'HumanMissile')
    and (ItemList[3] == 'border' or ItemList[3] == 'Wall' or ItemList[3] == 'RobotMissile' or ItemList[3] == 'HumanMissile')
    and (ItemList[5] == 'border' or ItemList[5] == 'Wall' or ItemList[5] == 'RobotMissile' or ItemList[5] == 'HumanMissile')):
      print ("Reversing direction")
      direction = cf.ReverseDirection(direction)
      Human.h, Human.v =  cf.CalculateDotMovement(h,v,direction)
      DotZerkAdjustSpeed(Human,'up')
      DotZerkAdjustSpeed(Human,'up')
      DotZerkAdjustSpeed(Human,'up')

    #Left Corner
    elif ((ItemList[3] == 'border' or ItemList[3] == 'Wall' or ItemList[3] == 'RobotMissile' or ItemList[3] == 'HumanMissile')
      and (ItemList[1] == 'border' or ItemList[1] == 'Wall' or ItemList[1] == 'RobotMissile' or ItemList[1] == 'HumanMissile')
      and (ItemList[5] == 'EmptyObject')):
      print ("Turn right")
      direction =  cf.TurnRight(direction)
      Human.h, Human.v =  cf.CalculateDotMovement(h,v,direction)

    #Right Corner
    elif ((ItemList[3] == 'border' or ItemList[3] == 'Wall' or ItemList[3] == 'RobotMissile')
      and (ItemList[5] == 'border' or ItemList[5] == 'Wall' or ItemList[5] == 'RobotMissile')
      and (ItemList[1] == 'EmptyObject')):
      #print ("Turn left")
      direction = cf.TurnLeft(direction)
      Human.h, Human.v =  cf.CalculateDotMovement(h,v,direction)
      
    
    #middle of wall
    elif ((ItemList[3] == 'border' or ItemList[3] == 'Wall'  or ItemList[3] == 'RobotMissile' or ItemList[3] == 'HumanMissile')
      and (ItemList[5] == 'EmptyObject')
      and (ItemList[1] == 'EmptyObject')):
      #print ("DZMH - Middle of the wall, turning left or right")
      direction = cf.TurnLeftOrRight(direction)
      Human.h, Human.v =  cf.CalculateDotMovement(h,v,direction)
      

    #three sides empty
    elif ((ItemList[3] == 'EmptyObject')
      and (ItemList[5] == 'EmptyObject')
      and (ItemList[1] == 'EmptyObject')):
      
      print ("Turn left or right or straight")
      r = random.randint(0,3)
      if (r == 1 or r == 2):
        direction = cf.TurnLeftOrRight(direction)
        #print ("Three sides were empty, turning left or right.  New Direction:",direction)
        Human.h, Human.v =  cf.CalculateDotMovement(h,v,direction)
      else:
        #print ("Three sides were empty.  Moving straight")
        Human.h, Human.v =  cf.CalculateDotMovement(h,v,direction)


    elif (ItemList[1] == 'Door'):
      direction = cf.TurnLeft(direction)
      Human.h, Human.v =  cf.CalculateDotMovement(h,v,direction)
      ExitingRoom = 1
      #print("Opening Door to left of human")    
    elif (ItemList[3] == 'Door'):
      Human.h, Human.v =  cf.CalculateDotMovement(h,v,direction)
      ExitingRoom = 1
      #print("Opening Door in front of human")    
    elif (ItemList[5] == 'Door'):
      direction =  cf.TurnRight(direction)
      Human.h, Human.v =  cf.CalculateDotMovement(h,v,direction)
      ExitingRoom = 1
      #print("Opening Door to right of human")    


        

    #left wall, front right empty
    elif ((ItemList[1] != 'EmptyObject')
      and (ItemList[3] == 'EmptyObject')
      and (ItemList[5] == 'EmptyObject')):
      
      #print ("Travelling along left wall.  Turn right or straight")
      r = random.randint(0,10)
      if (r == 1 ):
        direction =  cf.TurnRight(direction)
        #print ("Turning right direction: ",direction)
        Human.h, Human.v =  cf.CalculateDotMovement(h,v,direction)
      else:
        #print ("Staying straight")
        Human.h, Human.v =  cf.CalculateDotMovement(h,v,direction)
      

    #right wall, front left empty
    elif ((ItemList[1] == 'EmptyObject')
      and (ItemList[3] == 'EmptyObject')
      and (ItemList[5] != 'EmptyObject')):
      
      #print ("Travelling along right wall.  Turn left or straight")
      r = random.randint(0,10)
      if (r == 1 ):
        direction = cf.TurnLeft(direction)
        #print ("Turning left.  direction: ",direction)
        Human.h, Human.v =  cf.CalculateDotMovement(h,v,direction)
      else:
        #print ("Staying straight")
        Human.h, Human.v =  cf.CalculateDotMovement(h,v,direction)
      
      
      
      

     
     
      
    else:
      #print ("Go straight")
      Human.h, Human.v =  cf.CalculateDotMovement(h,v,direction)

  
  elif (RobotsAlive >= 1):
    #print ("DZMH - Robots Alive!")
    #Hit the road if you see a robot
    if ('Robot' in ItemList):
      #print ("DZMH - Robot Detected - Reversing direction")
      direction = cf.ReverseDirection(direction)
      Human.h, Human.v =  cf.CalculateDotMovement(h,v,direction)
      DotZerkAdjustSpeed(Human,'up')

    #Blocked on left, front and right -- reverse direction        
    elif ((ItemList[1] == 'border' or ItemList[1] == 'Wall' or ItemList[1] == 'RobotMissile'  or ItemList[1] == 'HumanMissile' or ItemList[1] == 'Door')
      and (ItemList[3] == 'border' or ItemList[3] == 'Wall' or ItemList[3] == 'RobotMissile'  or ItemList[3] == 'HumanMissile' or ItemList[3] == 'Door')
      and (ItemList[5] == 'border' or ItemList[5] == 'Wall' or ItemList[5] == 'RobotMissile'  or ItemList[5] == 'HumanMissile' or ItemList[5] == 'Door')):
      #print ("DZMH - blocked on left front and right - Reversing direction")
      direction = cf.ReverseDirection(direction)
      Human.h, Human.v =  cf.CalculateDotMovement(h,v,direction)
      DotZerkAdjustSpeed(Human,'down')

    #Left Corner
    elif ((ItemList[3] == 'border' or ItemList[3] == 'Wall' or ItemList[3] == 'RobotMissile' or ItemList[3] == 'HumanMissile' or ItemList[3] == 'Door')
      and (ItemList[1] == 'border' or ItemList[1] == 'Wall' or ItemList[1] == 'RobotMissile' or ItemList[1] == 'HumanMissile' or ItemList[1] == 'Door')
      and (ItemList[5] == 'EmptyObject')):
      #print ("DZMH - Left Corner - Turn right")
      direction =  cf.TurnRight(direction)
      Human.h, Human.v =  cf.CalculateDotMovement(h,v,direction)
      DotZerkAdjustSpeed(Human,'down')


    #Right Corner
    elif ((ItemList[3] == 'border' or ItemList[3] == 'Wall' or ItemList[3] == 'RobotMissile' or ItemList[3] == 'HumanMissile' or ItemList[3] == 'Door')
      and (ItemList[5] == 'border' or ItemList[5] == 'Wall' or ItemList[5] == 'RobotMissile' or ItemList[5] == 'HumanMissile' or ItemList[5] == 'Door')
      and (ItemList[1] == 'EmptyObject')):
      #print ("DZMH - Right Corner - Turn left")
      direction = cf.TurnLeft(direction)
      Human.h, Human.v =  cf.CalculateDotMovement(h,v,direction)
      DotZerkAdjustSpeed(Human,'down')
      

    #middle of wall
    elif ((ItemList[3] == 'border' or ItemList[3] == 'Wall'  or ItemList[3] == 'RobotMissile' or ItemList[3] == 'HumanMissile' or ItemList[3] == 'Door')
      and (ItemList[5] == 'EmptyObject')
      and (ItemList[1] == 'EmptyObject')):
      #print ("DZMH - Middle of the wall, turning left or right")
      direction = cf.TurnLeftOrRight(direction)
      Human.h, Human.v =  cf.CalculateDotMovement(h,v,direction)
      DotZerkAdjustSpeed(Human,'down')

      
    #empty both sides - turn left or right  
    elif ((ItemList[1] == 'EmptyObject')
      and (ItemList[3] == 'border' or ItemList[3] == 'Wall' or ItemList[3] == 'RobotMissile' or ItemList[3] == 'HumanMissile' or ItemList[3] == 'Door')
      and (ItemList[5] == 'EmptyObject')):
      
      #print ("DZMH - Empty both sides - Turn left or right")
      direction = cf.TurnLeftOrRight(direction)
      Human.h, Human.v =  cf.CalculateDotMovement(h,v,direction)
      DotZerkAdjustSpeed(Human,'down')


    #empty all sides - chance of turning left or right
    elif (('EmptyObject' in (ItemList[1],ItemList[2],ItemList[3],ItemList[4],ItemList[5]))):
      direction = cf.ChanceOfTurning(direction,10)
      Human.h, Human.v =  cf.CalculateDotMovement(h,v,direction)
      DotZerkAdjustSpeed(Human,'up')

      
    #Right side empty --  straight
    elif (ItemList[5] == 'EmptyObject'):
      #print("DZMH - Right side empty - Go straigt")
      Human.h, Human.v =  cf.CalculateDotMovement(h,v,direction)
      DotZerkAdjustSpeed(Human,'up')
    
    elif (ItemList[1] == 'EmptyObject' and (ItemList[5] == 'Wall' or ItemList[5] == 'RobotMissile' or ItemList[5] == 'HumanMissile' or ItemList[5] == 'Door')):
      #print ("DZMH - Left is empty, right is blocked - turn left")
      direction = cf.TurnLeft(direction)
      Human.h, Human.v =  cf.CalculateDotMovement(h,v,direction)

      
    else:
      #print ("DZMH - Give up - Go straight")
      Human.h, Human.v =  cf.CalculateDotMovement(h,v,direction)
      DotZerkAdjustSpeed(Human,'up')


  #Prevent Human from going into the walls (except for doors)

  
  
  
  #Don't let human hit outside walls
  
  if (Human.h == 15 and Human.v != 7):
    Human.h = 14
  if (Human.h == 0 and Human.v != 7):
    Human.h = 1
  if (Human.v == 15 and Human.h != 7):
    Human.v = 14
  if (Human.v == 0 and Human.h != 7):
    Human.v = 1
  
  
  if (Human.h == 7 and Human.v <= 0):
    if (Door1.locked == 1):
      Human.v = 1
      direction = cf.ReverseDirection(Human.direction)
      Human.h, Human.v =  cf.CalculateDotMovement(h,v,direction)
      
      #print("Stuck at door1. new direction:",direction)
  if (Human.h >= 15 and Human.v == 7):
    if (Door2.locked == 1):
      Human.h = 14
      direction = cf.ReverseDirection(Human.direction)
      Human.h, Human.v =  cf.CalculateDotMovement(h,v,direction)
      #print("Stuck at door2. new direction:",direction)
  if (Human.h == 7 and Human.v >= 15):
    if (Door3.locked == 1):
      Human.v = 14
      direction = cf.ReverseDirection(Human.direction)
      Human.h, Human.v =  cf.CalculateDotMovement(h,v,direction)
      #print("Stuck at door3. new direction:",direction)
  if (Human.h <= 0 and Human.v == 7):
    if (Door4.locked == 1):
      Human.h = 1
      direction = cf.ReverseDirection(direction)
      Human.h, Human.v =  cf.CalculateDotMovement(h,v,direction)
      #print("Stuck at door4. new direction:",Human.direction)
    
      

  Human.direction = direction
  Human.scandirection = direction      
  #print ("DZMH - HumanDirection:",Human.direction)

  
  
  #print("DZMH - Old hv: ",h,v, " New hv: ",Human.h,Human.v, "direction: ",Human.direction)
  if (Human.h == h and Human.v == v):
    #print ("Something is not right.  Human didn't move, forcing a move now...RobotsAlive:",RobotsAlive)
    Human.direction = cf.TurnLeftOrRight(direction)
    Human.scandirection = Human.direction
    Human.h, Human.v = cf.CalculateDotMovement(Human.h,Human.v,direction)

    #Don't let human hit outside walls (put this in its own function and remove duplication)
    if (Human.h == 15 and Human.v != 7):
      #print ("Hit a wall!")
      Human.h = 14
    if (Human.h == 0 and Human.v != 7):
      #print ("Hit a wall!")
      Human.h = 1
    if (Human.v == 15 and Human.h != 7):
      #print ("Hit a wall!")
      Human.v = 14
    if (Human.v == 0 and Human.h != 7):
      #print ("Hit a wall!")
      Human.v = 1
  

    print ("New scandirection hv:",Human.scandirection,Human.h,Human.v)

  Playfield[Human.h][Human.v]= Human
  Human.Display()
  



  
  #If missiles alive, place on playfield
  if (HumanMissile1.alive == 1):
    Playfield[HumanMissile1.h][HumanMissile1.v]=HumanMissile1
  if (HumanMissile2.alive == 1):
    Playfield[HumanMissile2.h][HumanMissile2.v]=HumanMissile2
  
  if ((h != Human.h or v != Human.v) or
     (Human.alive == 0)):
    if (Playfield[v][h].name != 'Wall' and Playfield[v][h].name != 'Door'):
      Playfield[v][h] = Empty
      cf.setpixel(h,v,0,0,0)
    #print ("MPS - Erasing Player")
  #unicorn.show()

  
  if (Human.h == 0 or Human.h == 15 or Human.v == 0 or Human.v == 15):
    print("***************************************")
    print("**HUMAN ENDED UP STUCK ON WALL*********")
    print("***************************************")
    print ("Before Human.h Human.v",Human.h,Human.v)
    print("Taking corrective actions.  Moving human to middle of screen.")
    Human.h = 7
    Human.v = 7
    print ("After Human.h Human.v",Human.h,Human.v)

  return 

          

def CheckRobotRadar(Robot, Human, RadarChance):
  HumanDetected = 0
  #Check robot radar:
  if (random.randint(1,100) < RadarChance):
    #print ("Robot radar on.  Current robot direction: ", Robot.direction)
    TurnTowardsOpponent4Way(Robot,Human)
    HumanDetected = 1
    #print ("Robot radar off. New robot direction:     ", Robot.direction)


  return HumanDetected
    

          
def TurnTowardsOpponent4Way(SourceCar,TargetCar):


#     1 
#   4   2
#     3

  #Source is to the left of target
  if (SourceCar.h < TargetCar.h):
    if (SourceCar.direction in (1,4)):
      SourceCar.direction =  cf.TurnRight(SourceCar.direction)
    if (SourceCar.direction == 3):
      SourceCar.direction = cf.TurnLeft(SourceCar.direction)
      
  if (SourceCar.h > TargetCar.h):
    if (SourceCar.direction in (1,2)):
      SourceCar.direction = cf.TurnLeft(SourceCar.direction)
    if (SourceCar.direction in (3,12)):
      SourceCar.direction =  cf.TurnRight(SourceCar.direction)


  if (SourceCar.v < TargetCar.v):
    if (SourceCar.direction in (1,4)):
      SourceCar.direction = cf.TurnLeft(SourceCar.direction)
    if (SourceCar.direction == 2):
      SourceCar.direction =  cf.TurnRight(SourceCar.direction)
      
  if (SourceCar.v > TargetCar.v):
    if (SourceCar.direction in (4,3)):
      SourceCar.direction =  cf.TurnRight(SourceCar.direction)
    if (SourceCar.direction == 2):
      SourceCar.direction = cf.TurnLeft(SourceCar.direction)

  SourceCar.scandirection = SourceCar.direction
  return;
  







          
          
def PlayDotZerk():
  
  cf.ClearBigLED()  
  
  
  #Local variables
  moves       = 0
  Roommoves   = 500
  Finished    = 'N'
  LevelCount  = 1
  SleepTime   = gv.MainSleep / 4
  Key         = ""
  
  #Global variables
  global ExitingRoom
  global RobotsAlive
  global DirectionOfTravel
  global DotZerkScore
  DotZerkScore = 0
  
  Human.lives     = 3
  LifeCounter     = Human.lives
  RobotRadarChance = 20

  #Title
  cf.ShowScrollingBanner("DotZerk",30,100,0,gv.ScrollSleep)
  cf.ShowLevelCount(Human.lives)
  
      
  
  
  
  #Main Game Loop
  while (Finished == 'N'):


  
    if (LifeCounter != Human.lives):
      cf.ShowLevelCount(Human.lives)
      LifeCounter = Human.lives
    
    
    #Reset Variables between rounds
    LevelFinished    = 'N'
    Human.alive      = 1
    Human.speed      = Gear[4]
    Roommoves        = 0
    
    
    Human.exploding  = 0
    HumanMissile1.exploding = 0
    HumanMissile2.exploding = 0
    HumanMissile1.speed = 15
    HumanMissile2.speed = 15
    HumanMissile1.alive = 0
    HumanMissile2.alive = 0

    #Fix walls and doors that accidentally blew up by missiles
    RedrawMapSpeed = 100
    
    Robot1.alive         = 1
    Robot1.direction     = 3
    Robot1.speed         = 15
    
    Robot2.alive         = 1
    Robot2.direction     = 3
    Robot2.speed         = 15

    Robot3.alive         = 1
    Robot3.direction     = 3
    Robot2.speed         = 15

    Robot4.alive         = 1
    Robot4.direction     = 3
    Robot4.speed         = 30


    
    #RobotBob is a killer, only appears to finish off Human if taking too long (bugs!)
    RobotBob.alive         = 0
    RobotBob.direction     = 1
    RobotBob.speed         = 25
    
    
    RobotsAlive          = 1
    
    Robot1.scandirection = 3
    Robot2.scandirection = 3
    Robot3.scandirection = 3
    Robot4.scandirection = 3
    Robot1Missile.alive  = 0
    Robot2Missile.alive  = 0
    Robot3Missile.alive  = 0
    Robot4Missile.alive  = 0
    RobotBobMissile.alive  = 0


    Robot1Missile.direction     = 0
    Robot1Missile.scandirection = 0
    Robot1Missile.speed         = 15
    Robot1Missile.exploding     = 0

    Robot2Missile.direction     = 0
    Robot2Missile.scandirection = 0
    Robot2Missile.speed         = 15
    Robot2Missile.exploding     = 0
    
    Robot3Missile.direction     = 0
    Robot3Missile.scandirection = 0
    Robot3Missile.speed         = 15
    Robot3Missile.exploding     = 0

    Robot4Missile.direction     = 0
    Robot4Missile.scandirection = 0
    Robot4Missile.speed         = 15
    Robot4Missile.exploding     = 0


    
    #Reset colors
    Robot1Missile.r = RobotMissileR
    Robot1Missile.g = RobotMissileG
    Robot1Missile.b = RobotMissileB
    Robot2Missile.r = RobotMissileR
    Robot2Missile.g = RobotMissileG
    Robot2Missile.b = RobotMissileB
    Robot3Missile.r = RobotMissileR
    Robot3Missile.g = RobotMissileG
    Robot3Missile.b = RobotMissileB
    Robot4Missile.r = RobotMissileR
    Robot4Missile.g = RobotMissileG
    Robot4Missile.b = RobotMissileB

    RobotBobMissile.r = RobotMissileR
    RobotBobMissile.g = RobotMissileG
    RobotBobMissile.b = RobotMissileB
    
    HumanMissile1.r = PlayerMissileR
    HumanMissile1.g = PlayerMissileG
    HumanMissile1.b = PlayerMissileB

    HumanMissile2.r = PlayerMissileR
    HumanMissile2.g = PlayerMissileG
    HumanMissile2.b = PlayerMissileB

    Robot1.r = cf.SDLowRedR
    Robot1.g = cf.SDLowRedG
    Robot1.b = cf.SDLowRedB
   
    Robot2.r = cf.SDLowRedR
    Robot2.g = cf.SDLowRedG
    Robot2.b = cf.SDLowRedB


    Robot3.r = cf.SDLowRedR
    Robot3.g = cf.SDLowRedG
    Robot3.b = cf.SDLowRedB

    Robot4.r = cf.SDLowRedR
    Robot4.g = cf.SDLowRedG
    Robot4.b = cf.SDLowRedB

    RobotBob.r = cf.SDMedYellowR
    RobotBob.g = cf.SDMedYellowG
    RobotBob.b = cf.SDMedYellowB


    ExitingRoom = 0
    
    
    #Show fancy effects only the first time through
    if(moves == 0):
      cf.setpixel(Robot1.h,Robot1.v,0,0,0)
      cf.setpixel(Robot2.h,Robot2.v,0,0,0)
      cf.setpixel(Robot3.h,Robot3.v,0,0,0)
      cf.setpixel(Robot4.h,Robot4.v,0,0,0)
      DotZerkResetPlayfield(ShowFlash=1)
      cf.setpixel(Robot1.h,Robot1.v,255,0,0)
      cf.setpixel(Robot2.h,Robot2.v,255,0,0)
      cf.setpixel(Robot3.h,Robot3.v,255,0,0)
      cf.setpixel(Robot4.h,Robot4.v,255,0,0)
    else:
      DotZerkResetPlayfield(ShowFlash=0)
    DotZerkResetPlayfield(ShowFlash=0)
    
    
    
    # Main timing loop
    while (LevelFinished == 'N' and Human.alive == 1):
      moves     = moves + 1
      Roommoves = Roommoves + 1
      
      
      #Check for keyboard input
      m,r = divmod(moves,KeyboardSpeed)
      if (r == 0):
        Key = cf.PollKeyboard()
        ProcessKeypress(Key)
        if (Key == 'q'):
          LevelFinished = 'Y'
          Finished      = 'Y'
          Human.alive   = 0
          Human.lives   = 0
          return
      
      if (Roommoves >= 2000 and RobotBob.alive == 0):
        RobotBob.alive = 1
        print ("*** Time to die, human! ***")
        Roommoves = 0
      
      if (Roommoves >= 20000):
        Human.alive = 0
        Human.exploding = 1
        print ("*** YOU TOOK TOO LONG ***")
        cf.ShowScrollingBanner("THE HUMANOID HAS TERMINATED!",30,100,0,gv.ScrollSleep)
        Roommoves = 0
      
      
      
      if (Human.alive == 1):
        #print ("M - Human HV speed alive exploding direction scandirection: ",Human.h, Human.v,Human.speed, Human.alive, Human.exploding, Human.direction,Human.ScanDirection)
        m,r = divmod(moves,Human.speed)
        if (r == 0):
          DotZerkMoveHuman(Human,MazeWorld.Playfield)
        
          
          #print ("M - ExitingRoom: ",ExitingRoom)
          if (ExitingRoom == 1 and RobotsAlive == 0):
            #Turn off killer robot
            
            if (RobotBob.alive == 1):
              ShowChickenTaunt(gv.ScrollSleep)

            RobotBob.alive = 0
            DotZerkExitRoom(Human.direction)
            ExitingRoom = 0
            LevelFinished = 'Y'
            DirectionOfTravel = Human.direction
            
            

            

          #print ("=================================================")
          #for H in range(0,gv.HatWidth-1):
          #  for V in range (0,gv.HatWidth-1):
          #   if (MazeWorld.Playfield[v][h].name != 'EmptyObject' and MazeWorld.Playfield[v][h].name != 'Wall'):
          #     print ("Playfield: HV Name Alive Lives",H,V,MazeWorld.Playfield[v][h].name,MazeWorld.Playfield[v][h].alive, Human.lives )
          #print ("Robot1.alive Robot2.alive RobotsAlive:",Robot1.alive,Robot2.alive,RobotsAlive)
          #print ("Robot1.exploding Robot2.exploding:",Robot1.exploding,Robot2.exploding)
          #print ("=================================================")
      


            
      
      if (Robot1.alive == 1):
        m,r = divmod(moves,Robot1.speed)
        if (r == 0):
          DotZerkMoveRobot(Robot1,Human,RobotRadarChance,MazeWorld.Playfield)
          
      if (Robot2.alive == 1):
        m,r = divmod(moves,Robot2.speed)
        if (r == 0):
          DotZerkMoveRobot(Robot2,Human,RobotRadarChance,MazeWorld.Playfield)

      if (Robot3.alive == 1):
        m,r = divmod(moves,Robot3.speed)
        if (r == 0):
          DotZerkMoveRobot(Robot3,Human,RobotRadarChance,MazeWorld.Playfield)

      if (Robot4.alive == 1):
        m,r = divmod(moves,Robot4.speed)
        if (r == 0):
          DotZerkMoveRobot(Robot4,Human,RobotRadarChance,MazeWorld.Playfield)



      if (RobotBob.alive == 1):
        m,r = divmod(moves,RobotBob.speed)
        if (r == 0):
          DotZerkMoveRobot(RobotBob,Human,RobotRadarChance,MazeWorld.Playfield)
        
          

          
      #We should pass in the shooter's object as well
      #This will allow the missile to provide feedback      
      if (Robot1Missile.alive == 1 and Robot1Missile.exploding == 0):
        m,r = divmod(moves,Robot1Missile.speed)
        if (r == 0):
          DotZerkMoveMissile(Robot1Missile,Robot1,MazeWorld.Playfield)

      if (Robot2Missile.alive == 1 and Robot2Missile.exploding == 0):
        m,r = divmod(moves,Robot2Missile.speed)
        if (r == 0):
          DotZerkMoveMissile(Robot2Missile,Robot2,MazeWorld.Playfield)

      if (Robot3Missile.alive == 1 and Robot3Missile.exploding == 0):
        m,r = divmod(moves,Robot3Missile.speed)
        if (r == 0):
          DotZerkMoveMissile(Robot3Missile,Robot3,MazeWorld.Playfield)
          
      if (Robot4Missile.alive == 1 and Robot4Missile.exploding == 0):
        m,r = divmod(moves,Robot4Missile.speed)
        if (r == 0):
          DotZerkMoveMissile(Robot4Missile,Robot4,MazeWorld.Playfield)
          
          
      if (RobotBobMissile.alive == 1 and RobotBobMissile.exploding == 0):
        m,r = divmod(moves,RobotBobMissile.speed)
        if (r == 0):
          DotZerkMoveMissile(RobotBobMissile,RobotBob,MazeWorld.Playfield)

          
      if (HumanMissile1.alive == 1 and HumanMissile1.exploding == 0):
        m,r = divmod(moves,HumanMissile1.speed)
        if (r == 0):
          DotZerkMoveMissile(HumanMissile1,Human,MazeWorld.Playfield)

      if (HumanMissile2.alive == 1 and HumanMissile2.exploding == 0):
        m,r = divmod(moves,HumanMissile2.speed)
        if (r == 0):
          DotZerkMoveMissile(HumanMissile2,Human,MazeWorld.Playfield)

          

      m,r = divmod(moves,RedrawMapSpeed)
      if (r== 0):
        print ("******************************")
        print ("** Redrawing Map and Doors  **")
        print ("******************************")
        
        MazeWorld.CopyMapToPlayfield()
        MazeWorld.DisplayPlayfield(0)
        DotZerkDisplayDoors()  

        
             
          

        

      #Check for exploding objects
      if (Robot1.exploding == 1):
        #print("------> Robot1.exploding: ",Robot1.exploding)
        DotZerkExplodeRobot(Robot1,MazeWorld.Playfield,20)


      #Check for exploding objects
      if (Robot2.exploding == 1):
        #print("------> Robot2.exploding: ",Robot2.exploding)
        DotZerkExplodeRobot(Robot2,MazeWorld.Playfield,20)

      #Check for exploding objects
      if (Robot3.exploding == 1):
        #print("------> Robot3.exploding: ",Robot3.exploding)
        DotZerkExplodeRobot(Robot3,MazeWorld.Playfield,20)

      #Check for exploding objects
      if (Robot4.exploding == 1):
        #print("------> Robot4.exploding: ",Robot4.exploding)
        DotZerkExplodeRobot(Robot4,MazeWorld.Playfield,20)
       
        
        
      #Check for exploding objects
      if (RobotBob.exploding == 1):
        #print("------> RobotBob.exploding: ",RobotBob.exploding)
        DotZerkExplodeRobot(RobotBob,MazeWorld.Playfield,20)

      if (HumanMissile1.exploding == 1):
        #print("------> HumanMissile1.exploding: ",HumanMissile1.exploding)
        DotZerkExplodeMissile(HumanMissile1,MazeWorld.Playfield,20)

      if (HumanMissile2.exploding == 1 ):
        #print("------> HumanMissile2.exploding: ",HumanMissile2.exploding)
        DotZerkExplodeMissile(HumanMissile2,MazeWorld.Playfield,20)


      if (Robot1Missile.exploding == 1 ):
        #print("------> Robot1Missile.exploding: ",Robot1Missile.exploding)
        DotZerkExplodeMissile(Robot1Missile,MazeWorld.Playfield,20)

      if (Robot2Missile.exploding == 1 ):
        #print("------> Robot2Missile.exploding: ",Robot2Missile.exploding)
        DotZerkExplodeMissile(Robot2Missile,MazeWorld.Playfield,20)


      if (Robot3Missile.exploding == 1 ):
        #print("------> Robot3Missile.exploding: ",Robot3Missile.exploding)
        DotZerkExplodeMissile(Robot3Missile,MazeWorld.Playfield,20)

      if (Robot4Missile.exploding == 1 ):
        #print("------> Robot4Missile.exploding: ",Robot4Missile.exploding)
        DotZerkExplodeMissile(Robot4Missile,MazeWorld.Playfield,20)


      if (RobotBobMissile.exploding == 1 ):
        #print("------> RobotBobMissile.exploding: ",RobotBobMissile.exploding)
        DotZerkExplodeMissile(RobotBobMissile,MazeWorld.Playfield,20)
        

      #Make sure robot alive indicator is set
      #And boost human speed
      if (Robot1.alive == 0 and Robot2.alive == 0):
        RobotsAlive = 0

        
      #=================================
      #= End of level conditions       =
      #=================================
     
      if (Human.alive == 0):
        Human.lives = Human.lives - 1

        if (Human.lives <=0):
          Finished = 'Y'

        Buffer = copy.deepcopy(unicorn.get_pixels())
        #HumanExplosion.Animate(Human.h-1,Human.v-1,'forward',0.5)
        HumanExplosion2.Animate(Human.h-1,Human.v-1,'forward',0.05)
        cf.setpixels(Buffer)
        Human.Erase()
        moves=0
        

      CheckTime = 60
      #Display animation and clock every X seconds
      if (CheckElapsedTime(CheckTime) == 1):
        ScrollScreenShowDotZerkRobotTime('down',gv.ScrollSleep)         



      cf.ClearBigLED()
      #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
  print ("M - The end?")    
  cf.ClearBigLED()

  if (Key != "q"):
    ScoreString = str(DotZerkScore) 
    cf.ShowScrollingBanner("Score",cf.SDLowPurpleR,cf.SDLowPurpleG,cf.SDLowPurpleB,gv.ScrollSleep)
    cf.ShowScrollingBanner(ScoreString,cf.SDLowGreenR,cf.SDLowGreenG,cf.SDLowGreenB,(gv.ScrollSleep * 2))
    cf.ShowScrollingBanner("GAME OVER",cf.SDMedRedR,cf.SDMedRedG,cf.SDMedRedB,gv.ScrollSleep)
















  



def ShowFroggerMessage(speed):
  #ScreenCap  = copy.deepcopy(unicorn.get_pixels())
  #cf.ScrollScreen('right',ScreenCap,speed)

  FrogSprite.LaserScan(0,0,speed/8)
  time.sleep(1)
  FrogSprite.LaserErase(0,0,speed/8)
  FrogSprite.HorizontalFlip()
  FrogSprite.ScrollAcrossScreen(0,0,'left',speed)
  FrogSprite.HorizontalFlip()

  cf.ScrollScreen('left',ScreenCap,speed)

  

  cf.ShowScrollingBanner("make clocks great again",cf.SDMedRedR,cf.SDMedRedG,cf.SDMedRedB,speed * 0.8)  
  ChickenRunning.Scroll(8,0,"left",16,speed)
   
  LittleShipFlying.HorizontalFlip()
  BigShipFlying.HorizontalFlip()

  LittleShipFlying.ScrollAcrossScreen(0,0,'left',speed * 0.6)
  BigShipFlying.ScrollAcrossScreen(0,0,'left',speed *0.8)

  LittleShipFlying.HorizontalFlip()
  BigShipFlying.HorizontalFlip()

  c#f.ScrollScreen('left',ScreenCap,speed)



def ShowAllAnimations(speed):
  #ScreenCap  = copy.deepcopy(unicorn.get_pixels())
  #cf.ScrollScreen('right',ScreenCap,speed)

  # FrogSprite.LaserScan(0,0,speed * 0.01)
  # time.sleep(1)
  # FrogSprite.LaserErase(0,0,speed* 0.01)
  # FrogSprite.Scroll(-gv.HatWidth,4,"right",36,speed)
  # FrogSprite.HorizontalFlip()
  # FrogSprite.Scroll(gv.HatWidth+4,4,"left",32,speed)
  # FrogSprite.HorizontalFlip()

  ChickenRunning.LaserScan(4,4,speed/8)
  time.sleep(1)
  ChickenRunning.LaserErase(4,4,speed/8)
  ChickenRunning.HorizontalFlip()
  ChickenRunning.Scroll(-gv.HatWidth,0,"right",32,speed)
  ChickenRunning.HorizontalFlip()
  ChickenRunning.Scroll(gv.HatWidth,0,"left",32,speed)

  ChickenChasingWorm.ScrollAcrossScreen(0,0,'left',gv.ScrollSleep)
  ChickenChasingWorm.HorizontalFlip()
  ChickenChasingWorm.ScrollAcrossScreen(0,0,'right',speed)
  ChickenChasingWorm.HorizontalFlip()
  

  DotZerkRobotWalking.LaserScan(0,0,speed/8)
  time.sleep(1)
  DotZerkRobotWalking.LaserErase(0,0,speed/8)
  DotZerkRobotWalking.ScrollAcrossScreen(0,0,'left',speed)
  DotZerkRobotWalking.HorizontalFlip()
  DotZerkRobotWalking.ScrollAcrossScreen(0,0,'right',speed)
  DotZerkRobotWalking.HorizontalFlip()

  DotZerkRobotWalkingSmall.LaserScan(0,2,speed/8)
  time.sleep(1)
  DotZerkRobotWalkingSmall.LaserErase(0,2,speed/8)
  DotZerkRobotWalkingSmall.ScrollAcrossScreen(0,2,'left',speed)
  DotZerkRobotWalkingSmall.HorizontalFlip()
  DotZerkRobotWalkingSmall.ScrollAcrossScreen(0,2,'right',speed)
  DotZerkRobotWalkingSmall.HorizontalFlip()
  
  TinyInvader.LaserScan(2,1,speed/8)
  time.sleep(1)
  TinyInvader.LaserErase(2,1,speed/8)
  TinyInvader.ScrollAcrossScreen(0,1,'left',speed)
  TinyInvader.HorizontalFlip()
  TinyInvader.ScrollAcrossScreen(0,1,'right',speed)
  TinyInvader.HorizontalFlip()
  
  SmallInvader.LaserScan(0,1,speed/8)
  time.sleep(1)
  SmallInvader.LaserErase(0,1,speed/8)
  SmallInvader.ScrollAcrossScreen(0,1,'left',speed)
  SmallInvader.HorizontalFlip()
  SmallInvader.ScrollAcrossScreen(0,1,'right',speed)
  SmallInvader.HorizontalFlip()

  SpaceInvader.LaserScan(-1,0,speed/8)
  time.sleep(1)
  SpaceInvader.LaserErase(-1,0,speed/8)
  SpaceInvader.ScrollAcrossScreen(0,0,'left',speed)
  SpaceInvader.HorizontalFlip()
  SpaceInvader.ScrollAcrossScreen(0,0,'right',speed)
  SpaceInvader.HorizontalFlip()
  
  LittleShipFlying.HorizontalFlip()
  BigShipFlying.HorizontalFlip()

  LittleShipFlying.ScrollAcrossScreen(0,0,'left',speed)
  BigShipFlying.ScrollAcrossScreen(0,0,'left',speed)

  LittleShipFlying.HorizontalFlip()
  BigShipFlying.HorizontalFlip()
  LittleShipFlying.ScrollAcrossScreen(0,0,'right',speed * 0.50)
  BigShipFlying.ScrollAcrossScreen(0,0,'right',speed * 0.50)

  #cf.ScrollScreen('left',ScreenCap,speed)



def ShowLongIntro(speed):
  ScreenCap = unicorn.get_pixels()
  Buffer    = unicorn.get_pixels()
  EmptyCap = [[(0,0,0) for i in range (gv.HatWidth)] for j in range (gv.HatWidth)]

  for x in range (0,16):
    cf.setpixel(x,3,cf.SDLowRedR,cf.SDLowRedG,cf.SDLowRedB)
  
  #Delete top row, insert blank on bottom, pushing remaining up
  for x in range(0,16):
    #del ScreenCap[0]
    ScreenCap.append(EmptyCap[0])
    cf.setpixels(ScreenCap)
    #unicorn.show()
    #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
    time.sleep(speed)

  
  cf.ShowScrollingBanner("Arcade retro clock",cf.SDLowYellowR,cf.SDLowYellowG,cf.SDLowYellowB,speed)
  cf.ShowScrollingBanner("by Datagod",cf.SDLowGreenR,cf.SDLowGreenG,cf.SDLowGreenB,speed)

  DotZerkRobotWalking.LaserScan(0,0,speed/8)
  time.sleep(0.5)
  ScrollScreenScrollBanner("multiple games",cf.SDMedBlueR,cf.SDMedBlueG,cf.SDMedBlueB,'down',speed)
  time.sleep(0.5)
  DotZerkRobotWalking.LaserErase(0,0,speed/8)
  DotZerkRobotWalking.ScrollAcrossScreen(0,0,'left',speed)

  cf.ShowScrollingBanner("cut scenes",cf.SDLowPurpleR,cf.SDLowPurpleG,cf.SDLowPurpleB,speed)
  
  ChickenChasingWorm.ScrollAcrossScreen(0,0,'left',gv.ScrollSleep)
  DotZerkRobotWalkingSmall.ScrollAcrossScreen(0,2,'left',speed)


  TinyInvader.LaserScan(2,1,speed/8)
  time.sleep(0.5)
  ScrollScreenScrollBanner("aliens!",cf.SDLowRedR,cf.SDLowRedG,cf.SDLowRedB,'up',speed)
  time.sleep(0.5)
  TinyInvader.LaserErase(2,1,speed/8)
  TinyInvader.ScrollAcrossScreen(0,1,'left',speed)
  SmallInvader.ScrollAcrossScreen(0,1,'left',speed)
  SpaceInvader.ScrollAcrossScreen(0,0,'left',speed)

  cf.ShowScrollingBanner("epic space battles",cf.SDLowOrangeR,cf.SDLowOrangeG,cf.SDLowOrangeB,speed)  
  LittleShipFlying.HorizontalFlip()
  BigShipFlying.HorizontalFlip()

  LittleShipFlying.ScrollAcrossScreen(0,0,'left',speed)
  BigShipFlying.ScrollAcrossScreen(0,0,'left',speed)
  LittleShipFlying.HorizontalFlip()
  BigShipFlying.HorizontalFlip()

  cf.ShowScrollingBanner("tells time too!",cf.SDLowOrangeR,cf.SDLowOrangeG,cf.SDLowOrangeB,speed)  
  TheTime = cf.CreateClockSprite(12)    
  TheTime.r = cf.SDMedRedR
  TheTime.g = cf.SDMedRedG
  TheTime.b = cf.SDMedRedB
  TheTime.ScrollAcrossScreen(0,1,"left",speed)
  TheTime.ScrollAcrossScreen(0,1,"left",speed)
  
  
  cf.ShowScrollingBanner("Ready Player One?      GO!",cf.SDLowOrangeR,cf.SDLowOrangeG,cf.SDLowOrangeB,speed)  
 
  
  #Reverse direction, bringing screen back down  
  for x in range (0,gv.HatWidth):
    del ScreenCap[-1]
    ScreenCap.insert(0,Buffer[HatWidth-1 -x])
    cf.setpixels(ScreenCap)
    #unicorn.show()
    #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
    time.sleep(speed)

    
    
    
    

def ScrollScreenShowFrogTime(direction,speed):
  ScreenCap  = copy.deepcopy(unicorn.get_pixels())
  cf.ScrollScreen(direction,ScreenCap,speed)
  ShowFrogTime(speed)
  cf.ScrollScreen('left',ScreenCap,speed)


  
def ShowFrogTime(speed):
  TheTime = cf.CreateClockSprite(12)
  TheTime.r = cf.SDLowGreenR
  TheTime.g = cf.SDLowGreenG
  TheTime.b = cf.SDLowGreenB

  if (random.randint(0,2) == 1):
    TheTime.ScrollAcrossScreen(0,1,"right",speed)
    FrogSprite.LaserScan(0,0,speed/8)
    time.sleep(1)
    FrogSprite.LaserErase(0,0,speed/8)
    TheTime.ScrollAcrossScreen(0,1,"left",speed)
  else:
    FrogSprite.Scroll(-8,0,"right",16,speed)
    TheTime.ScrollAcrossScreen(0,1,"right",speed)
    FrogSprite.HorizontalFlip()
    FrogSprite.Scroll(8,0,"left",16,speed)
    TheTime.ScrollAcrossScreen(0,1,"left",speed)
    


    
    


def ScrollScreenShowChickenWormTime(direction,speed):
  ScreenCap  = copy.deepcopy(unicorn.get_pixels())
  cf.ScrollScreen('right',ScreenCap,0.01)
  ShowChickenWorm(speed)
  cf.ScrollScreen('left',ScreenCap,0.01)

      
      

def ShowChickenWorm(speed):
 
  TheTime   = cf.CreateClockSprite(12)
  TheTime.r = cf.SDLowGreenR
  TheTime.g = cf.SDLowGreenG
  TheTime.b = cf.SDLowGreenB
    
  r = random.randint(0,2)
  if (r == 0):
    ChickenChasingWorm.ScrollAcrossScreen(0,0,'left',gv.ScrollSleep)
    TheTime.ScrollAcrossScreen(0,1,"left",speed)
    ChickenChasingWorm.HorizontalFlip()
    ChickenChasingWorm.ScrollAcrossScreen(0,0,'right',speed)
    TheTime.ScrollAcrossScreen(0,1,"right",speed)
    ChickenChasingWorm.HorizontalFlip()

  elif (r == 1):
    WormChasingChicken.ScrollAcrossScreen(0,0,'left',speed)
    TheTime.ScrollAcrossScreen(0,1,"left",speed)
    WormChasingChicken.HorizontalFlip()
    WormChasingChicken.ScrollAcrossScreen(0,0,'right',speed)
    TheTime.ScrollAcrossScreen(0,1,"right",speed)
    WormChasingChicken.HorizontalFlip()

  elif (r == 2):
    ShowWorms(speed)
    TheTime.ScrollAcrossScreen(0,1,"left",speed)
  


def ShowChickenTaunt(speed):
  cf.ClearBigLED()

  cf.ShowScrollingBanner("Chicken",100,100,0,speed * 0.8)
  ChickenRunning.ScrollAcrossScreen(0,0,'left',speed)
  DotZerkRobotWalking.ScrollAcrossScreen(0,0,'left',speed)
  #ShowScrollingBanner("fight like a robot",35,80,0,speed * 0.8)
  
    
    


  
  
def ScrollScreenShowDotZerkRobotTime(direction,speed):
  TheTime = cf.CreateClockSprite(12)
  TheTime.r = cf.SDLowGreenR
  TheTime.g = cf.SDLowGreenG
  TheTime.b = cf.SDLowGreenB

  ScreenCap  = copy.deepcopy(unicorn.get_pixels())
  cf.ScrollScreen('right',ScreenCap,speed)

  ShowDotZerkRobotTime(speed)

  cf.ScrollScreen('left',ScreenCap,speed)

    
      

def ShowDotZerkRobotTime(speed):
  TheTime = cf.CreateClockSprite(12)
  TheTime.r = cf.SDLowGreenR
  TheTime.g = cf.SDLowGreenG
  TheTime.b = cf.SDLowGreenB
  
    
  r = random.randint(0,1)
  if (r == 0):
    DotZerkRobotWalkingSmall.ScrollAcrossScreen(0,5,'left',speed)
    DotZerkRobotWalkingSmall.HorizontalFlip()
    TheTime.ScrollAcrossScreen(0,5,"left",speed)
    DotZerkRobotWalkingSmall.ScrollAcrossScreen(0,5,'right',speed)
    TheTime.ScrollAcrossScreen(0,5,"right",speed)
    DotZerkRobotWalkingSmall.HorizontalFlip()

  elif (r == 1):
    DotZerkRobotWalking.ScrollAcrossScreen(0,5,'left',speed)
    DotZerkRobotWalking.HorizontalFlip()
    TheTime.ScrollAcrossScreen(0,5,"left",speed)
    DotZerkRobotWalking.ScrollAcrossScreen(0,5,'right',speed)
    TheTime.ScrollAcrossScreen(0,5,"right",speed)
    DotZerkRobotWalking.HorizontalFlip()
  



def ShowDropShip(h,v,action,speed):
  cf.setpixel(h,v,PlayerShipR,PlayerShipG,PlayerShipB)
  Canvas = unicorn.get_pixels()
  cf.setpixel(h,v,0,0,0)
  Buffer2 = unicorn.get_pixels()
  cf.setpixel(h,v,PlayerShipR,PlayerShipG,PlayerShipB)
  
  if (action == 'pickup'):
    for y in range(-14,v-5):
      cf.setpixels(Canvas)
      DropShip.Animate(h-2,y,'forward',speed)
      cf.setpixels(Canvas)
      DropShip.Animate(h-2,y,'forward',speed)
      cf.setpixels(Canvas)
      DropShip.Animate(h-2,y,'forward',speed)
      cf.setpixels(Canvas)
    
    DropShip.Animate(h-2,y+1,'forward',speed)
    DropShip.Animate(h-2,y+1,'forward',speed)
    DropShip.Animate(h-2,y+1,'forward',speed)
    DropShip.Animate(h-2,y+1,'forward',speed)
    DropShip.Animate(h-2,y+1,'forward',speed)
    DropShip.Animate(h-2,y+1,'forward',speed)
    DropShip.Animate(h-2,y+1,'forward',speed)
    DropShip.Animate(h-2,y+1,'forward',speed)
    DropShip.Animate(h-2,y+1,'forward',speed)

    #print("Sleeping")
    for y in range(v-5,-10,-1):
      DropShip.Animate(h-2,y,'forward',speed)
      cf.setpixels(Buffer2)
      DropShip.Animate(h-2,y,'forward',speed)
      cf.setpixels(Buffer2)
      DropShip.Animate(h-2,y,'forward',speed)
      cf.setpixels(Buffer2)
  else:
    for y in range(-14,v-5):
      cf.setpixels(Buffer2)
      DropShip.Animate(h-2,y,'forward',speed)
      cf.setpixels(Buffer2)
      DropShip.Animate(h-2,y,'forward',speed)
      cf.setpixels(Buffer2)
      DropShip.Animate(h-2,y,'forward',speed)
      cf.setpixels(Buffer2)

    DropShip.Animate(h-2,y+1,'forward',speed)
    DropShip.Animate(h-2,y+1,'forward',speed)
    DropShip.Animate(h-2,y+1,'forward',speed)
    DropShip.Animate(h-2,y+1,'forward',speed)
    DropShip.Animate(h-2,y+1,'forward',speed)
    DropShip.Animate(h-2,y+1,'forward',speed)
    DropShip.Animate(h-2,y+1,'forward',speed)
    DropShip.Animate(h-2,y+1,'forward',speed)
    DropShip.Animate(h-2,y+1,'forward',speed)
    print("Sleeping")
    
    for y in range(v-5,-10,-1):
      DropShip.Animate(h-2,y,'forward',speed)
      cf.setpixels(Canvas)
      DropShip.Animate(h-2,y,'forward',speed)
      cf.setpixels(Canvas)
      DropShip.Animate(h-2,y,'forward',speed)
      cf.setpixels(Canvas)


#is this a dupe?
def ScrollScreenShowWormsTime(direction,speed):
  ScreenCap = unicorn.get_pixels()
  Buffer    = unicorn.get_pixels()
  EmptyCap = [[(0,0,0) for i in range (gv.HatWidth)] for j in range (gv.HatWidth)]

  for x in range (0,gv.HatWidth):
    cf.setpixel(x,3,99,99,200)
  
  #Delete top row, insert blank on bottom, pushing remaining up
  if (direction == 'up'):
    for x in range (0,gv.HatWidth):
      del ScreenCap[0]
      ScreenCap.append(EmptyCap[0])
      cf.setpixels(ScreenCap)
      #unicorn.show()
      #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
      time.sleep(speed)
    
      ShowWorms(speed)
      ShowClock(speed)
  
    #Reverse direction, bringing screen back down  
    for x in range (0,gv.HatWidth):
      del ScreenCap[-1]
      ScreenCap.insert(0,Buffer[HatWidth-1 -x])
      cf.setpixels(ScreenCap)
      #unicorn.show()
      #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
      time.sleep(speed)

      
      
      
      
def ScrollScreenShowSpaceInvaderTime(direction,speed):
  ScreenCap = unicorn.get_pixels()
  Buffer    = unicorn.get_pixels()
  EmptyCap = [[(0,0,0) for i in range (gv.HatWidth)] for j in range (gv.HatWidth)]

  for x in range (0,gv.HatWidth):
    cf.setpixel(x,3,99,99,200)
  
  #Delete top row, insert blank on bottom, pushing remaining up
  if (direction == 'up'):
    for x in range (0,gv.HatWidth):
      del ScreenCap[0]
      ScreenCap.append(EmptyCap[0])
      cf.setpixels(ScreenCap)
      #unicorn.show()
      #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
      time.sleep(speed)
    
    ShowSpaceInvaderTime(speed)
    
  
    #Reverse direction, bringing screen back down  
    for x in range (0,gv.HatWidth):
      del ScreenCap[-1]
      ScreenCap.insert(0,Buffer[HatWidth-1 -x])
      cf.setpixels(ScreenCap)
      #unicorn.show()
      #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
      time.sleep(speed)

      



      
def ScrollScreenShowWormsTime(direction,speed):
  ScreenCap = unicorn.get_pixels()
  Buffer    = unicorn.get_pixels()
  EmptyCap = [[(0,0,0) for i in range (gv.HatWidth)] for j in range (gv.HatWidth)]

  for x in range (0,gv.HatWidth):
    cf.setpixel(x,3,99,99,200)
  
  #Delete top row, insert blank on bottom, pushing remaining up
  if (direction == 'up'):
    for x in range (0,gv.HatWidth):
      del ScreenCap[0]
      ScreenCap.append(EmptyCap[0])
      cf.setpixels(ScreenCap)
      #unicorn.show()
      #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
      time.sleep(speed)
    
    ShowWorms(speed)
    ShowClock(speed)
  
    #Reverse direction, bringing screen back down  
    for x in range (0,gv.HatWidth):
      del ScreenCap[-1]
      ScreenCap.insert(0,Buffer[HatWidth-1 -x])
      cf.setpixels(ScreenCap)
      #unicorn.show()
      #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
      time.sleep(speed)
      
      

def ScrollScreenShowPacTime(direction,speed):
  ScreenCap = unicorn.get_pixels()
  Buffer    = unicorn.get_pixels()
  EmptyCap = [[(0,0,0) for i in range (gv.HatWidth)] for j in range (gv.HatWidth)]

  for x in range (0,gv.HatWidth):
    cf.setpixel(x,3,99,99,200)
  
  #Delete top row, insert blank on bottom, pushing remaining up
  if (direction == 'up'):
    for x in range (0,gv.HatWidth):
      del ScreenCap[0]
      ScreenCap.append(EmptyCap[0])
      cf.setpixels(ScreenCap)
      #unicorn.show()
      #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
      time.sleep(speed)
    

    ShowScrollingClock()
    
  
    #Reverse direction, bringing screen back down  
    for x in range (0,gv.HatWidth):
      del ScreenCap[-1]
      ScreenCap.insert(0,Buffer[HatWidth-1 -x])
      cf.setpixels(ScreenCap)
      #unicorn.show()
      #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
      time.sleep(speed)
      
      


def ShowScrollingClock():
  TheTime = cf.CreateClockSprite(12)
  
  
  #PacRightAnimatedSprite.Scroll(-5,1,'right',13,gv.ScrollSleep)
  #OrangeGhostSprite.ScrollAcrossScreen(0,1,"right",gv.ScrollSleep)

  ThreeGhostPacSprite.ScrollAcrossScreen(0,5,"right",gv.ScrollSleep)
  TheTime.ScrollAcrossScreen(0,5,"right",gv.ScrollSleep)

  #PacSprite.HorizontalFlip()
  #BlueGhostSprite.ScrollAcrossScreen(0,1,"left",gv.ScrollSleep)
  ThreeBlueGhostPacSprite.ScrollAcrossScreen(0,5,"left",gv.ScrollSleep)
  
  #PacLeftAnimatedSprite.Scroll(8,1,'left',13,gv.ScrollSleep)

  TheTime.ScrollAcrossScreen(0,5,"left",gv.ScrollSleep)
  #PacSprite.HorizontalFlip()
  



def ScrollScreenShowLittleShipTime(speed):
  
  ScreenCapBefore = copy.deepcopy(unicorn.get_pixels())
  ScreenCap       = copy.deepcopy(ScreenCapBefore)
  
  cf.ScrollScreen('up',ScreenCap,speed)
  ShowLittleShipTime(speed)
  cf.ScrollScreen('down',ScreenCapBefore,speed)
      

def ScrollScreenShowBigShipTime(direction,speed):

  ScreenCap  = copy.deepcopy(unicorn.get_pixels())
  cf.ScrollScreen('right',ScreenCap,speed)
  ShowBigShipTime(speed)
  cf.ScrollScreen('left',ScreenCap,speed)
    
    


      
def ScrollScreenShowClock(direction,speed):


  TheTime = cf.CreateClockSprite(12)
  TheTime.r = cf.SDLowGreenR
  TheTime.g = cf.SDLowGreenG
  TheTime.b = cf.SDLowGreenB
  
  #If we don't do a deep copy, ScreenCap ends up simply pointing to the Buffer 
  #and gets modified by scrolling functions!
  ScreenCap  = copy.deepcopy(unicorn.get_pixels())
  cf.ScrollScreen('up',ScreenCap,0.01)
  #ScrollScreen('right',ScreenCap,0.01)

  TheTime.ScrollAcrossScreen(0,5,"right",speed)
  cf.ScrollScreen('down',ScreenCap,0.01)


def ActivateBigClock():
  cf.ScrollBigClock('up',0.01, ZoomFactor=3,RGB=(200,0,0))

      
def ActivateClockMode(ClockOnDuration):
  #This method is the simplest
  #ShowDigitalClock(1,1,1)

  #If we don't do a deep copy, ScreenCap ends up simply pointing to the Buffer 
  #and gets modified by scrolling functions!
  #ScreenCap  = copy.deepcopy(unicorn.get_pixels())
  ScreenCap  = copy.deepcopy(gv.ScreenArray)
  cf.ScrollScreen('up',ScreenCap,0.01)
  cf.ClearBigLED()

  #Start a timer
  StartClockTime = time.time()
  DisplayTime = time.time()
  TheTime = cf.CreateClockSprite(12)
  TheTime.r = cf.SDLowGreenR
  TheTime.g = cf.SDLowGreenG
  TheTime.b = cf.SDLowGreenB

  
  Oldmm = 0
  done  = 0
  ShownOnce = 0


  print ("ACM - Started1")

  #Get EtheriumBalance in CDN funds
  #CashBalance, CurrencyPrice, ETHWalletBalance = cf.GetEthereumBalance()



  #Display Day of Week
  while ((CheckTimer(StartClockTime, ClockOnDuration) != 1) and (done == 0)):
    
    DOW = cf.CreateDayOfWeekSprite()

    
    
    #If the time has changed, draw a new time
    mm = datetime.now().strftime('%M')
    if (mm != Oldmm):
      #Erase old time
      Oldmm = mm
      TheTime.EraseNoShow(TheTime.h,TheTime.v)


      TheTime = cf.CreateClockSprite(12)
      TheTime.r = cf.SDMedGreenR
      TheTime.g = cf.SDMedGreenG
      TheTime.b = cf.SDMedGreenB

      #if the HH has double digits, sprite is too wide.  Trim the left empty columns.
      if (TheTime.width >= 14):
        TheTime = cf.LeftTrimSprite(TheTime,1)

      TheTime.h = 7 - (TheTime.width / 2)
      TheTime.v = 0
      
      if (TheTime.h < 0):
        TheTime.h = 0
    
      #Display New Time
      TheTime.CopySpriteToBuffer(TheTime.h,TheTime.v)
      


    
    time.sleep(0.5)    

    if (CheckTimer(DisplayTime,5) == 1):
      #Reset timer 
      DisplayTime = time.time()
      DOW.CopySpriteToBuffer(DOW.h,6)
      ShowRandomAnimation()
      #af.ShowFloatingBanner("ETH PRICE: " + str(CurrencyPrice)        ,(0,220,0),gv.ScrollSleep * 1.5,10)
      #af.ShowFloatingBanner("ETH OWNED: " + str(ETHWalletBalance / 1000000000000)     ,(0,0,240),gv.ScrollSleep * 1.5,10)
      cf.ShowFloatingBanner("ETH $"     + str(CashBalance)[0:7] + " CDN" ,(255,0,0),gv.ScrollSleep * 1.5,10)
      time.sleep(0.5)    

    else:  
      #Display the DOW (day of week)
      DOW.CopySpriteToBuffer(DOW.h,6)

    time.sleep(0.5)    

    #Zoom in to the time, but only once
    if (ShownOnce == 0):
      print ("ShownOnce:",ShownOnce)
      ScreenCap  = copy.deepcopy(unicorn.get_pixels())
      cf.ClearBigLED()
      cf.ZoomScreen(ScreenCap,2,17,0.025)
      ShownOnce = 1

    #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)


    #Check for keyboard input
    Key = cf.PollKeyboard()
    if (Key == 'q'):
      ProcessKeypress(Key)
      ClockOnDuration = 0
      done = 1
      print ("Trying to quit!")
    
    
    #unicorn.show()
    print (datetime.now())
    time.sleep(1)


  #Zoom Clock at end
  ScreenCap  = copy.deepcopy(unicorn.get_pixels())
  cf.ZoomScreen(ScreenCap,16,2,0.025)


  
  
  





def ActivateCurrencyMode(CurrencyOnDuration):

  #If we don't do a deep copy, ScreenCap ends up simply pointing to the Buffer 
  #and gets modified by scrolling functions!
  ScreenCap  = copy.deepcopy(unicorn.get_pixels())
  cf.ScrollScreen('up',ScreenCap,0.01)
  cf.ClearBigLED()

  #Start a timer
  StartClockTime = time.time()
  DisplayTime    = time.time()
  TheTime        = cf.CreateCurrencySprite()
  TheTime.r      = cf.SDLowGreenR
  TheTime.g      = cf.SDLowGreenG
  TheTime.b      = cf.SDLowGreenB

  
  Oldmm = 0
  done  = 0
  ShownOnce = 0


  print ("ACM - Started1")

  

  #Secondary Message
  while ((CheckTimer(StartClockTime, CurrencyOnDuration) != 1) and (done == 0)):
    
    #DOW = cf.CreateDayOfWeekSprite()
    DOW = cf.CreateBannerSprite('ETH')
   
    DOW.r = cf.SDMedOrangeR
    DOW.g = cf.SDMedOrangeG
    DOW.b = cf.SDMedOrangeB
    DOW.h = ((gv.HatWidth - DOW.width) // 2) -1
    DOW.v = 5
    DOW.rgb = (cf.SDMedGreenR,cf.SDMedGreenG,cf.SDMedGreenB)
  

    
    #get new price
    mm = datetime.now().strftime('%M')
    

    if (mm != Oldmm):
      #Erase old time
      Oldmm = mm
      TheTime.EraseNoShow(TheTime.h,TheTime.v)

      print("Get new cryptocurrency price")
      TheTime = cf.CreateCurrencySprite()
      TheTime.r = cf.SDMedGreenR
      TheTime.g = cf.SDMedGreenG
      TheTime.b = cf.SDMedGreenB

      #if the HH has double digits, sprite is too wide.  Trim the left empty columns.
      #if (TheTime.width >= 14):
      #  TheTime = cf.LeftTrimSprite(TheTime,1)

      TheTime.h = 7 - (TheTime.width / 2)
      TheTime.v = 0
      
      if (TheTime.h < 0):
        TheTime.h = 0
    
      #Display New Time
      TheTime.CopySpriteToBuffer(TheTime.h,TheTime.v)
      


    
    time.sleep(0.5)    

    if (CheckTimer(DisplayTime,5) == 1):
      #Reset timer 
      DisplayTime = time.time()
      DOW.CopySpriteToBuffer(DOW.h,6)
      ShowRandomAnimation()


      cf.ShowFloatingBanner("$" + TheTime.AccountBalance + " CDN",(220,220,0),gv.ScrollSleep * 1.5,10)
      #need to convert this to a animated color sprite so it can float across the screen, or add the function to Sprite
      time.sleep(0.5)    

    else:  
      #Display the DOW (day of week)
      DOW.CopySpriteToBuffer(DOW.h,6)

    time.sleep(0.5)    

    #Zoom in to the time, but only once
    if (ShownOnce == 0):
      print ("ShownOnce:",ShownOnce)
      ScreenCap  = copy.deepcopy(unicorn.get_pixels())
      cf.ClearBigLED()
      cf.ZoomScreen(ScreenCap,2,17,0.025)
      ShownOnce = 1

    #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)


    #Check for keyboard input
    Key = cf.PollKeyboard()
    if (Key == 'q'):
      ProcessKeypress(Key)
      ClockOnDuration = 0
      done = 1
      print ("Trying to quit!")
    
    
    #unicorn.show()
    print (datetime.now())
    time.sleep(1)


  #Zoom Clock at end
  ScreenCap  = copy.deepcopy(unicorn.get_pixels())
  cf.ZoomScreen(ScreenCap,16,2,0.025)


  
  
  


def CreateCurrencySprite():

  
  #check timers
  ElapsedSeconds = cf.GetElapsedSeconds(gv.StartTime)
  

  if(ElapsedSeconds >= gv.CryptoTimer):
    #Get EtheriumBalance in CDN funds
    gv.CryptoBalance, CurrencyPrice, ETHWalletBalance = cf.GetEthereumBalance()
    cf.SaveConfigData()


  TheSprite = cf.CreateBannerSprite(str(gv.CryptoBalance)[0:7])
  TheSprite = cf.JoinSprite(cf.DollarSignSprite, cf.LeftTrimSprite(TheSprite,0),0)
  TheSprite.r = 200
  TheSprite.g = 0
  TheSprite.b = 0
  

  return TheSprite;




def ShowRandomAnimation():
  #Make a banner to scroll -- need to make th is not erase the background
  #TheMessage = "The Time Is Now"
  #TheMessage = TheMessage.upper()
  #TheBanner = cf.CreateBannerSprite(TheMessage)
  #TheBanner.r = 0
  #TheBanner.g = 0 
  #TheBanner.b = 250 
  #TheBanner.ScrollAcrossScreen(gv.HatWidth-1,8,"left",0.1)
  #TheBanner.ScrollAcrossScreen(0-TheBanner.width,8,"right",0.1)
  #ShowScrollingBanner("Infection Cured!",cf.SDLowYellowR,cf.SDLowYellowG,cf.SDLowYellowB,gv.ScrollSleep *0.8)


  r = random.randint(0,25)
  if (r == 0):
    TinyInvader.FloatAcrossScreen(0,9,'right',gv.ScrollSleep)
  elif (r == 1):
    SmallInvader.FloatAcrossScreen(0,9,'right',gv.ScrollSleep)
  elif (r == 2):
    SpaceInvader.FloatAcrossScreen(0,8,'right',gv.ScrollSleep)
  elif (r == 3):
    TinyInvader.FloatAcrossScreen(0,9,'left',gv.ScrollSleep)
  elif (r == 4):
    SmallInvader.FloatAcrossScreen(0,9,'left',gv.ScrollSleep)
  elif (r == 5):
    SpaceInvader.FloatAcrossScreen(0,8,'left',gv.ScrollSleep)
  elif (r == 6):
    ThreeGhostPacSprite.FloatAcrossScreen(0,10,'right',gv.ScrollSleep)
  elif (r == 7):
    ThreeBlueGhostPacSprite.FloatAcrossScreen(0,10,'left',gv.ScrollSleep)
  elif (r == 8):
    DotZerkRobotWalking.FloatAcrossScreen(0,8,'left',gv.ScrollSleep)
  elif (r == 9):
    DotZerkRobotWalking.HorizontalFlip()
    DotZerkRobotWalking.FloatAcrossScreen(0,8,'right',gv.ScrollSleep)
    DotZerkRobotWalking.HorizontalFlip()
  elif (r == 11):
    DotZerkRobotWalkingSmall.FloatAcrossScreen(0,10,'left',gv.ScrollSleep)
  elif (r == 12):
    DotZerkRobotWalkingSmall.HorizontalFlip()
    DotZerkRobotWalkingSmall.FloatAcrossScreen(0,10,'right',gv.ScrollSleep)
    DotZerkRobotWalkingSmall.HorizontalFlip()
  elif (r == 13):
    LittleShipFlying.HorizontalFlip()
    BigShipFlying.HorizontalFlip()
    LittleShipFlying.FloatAcrossScreen(0,8,'left',gv.ScrollSleep)
    BigShipFlying.FloatAcrossScreen(0,8,'left',gv.ScrollSleep)
    LittleShipFlying.HorizontalFlip()
    BigShipFlying.HorizontalFlip()
  elif (r == 14):
    LittleShipFlying.FloatAcrossScreen(0,8,'right',gv.ScrollSleep)
    BigShipFlying.FloatAcrossScreen(0,8,'right', gv.ScrollSleep)
  elif (r == 15):
    ThreeGhostSprite.FloatAcrossScreen(0,11,'right',gv.ScrollSleep)
  elif (r == 16):
    ThreeGhostSprite.FloatAcrossScreen(0,11,'left',gv.ScrollSleep)
  elif (r == 17):
    PacLeftAnimatedSprite.Scroll(gv.HatWidth,11,'left',22,gv.ScrollSleep)
  elif (r == 18):
    PacRightAnimatedSprite.Scroll(gv.HatWidth,11,'right',22,gv.ScrollSleep)
  elif (r == 19):
    WheelAnimatedSprite.FloatAcrossScreen(0,8,'right',gv.ScrollSleep)
  elif (r == 20):
    ChickenRunning.FloatAcrossScreen(0,8,'left',gv.ScrollSleep)
  elif (r == 21):
    ChickenRunning.HorizontalFlip()
    ChickenRunning.FloatAcrossScreen(0,8,'right',gv.ScrollSleep)
    ChickenRunning.HorizontalFlip()
  elif (r == 22):
    WormChasingChicken.FloatAcrossScreen(0,8,'left',gv.ScrollSleep)
  elif (r == 23):
    WormChasingChicken.HorizontalFlip()
    WormChasingChicken.FloatAcrossScreen(0,8,'right',gv.ScrollSleep)
    WormChasingChicken.HorizontalFlip()
  elif (r == 24):
    ChickenChasingWorm.FloatAcrossScreen(0,8,'left',gv.ScrollSleep)
  elif (r == 25):
    ChickenChasingWorm.HorizontalFlip()
    ChickenChasingWorm.FloatAcrossScreen(0,8,'right',gv.ScrollSleep)
    ChickenChasingWorm.HorizontalFlip()
    

   


      

def ShowBigShipTime(speed):
  print ("SHowBigShipTime")
  TheTime = cf.CreateClockSprite(12)
  TheTime.r = cf.SDLowGreenR
  TheTime.g = cf.SDLowGreenG
  TheTime.b = cf.SDLowGreenB
  
  BigShipFlying.ScrollAcrossScreen(-16,0,'right',speed)
  BigShipFlying.HorizontalFlip()
  TheTime.ScrollAcrossScreen(0,1,"right",speed)
  BigShipFlying.ScrollAcrossScreen(8,0,'left',speed)
  BigShipFlying.HorizontalFlip()
  TheTime.ScrollAcrossScreen(0,1,"left",speed)


def ShowLittleShipTime(speed):
  TheTime = cf.CreateClockSprite(12)
  TheTime.r = cf.SDLowGreenR
  TheTime.g = cf.SDLowGreenG
  TheTime.b = cf.SDLowGreenB
  
  LittleShipFlying.ScrollAcrossScreen(-15,0,'right',speed)
  LittleShipFlying.HorizontalFlip()
  TheTime.ScrollAcrossScreen(0,1,"right",speed)
  LittleShipFlying.ScrollAcrossScreen(8,0,'left',speed)
  LittleShipFlying.HorizontalFlip()
  TheTime.ScrollAcrossScreen(0,1,"left",speed)



def ShowSpaceInvaderTime(speed):
  TheTime = cf.CreateClockSprite(12)
  TheTime.r = cf.SDLowGreenR
  TheTime.g = cf.SDLowGreenG
  TheTime.b = cf.SDLowGreenB
  
  
  
  r = random.randint(0,2)
  if (r == 0):
    TinyInvader.ScrollAcrossScreen(0,2,'right',speed)
    TheTime.ScrollAcrossScreen(0,2,"right",speed)
    TinyInvader.ScrollAcrossScreen(0,2,'left',speed)
    TheTime.ScrollAcrossScreen(0,2,"left",speed)
  elif (r == 1):
    SmallInvader.ScrollAcrossScreen(0,2,'right',speed)
    TheTime.ScrollAcrossScreen(0,2,"right",speed)
    SmallInvader.ScrollAcrossScreen(0,1,'left',speed)
    TheTime.ScrollAcrossScreen(0,2,"left",speed)
  elif (r == 2):
    SpaceInvader.ScrollAcrossScreen(0,2,'right',speed)
    TheTime.ScrollAcrossScreen(0,2,"right",speed)
    SpaceInvader.ScrollAcrossScreen(0,2,'left',speed)
    TheTime.ScrollAcrossScreen(0,2,"left",speed)
  

  

def movesparkyDot(Dot):
  h = 0
  v = 0
  Dot.trail.append((Dot.h, Dot.v))
  ItemList = []
  #Scan all around, make decision, move
  ItemList = ScanSuperWormsDirection(Dot.h,Dot.v,Dot.direction)
  
  #get possible items, then prioritize

  #empty = move forward
  if (ItemList[3] == 'EmptyObject'):
    Dot.h, Dot.v = cf.CalculateDotMovement(Dot.h,Dot.v,Dot.direction)
    
    
  #if heading to boundary or wall
  elif (ItemList[3] == 'wall' or ItemList[3] != 'EmptyObject' ):
    if (ItemList[1] == 'EmptyObject' and ItemList[5] == 'EmptyObject'):
      #print ("both empty picking random direction")
      Dot.direction = cf.TurnLeftOrRight(Dot.direction)
      Dot.h, Dot.v = cf.CalculateDotMovement(Dot.h,Dot.v,Dot.direction)
    elif (ItemList[1] == 'EmptyObject' and ItemList[5] != 'EmptyObject'):
      #print ("left empty turning left")
      Dot.direction = cf.TurnLeft(Dot.direction)
      Dot.h, Dot.v = cf.CalculateDotMovement(Dot.h,Dot.v,Dot.direction)
    elif (ItemList[5] == 'EmptyObject' and ItemList[1] != 'EmptyObject'):
      #print ("left empty turning right")
      Dot.direction =  cf.TurnRight(Dot.direction)
      Dot.h, Dot.v = cf.CalculateDotMovement(Dot.h,Dot.v,Dot.direction)
    else:
      print ("you died")
      Dot.alive = 0
      Dot.trail.append((Dot.h, Dot.v))
      #Dot.ColorizeTrail()
      #Dot.EraseTrail()
  
  return Dot



def DrawSnake(h,v,RGB,snakedirection,snakespeed):

  print ("DrawSnake")
  moves     = 0
  SleepTime = gv.MainSleep / 16

  #def __init__(self,h,v,r,g,b,direction,speed,alive,name,trail,score, maxtrail, erasespeed):
  r,g,b = (RGB)
  SparkyDot = cf.Dot(h,v,r,g,b,snakedirection,snakespeed,1,'Sparky',(0, 0), 0, 63,0.001)
  SparkyDot.Display()

  while (SparkyDot.alive == 1):
    moves = moves + 1
    #print("Moves:",moves)
    #m,r = divmod(moves,SparkyDot.speed)
    #if (r == 0):
    movesparkyDot(SparkyDot)
    SparkyDot.Display()
    #unicorn.show()
    #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
    

   #time.sleep(SleepTime)

    
  #time.sleep(MainSleep * 5)
  SparkyDot.EraseTrail('backward','noflash')
  cf.ClearBigLED()

  
  

def ShowBouncingSquare():
  WheelAnimatedSprite.Animate(4,1,0.05,'forward')
  WheelAnimatedSprite.Animate(4,1,0.05,'reverse')
  WheelAnimatedSprite.Animate(4,2,0.05,'forward')
  WheelAnimatedSprite.Animate(4,2,0.05,'reverse')
  WheelAnimatedSprite.Animate(4,3,0.05,'forward')
  WheelAnimatedSprite.Animate(4,3,0.05,'reverse')
  WheelAnimatedSprite.Animate(4,4,0.05,'forward')
  WheelAnimatedSprite.Animate(4,4,0.05,'reverse')
  WheelAnimatedSprite.Animate(4,5,0.05,'forward')




def ShowWorms(speed):
  print ("worms begin")
  #(width,height,r,g,b,frames,grid):
  Worm1 = cf.AnimatedSprite(4,2,75,75,0,1,[])
  Worm1.grid.append([0,0,0,0,
                     1,1,1,1])
  Worm1.grid.append([0,0,1,0,
                     0,1,0,1])

  Worm1.Scroll(gv.HatWidth+2,6,"left",gv.HatWidth+7,gv.ScrollSleep * 1.75)

  Worm2 = cf.AnimatedSprite(5,2,0,100,0,1,[])
  Worm2.grid.append([0,0,0,0,0,
                     1,1,1,1,1])
  Worm2.grid.append([0,0,1,0,0,
                     0,1,0,1,0])
  
  Worm2.Scroll(gv.HatWidth,3,"left",gv.HatWidth+7,gv.ScrollSleep * 1.75)
  
  
  Worms = cf.AnimatedSprite(7,6,100,0,75,1,[])
  Worms.grid.append([0,0,0,0,0,0,0,
                     0,0,0,1,1,1,1,
                     0,0,0,0,0,0,0,
                     0,0,0,0,0,0,0,
                     0,0,1,0,0,0,0,
                     0,1,0,1,0,0,0])

  Worms.grid.append([0,0,0,0,0,1,0,
                     0,0,0,0,1,0,1,
                     0,0,0,0,0,0,0,
                     0,0,0,0,0,0,0,
                     0,0,0,0,0,0,0,
                     1,1,1,1,0,0,0])


  Worms.Scroll(gv.HatWidth,1,"left",gv.HatWidth + 7,(gv.ScrollSleep * 1.25))
  
  print ("worms end")


def ShowClock(speed):
  TheTime = cf.CreateClockSprite(12)
  spritelen = len(TheTime.grid)
  TheTime.ScrollAcrossScreen(0,1,"right",speed)
  TheTime.ScrollAcrossScreen(0,1,"left",speed)
  

def CheckElapsedTime(seconds):
  global start_time
  elapsed_time = time.time() - start_time
  elapsed_hours, rem = divmod(elapsed_time, 3600)
  elapsed_minutes, elapsed_seconds = divmod(rem, 60)


  m,r = divmod(round(elapsed_seconds), seconds)
  #print("Elapsed Time: {:0>2}:{:0>2}:{:05.2f}".format(int(elapsed_hours),int(elapsed_minutes),elapsed_seconds)," CheckSeconds:",seconds," remainder:",r,end="\r")

  #if (elapsed_seconds >= seconds ):
    #start_time = time.time()
  if (r == 0):
    return 1
  else:
    return 0
  
  
def CheckClockTimer(ClockSprite):
  # if the clock is off, see if enough time has elapsed to turn it back on
  # if the clock is on, see if enough time has elapsed to turn it off

  #print ("CheckClockTimer: ",ClockSprite.StartTime)
  
  elapsed_time = time.time() - ClockSprite.StartTime
  elapsed_hours, rem = divmod(elapsed_time, 3600)
  elapsed_minutes, elapsed_seconds = divmod(rem, 60)
  #print("Clock Timer: {:0>2}:{:0>2}:{:05.2f}".format(int(elapsed_hours),int(elapsed_minutes),elapsed_seconds))
  
  
  if (ClockSprite.on == 1):
   #Turn off the clock if it is time to do so, but let it scroll off the screen
    if (elapsed_seconds >= ClockOnDuration and ClockSprite.v <= -5):
      print ("Turning off clock")
      ClockSprite.on = 0
      ClockSprite.StartTime = time.time()
      ClockSprite.h = (gv.HatWidth - ClockSprite.width) // 2
      ClockSprite.v = -5
  
  
  elif (ClockSprite.on == 0):
    if (elapsed_seconds >= ClockOffDuration ):
      print ("Turning on clock")
      ClockSprite.on = 1
      ClockSprite.StartTime = time.time()
      ClockSprite.h = (gv.HatWidth - ClockSprite.width) // 2
      ClockSprite.v = -5
  
  
    return 0



def CheckTimer(starttime, seconds):
  elapsed_time = time.time() - starttime
  elapsed_hours   = elapsed_time / 3600
  elapsed_minutes = elapsed_time / 60
  elapsed_seconds = elapsed_time 
  #print ("StartTime:",starttime,"Seconds:",seconds)
  #print("Clock Timer: {:0>2}:{:0>2}:{:05.2f}".format(int(elapsed_hours),int(elapsed_minutes),elapsed_seconds),"Elapsed seconds:",elapsed_seconds, "Check seconds:",seconds)
  
  if (elapsed_seconds >= seconds):
    return 1
  else:
    return 0


    
    
    
  
def MoveMessageSprite(moves,MessageSprite):

  
    m,r = divmod(moves,ClockSlideSpeed)
    if (r == 0):
      
      #print ("MessageSprite v:",MessageSprite.v)
      #if while moving the clock, it reaches the pause position, turn on the timer
      #only allow moves to happen if the timer has expired
      #this will allow the clock to display without moving for X seconds
      
      #March 2019 -- I want the clock to come down to half way point, pause, then go back up.
      
      
      if (MessageSprite.v == MessageSprite.PausePositionV):
        if (MessageSprite.PauseTimerOn == 0):
          MessageSprite.PauseTimerOn = 1
          MessageSprite.PauseStartTime = time.time()
        
        elapsed_time = time.time() - MessageSprite.PauseStartTime
        elapsed_hours, rem = divmod(elapsed_time, 3600)
        elapsed_minutes, elapsed_seconds = divmod(rem, 60)
        
        if (elapsed_seconds >= MessageSprite.Delay):
          if (MessageSprite.DirectionIncrement >= 0):
            MessageSprite.DirectionIncrement = MessageSprite.DirectionIncrement * -1
          MessageSprite.v = MessageSprite.v + MessageSprite.DirectionIncrement
         
      else:
        MessageSprite.PauseTimerOn = 0
        MessageSprite.v = MessageSprite.v + MessageSprite.DirectionIncrement

    #This causes the clock to bounce up from the bottom.
    #if (MessageSprite.v >= gv.HatHeight + 2 or MessageSprite.v <= -8):
      #reverse direction
    #  MessageSprite.DirectionIncrement = MessageSprite.DirectionIncrement * -1
  
    #This turns off clock at bottom
    # if (MessageSprite.v >= gv.HatHeight + 2 or MessageSprite.v <= -8):
      # MessageSprite.h = (gv.HatWidth - MessageSprite.width) / 2
      # MessageSprite.v = -4
      # MessageSprite.on = 0

    #This causes the clock to bounce up from the half way point
    if (MessageSprite.v >= MessageSprite.PausePositionV):
      #reverse direction
      MessageSprite.DirectionIncrement = MessageSprite.DirectionIncrement * -1
  
  
  #This turns off clock once off the screen
    if (MessageSprite.v >= gv.HatHeight + 2 or (MessageSprite.v < (0 - MessageSprite.height) and MessageSprite.DirectionIncrement < 0)) :
      MessageSprite.h = (gv.HatWidth - MessageSprite.width) // 2
      MessageSprite.v = 0 - MessageSprite.height
      MessageSprite.on = 0



      
#--------------------------------------
#  Dotster                           --
#--------------------------------------

def PlayDotster():
  
  cf.ClearBigLED()

  r,g,b = cf.ColorList[14]

  #Draw Test Car
  cf.setpixel(1,1,r,g,b)
  cf.setpixel(1,2,r,g,b)
  cf.setpixel(2,2,r,g,b)
  cf.setpixel(3,2,r,g,b)
  #unicorn.show()
  time.sleep(0.2)
  cf.ClearBigLED()
  cf.setpixel (0,1,r,g,b)
  cf.setpixel (1,2,r,g,b)
  cf.setpixel (2,1,r,g,b)
  #unicorn.show()
  time.sleep(0.2)
  cf.ClearBigLED() 
  cf.setpixel(1,1,r,g,b)
  cf.setpixel(1,2,r,g,b)
  cf.setpixel(2,2,r,g,b)
  cf.setpixel(3,2,r,g,b)
  #unicorn.show()
  time.sleep(0.2)
  cf.ClearBigLED()
  cf.setpixel (0,1,r,g,b)
  cf.setpixel (1,2,r,g,b)
  cf.setpixel (2,1,r,g,b)
  #unicorn.show()
  time.sleep(0.2)
  cf.ClearBigLED() 
  cf.setpixel(1,1,r,g,b)
  cf.setpixel(1,2,r,g,b)
  cf.setpixel(2,2,r,g,b)
  cf.setpixel(3,2,r,g,b)
  #unicorn.show()
  time.sleep(0.2)
  cf.ClearBigLED()
  cf.setpixel (0,1,r,g,b)
  cf.setpixel (1,2,r,g,b)
  cf.setpixel (2,1,r,g,b)
  #unicorn.show()
  time.sleep(0.2)
  cf.ClearBigLED() 
  cf.setpixel(1,1,r,g,b)
  cf.setpixel(1,2,r,g,b)
  cf.setpixel(2,2,r,g,b)
  cf.setpixel(3,2,r,g,b)
  #unicorn.show()
  time.sleep(0.2)
  cf.ClearBigLED()
  cf.setpixel (0,1,r,g,b)
  cf.setpixel (1,2,r,g,b)
  cf.setpixel (2,1,r,g,b)
  #unicorn.show()
  time.sleep(0.2)
  cf.ClearBigLED() 
  cf.setpixel(1,1,r,g,b)
  cf.setpixel(1,2,r,g,b)
  cf.setpixel(2,2,r,g,b)
  cf.setpixel(3,2,r,g,b)

  #unicorn.show()
  time.sleep(2)
  
  


  
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



        
def CreateRaceWorld(MapLevel):

  #The map is an array of a lists.  You can address each element has VH e.g. [V][H]
  #Copying the map to the playfield needs to follow the exact same shape


  if (MapLevel == 1):

    #Set world dimensions
    RaceWorld = cf.GameWorld(name='Level1',
                          width        = 48,
                          height       = 64,
                          Map          = [[]],
                          Playfield    = [[]],
                          CurrentRoomH = 2,
                          CurrentRoomV = 2,
                          DisplayH=1,
                          DisplayV=1)
    
    #Populate Map
    RaceWorld.Map = []
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10,10, 9, 9, 9, 9,10, 9, 9,  9, 9,10, 9, 9, 9, 9, 9,10, 9, 9, 9, 9,10, 9, 9,  9, 9,10, 9, 9, 9, 9,10,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0,26,26,26,26,26,26,26, 26, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0,26,26,26,26,26, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0,26, 0, 0, 0, 0, 0, 0, 26, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0,26, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0,26, 0, 0, 0, 0, 0, 0, 26, 0, 0, 0,26,26,26,26,26,26,26,26,26,26,26, 0,  0, 0, 0,26, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0,26, 0,27,27,27,27, 0, 26, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,26, 0,  0, 0, 0,26, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0,26, 0,27,27,27,27, 0, 26, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,26, 0,  0, 0, 0,26, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0,26, 0, 0,28,28, 0, 0, 26, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,26, 0,  0, 0, 0,26, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
                                                                                                                                                                              
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0,26, 0, 0,27,27, 0, 0, 26, 0, 0, 0,26,26,26,26, 0, 0, 0, 0, 0, 0,26, 0,  0, 0, 0,26, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0,26, 0, 0, 0, 0, 0, 0, 26, 0, 0, 0,26, 0, 0,26, 0, 0, 0, 0, 0, 0,26, 0,  0, 0, 0,26, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0,26, 0, 0, 0, 0, 0, 0, 26, 0, 0, 0,26, 0, 0,26, 0, 0, 0, 0, 0, 0,26, 0,  0, 0, 0,26, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0,26, 0, 0, 0, 0, 0, 0, 26, 0, 0, 0,26, 0, 0,26, 0, 0, 0, 0, 0, 0,26, 0,  0, 0, 0,26, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0,26, 0, 0, 0, 0, 0, 0, 26, 0, 0, 0,26, 0, 0,26, 0, 0, 0, 0, 0, 0,26, 0,  0, 0, 0,26, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0,26,26, 0, 0,  0, 0, 0, 0,26, 0, 0,26, 0, 0, 0, 0, 0, 0,26, 0,  0, 0, 0,26, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0,26,13,13,26, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,26, 0,  0, 0, 0,26, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0,26,14,14,26, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,26, 0,  0,26,26,26,26,26, 0, 0,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0,26,15,15,26, 0,  0,26,26,26,26,26,26,26,26,26,26, 0, 0, 0,26, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0,26,15,15,26, 0,  0,26, 0, 0,26, 0, 0,26, 0, 0,26, 0, 0, 0,26, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0,26,14,14,26, 0,  0,26, 0, 0,26, 0, 0,26, 0, 0,26, 0, 0, 0,26, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0,26,13,13,26, 0,  0,26, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,26, 0,  0,26, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0,26,26, 0, 0,  0,26, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,26, 0,  0, 0,26, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0,26, 0, 0,26, 0, 0,26, 0, 0,26, 0, 0, 0,26, 0,  0, 0, 0,26, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0,26, 0, 0,26, 0, 0,26, 0, 0,26, 0, 0, 0,26, 0,  0, 0, 0, 0,26, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0,26,26,26,26,26,26,26,26,26,26, 0, 0, 0,26, 0,  0, 0, 0, 0, 0,26, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
                                                                                                                                                                              
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0,26, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25,25,25,25,25,25, 25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0,26, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25,21,22,23,22,21, 25, 0, 0,25, 0, 0,25,25,25,25,25, 0, 0, 0, 0, 0,  0, 0,26, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0,25,21,22,23,22,21, 25, 0, 0,25, 0, 0,25,26,26,26,25, 0, 0, 0, 0, 0,  0,26, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25,21,22,23,22,21, 25, 0, 0,25, 0, 0,25,27,27,27,25, 0, 0, 0, 0, 0,  0, 0,26, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25,25,25,25,25,25, 25, 0, 0,25, 0, 0,25,28,28,28,25, 0, 0, 0, 0, 0,  0, 0, 0,26, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0,25, 0, 0,25,27,27,27,25, 0, 0, 0, 0, 0,  0, 0, 0, 0,26, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0,25, 0, 0,25,26,26,26,25, 0, 0, 0,26, 0,  0, 0, 0, 0, 0,26, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0,25, 0, 0,25,25,25,25,25, 0, 0,26,26,26,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0,25, 0, 0, 0, 0, 0, 0,25, 0, 0, 0,26, 0,  0,26, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0,25,25,25,25,25,  0, 0, 0,25, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0,  0, 0,26, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0,25,18,19,18,25,  0, 0, 0,25, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0,26, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0,25,18,19,18,25,  0, 0, 0,25, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0,26, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0,25,25,25,25,25,  0, 0, 0,25,25,25,25,25,25,25,25, 0, 0, 0,26, 0,  0, 0, 0, 0, 0,26, 0, 0,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,26,26,26,  0, 0, 0, 0,26, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,26, 0,  0, 0, 0,26, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
                                                                                                                                                                              
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0,26, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25,25,25,25,25,25, 25, 0, 0, 0,25,25,25,25,25,25,25, 0, 0, 0, 0, 0,  0,26, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0,25, 5, 6, 7, 6, 5, 25, 0, 0, 0,25,29,30,31,30,29,25, 0, 0, 0, 0, 0,  0, 0,26, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 5, 6, 7, 6, 5, 25, 0, 0, 0,25,29,30,31,30,20,25, 0, 0, 0,26, 0,  0, 0, 0,26, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 5, 6, 7, 6, 5, 25, 0, 0, 0,25,25,25,25,25,25,25, 0, 0,26,26,26,  0, 0, 0, 0,26, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25,25,25,25,25,25, 25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,26, 0,  0, 0, 0, 0, 0,26, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10,10, 9, 9, 9, 9,10, 9, 9,  9, 9,10, 9, 9, 9, 9,10,10, 9, 9, 9,10, 9, 9, 9,  9,10, 9, 9, 9, 9, 9,10,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])


    RaceWorld.CopyMapToPlayfield()




    
  
  if (MapLevel == 2):

    #Set world dimensions
    RaceWorld = cf.GameWorld(name='Level1',
                          width        = 48,
                          height       = 64,
                          Map          = [[]],
                          Playfield    = [[]],
                          CurrentRoomH = 2,
                          CurrentRoomV = 2,
                          DisplayH=1,
                          DisplayV=1)
    
    #Populate Map
    RaceWorld.Map = []
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10,10, 9, 9, 9, 9,10, 9, 9,  9, 9,10, 9, 9, 9, 9, 9,10, 9, 9, 9, 9,10, 9, 9,  9, 9,10, 9, 9, 9, 9,10,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0,25,25, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0,25,26,26,25, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0,25,25,25,25, 25, 0, 0, 0, 0,25,27, 0, 0,27,25, 0, 0, 0, 0,25, 25,25,25,25, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0,25,26,27,26, 25,25,25,25,25,25, 0, 0, 0, 0,25,25,25,25,25,25, 26,27,26,25, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0,25,26,27,26, 25,25,25,25,25,25, 0, 0, 0, 0,25,25,25,25,25,25, 26,27,26,25, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0,25,25,25,25, 25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25, 26,27,26,25, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25, 25,25,25,25, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])

    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0,25,25,25,25, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0,26,25,25,25,25,25,25,26, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0,26,25,25,26, 0, 0, 0, 0,26,25,25,26, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0,25,25,26, 0, 0, 0, 0, 0, 0, 0, 0,26,25,25, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0,25,26, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0,25,25,26, 0, 0, 0, 0, 0, 0, 0, 0,26,25,25, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0,26,25,25,26, 0, 0, 0, 0,26,25,25,26, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0,26,25,25,25,25,25,25,26, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0,25,25,25,25, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])

    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0,25,26, 0,  0, 0, 0, 0, 0, 0, 0,25,25, 0, 0, 0, 0, 0, 0, 0,  0,26,25, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0,25,26, 0,  0, 0, 0, 0, 0, 0,25,25,25,25, 0, 0, 0, 0, 0, 0,  0,26,25, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0,25,26, 0,  0, 0, 0,25,25,25,25,25,25,25,25,25,25, 0, 0, 0,  0,26,25, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0,25,26, 0,  0, 0, 0,25,26,26,26,26,26,26,26,26,25, 0, 0, 0,  0,26,25, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0,25,26, 0,  0, 0, 0,25,26,27,27,27,27,27,27,26,25, 0, 0, 0,  0,26,25, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0,25,26, 0,  0, 0, 0,25,26,27,28,28,28,28,27,26,25, 0, 0, 0,  0,26,25, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0,25,25,25, 25,25,25,25,26,27,28,20,20,28,27,26,25,25,25,25, 25,25,25, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0,25,26,26, 26,26,26,25,26,27,28,20,20,28,27,26,25,26,26,26, 26,26,25, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0,25,26, 0,  0, 0, 0,25,26,27,28,28,28,28,27,26,25, 0, 0, 0,  0,26,25, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0,25,26, 0,  0, 0, 0,25,26,27,27,27,27,27,27,26,25, 0, 0, 0,  0,26,25, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0,25,26, 0,  0, 0, 0,25,26,26,26,26,26,26,26,26,25, 0, 0, 0,  0,26,25, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0,25,26, 0,  0, 0, 0,25,25,25,25,25,25,25,25,25,25, 0, 0, 0,  0,26,25, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0,25,26, 0,  0, 0, 0, 0, 0, 0,25,25,25,25, 0, 0, 0, 0, 0, 0,  0,26,25, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0,25,26, 0,  0, 0, 0, 0, 0, 0, 0,25,25, 0, 0, 0, 0, 0, 0, 0,  0,26,25, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])

    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,26,26, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0,26,26,26, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0,26,26, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,26,26, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0,26,26,26, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0,26,26, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10,10, 9, 9, 9, 9,10, 9, 9,  9, 9,10, 9, 9, 9, 9,10,10, 9, 9, 9,10, 9, 9, 9,  9,10, 9, 9, 9, 9, 9,10,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])


    RaceWorld.CopyMapToPlayfield()

    print (RaceWorld.Map[0])
    print (RaceWorld.Map[1])
    print (RaceWorld.Map[2])
    print (RaceWorld.Map[3])
  
    
    
  if (MapLevel == 3):
    #Set world dimentions
    RaceWorld = cf.GameWorld(name='Level3',
                          width        = 40,
                          height       = 40,
                          Map          = [[]],
                          Playfield    = [[]],
                          CurrentRoomH = 2,
                          CurrentRoomV = 2,
                          DisplayH=8,
                          DisplayV=8)

    RaceWorld.Map = []
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  ])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  ])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  ])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  ])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  ])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  ])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  ])  
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10,10, 9, 9, 9,  9,10,10, 9, 9, 9, 9,10, 10, 9, 9, 9, 9,10,10, 9,  9, 9, 9,10,10, 9, 9, 9, 9, 9, 9, 9,  ])  
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,  ])  
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,  ])  
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,  ])  
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,  ])  
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0,25,25,25, 25,25, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0,25,25, 25,25,25, 0, 9, 9, 9, 9, 9, 9, 9, 9,  ])  
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0,  0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0,25, 0, 0,  0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9,  ])  
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0,25, 0, 0, 0, 0,  0, 0, 0, 0,25, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,  ])  
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0,26,26,26,26, 0,  0,26,26,26,26, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,  ])  

    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0,  0, 0,25,25,25,25,25, 0,  0,25,25,25,25,25, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,  ])  
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0,  0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0,25, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,  ])  
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0,  0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0,25, 0, 0,  0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9,  ])  
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0,  0, 0,25, 0, 0, 5, 5, 0,  0, 5, 5, 0, 0,25, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,  ])  
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0,  0, 0,25, 0, 0, 5, 7, 0,  0, 7, 5, 0, 0,25, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,  ])  
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9,25,25,25, 0,  0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0,25, 0, 0,  0,25,25,25, 9, 9, 9, 9, 9, 9, 9, 9,  ])  
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0,25, 0,  0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0,25, 0, 0,  0,25, 0, 0,10, 9, 9, 9, 9, 9, 9, 9,  ])  
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0,  0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0,25, 0, 0,  0,25, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,  ])  
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0,  0, 0,25,25,25,25,25, 0,  0, 0,25,25,25,25, 0, 0,  0,25, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,  ])  
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0,  0, 0, 0,26,26,26,26, 0,  0, 0,26,26,26, 0, 0, 0,  0,25, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,  ])  
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0, 0, 0,26,26, 0,  0, 0,26,26, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,  ])  
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9,  ])  
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25,25, 25,25, 0, 0, 0, 0,17, 0,  0,17, 0, 0, 0, 0,25,25, 25,25, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,  ])  
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0,17, 0,  0,17, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,  ])  
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0,17, 0,  0,17, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,  ])  
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,  ])  

    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10,10, 9, 9, 9,  9,10,10, 9, 9, 9, 9,10, 10, 9, 9, 9, 9,10,10, 9,  9, 9, 9,10,10, 9, 9, 9, 9, 9, 9, 9,  ])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  ])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  ])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  ])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  ])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  ])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  ])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  ])

    RaceWorld.CopyMapToPlayfield()


  if (MapLevel == 4):

    #Set world dimensions
    RaceWorld = cf.GameWorld(name='Level1',
                          width        = 48,
                          height       = 64,
                          Map          = [[]],
                          Playfield    = [[]],
                          CurrentRoomH = 1,
                          CurrentRoomV = 1,
                          DisplayH=1,
                          DisplayV=1)
    
    #Populate Map
    RaceWorld.Map = []
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10,10, 9, 9, 9, 9,10, 9, 9,  9, 9,10, 9, 9, 9, 9, 9,10, 9, 9, 9, 9,10, 9, 9,  9, 9,10, 9, 9, 9, 9,10,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])

    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0,25,26, 0,  0, 0, 0, 0, 0, 0, 0,25,25, 0, 0, 0, 0, 0, 0, 0,  0,26,25, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0,25,26, 0,  0, 0, 0, 0, 0, 0,25,25,25,25, 0, 0, 0, 0, 0, 0,  0,26,25, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0,25,26, 0,  0, 0, 0,25,25,25,25,25,25,25,25,25,25, 0, 0, 0,  0,26,25, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0,25,26, 0,  0, 0, 0,25,26,26,26,26,26,26,26,26,25, 0, 0, 0,  0,26,25, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0,25,26, 0,  0, 0, 0,25,26,27,27,27,27,27,27,26,25, 0, 0, 0,  0,26,25, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0,25,26, 0,  0, 0, 0,25,26,27,28,28,28,28,27,26,25, 0, 0, 0,  0,26,25, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0,25,25,25, 25,25,25,25,26,27,28,20,20,28,27,26,25,25,25,25, 25,25,25, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0,25,26,26, 26,26,26,25,26,27,28,20,20,28,27,26,25,26,26,26, 26,26,25, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0,25,26, 0,  0, 0, 0,25,26,27,28,28,28,28,27,26,25, 0, 0, 0,  0,26,25, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0,25,26, 0,  0, 0, 0,25,26,27,27,27,27,27,27,26,25, 0, 0, 0,  0,26,25, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0,25,26, 0,  0, 0, 0,25,26,26,26,26,26,26,26,26,25, 0, 0, 0,  0,26,25, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0,25,26, 0,  0, 0, 0,25,25,25,25,25,25,25,25,25,25, 0, 0, 0,  0,26,25, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0,25,26, 0,  0, 0, 0, 0, 0, 0,25,25,25,25, 0, 0, 0, 0, 0, 0,  0,26,25, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0,25,26, 0,  0, 0, 0, 0, 0, 0, 0,25,25, 0, 0, 0, 0, 0, 0, 0,  0,26,25, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])


    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0,25,26, 0,  0, 0, 0, 0, 0, 0, 0,25,25, 0, 0, 0, 0, 0, 0, 0,  0,26,25, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0,25,26, 0,  0, 0, 0, 0, 0, 0,25,25,25,25, 0, 0, 0, 0, 0, 0,  0,26,25, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0,25,26, 0,  0, 0, 0,25,25,25,25,25,25,25,25,25,25, 0, 0, 0,  0,26,25, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0,25,26, 0,  0, 0, 0,25,26,26,26,26,26,26,26,26,25, 0, 0, 0,  0,26,25, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0,25,26, 0,  0, 0, 0,25,26,27,27,27,27,27,27,26,25, 0, 0, 0,  0,26,25, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0,25,26, 0,  0, 0, 0,25,26,27,28,28,28,28,27,26,25, 0, 0, 0,  0,26,25, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0,25,25,25, 25,25,25,25,26,27,28,20,20,28,27,26,25,25,25,25, 25,25,25, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0,25,26,26, 26,26,26,25,26,27,28,20,20,28,27,26,25,26,26,26, 26,26,25, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0,25,26, 0,  0, 0, 0,25,26,27,28,28,28,28,27,26,25, 0, 0, 0,  0,26,25, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0,25,26, 0,  0, 0, 0,25,26,27,27,27,27,27,27,26,25, 0, 0, 0,  0,26,25, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0,25,26, 0,  0, 0, 0,25,26,26,26,26,26,26,26,26,25, 0, 0, 0,  0,26,25, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0,25,26, 0,  0, 0, 0,25,25,25,25,25,25,25,25,25,25, 0, 0, 0,  0,26,25, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0,25,26, 0,  0, 0, 0, 0, 0, 0,25,25,25,25, 0, 0, 0, 0, 0, 0,  0,26,25, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0,25,26, 0,  0, 0, 0, 0, 0, 0, 0,25,25, 0, 0, 0, 0, 0, 0, 0,  0,26,25, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])

    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10,10, 9, 9, 9, 9,10, 9, 9,  9, 9,10, 9, 9, 9, 9,10,10, 9, 9, 9,10, 9, 9, 9,  9,10, 9, 9, 9, 9, 9,10,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])

    RaceWorld.CopyMapToPlayfield()


    
  if (MapLevel == 5):
    #Set world dimentions
    RaceWorld = cf.GameWorld(name='Level5',
                          width        = 48,
                          height       = 64,
                          Map          = [[]],
                          Playfield    = [[]],
                          CurrentRoomH = 2,
                          CurrentRoomV = 1,
                          DisplayH=1,
                          DisplayV=1)
    
    
        #Populate Map
    RaceWorld.Map = []
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10,10, 9, 9, 9, 9,10, 9, 9,  9, 9,10, 9, 9, 9, 9, 9,10, 9, 9, 9, 9,10, 9, 9,  9, 9,10, 9, 9, 9, 9,10,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
                                                                                                                                                                              
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0,25, 0, 0, 0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0,25,25, 0, 0, 0, 0,25,25, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0,25,26,25, 0, 0, 0, 0,25,26,25, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0,25,26,26,25, 0, 0, 0, 0,25,26,26,25, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0,25,26,26,26,25, 0, 0, 0, 0,25,26,26,26,25, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0, 25,26,26,27,26,25, 0, 0, 0, 0,25,26,27,26,26,25,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0, 25,26,26,26,26,25, 0, 0, 0, 0,25,26,26,26,26,25,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0, 25,25,25,25,25, 0, 0, 0, 0, 0, 0,25,25,25,25,25,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0, 25,25,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25,25,25,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0, 25,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25,25,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0, 25,25, 0,25,25, 0, 0, 0, 0, 0, 0,25,25, 0,25,25,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0, 25,25, 0,26,27, 0, 0, 0, 0, 0, 0,26,27, 0,25,25,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0, 25,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25,25,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0, 25,25, 0, 0, 0, 0,25,25,25,25, 0, 0, 0, 0,25,25,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0, 25,25, 0, 0, 0, 0,25,26,26,25, 0, 0, 0, 0,25,25,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0, 25,25, 0, 0, 0, 0,25,27,27,25, 0, 0, 0, 0,25,25,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
                                                                                                                                                                              
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0, 25,25, 0, 0, 0, 0,25,27,27,25, 0, 0, 0, 0,25,25,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0,25,25, 25,25, 0, 0, 0, 0,25,26,26,25, 0, 0, 0, 0,25,25, 25,25, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0,25,25, 25,25, 0, 0, 0, 0,25,25,25,25, 0, 0, 0, 0,25,25, 25,25, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0,25,25,25,25, 25,25, 0, 0, 0, 0, 0,25,25, 0, 0, 0, 0, 0,25,25, 25,25,25,25, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25,25,25,25,25, 0, 25,25, 0, 0, 0, 0, 0,25,25, 0, 0, 0, 0, 0,25,25,  0,25,25,25,25,25, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25,25, 0, 0, 0, 0, 25,25, 0, 0, 0, 0, 0,25,25, 0, 0, 0, 0, 0,25,25,  0, 0, 0, 0,25,25, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25,25, 0, 0, 0, 0, 25,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25,25,  0, 0, 0, 0,25,25, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,26,26, 0, 0, 0, 0, 25,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25,25,  0, 0, 0, 0,26,26, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0,26,26, 0, 0, 0, 0, 25,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25,25,  0, 0, 0, 0,26,26, 0, 0,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,27,27, 0, 0, 0, 0, 25,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25,25,  0, 0, 0, 0,27,27, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,27,27, 0, 0, 0, 0, 25,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25,25,  0, 0, 0, 0,27,27, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,28,28, 0, 0, 0, 0,  0,25,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25,25, 0,  0, 0, 0, 0,28,28, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0,25,25, 0, 0, 0, 0, 0, 0, 0, 0,25,25, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0,25,25, 0, 0, 0, 0, 0, 0,25,25, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0,25,25,25,25,25,25,25,25, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0,25,25,25,25,25,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])

    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10,10, 9, 9, 9, 9,10, 9, 9,  9, 9,10, 9, 9, 9, 9,10,10, 9, 9, 9,10, 9, 9, 9,  9,10, 9, 9, 9, 9, 9,10,10, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,])

    RaceWorld.CopyMapToPlayfield()


  if (MapLevel == 6):
    #Set world dimentions
    RaceWorld = cf.GameWorld(name='Level6',
                          width        = 80,
                          height       = 144,
                          Map          = [[]],
                          Playfield    = [[]],
                          CurrentRoomH = 2,
                          CurrentRoomV = 1,
                          DisplayH=1,
                          DisplayV=1)
    
    
        #Populate Map
    RaceWorld.Map = []
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10,10, 9, 9, 9, 9,10, 9, 9,  9, 9,10, 9, 9, 9, 9, 9,10, 9, 9, 9, 9,10, 9, 9,  9, 9,10, 9, 9, 9, 9,10,10, 9, 9, 9, 9, 9, 9, 9,  9, 9,10, 9, 9, 9, 9, 9,10, 9, 9, 9, 9,10, 9, 9,  9, 9,10, 9, 9, 9, 9,10,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0,25,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0,25,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25,25,25,25,25,25, 25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,  0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0,25, 25,25,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0, 0, 0,25, 25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25,  0, 0, 0, 0, 0, 0,25, 0, 0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0, 0, 0,25, 25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25,  0, 0, 0, 0, 0, 0,25, 0, 0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0, 0, 0,25, 25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25,  0, 0, 0, 0, 0, 0,25, 0, 0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25,  0, 0, 0, 0, 0, 0,25, 0, 0, 0,25, 0, 0, 0, 0,25, 25,25,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25,  0, 0, 0, 0, 0, 0,25, 0, 0, 0,25, 0, 0, 0, 0,25,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
                                                                                                                                                                                                                                                                               
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25,  0, 0, 0, 0, 0, 0,25, 0, 0, 0,25, 0, 0, 0, 0,25,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0,25,25, 0,  0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25,  0, 0, 0, 0, 0, 0,25, 0, 0, 0,25, 0, 0, 0, 0,25,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0,25, 0, 0,  0, 0,25,25,25,25,25,25,25,25,25,25, 0, 0, 0,25,  0, 0, 0, 0, 0, 0,25,25,25,25,25, 0, 0, 0, 0,25,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0,25, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0,25,  0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0,25,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0,25, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0,25,  0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0,25,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0,25, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0,25,  0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0,25,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0,25, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0,25,  0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0,25,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0,25, 0, 0,25, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0,25,  0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0,25,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0,25, 0, 0,25, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0,25,  0, 0, 0, 0, 0, 0,25,25,25,25,25,25,25,25,25,25,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0,25, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0,25,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0,25, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0,25,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0,25, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0,25,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0,25, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0, 0,25,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0,25, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0,25,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0,25, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25, 0,25,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0,25, 0, 0,25,25,25,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25,25,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
                                                                                                                                                                                                                                                                               
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0,25, 0, 0, 0, 0, 0,  0, 0,25,25,25,25,25,25,25,25, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0, 0, 0, 0,  0, 0,25, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0, 0, 0, 0,  0, 0,25, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0, 0, 0, 0,  0, 0,25, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0, 0, 0, 0,  0, 0,25, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0, 0, 0, 0,  0, 0,25, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0, 0, 0, 0,  0, 0,25, 0, 0, 0, 0, 0, 0,25,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0,25, 0, 0, 0, 0, 0,  0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0,25, 0, 0, 0, 0, 0,  0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0, 0, 0, 0,  0, 0,25,25,25,25,25,25, 0, 0, 0, 0, 0,25, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
                                                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                               
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25, 25,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25,  5,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0, 0, 0, 0,  0, 0,25,25,25,25,25, 0, 0, 0, 0, 0, 0, 0, 0,25,  5,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0, 0, 0, 0,  0, 0,25,26,27,26,25, 0, 0, 0, 0, 0, 0, 0, 0,25,  5,25, 0, 0, 0, 0, 0, 0,25,25,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25,25,25,25, 0, 0,  0, 0,25,26,27,26,25, 0, 0, 0, 0, 0, 0, 0, 0,25,  5,25, 0, 0, 0, 0, 0,25,26,26,26,25, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25,25,25,25, 0, 0,  0, 0,25,26,27,26,25,25,25,25,25,25,25,25,25,25,  5,25, 0, 0, 0, 0,25,26,27,27,27,26,25, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0,25, 0, 0, 0, 0, 0,  0, 0,25,26,27,26,26,26,26,26,26,26,26,26,26,26,  5,25, 0, 0, 0,25,26,27,28,28,28,27,26,25, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0,25, 0, 0, 0, 0, 0,  0, 0,25,26,27,26,26,26,26,26,26,26,26,26,26,26,  5,25, 0, 0, 0,25,26,27,28, 4,28,27,26,25, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0, 0, 0, 0,  0, 0,25,26,27,26,25,25,25,25,25,25,25,25,25,25,  5,25, 0, 0, 0,25,26,27,28, 4,28,27,26,25, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0, 0, 0, 0,  0, 0,25,26,27,26,25, 0, 0, 0, 0, 0, 0, 0, 0,25,  5,25, 0, 0, 0,25,26,27,28, 4,28,27,26,25, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0, 0, 0, 0,  0, 0,25,26,27,26,25, 0, 0, 0, 0, 0, 0, 0, 0,25,  5,25, 0, 0, 0,25,26,27,28,28,28,27,26,25, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0, 0, 0, 0,  0, 0,25,26,27,26,25, 0, 0, 0, 0, 0, 0, 0, 0,25, 25,25, 0, 0, 0, 0,25,26,27,27,27,26,25, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0, 0, 0, 0,  0, 0,25,25,25,25,25, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0,25,26,26,26,25, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,25,25,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
                                                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                               
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25,25,25, 25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25,  0, 0, 0, 0, 0, 0, 0, 0, 0,25,25,25,25, 0, 0, 0, 25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0, 0, 0, 0, 25,25,25,25,25,25,25,25, 0, 0, 0, 0, 0, 0, 0,25,  0, 0, 0, 0, 0,25,25,25,25, 0, 0, 0, 0, 0, 0, 0, 25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0,25,  0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0,25,  0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0,25,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0,25,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0,25,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0,25,  0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0,25,25,25, 25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0,25,25,25,25,25,25,25,25,25,25, 0, 0,25,  0, 0, 0, 0, 0,25, 0, 0, 0,25,25,25,25, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25,  0, 0, 0, 0, 0,25,25,25,25, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0,25, 0, 0, 0, 0,25,25,25,25,25, 0, 0,25,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0,25, 0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0,25,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0,25, 0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0,25,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
                                                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                               
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0,25, 0, 0, 0,25,25, 25,25,25,25, 0, 0, 0, 0,25,25,25, 0, 0, 0, 0,25,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0, 0,25, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0,25,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0, 0,25, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0,25,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0, 0,25, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0,25,  0, 0, 0, 0,25,25,25,25,25, 0, 0, 0, 0, 0, 0, 0,  0, 0,25,25,25,25,25, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0, 0,25, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0,25,  0, 0, 0, 0,25,18,19,20,19,25,25,25,25, 0, 0, 0,  0, 0,25, 6, 6, 6,25, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0, 0,25,25, 25,25,25,25,25,25,25,25,25,25,25, 0, 0, 0, 0,25,  0, 0, 0, 0,25,18,19,20,19,18,18,18,18,25,25,25,  0, 0,25, 6, 7, 6,25, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25,  0, 0, 0, 0,25,18,19,20,20,20,20,20,20,20,20, 0, 25,25,25, 6, 8, 6,25, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25,  0, 0, 0, 0,25,18,19,20,19,18,18,18,18,25,25,25,  0, 0,25, 6, 7, 6,25, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25,  0, 0, 0, 0,25,18,19,20,19,25,25,25,25, 0, 0, 0,  0, 0,25, 6, 6, 6,25, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25,  0, 0, 0, 0,25,25,25,25,25, 0, 0, 0, 0, 0, 0, 0,  0, 0,25,25,25,25,25, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0,25,25,25,25,25,25, 25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0,25,25,25,25,25,25,25,25,25,25,25,25, 25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,25, 25,25, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
                                                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                               
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0,25, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0,25, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 5, 0, 0,  0,25, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9,25,25,25,25,25,25,25,25, 25,25,25,25,25,25,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 25,25,25,25,25, 0, 0, 0,18,18,18,18,18,18,18, 0,  0, 0, 0, 0, 0, 0, 0,18,18,18,18,18,18,18, 0, 0,  0,25, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9,25,26,26,26,26,26,26,26, 26,26,26,26,26,26,25, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,18, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,18, 0, 0, 0,  0,25, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9,25,26, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0,26,25, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,18, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,18, 0, 0, 0, 0,  0,25, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9,25,26, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0,26,25, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,18, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,18, 0, 0, 0, 0,  0,25, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10,25,26, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0,26,25, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,18, 0, 0, 0,  0,18,18,18,18,18,18, 0, 0, 0,18, 0, 0, 0, 0, 0,  0,25, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10,25,26, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0,26,25, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,18,18, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0,18, 0, 0, 0, 0, 0,  0,25, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9,25,26, 0, 0,15,15,15,15, 15,15,15, 0, 0,26,25, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,18, 0,18, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0,18, 0, 0, 0, 0, 0, 0,  0,25, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9,25,26, 0, 0,15,14,14,14, 14,14,15, 0, 0,26,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 25,25,25,25,25, 0, 0, 0, 0, 0,18, 0, 0, 0,18, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0,18, 0, 0, 0, 0, 0, 0,  0,25, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9,25,26, 0, 0,15,14,13,13, 13,14,15, 0, 0,26,25, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0,25, 0, 0, 0, 0,18, 0, 0, 0, 0, 0,18,  0, 0, 0, 0, 0, 0, 0, 0,18, 0, 0, 0, 0, 0, 0, 0,  0,25, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9,25,26, 0, 0,15,14,13,13, 13,14,15, 0, 0,26,25, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0,25, 0, 0, 0,18, 0, 0, 0, 0, 0, 0, 0, 18, 0, 0, 0, 0, 0, 0,18, 0, 0, 0, 0, 0, 0, 0, 0,  0,25, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9,25,26, 0, 0,15,14,13,13, 13,14,15, 0, 0,26,25, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0,25, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9,25,26, 0, 0,15,14,13,13, 13,14,15, 0, 0,26,25, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0,25, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10,25,26, 0, 0,15,14,13,13, 13,14,15, 0, 0,26,25, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0,25, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
                                                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                               
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10,25,26, 0, 0,15,14,13,13, 13,14,15, 0, 0,26,25, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0,25,25,25,25,25,25,25,25,25,25,25,25, 25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,25, 25,25, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9,25,26, 0, 0,15,14,13,13, 13,14,15, 0, 0,26,25, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,25,26,26,26,25, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9,25,26, 0, 0,15,14,13,13, 13,14,15, 0, 0,26,25, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,25,26,26,26,25, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9,25,26, 0, 0,15,14,13,13, 13,14,15, 0, 0,26,25, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,25,25,25,25,25, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9,25,26, 0, 0,15,14,13,13, 13,14,15, 0, 0,26,25, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9,25,26, 0, 0,15,14,13,13, 13,14,15, 0, 0,26,25, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0,25,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0,25,25, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9,25,26, 0, 0,15,14,13,13, 13,14,15, 0, 0,26,25, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0,25, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10,25,26, 0, 0,15,14,13,13, 13,14,15, 0, 0,26,25, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0,25, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10,25,26, 0, 0,15,14,14,14, 14,14,15, 0, 0,26,25, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0,25, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9,25,26, 0, 0,15,15,15,15, 15,15,15, 0, 0,26,25, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0,25, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9,25,26, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0,26,25, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0,25,26,25, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0,25, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9,25,26, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0,26,25, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0,25,26,26,26,25, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0,25, 0, 0, 0,25,25,25,25,25,25,25,25,25,25,  0, 0, 0,25, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9,25,26, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0,26,25, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0,25,26,26,27,26,26,25, 0, 0, 0, 0, 0, 0, 0,  0, 0,25, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0,25,  0, 0, 0,25, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9,25,26, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0,26,25, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0,25,26,26,27,28,27,26,26,25, 0, 0, 0, 0, 0, 0,  0, 0,25, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0,25,  0, 0, 0,25, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9,25,26,26,26,26, 0, 0, 0, 26,26,26,26,26,26,25, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0,25,26,26,27,26,26,25, 0, 0, 0, 0, 0, 0, 0,  0, 0,25, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0,25,  0, 0, 0,25, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10,25,25,25,25,25, 0, 0, 0, 25,25,25,25,25,25,25, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0,25,26,26,26,25, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0,25, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0,25,  0, 0, 0,25, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
                                                                                                                                                                                                                                                                               
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0,25,25, 0, 0, 0, 25,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0,25,26,25, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0,25,25,25,25,25, 0, 0, 0, 0, 0, 0, 0, 0,25, 25,25,25,25, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0,25,25, 0, 0, 0, 25,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0,25, 0, 0, 0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0,25,25, 0, 0, 0, 25,25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25,25, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25,25,25, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0,25,25,25, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0,25,25,25, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25,25,25,25, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,25,25,25,25,25, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,25,25,25,25,25, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25,25,25,25,25, 0,  0, 0, 0, 0, 0, 0, 0,25,25,25,25,25,25,25, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0,25,25,25,25,25,25,25, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25,25,25,25,25,25,  0, 0, 0, 0, 0, 0,25,25,25,25,25,25,25,25,25, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0,25,25,25,25,25,25,25,25,25, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0,25,25,25,25,25,25, 25, 0, 0, 0, 0,25,25,25,25,25,25,25,25,25,25,25,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10,10, 9, 9, 9, 9,10, 9, 9,  9, 9,10, 9, 9, 9, 9, 9,10, 9, 9, 9, 9,10, 9, 9,  9, 9,10, 9, 9, 9, 9,10,10, 9, 9, 9, 9, 9, 9, 9,  9, 9,10, 9, 9, 9, 9, 9,10, 9, 9, 9, 9,10, 9, 9,  9, 9,10, 9, 9, 9, 9,10,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9])
                                                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                               

    RaceWorld.CopyMapToPlayfield()


    
    
  if (MapLevel == 99):
    #Set world dimentions
    RaceWorld = cf.GameWorld(name='Level6',
                          width        = 80,
                          height       = 144,
                          Map          = [[]],
                          Playfield    = [[]],
                          CurrentRoomH = 2,
                          CurrentRoomV = 1,
                          DisplayH=1,
                          DisplayV=1)
    
    
        #Populate Map
    RaceWorld.Map = []
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10,10, 9, 9, 9, 9,10, 9, 9,  9, 9,10, 9, 9, 9, 9, 9,10, 9, 9, 9, 9,10, 9, 9,  9, 9,10, 9, 9, 9, 9,10,10, 9, 9, 9, 9, 9, 9, 9,  9, 9,10, 9, 9, 9, 9, 9,10, 9, 9, 9, 9,10, 9, 9,  9, 9,10, 9, 9, 9, 9,10,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
                                                                                                                                                                                                                                                                               
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
                                                                                                                                                                                                                                                                               
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
                                                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                               
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
                                                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                               
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
                                                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                               
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
                                                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                               
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
                                                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                               
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
                                                                                                                                                                                                                                                                               
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9,10,10, 9, 9, 9, 9,10, 9, 9,  9, 9,10, 9, 9, 9, 9, 9,10, 9, 9, 9, 9,10, 9, 9,  9, 9,10, 9, 9, 9, 9,10,10, 9, 9, 9, 9, 9, 9, 9,  9, 9,10, 9, 9, 9, 9, 9,10, 9, 9, 9, 9,10, 9, 9,  9, 9,10, 9, 9, 9, 9,10,10, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9])
    RaceWorld.Map.append([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9])
                                                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                               

    RaceWorld.CopyMapToPlayfield()
    

    
  return RaceWorld;


def ShowShortMessage(RaceWorld,PlayerCar,ShortMessage):
  moves = 1
  ShortMessageSprite    = cf.CreateShortMessageSprite(ShortMessage)
  ShortMessageSprite.on = 1
  while (ShortMessageSprite.on == 1):
    RaceWorld.DisplayWindowWithSprite(PlayerCar.h-7,PlayerCar.v-7,ShortMessageSprite)
    MoveMessageSprite(moves,ShortMessageSprite)
    moves = moves + 1
    #print ("Message On")
    
  ShortMessageSprite.on = 0

  













def MoveCar(Car,Playfield):
  
  #print ("")
  #print ("== RD Move Car: ",Car.name," --")
  h = Car.h
  v = Car.v
  oldh  = h
  oldv  = v
  ScanH = 0
  ScanV = 0
  ItemList = []
  DoNothing = ""

  #SolidObjects
  SolidObjects = []
  SolidObjects.append("Wall")
  SolidObjects.append("Fuel")
  
  
  #print("Current Car hv direction:",h,v,Car.direction)
  
  ItemList = RallyDotScanAroundCar(Car,Playfield)
  #print (ItemList[1])

  
  # #Handle Enemy actions first
  if (Car.name == "Enemy"):
    #Decrease color if no player nearby
    #Increase if player nearby
    if ('Player' not in ItemList):
      cf.DecreaseColor(Car)
    else:
      #print ("Player nearby, increasing color of Enemy")
      cf.IncreaseColor(Car)

    if ("Player" in ItemList):
      if (ItemList[1] == 'Player'):
        #Deplete player car lives (health)
        ScanH,ScanV = cf.CalculateDotMovement8Way(h,v,Car.direction)
        Playfield[ScanV][ScanH].lives = Playfield[ScanV][ScanH].lives - 1
      elif (ItemList[2] == 'Player'):
        #print("Turn NE")
        Car.direction = cf.TurnRight8Way(Car.direction)
      elif (ItemList[3] == 'Player'):
        #print("Turn E")
        Car.direction = cf.TurnRight8Way(Car.direction)
        Car.direction = cf.TurnRight8Way(Car.direction)
      elif (ItemList[4] == 'Player'):
        #print("Turn SE")
        Car.direction = cf.TurnRight8Way(Car.direction)
        Car.direction = cf.TurnRight8Way(Car.direction)
        Car.direction = cf.TurnRight8Way(Car.direction)
      elif (ItemList[5] == 'Player'):
        #print("Turn S")
        Car.direction = cf.ReverseDirection8Way(Car.direction)
      elif (ItemList[8] == 'Player'):
        #print("Turn NW")
        Car.direction = cf.TurnLeft8Way(Car.direction)
      elif (ItemList[7] == 'Player'):
        #print("Turn W")
        Car.direction = cf.TurnLeft8Way(Car.direction)
        Car.direction = cf.TurnLeft8Way(Car.direction)      
      elif (ItemList[6] == 'Player'):
        #print("Turn SW")
        Car.direction = cf.TurnLeft8Way(Car.direction)
        Car.direction = cf.TurnLeft8Way(Car.direction)      
        Car.direction = cf.TurnLeft8Way(Car.direction)      

      

  #Handle Player actions
  if (Car.name == "Player"):
    #Handle Wall Movements
    if (ItemList[1] == "Wall"):
      #print ("--Wall found--")
      
      #When you hit the middle of a wall, go left or right (randomly)
      if (ItemList[3] == 'EmptyObject' and ItemList[7] == 'EmptyObject'):
        Car.direction = cf.TurnLeftOrRightTwice8Way(Car.direction)
      
      #If you are surrounded, turn around
      elif (ItemList[3] == "Wall" and ItemList[7] == "Wall"):
        Car.direction = cf.ReverseDirection8Way(Car.direction)
      
      elif (ItemList[8] == 'EmptyObject'):
        Car.direction = cf.TurnLeft8Way(Car.direction)
      elif (ItemList[7] in ('EmptyObject',"Fuel")):
        Car.direction = cf.TurnLeft8Way(Car.direction)
        Car.direction = cf.TurnLeft8Way(Car.direction)
      elif (ItemList[2] == 'EmptyObject'):
        Car.direction = cf.TurnRight8Way(Car.direction)
      elif (ItemList[3] in ('EmptyObject',"Fuel")):
        Car.direction = cf.TurnRight8Way(Car.direction)
        Car.direction = cf.TurnRight8Way(Car.direction)
    
    elif (ItemList[1] == "Enemy"):
      if (ItemList[2] != 'EmptyObject' and ItemList[8] != 'EmptyObject' and ItemList[5] == 'EmptyObject'):
        Car.direction = cf.ReverseDirection8Way(Car.direction)
      elif (ItemList[2] == 'EmptyObject'):
        Car.direction = cf.TurnRight8Way(Car.direction)    
      elif (ItemList[3] == 'EmptyObject'):
        Car.direction = cf.TurnRight8Way(Car.direction)    
        Car.direction = cf.TurnRight8Way(Car.direction)    
      elif (ItemList[4] == 'EmptyObject'):
        Car.direction = cf.TurnRight8Way(Car.direction)    
        Car.direction = cf.TurnRight8Way(Car.direction)    
        Car.direction = cf.TurnRight8Way(Car.direction)    
      elif (ItemList[8] == 'EmptyObject'):
        Car.direction = cf.TurnLeft8Way(Car.direction)    
      elif (ItemList[7] == 'EmptyObject'):
        Car.direction = cf.TurnLeft8Way(Car.direction)    
        Car.direction = cf.TurnLeft8Way(Car.direction)    
      elif (ItemList[6] == 'EmptyObject'):
        Car.direction = cf.TurnLeft8Way(Car.direction)    
        Car.direction = cf.TurnLeft8Way(Car.direction)    
        Car.direction = cf.TurnLeft8Way(Car.direction)    
    
    
    #Cars eat fuel
    elif ("Fuel" in ItemList):
      if (ItemList[1] == "Fuel"):
        DoNothing = "nothing"
      elif (ItemList[2] == "Fuel"):
        Car.direction = cf.TurnRight8Way(Car.direction) 
      elif (ItemList[3] == "Fuel"):
        Car.direction = cf.TurnRight8Way(Car.direction) 
        Car.direction = cf.TurnRight8Way(Car.direction) 
      elif (ItemList[4] == "Fuel"):
        Car.direction = cf.TurnRight8Way(Car.direction) 
        Car.direction = cf.TurnRight8Way(Car.direction) 
        Car.direction = cf.TurnRight8Way(Car.direction) 
      elif (ItemList[5] == "Fuel"):
        Car.direction = cf.ReverseDirection8Way(Car.direction) 
      elif (ItemList[8] == "Fuel"):
        Car.direction = cf.TurnLeft8Way(Car.direction) 
      elif (ItemList[7] == "Fuel"):
        Car.direction = cf.TurnLeft8Way(Car.direction) 
        Car.direction = cf.TurnLeft8Way(Car.direction) 
      elif (ItemList[6] == "Fuel"):
        Car.direction = cf.TurnLeft8Way(Car.direction) 
        Car.direction = cf.TurnLeft8Way(Car.direction) 
        Car.direction = cf.TurnLeft8Way(Car.direction) 

      Fuelh, Fuelv = cf.CalculateDotMovement8Way(h,v,Car.direction)
      Playfield[Fuelv][Fuelh].alive = 0
      Playfield[Fuelv][Fuelh] = cf.EmptyObject('EmptyObject')
      Car.destination = ""
      Car.lives = Car.lives + 50
      
      #make car go faster by lowering the speed value
      Car.ShiftGear("up")
    
    #Turn if following a wall and a corridor opens up
    elif(ItemList[7] == "Wall" and ItemList[8] == 'EmptyObject'):
      Car.direction = cf.ChanceOfTurning8Way(Car.direction,50)
    elif(ItemList[3] == "Wall" and ItemList[2] == 'EmptyObject'):
      Car.direction = cf.ChanceOfTurning8Way(Car.direction,50)


      
  #Only move if the space decided upon is actually empty!
  ScanH,ScanV = cf.CalculateDotMovement8Way(h,v,Car.direction)
  if (Playfield[ScanV][ScanH].name == 'EmptyObject'):
    h = ScanH
    v = ScanV

    

  #print ("oldh oldv hv",oldh,oldv,h,v)  
  #IF the car actually moved, update the locations
  if (oldh != h or oldv != v):
    Car.h = h
    Car.v = v  
    Playfield[v][h] = Car
    Playfield[oldv][oldh] = cf.EmptyObject('EmptyObject')


    
  # #Randomly change direction for a bit of chaos
  # if (Car.name == 'Player'):
    # m,r = divmod(moves,800)
    # if (r == 0):
      # Car.direction = cf.TurnLeftOrRight8Way(Car.direction)
    

  return 



def CountFuelDotsLeft(FuelDots,FuelCount):
  FuelDotsLeft = 0
  for x in range (FuelCount):
    if (FuelDots[x].alive == 1):
      FuelDotsLeft = FuelDotsLeft + 1
  return FuelDotsLeft;

  
def CopyFuelDotsToPlayfield(FuelDots,FuelCount,RaceWorld):
  width  = RaceWorld.width
  height = RaceWorld.height
  
   
  for x in range (FuelCount):
    finished = 'N'
    while (finished == 'N'):
      #Don't put fuel in border area
      h = random.randint(8,width-8)
      v = random.randint(8,height-8)
      
      name = RaceWorld.Playfield[v][h].name
      #print ("Playfield name: ",name)
      
      #print ("FuelDot x h v: ",x,h,v)
      if (name == 'EmptyObject'):
        #print ("Placing Fuel x name: ",x,FuelDots[x].name)
        RaceWorld.Playfield[v][h] = FuelDots[x]
        FuelDots[x].h = h
        FuelDots[x].v = v
        FuelDots[x].alive = 1
        finished = 'Y'


def CopyEnemyCarsToPlayfield(EnemyCars,EnemyCount,RaceWorld):
  width  = RaceWorld.width
  height = RaceWorld.height
  
   
  for x in range (EnemyCount):
    finished = 'N'
    while (finished == 'N'):
      #Don't put cars in border area
      h = random.randint(8,width-8)
      v = random.randint(8,height-8)
      
      name = RaceWorld.Playfield[v][h].name
      #print ("Playfield name: ",name)
      
      #print ("FuelDot x h v: ",x,h,v)
      if (name == 'EmptyObject'):
        #print ("Placing car x name: ",x,EnemyCars[x].name)
        RaceWorld.Playfield[v][h] = EnemyCars[x]
        EnemyCars[x].h = h
        EnemyCars[x].v = v
        EnemyCars[x].alive = 1
        finished = 'Y'
      #else:
      #  print ("Spot occupied: ",name)  



  
        













def GetDistanceBetweenCars(Car1,Car2):
  a = abs(Car1.h - Car2.h)
  b = abs(Car1.v - Car2.v)
  c = math.sqrt(a**2 + b**2)

  return c;  
        




def FindClosestFuel(Car,FuelDots,FuelCount):
  #We want the player car to journey towards the closes fuel dot
  #So far, this function points the car.   How do we make it journey there?
  ClosestX     = 0
  MinDistance  = 9999
  FuelDotsLeft = 0
  Distance = 0
  for x in range(FuelCount):
    if (FuelDots[x].alive == 1):
      FuelDotsLeft = FuelDotsLeft + 1
      Distance = GetDistanceBetweenCars(Car,FuelDots[x])
      if (Distance < MinDistance):
        MinDistance = Distance
        ClosestX = x
    
  return ClosestX, MinDistance, FuelDotsLeft;


def ScrollToCar(Car,RaceWorld):
  x = 0
  y = 0
  for x in range(int(Car.h-8)):
    RaceWorld.DisplayWindow(x,0)
    time.sleep(0.01)
    
  for y in range(Car.v-7):
    RaceWorld.DisplayWindow(x,y)
    time.sleep(0.01)

  cf.FlashDot(3,4,gv.FlashSleep * 3)


def AdjustCarColor(Car):
  r = 0
  g = 0
  b = 200 + Car.lives
  if (b >= 255):
    b = 255
  if (b <= 200):
    b = 200
  Car.b = b        





def TurnTowardsCarDestination(SourceCar):
  print ("Turning towards: ",SourceCar.name)
  if (SourceCar.h < SourceCar.dh):
    if (SourceCar.direction in (7,8,1,2)):
      SourceCar.direction = cf.TurnRight8Way(SourceCar.direction)
    if (SourceCar.direction in (6,5,4)):
      SourceCar.direction = cf.TurnLeft8Way(SourceCar.direction)
      
  if (SourceCar.h > SourceCar.dh):
    if (SourceCar.direction in (8,1,2,3)):
      SourceCar.direction = cf.TurnLeft8Way(SourceCar.direction)
    if (SourceCar.direction in (6,5,4)):
      SourceCar.direction = cf.TurnRight8Way(SourceCar.direction)


  if (SourceCar.v < SourceCar.dv):
    if (SourceCar.direction in (6,7,8,1)):
      SourceCar.direction = cf.TurnLeft8Way(SourceCar.direction)
    if (SourceCar.direction in (2,3,4)):
      SourceCar.direction = cf.TurnRight8Way(SourceCar.direction)
      
  if (SourceCar.v > SourceCar.dv):
    if (SourceCar.direction in (6,7,8)):
      SourceCar.direction = cf.TurnRight8Way(SourceCar.direction)
    if (SourceCar.direction in (5,4,3,2)):
      SourceCar.direction = cf.TurnLeft8Way(SourceCar.direction)
  return;



  
def TurnTowardsCar(SourceCar,TargetCar):
  if (SourceCar.h < TargetCar.h):
    if (SourceCar.direction in (7,8,1,2)):
      SourceCar.direction = cf.TurnRight8Way(SourceCar.direction)
    if (SourceCar.direction in (6,5,4)):
      SourceCar.direction = cf.TurnLeft8Way(SourceCar.direction)
      
  if (SourceCar.h > TargetCar.h):
    if (SourceCar.direction in (8,1,2,3)):
      SourceCar.direction = cf.TurnLeft8Way(SourceCar.direction)
    if (SourceCar.direction in (6,5,4)):
      SourceCar.direction = cf.TurnRight8Way(SourceCar.direction)


  if (SourceCar.v < TargetCar.v):
    if (SourceCar.direction in (6,7,8,1)):
      SourceCar.direction = cf.TurnLeft8Way(SourceCar.direction)
    if (SourceCar.direction in (2,3,4)):
      SourceCar.direction = cf.TurnRight8Way(SourceCar.direction)
      
  if (SourceCar.v > TargetCar.v):
    if (SourceCar.direction in (6,7,8)):
      SourceCar.direction = cf.TurnRight8Way(SourceCar.direction)
    if (SourceCar.direction in (5,4,3,2)):
      SourceCar.direction = cf.TurnLeft8Way(SourceCar.direction)
  return;
  
  
def TurnTowardsFuelIfThereIsRoom(Car,Playfield,FuelDots,ClosestFuel):
  ItemList = []
  ItemList = RallyDotScanAroundCar(Car,Playfield)          
  if (all('EmptyObject' == Item for Item in ItemList)):
    #print ("Scanners indicate emptiness all around")
    TurnTowardsCar(Car,FuelDots[ClosestFuel])
    #Car.ShiftGear("up")
  elif (ItemList[1] == "Empty" 
    and ItemList[2] == "Empty" 
    and ItemList[3] == "Empty" 
    and ItemList[4] == "Empty" 
    and ItemList[5] == "Empty" 
    and ItemList[8] == "Wall"
    and ItemList[7] == "Wall"
    and ItemList[6] == "Wall"):
    print ("Wall on entire left left")
    cf.TurnRight8Way(Car.direction)
    Car.ShiftGear("up")
  elif (ItemList[1] == "Empty" 
    and ItemList[2] == "Wall" 
    and ItemList[3] == "Wall" 
    and ItemList[4] == "Wall" 
    and ItemList[5] == "Wall" 
    and ItemList[8] == "Empty"
    and ItemList[7] == "Empty"
    and ItemList[6] == "Empty"):
    print ("Wall on entire right left")
    cf.TurnLeft8Way(Car.direction)
    Car.ShiftGear("up")

    
    
  #If the car is near enough, turn towards the fuel (random chance)
  #this is an attempt to get the car out of a loop where it just can't
  #navigate out of a situation
  
  m,r = divmod(moves,500)
  if (r == 0):
    Distance = GetDistanceBetweenCars(Car,FuelDots[ClosestFuel])    
    if (Distance < 3):
      TurnTowardsCar(Car,FuelDots[ClosestFuel])
    

    
  return
      





  

def RallyDotScanStraightLine(h,v,direction,Playfield):
 
  ScanDirection = direction
  ScanH         = 0
  ScanV         = 0
  Item          = ''
  ItemList      = ['NULL']
  WallHit       = 0
  count         = 0    #represents number of spaces to scan

#           7
#           6
#           5                             
#           4                             
#           3                             
#           2                            
#           1                              
                                           

  #print ("")
  #print("== RD Scan Straight Line")     
  #print("SSL - hv direction",h,v,direction)

  for count in range (8):
    ScanH, ScanV = cf.CalculateDotMovement(h,v,ScanDirection)
    Item = Playfield[ScanV][ScanH].name
    
    if (Item == 'Wall' or WallHit == 1):
      ItemList.append('Wall')
      WallHit = 1
    else:
      ItemList.append(Item)
    #print ("RDSSL - count hv ScanH ScanV Item",count,h,v,ScanH,ScanV, Item)
    
  
  return ItemList;


  
def RallyDotScanAroundCar(Car,Playfield):
  # hv represent car location
  # ScanH and ScanV is where we are scanning
  
  #print ("== Scan around car ==")
  
  ScanDirection = Car.direction
  ScanH         = 0
  ScanV         = 0
  h             = Car.h
  v             = Car.v
  Item          = ''
  ItemList      = ['EmptyObject']
  count         = 0    #represents number of spaces to scan


#         8 1 2
#         7 x 3                             
#         6 5 4
        
  


  for count in range (8):
    ScanH, ScanV = cf.CalculateDotMovement8Way(h,v,ScanDirection)
    
    

    Item = Playfield[ScanV][ScanH].name
    if (Item == 'Wall'):
      ItemList.append('Wall')
    else:
      ItemList.append(Item)
    #print ("RDSAC - count hv ScanH ScanV Item",count,h,v,ScanH,ScanV, Item)

    #Turn to the right
    ScanDirection = cf.TurnRight8Way(ScanDirection)
      

  return ItemList;
  





def RallyDotBlowUp(Car,Playfield):
  
  # Blow up car, do damage all around
  # hv represent car location
  # ScanH and ScanV is where we are scanning
  
  #print ("== Scan around car ==")
  
  ScanDirection = Car.direction
  ScanH         = 0
  ScanV         = 0
  h             = Car.h
  v             = Car.v
  Item          = ''
  ItemList      = ['EmptyObject']
  count         = 0    #represents number of spaces to scan

#         8 1 2
#         7 x 3                             
#         6 5 4
        
  for count in range (8):
    #print ("ScanDirection: ",ScanDirection)
    ScanH, ScanV = cf.CalculateDotMovement8Way(h,v,ScanDirection)

    Item = Playfield[ScanV][ScanH].name
    if (Item == "Enemy"): 
        Playfield[ScanV][ScanH].exploding = 1
    if (Item == "Player"):
      #lives is used as health
      Playfield[ScanV][ScanH].lives = Playfield[ScanV][ScanH].lives -10
      Playfield[ScanV][ScanH].ShiftGear("down")

    #Turn to the right
    ScanDirection = cf.TurnRight8Way(ScanDirection)
  
  Car.alive = 0
  Car.exploding = 1

  return;  








  
def PlayRallyDot():
  
  print ("")
  print ("")
  print ("----------------------")
  print ("-- Rally Dot      ----")
  print ("----------------------")
  print ("")
  
  #Local Variables 
  LevelCount       = 0
  LevelFinished    = "N"
  m                = 0
  r                = 0
  moves            = 0
  MaxMoves         = 10000

  Finished         = 'N'
  Distance         = 0
  ClosestFuelDistance = 0
  Minx             = 0
  MinDistance      = 9999
  x                = 0
  y                = 0
  ItemList         = []
  CarOriginalSpeed = 0
  Diaganols        = [2,4,6,8]
  #SpeedModifier    = 1.2 -- decimals seem to cause car to stop working
  SpeedModifier    = 2
  EnemyRadarSpeed  = 10 * gv.CPUModifier
  PlayerRadarSpeed = 10 * gv.CPUModifier
  EnemyCount       = 0
  ACarHasExploded  = 0
  EnemyCarSpawnSpeed = 500
  CarWinSleep       = 1
  DisolveSleep      = 0.01
  
  ClockSprite = cf.CreateClockSprite(12)
  ClockSprite.on = 0

  #ShortWordSprite = CreateShortWordSprite("WIN!")
  #ShortWordSprite.on = 0

  
  #Show Intro
  cf.ClearBigLED()
  cf.ShowScrollingBanner("Rally Dot", cf.SDLowGreenR,cf.SDLowGreenG,cf.SDLowGreenB,gv.ScrollSleep)
  
  
  #---------------------------------
  #-- Prepare World 1             --
  #---------------------------------

  #Create Player Car
  PlayerCar = cf.CarDot(h=8,v=19,dh=8,dv=8,r=0,g=150,b=255,direction=1,scandirection=1,
              gear=[1],
              speed=10,
              currentgear=1,
              alive=1,
              lives=200, name="Player",score=0,exploding=0,radarrange=16,destination="")

  #Create FuelDots
  FuelCount    = 50
  FuelDotsLeft = FuelCount
  ClosestFuel  = 0
  FuelDots     = []
  FuelDots     = [ cf.CarDot(h=8,v=8,dh=-1,dv=-1,r= cf.SDLowYellowR,g= cf.SDLowYellowG,b= cf.SDLowYellowB,direction=1,scandirection=1,gear=[],speed=1,currentgear=1,alive=1,lives=1, name="Fuel",score=0,exploding=0,radarrange=0,destination="") for i in range(FuelCount)]
  
  #Create RaceWorld, load map 1
  RaceWorld = CreateRaceWorld(6)
  CopyFuelDotsToPlayfield(FuelDots,FuelCount,RaceWorld)
  
  #Create Enemy cars
  EnemyCarCount = 50
  EnemyCars = []
  EnemyCars = [ cf.CarDot(h=5,v=19,dh=-1,dv=-1,r= cf.SDLowRedR,g= cf.SDLowRedG,b= cf.SDLowRedB,direction=2,scandirection=2,gear=[],
               speed=10,
               currentgear=1,
               alive=1,
               lives=1,
               name="Enemy",score=0,exploding=0,
               radarrange=40,
               destination="") for i in range(EnemyCarCount)]
  
  CopyEnemyCarsToPlayfield(EnemyCars,EnemyCarCount,RaceWorld)
    
  
  #Set Player car properties
  PlayerCar.h          = RaceWorld.width // 2
  PlayerCar.v          = RaceWorld.height - 9
  PlayerCar.speed      = PlayerCar.gear[1]
  CarOriginalSpeed     = PlayerCar.speed
  PlayerCar.radarrange = 8
  PlayerCar.lives      = 100
   
  
  #Display Intro
  #ShowLevelCount(1)
  ScrollToCar(PlayerCar,RaceWorld)  

  #--------------------------------------------------------
  #-- MAIN TIMER LOOP                                    --
  #--------------------------------------------------------
    
  while (LevelFinished == 'N' and PlayerCar.lives >= 0):
    #Reset Variables
    moves = moves + 1
    Key   = ''
    LevelCount = LevelCount + 1
    LetEnemyRespawn = 1
    


    #Check for keyboard input
    m,r = divmod(moves,KeyboardSpeed)
    if (r == 0):
      Key = cf.PollKeyboard()
      ProcessKeypress(Key)
      if (Key == 'q'):
        LevelFinished = 'Y'
        Finished      = 'Y'
        return


    #--------------------------------
    #-- Player actions             --
    #--------------------------------

    if (PlayerCar.lives > 0):
      #print ("M - PlayerCar.hv speed alive exploding direction scandirection: ",PlayerCar.h, PlayerCar.v,PlayerCar.speed, PlayerCar.alive, PlayerCar.exploding, PlayerCar.direction,PlayerCar.scandirection)
      #print ("M - PlayerCar.hv speed direction scandirection: ",PlayerCar.h, PlayerCar.v,PlayerCar.speed, PlayerCar.direction,PlayerCar.scandirection)
      #print ("M - PlayerCar.rgb lives",PlayerCar.r,PlayerCar.g,PlayerCar.b, PlayerCar.lives)
      m,r = divmod(moves,PlayerCar.speed)
      if (r == 0):
        #Find closest Fuel
        ClosestFuel,ClosestFuelDistance, FuelDotsLeft = FindClosestFuel(PlayerCar,FuelDots,FuelCount)
        #print ("destination: ",PlayerCar.destination)
        
        #If no destination yet, set to nearest fuel if it exists
        if (ClosestFuelDistance <= PlayerCar.radarrange 
            and FuelDotsLeft > 0 
            and PlayerCar.destination == ""):
          PlayerCar.destination = FuelDots[ClosestFuel].name

        
        #Perform radar check around car.  If no solid objects, then move towards destination
        if (FuelDotsLeft > 0 and PlayerCar.destination == "Fuel"):
          TurnTowardsFuelIfThereIsRoom(PlayerCar,RaceWorld.Playfield,FuelDots,ClosestFuel)
          
        #Move car and determine direction
        MoveCar(PlayerCar,RaceWorld.Playfield)
        direction = PlayerCar.direction
        AdjustCarColor(PlayerCar)

        #Adjust speed if diaganol
        #if (PlayerCar.direction in Diaganols):
        #  PlayerCar.speed = CarOriginalSpeed * SpeedModifier
        #else:
        #  PlayerCar.speed = CarOriginalSpeed

    #Player lost all health (lives)
    elif (PlayerCar.lives == 0):
      PlayerCar.lives = 100
      PlayerCar.h = (RaceWorld.width // 2) + 2
      PlayerCar.v = RaceWorld.height -5
      RaceWorld.Playfield[PlayerCar.v][PlayerCar.h] = PlayerCar
      ScrollToCar(PlayerCar,RaceWorld)  
  
          
    #--------------------------------
    #-- Enemy actions              --
    #--------------------------------

    #keep cars alive until they finish exploding
    #Remember, not everythign gets displayed so be careful with how the display module handles explosions and alive
    #maybe have a separate function to handle all exploding cars

    
    #---------------------
    #-- move enemy cars --
    #---------------------

    EnemyCount = 0
    ACarHasExploded = 0
    
    for x in range (EnemyCarCount):
      if (EnemyCars[x].alive == 1):
        EnemyCount = EnemyCount + 1
        m,r = divmod(moves,EnemyCars[x].speed)
        if (r == 0):
            
          #Check radar.  If player is near by, move towards
          m,r = divmod(moves,EnemyRadarSpeed)
          if (r == 0):
            Distance = GetDistanceBetweenCars(EnemyCars[x],PlayerCar)

            if (Distance < EnemyCars[x].radarrange):
              TurnTowardsCar(EnemyCars[x],PlayerCar)
              EnemyCars[x].destination = "PlayerCar"
              EnemyCars[x].ShiftGear("up")
            else:
              EnemyCars[x].ShiftGear("down")
              EnemyCars[x].destination = ""
  
          EnemyCars[x].direction = cf.ChanceOfTurning8Way(EnemyCars[x].direction,10)
          MoveCar(EnemyCars[x],RaceWorld.Playfield)

          
          #print ("Enemy car X lives heat: ",x,EnemyCars[x].lives, EnemyCars[x].r)
          #Reduce enemy health and speed if they are overheated
          if (EnemyCars[x].name == "Enemy" and EnemyCars[x].r >= 255):
            EnemyCars[x].lives = EnemyCars[x].lives -1
            EnemyCars[x].ShiftGear("down")

          #if they are out of health, they detonate
          if (EnemyCars[x].lives <= 0):
            ACarHasExploded = 1
            #print ("Enemy car[x] exploding: ",x)        
            EnemyCars[x].exploding = 1
            RallyDotBlowUp(EnemyCars[x],RaceWorld.Playfield)



      

      #spawn new enemy      
      else:
        m,r = divmod(moves,EnemyCarSpawnSpeed)
        if (r == 0):
          if (LetEnemyRespawn == 1):
            EnemyCars[x].alive = 1
            EnemyCars[x].speed = 1
            EnemyCars[x].radar = 30
            EnemyCars[x].lives = 5
            LetEnemyRespawn    = 0
          
        

    #------------------------------------
    #-- Deal with explosions and death --
    #------------------------------------
        
    #Display exploding objects 
    if (ACarHasExploded ==1):
      RaceWorld.DisplayExplodingObjects(PlayerCar.h-7,PlayerCar.v-7)

           
    print ("Moves: ",moves,"Enemy Alive:",EnemyCount," Playerlives:",PlayerCar.lives, "PlayerSpeed: ",PlayerCar.speed,end="\r")
          
    
    #-------------------------
    #- Main Display         --
    #-------------------------

    #-----------------------------------------------------------
    #The cars move virtually on the playfield                 --
    #We can display the screen from any point of view we like --
    #For now we show what the player car is doing             --
    #-----------------------------------------------------------
    
    #These display coordinates are from the point of view of the entire playfield
    #print ("PlayerCar hv:",PlayerCar.h,PlayerCar.v)
 
    
    m,r = divmod(moves,CheckClockSpeed)
    if (r == 0):  
      CheckClockTimer(ClockSprite)
        
    if (ClockSprite.on == 1):
      RaceWorld.DisplayWindowWithSprite(PlayerCar.h-7,PlayerCar.v-7,ClockSprite)
      MoveMessageSprite(moves,ClockSprite)
    else:
      RaceWorld.DisplayWindow(PlayerCar.h-7,PlayerCar.v-7)

    
    
    #print ("moves",moves,"Carh Carv ", PlayerCar.h,PlayerCar.v,"Direction",PlayerCar.direction,"Destination ",PlayerCar.destination,ClosestFuel,"FuelDotsLeft",FuelDotsLeft,FuelDots[0].dh, FuelDots[0].dv,"PlayerCar.lives",PlayerCar.lives,"Player.b",PlayerCar.b,"      ",end="\r")
    #sys.stdout.flush()

    
    
    #--------------------------
    #-- Display message      --
    #--------------------------
    
    #car got all the fuel
    if (FuelCount == 0):
      ShowShortMessage(RaceWorld,PlayerCar,"you win")
      
      
      
    
    #-------------------------
    #-- Load different maps --
    #-------------------------
    
    
    if (moves >= MaxMoves):
      ShowShortMessage(RaceWorld,PlayerCar,"you die")
      cf.FlashDot4(3,4,CarWinSleep)    
      RaceWorld.DisolveWindow(PlayerCar.h-7,PlayerCar.v-7,DisolveSleep)    
     

      cf.ClearBigLED()
      cf.ShowScrollingBanner("Game Over",cf.SDMedPurpleR,cf.SDMedPurpleG,cf.SDMedPurpleB,gv.ScrollSleep  * 0.75)
      return

    
    
    if (moves == 2000 or FuelDotsLeft == 0):
      if (FuelCount > 0):
        ShowShortMessage(RaceWorld,PlayerCar,"frown")
      elif(FuelCount == 0):
        ShowShortMessage(RaceWorld,PlayerCar,"smile")
      
      cf.FlashDot4(3,4,CarWinSleep)    
      RaceWorld.DisolveWindow(PlayerCar.h-7,PlayerCar.v-7,DisolveSleep)    

      #---------------------------------
      #-- Prepare World 2             --
      #---------------------------------
  


      #Create RaceWorld, load map 2
      RaceWorld = CreateRaceWorld(2)
    
      #Create FuelDots
      FuelCount    = 50
      FuelDotsLeft = FuelCount
      ClosestFuel  = 0
      FuelDots     = []
      FuelDots     = [ cf.CarDot(h=8,v=8,dh=-1,dv=-1,r= cf.SDLowYellowR,g= cf.SDLowYellowG,b= cf.SDLowYellowB,direction=1,scandirection=1,gear=[],speed=1,currentgear=1,alive=1,lives=1, name="Fuel",score=0,exploding=0,
      radarrange=0,destination="") for i in range(FuelCount)]
      CopyFuelDotsToPlayfield(FuelDots,FuelCount,RaceWorld)

      #Create Enemy cars
      EnemyCarCount = 50
      EnemyCars = []
      EnemyCars = [ cf.CarDot(h=8,v=8,dh=-1,dv=-1,r= cf.SDLowRedR,g= cf.SDLowRedG,b= cf.SDLowRedB,direction=2,scandirection=2,
                  gear=[],
                  speed=1,currentgear=1,
                  alive=1,lives=1, name="Enemy",score=0,exploding=0,
                  radarrange=10,destination="") for i in range(EnemyCarCount)]
      CopyEnemyCarsToPlayfield(EnemyCars,EnemyCarCount,RaceWorld)
      
      #Set Player car properties
      PlayerCar.h          = RaceWorld.width // 2
      PlayerCar.v          = RaceWorld.height - 9
      PlayerCar.speed      = PlayerCar.gear[1]
      CarOriginalSpeed     = PlayerCar.speed
      PlayerCar.radarrange = 8
   
      
      #Display Intro
      cf.ShowLevelCount(2)
      ScrollToCar(PlayerCar,RaceWorld)  
        
      
      
    if (moves == 4000 or FuelDotsLeft == 0):
      if (FuelCount > 0):
        ShowShortMessage(RaceWorld,PlayerCar,"frown")
      elif(FuelCount == 0):
        ShowShortMessage(RaceWorld,PlayerCar,"smile")
      cf.FlashDot4(3,4,CarWinSleep)
      RaceWorld.DisolveWindow(PlayerCar.h-7,PlayerCar.v-7,DisolveSleep)    

      #---------------------------------
      #-- Prepare World 3             --
      #---------------------------------


      #Create RaceWorld, load map 3
      RaceWorld = CreateRaceWorld(3)
    
      #Create FuelDots
      FuelCount = 25
      FuelDots = []
      FuelDots = [ cf.CarDot(h=8,v=8,dh=-1,dv=-1,r= cf.SDLowYellowR,g= cf.SDLowYellowG,b= cf.SDLowYellowB,direction=1,scandirection=1,gear=[],speed=1,currentgear=1,alive=1,lives=1, name="Fuel",score=0,exploding=0,
                 radarrange=4,destination="") for i in range(FuelCount)]
      CopyFuelDotsToPlayfield(FuelDots,FuelCount,RaceWorld)

      #Create Enemy cars
      EnemyCarCount = 100
      EnemyCars = []
      EnemyCars = [ cf.CarDot(h=8,v=8,dh=-1,dv=-1,r= cf.SDLowRedR,g= cf.SDLowRedG,b= cf.SDLowRedB,direction=2,scandirection=2,gear=[],
                  speed=5,currentgear=1,
                  alive=1,
                  lives=5, name="Enemy",score=0,exploding=0,
                  radarrange=10,destination="") for i in range(EnemyCarCount)]
      CopyEnemyCarsToPlayfield(EnemyCars,EnemyCarCount,RaceWorld)
    
      #Set Player car properties
      PlayerCar.h          = RaceWorld.width // 2
      PlayerCar.v          = RaceWorld.height - 9
      PlayerCar.speed      = PlayerCar.gear[1]
      CarOriginalSpeed     = PlayerCar.speed
      PlayerCar.radarrange = 8

      #Display Intro
      cf.ShowLevelCount(3)
      ScrollToCar(PlayerCar,RaceWorld)  
  
    if (moves == 6000 or FuelDotsLeft == 0):
      if (FuelCount > 0):
        ShowShortMessage(RaceWorld,PlayerCar,"frown")
      elif(FuelCount == 0):
        ShowShortMessage(RaceWorld,PlayerCar,"smile")
      cf.FlashDot4(3,4,CarWinSleep)    
      RaceWorld.DisolveWindow(PlayerCar.h-7,PlayerCar.v-7,DisolveSleep)    

      #---------------------------------
      #-- Prepare World 4            --
      #---------------------------------


      #Create RaceWorld, load map 3
      RaceWorld = CreateRaceWorld(4)
    
      #Create FuelDots
      FuelCount = 25
      FuelDots = []
      FuelDots = [ cf.CarDot(h=8,v=8,dh=-1,dv=-1,r= cf.SDLowYellowR,g= cf.SDLowYellowG,b= cf.SDLowYellowB,direction=1,scandirection=1,gear=[],speed=1,currentgear=1,alive=1,lives=1, name="Fuel",score=0,exploding=0,radarrange=4,destination="") for i in range(FuelCount)]
      CopyFuelDotsToPlayfield(FuelDots,FuelCount,RaceWorld)

      #Create Enemy cars
      EnemyCarCount = 50
      EnemyCars = []
      EnemyCars = [ cf.CarDot(h=8,v=8,dh=-1,dv=-1,r= cf.SDLowRedR,g= cf.SDLowRedG,b= cf.SDLowRedB,direction=2,scandirection=2,gear=[],
                  speed=5,currentgear=1,
                  alive=1,
                  lives=5, name="Enemy",score=0,exploding=0,
                  radarrange=10,
                  destination="") for i in range(EnemyCarCount)]
      CopyEnemyCarsToPlayfield(EnemyCars,EnemyCarCount,RaceWorld)
    
      #Set Player car properties
      PlayerCar.h          = RaceWorld.width // 2
      PlayerCar.v          = RaceWorld.height - 9
      PlayerCar.speed      = PlayerCar.gear[1]
      CarOriginalSpeed     = PlayerCar.speed
      PlayerCar.radarrange = 8
      PlayerCar.lives      = 100
       

      #Display Intro
      cf.ShowLevelCount(4)
      ScrollToCar(PlayerCar,RaceWorld)  

    
    
    if (moves == 8000 or FuelDotsLeft == 0):
      if (FuelCount > 0):
        ShowShortMessage(RaceWorld,PlayerCar,"frown")
      elif(FuelCount == 0):
        ShowShortMessage(RaceWorld,PlayerCar,"smile")
      cf.FlashDot4(3,4,CarWinSleep)    
      RaceWorld.DisolveWindow(PlayerCar.h-7,PlayerCar.v-7,DisolveSleep)    

      #---------------------------------
      #-- Prepare World 5            --
      #---------------------------------


      #Create RaceWorld, load map 5
      RaceWorld = CreateRaceWorld(5)
    
      #Create FuelDots
      FuelCount = 50
      FuelDots = []
      FuelDots = [ cf.CarDot(h=8,v=8,dh=-1,dv=-1,r= cf.SDLowYellowR,g= cf.SDLowYellowG,b= cf.SDLowYellowB,direction=1,scandirection=1,gear=[],speed=1,currentgear=1,alive=1,lives=1, name="Fuel",score=0,exploding=0,radarrange=4,destination="") for i in range(FuelCount)]
      CopyFuelDotsToPlayfield(FuelDots,FuelCount,RaceWorld)

      #Create Enemy cars
      EnemyCarCount = 50
      EnemyCars = []
      EnemyCars = [ cf.CarDot(h=8,v=8,dh=-1,dv=-1,r= cf.SDLowRedR,g= cf.SDLowRedG,b= cf.SDLowRedB,direction=2,scandirection=2,gear=[],
                  speed=5,currentgear=1,
                  alive=1,
                  lives=5, name="Enemy",score=0,exploding=0,
                  radarrange=10,
                  destination="") for i in range(EnemyCarCount)]
      CopyEnemyCarsToPlayfield(EnemyCars,EnemyCarCount,RaceWorld)
    
      #Set Player car properties
      PlayerCar.h          = RaceWorld.width // 2
      PlayerCar.v          = RaceWorld.height - 9
      PlayerCar.speed      = PlayerCar.gear[1]
      CarOriginalSpeed     = PlayerCar.speed
      PlayerCar.radarrange = 8
      PlayerCar.lives      = 100
       

      #Display Intro
      cf.ShowLevelCount(4)
      ScrollToCar(PlayerCar,RaceWorld)  

    


    
    #-------------------------
    #-- Create Clock Sprite --
    #-------------------------
    # we want to display the clock ever X seconds, so we call the function CheckElapsedTime to see if that many
    # seconds have passed.  If so, create the clock and start sliding it onto the screen at a specific speed.
    # After X seconds, slide off screen and reset the timers.
   
    if (CheckElapsedTime(CheckTime) == 1):
      if (ClockSprite.on == 0):
        ClockSprite = cf.CreateClockSprite(12)
      
      
    #time.sleep(MainSleep * 0.01 )
    
    
  





#--------------------------------------
#--            PacDot                --
#--------------------------------------


# Note:
#   - after ghosts turn back to normal from blue, their dots don't disappear and I think the numdots counter gets messed up
#





def TurnTowardsDot4Way(SourceH,SourceV,SourceDirection,TargetH,TargetV):

#     1 
#   4   2
#     3

  NewDirection = SourceDirection
  #FlashDot4(TargetH,TargetV,0.001)
  
  #print ("----start-------")
  #print ("SourceHV: ",SourceH,SourceV, "TargetHV:",TargetH,TargetV,"Direction:",SourceDirection)

  # Decide what is closer, H or V of target
  
  x = SourceH - TargetH
  y = SourceV - TargetV
  
  #further away vertically than horizontally
  if abs(y) >= abs(x):
    #print ("Further vertically: xy",x,y)
    #If above, new direction is down
    if (y <= 0):
      NewDirection = 3
      #print ("Above.  OldDirection",SourceDirection,"NewDirection: ",NewDirection)
    
    #if below, new direction is up
    if (y >= 0):
      NewDirection = 1
      #print ("Below.  OldDirection",SourceDirection,"NewDirection: ",NewDirection)
    
  #futher away horizontally than vertically
  elif abs(x) >= abs(y):
    #print ("Further horizontally: xy",x,y)
    #If to the left, new direction is right
    if (x <= 0):
      NewDirection = 2
      #print ("Left.  OldDirection",SourceDirection,"NewDirection: ",NewDirection)
    
    #if below, new direction is right
    if (x >= 0):
      NewDirection = 4
      #print ("Right.  OldDirection",SourceDirection,"NewDirection: ",NewDirection)
  
  #print ("NewDirection:",NewDirection)
  #print ("----end------------")
  #print (" ")  
  return NewDirection;




def TurnAwayFromDot4Way(SourceH,SourceV,SourceDirection,TargetH,TargetV):

#     1 
#   4   2
#     3

  NewDirection = SourceDirection
  
  
  #print ("----start-------")
  #print ("SourceHV: ",SourceH,SourceV, "TargetHV:",TargetH,TargetV,"Direction:",SourceDirection)

  # Decide what is closer, H or V of target
  
  x = SourceH - TargetH
  y = SourceV - TargetV
  
  #further away vertically than horizontally
  if abs(y) >= abs(x):
    #print ("Further vertically: xy",x,y)
    #If above, new direction is up
    if (y <= 0):
      NewDirection = 1
      #print ("Above.  OldDirection",SourceDirection,"NewDirection: ",NewDirection)
    
    #if below, new direction is down
    if (y >= 0):
      NewDirection = 3
      #print ("Below.  OldDirection",SourceDirection,"NewDirection: ",NewDirection)
    
  #futher away horizontally than vertically
  elif abs(x) >= abs(y):
    #print ("Further horizontally: xy",x,y)
    #If to the left, new direction is left
    if (x <= 0):
      NewDirection = 4
      #print ("Left.  OldDirection",SourceDirection,"NewDirection: ",NewDirection)
    
    #if to the right, new direction is right
    if (x >= 0):
      NewDirection = 2
      #print ("Right.  OldDirection",SourceDirection,"NewDirection: ",NewDirection)
  
  #print ("NewDirection:",NewDirection)
  #print ("----end------------")
  #print (" ")  
  return NewDirection;









def ScrollThreeGhostSprite(direction):
  ThreeGhostSprite = JoinSprite(RedGhostSprite, OrangeGhostSprite, 2)
  ThreeGhostSprite = JoinSprite(ThreeGhostSprite, PurpleGhostSprite, 2)
  ThreeGhostSprite.ScrollAcrossScreen(0,1,direction,gv.ScrollSleep)








def PlayPacDot(NumDots):  

#----------------------------
#-- PacDot                 --
#----------------------------


  #gv.TheMatrix = RGBMatrix(options = options)

  

  
  global PowerPills
  global moves     
  global MaxPacmoves
  global DotsEaten  
  global Pacmoves   
  global PowerPillActive
  global PowerPillMoves 
  global BlueGhostmoves 
  global StartGhostSpeed1
  global StartGhostSpeed2
  global StartGhostSpeed3
  global StartGhostSpeed4
  global GhostSpeed1    
  global GhostSpeed2    
  global GhostSpeed3    
  global GhostSpeed4    
  global PacSpeed       
  global BlueGhostSpeed 
  global LevelCount     
  global PacPoints      
  global PacStuckMaxCount
  global PacStuckCount   
  global PacOldH         
  global PacOldV         

  #Pac Scoring
  global DotPoints       
  global BlueGhostPoints 
  global PillPoints      
  global PacDotScore     
  

  global start_time


  global Ghost1Alive
  global Ghost2Alive
  global Ghost3Alive
  global Ghost3Alive
  global Ghost4Alive
  global Ghost1H
  global Ghost1V
  global Ghost2H
  global Ghost2V
  global Ghost3H
  global Ghost3V
  global Ghost4H
  global Ghost4V

  Ghost1H = 6
  Ghost1V = 15
  Ghost1Alive = 1
  Ghost2H = 7
  Ghost2V = 15
  Ghost2Alive = 1
  Ghost3H = 8
  Ghost3V = 15
  Ghost3Alive = 1
  Ghost4H = 9
  Ghost4V = 15
  Ghost4Alive = 1
  PacDotH = 0
  PacDotV = 0

  
  
  PowerPills  = 25
  moves       = 0
  MaxPacmoves = 5
  DotsEaten   = 0
  Pacmoves    = 0
  PowerPillActive  = 0
  PowerPillMoves   = 0
  BlueGhostmoves   = 500
  StartGhostSpeed1 = 5
  StartGhostSpeed2 = 6
  StartGhostSpeed3 = 7
  StartGhostSpeed4 = 10
  GhostSpeed1      = StartGhostSpeed1
  GhostSpeed2      = StartGhostSpeed2
  GhostSpeed3      = StartGhostSpeed3
  GhostSpeed4      = StartGhostSpeed4
  PacSpeed         = 4
  BlueGhostSpeed   = 15
  LevelCount       = 1
  PacPoints        = 0
  PacStuckMaxCount = 300
  PacStuckCount    = 1
  PacOldH          = 0
  PacOldV          = 0
  IgnoreH          = 0
  IgnoreV          = 0
  RecentMoves      = 0


  MinDots = 128
  MaxDots = 200
  MaxMoves = 50000



  #Pac Scoring
  DotPoints         = 1
  BlueGhostPoints   = 5
  PillPoints        = 10
  PacDotScore       = 0
  gv.DotMatrix = [[0 for x in range(gv.HatWidth)] for y in range(gv.HatWidth)] 
  DotsRemaining = 0



  #Clear screen show banner
  cf.ClearBigLED()
  cf.ClearBuffers()
  print ("")
  print ("P-A-C-D-O-T")
  print ("")
  # cf.ClearBigLED()


  #Draw the Big text
  #Clear only the LED matrix
  #Draw the next size down
  #When at the final zoom level
  #  - clear the LED Matrix
  #  - clear all buffers (canvas and ScreenArray[V][H])
  #  - draw the text at desired last zoom level
  #  - draw the rest of the text, at this point it is all written to ArrayBuffer
  #  - clear the LED Matrix
  #  - clear all buffers (canvas and ScreenArray[V][H])
  #Call the ZoomScreen function to redraw the display using ScreenArray[V][H] which at this point
  #contains the values last written to the screen.


  cf.ShowGlowingText(CenterHoriz = True,h = -8,v = 1,   Text = 'PAKDOT', RGB = cf.HighYellow, ShadowRGB = cf.DarkYellow, ZoomFactor = 8,GlowLevels=0,DropShadow=False)
  gv.TheMatrix.Clear()
  cf.ShowGlowingText(CenterHoriz = True,h = -8,v = 1,   Text = 'PAKDOT', RGB = cf.HighYellow, ShadowRGB = cf.DarkYellow, ZoomFactor = 7,GlowLevels=0,DropShadow=False)
  gv.TheMatrix.Clear()
  cf.ShowGlowingText(CenterHoriz = True,h = -8,v = 1,   Text = 'PAKDOT', RGB = cf.HighYellow, ShadowRGB = cf.DarkYellow, ZoomFactor = 6,GlowLevels=0,DropShadow=False)
  gv.TheMatrix.Clear()
  cf.ShowGlowingText(CenterHoriz = True,h = -8,v = 1,   Text = 'PAKDOT', RGB = cf.HighYellow, ShadowRGB = cf.DarkYellow, ZoomFactor = 5,GlowLevels=0,DropShadow=False)
  gv.TheMatrix.Clear()
  cf.ShowGlowingText(CenterHoriz = True,h = -8,v = 1,   Text = 'PAKDOT', RGB = cf.HighYellow, ShadowRGB = cf.DarkYellow, ZoomFactor = 4,GlowLevels=0,DropShadow=False)
  gv.TheMatrix.Clear()
  cf.ShowGlowingText(CenterHoriz = True,h = -8,v = 1,   Text = 'PAKDOT', RGB = cf.HighYellow, ShadowRGB = cf.DarkYellow, ZoomFactor = 3,GlowLevels=0,DropShadow=False)

  gv.TheMatrix.Clear()
  cf.ClearBuffers()
  cf.ShowGlowingText(CenterHoriz = True,h = 0 ,v = 1,   Text = 'PAKDOT',     RGB = cf.HighYellow, ShadowRGB = cf.ShadowYellow, ZoomFactor = 2,GlowLevels=50, DropShadow=True)
  cf.ShowGlowingText(CenterHoriz = True,h = 0 ,v = 16,  Text = 'EAT EM UP',  RGB = cf.HighRed,    ShadowRGB = cf.ShadowRed,    ZoomFactor = 1,GlowLevels=200,DropShadow=True)
  cf.ShowGlowingText(CenterHoriz = True,h = 0 ,v = 26,  Text = 'BY DATAGOD', RGB = cf.HighPurple, ShadowRGB = cf.ShadowPurple, ZoomFactor = 1,GlowLevels=100,FadeLevels=50,DropShadow=True)
  
  ThreeGhostPacSprite.ScrollAcrossScreen(0,26,'right',gv.ScrollSleep)
  ThreeBlueGhostPacSprite.ScrollAcrossScreen(gv.HatWidth,26,'left',gv.ScrollSleep)
  gv.TheMatrix.Clear()
  gv.Canvas.Clear()
  cf.ZoomScreen(gv.ScreenArray,32,1,0,Fade=True)
  gv.TheMatrix.Clear()







  #Keeping track of eating
  gv.MovesSinceSmartSeekFlip = 0
  MovesSinceSmartSeekFlip    = 0
  MovesSinceEatingGhost      = 0
  gv.PacDotSmarkSeekMode     = 1





  #Timers / Clock display
  ClockSprite = cf.CreateClockSprite(12)
  #lockH        = gv.HatWidth  // 2 - (ClockSprite.width // 2)
  #lockV        = gv.HatHeight // 2 - (ClockSprite.height // 2)
  start_time    = time.time()
  DayOfWeekSprite     = cf.CreateDayOfWeekSprite()
  MonthSprite         = cf.CreateMonthSprite()
  DayOfMonthSprite    = cf.CreateDayOfMonthSprite()
  CurrencySprite      = CreateCurrencySprite()





  #--------------------------------------
  #Create Mazes                        --
  #--------------------------------------




  #63 x 32
  # PacMaze[0].map= (
   # #0         1         2         3         4         5         6      #0
    # "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO",   
    # "O                                                              O",
    # "O                                                              O",
    # "O                                                              O",
    # "O                                                              O",
    # "O                                                              O",
    # "O                                                              O",
    # "O                                                              O",
    # "O                                                              O", 
    # "O                                                              O", #10
    # "O                                                              O",
    # "O                                                              O",
    # "O                                                              O",
    # "O                                                              O",
    # "O                                                              O",
    # "O                                                              O",
    # "O                                                              O",
    # "O                                                              O",    
    # "O                                                              O",
    # "O                                                              O", #20
    # "O                                                              O",
    # "O                                                              O",
    # "O                                                              O",
    # "O                                                              O",
    # "O                                                              O",
    # "O                                                              O",
    # "O                                                              O",
    # "O                                                              O",
    # "O                                                              O",
    # "O                                                              O", #30
    # "O                                                              O",
    # "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO"
  # )


  # PacMaze[0].map= (
   # #0         1         2         3         4   #0
    # "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO",   
    # "O                                      O",
    # "O                                      O",
    # "O                                      O",
    # "O                                      O",
    # "O                                      O",
    # "O                                      O",
    # "O                                      O",
    # "O                                      O", 
    # "O                                      O", #10
    # "O                                      O",
    # "O                                      O",
    # "O                                      O",
    # "O                                      O",
    # "O                                      O",
    # "O                                      O",
    # "O                                      O",
    # "O                                      O",    
    # "O                                      O",
    # "O                                      O", #20
    # "O                                      O",
    # "O                                      O",
    # "O                                      O",
    # "O                                      O",
    # "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO"
  # )


  
  #Create maze 0
  PacMaze = []
  PacMaze.append(cf.Maze(
    h      = 24,
    v      = 0,
    width  = 40, 
    height = 25
    )
  )
  PacMaze[0].ColorList = {
    ' ' : (0,0,0),
    'O' : cf.WallRGB,
    '-' : cf.WallRGB,
    '|' : cf.WallRGB,
    '.' : cf.DotRGB,
    '*' : (cf.PillR, cf.PillG, cf.PillB)
  }


  PacMaze[0].TypeList = {
    ' ' : 'EmptyObject',
    'O' : 'wall',
    '-' : 'wall',
    '|' : 'wall',
    '.' : 'dot',
    '*' : 'pill'
  }


  PacMaze[0].map= (
   #0         1         2         3         4   #0
    "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO",   
    "O*....................................*O",
    "O.OOOOOO    OOOOOOOOOOOOOOOO    OOOOOO.O",
    "O.O..................................O.O",
    "O.O.OOOOOOOOO  OOOOOOOOOO  OOOOOOOOO.O.O",
    "O.O.O**                           *O.O.O",
    "O.O.O**                            O.O.O",
    "O.O O    OOOOOOOOOOOOOOOOOOOOOO    O.O.O",
    "O.O O    O*                  *O    O.O.O", 
    "O.O O    O       O...O        O    O.O.O", #10
    "O.  O       OOOOOO...OOOOOO        O...O",
    "O.  O  O    O.............O     O  O...O",
    "O.     O    O.............O     O   ...O",
    "O.  O  O    O.............O     O  O...O",
    "O.  O       O.............O        O...O",
    "O.O O  OOO  OOO  OOOOO  OOO  OOO   O.O.O",
    "O.O O    O         O         O     O.O.O",
    "O.O O    O**               **O     O.O.O",    
    "O.O O**  OOOOOOOOOOOOOOOOOOOOO     O.O.O",
    "O.O O**                          **O.O.O", #20
    "O.O OOOOOOOO       O        OOOOOOOO.O.O",
    "O.O................O.................O.O",
    "O.OOOOOOOO  OOOOOOOOOOOOOOOO  OOOOOOOO.O",
    "O*....................................*O",
    "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO"
  )






  #Create Maze 1
  PacMaze.append(cf.Maze(
    h      = 20,
    v      = 0,
    width  = 40, 
    height = 25
    )
  )
  PacMaze[1].ColorList = {
    ' ' : (0,0,0),
    '-' : cf.WallRGB,
    '|' : cf.WallRGB,
    '.' : cf.DotRGB,
    '*' : (cf.PillR, cf.PillG, cf.PillB)
  }


  PacMaze[1].TypeList = {
    ' ' : 'EmptyObject',
    '-' : 'wall',
    '|' : 'wall',
    '.' : 'dot',
    '*' : 'pill'
  }


  PacMaze[1].map= (
    #0         1         2         3         4
    "|--------------------------------------|",
    "|*                                    *|",
    "|      .............................   |",
    "| ---  .                           .   |",
    "| -*-  .                           .   |",
    "| -.-  .   |--------   -------|    .   |",
    "| -.-  .   |..................|    .   |",
    "| -.-  .   |..................|    .   |",
    "| -.-  .    ...-  -  -  -  ...     .   |",
    "| -.-  .    ...-**-**-**-  ...     .   |",
    "| -.-  .   |...-  -  -  -  ...|    . --|",
    "| -.-  .   |..................|    .   |",
    "|      .   |..................|    .   |",
    "|      .   |--------   --------    .   |",
    "| -.-  .                           .   |",
    "| -.-  .                           .   |",
    "| -.-  .............................   |",
    "| -.-  .............................   |",
    "| -.-  ..-----....-----....-----....   |",
    "| -.-  ..-...-....-...-....-...-....   |",
    "| -.-  ..-...-....-...-....-...-....   |",
    "| ---  ..-...-....-...-....-...-....   |",
    "|      .............................   |",
    "|*     .............................  *|",
    "|--------------------------------------|"
  )





  #Create Maze 2
  PacMaze.append(cf.Maze(
    h      = 28,
    v      = 0,
    width  = 34, 
    height = 26
    )
  )
  PacMaze[2].ColorList = {
    ' ' : (0,0,0),
    '-' : cf.WallRGB,
    '|' : cf.WallRGB,
    '.' : cf.DotRGB,
    '*' : (cf.PillR, cf.PillG, cf.PillB)
  }


  PacMaze[2].TypeList = {
    ' ' : 'EmptyObject',
    '-' : 'wall',
    '|' : 'wall',
    '.' : 'dot',
    '*' : 'pill'
  }


  PacMaze[2].map= (
    #0         1         2         3         4
    "|--------------------------------|",
    "|                *               |",
    "|    -          ***         -    |",
    "|              -***-    -        |",
    "|        -     --.--             |",
    "|      .       --.--       -     |",
    "|     .-.       -.-        --    |",
    "|      .        -.-              |",
    "|                .    .          |",
    "|--                  .*.       --|",
    "|     ..     .        *          |",
    "|    ....   .-.                  |",
    "|     ...    .                   |",
    "|      ..          ---     -     |",
    "|                   -     -..    |",
    "|      -                   .     |",
    "|     ---   -       -            |",
    "|--    -           *-*         --|",
    "|              .    -    --      |",
    "|                                |",
    "|   -.    -                      |",
    "|   .-   .--             -       |",
    "|         .        -    .*-      |",
    "|                        .       |",
    "|                                |",
    "|--------------------------------|"
  )








  #Create Maze 3
  PacMaze.append(cf.Maze(
    h      = 20,
    v      = 0,
    width  = 20, 
    height = 26
    )
  )
  PacMaze[3].ColorList = {
    ' ' : (0,0,0),
    '-' : cf.WallRGB,
    '|' : cf.WallRGB,
    '.' : cf.DotRGB,
    '*' : (cf.PillR, cf.PillG, cf.PillB)
  }


  PacMaze[3].TypeList = {
    ' ' : 'EmptyObject',
    '-' : 'wall',
    '|' : 'wall',
    '.' : 'dot',
    '*' : 'pill'
  }


 
  PacMaze[3].map= (
    #0         1         2         3         4
    "|------------------|",
    "|..................|",
    "|.-------..-------.|", 
    "|.-     -..-     -.|",
    "|.-     -..-     -.|",
    "|.- **  -..- **  -.|",
    "|.- **  -..- **  -.|",
    "|.-     -..-     -.|",
    "|.-     -..-     -.|",
    "|.-     -..-     -.|",
    "|.-  .........   -.|",
    "|.....*  *  *......|",
    "|.-  .........   -.|",
    "|.-      ..      -.|",
    "|.-     -..-     -.|",
    "|.-     -..-     -.|",
    "|.-     -..-     -.|",
    "|.-     -..-     -.|",
    "|.-     -..-     -.|",
    "|.- **  -..- **  -.|",
    "|.- **  -..- **  -.|",
    "|.-     -..-     -.|",
    "|.-     -..-     -.|",
    "|.-------..-------.|",
    "|..................|",
    "|-------------------|"
  )



  #Create Maze 4
  PacMaze.append(cf.Maze(
    h      = 20,
    v      = 0,
    width  = 40, 
    height = 25
    )
  )
  PacMaze[4].ColorList = {
    ' ' : (0,0,0),
    'O' : cf.WallRGB,
    '-' : cf.WallRGB,
    '|' : cf.WallRGB,
    '.' : cf.DotRGB,
    '*' : (cf.PillR, cf.PillG, cf.PillB)
  }


  PacMaze[4].TypeList = {
    ' ' : 'EmptyObject',
    'O' : 'wall',
    '-' : 'wall',
    '|' : 'wall',
    '.' : 'dot',
    '*' : 'pill'
  }

  PacMaze[4].map= (
    "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO",
    "OO                               ...  OO",
    "O                                ...   O",
    "O    ...OOOOOOOOOO.....OOOOOOOOOO      O",
    "O    O.............................O   O",
    "O    O.............................O   O",
    "O    O.............................O   O",
    "O       OOOOOO.............OOOOOOO     O",
    "O            O.O.O.O.O.O.O.O           O", 
    "O            O.............O           O", #10
    "O            OOOOOOOOOOOOOOO           O",
    "O    ..... -                  -.....   O",
    "O    ..... -                  -.....   O",
    "O    ..... -     OO..OO       -.....   O",
    "O                .O..O.                O",
    "O               ..O..O..               O",
    "O              ..O....O..              O",
    "O****-          O......O    --------   O",
    "O****-           OO..OO     .......-   O",
    "O****                       - - -..-   O", #20
    "O---                        -.*.-..-   O",
    "O                   O       -......-   O",
    "O                   O       --------   O",
    "OO                  O                 OO",
    "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO"
)
 




  #Create Maze 5
  PacMaze.append(cf.Maze(
    h      = 18,
    v      = 0,
    width  = 43, 
    height = 27
    )
  )
  PacMaze[5].ColorList = {
    ' ' : cf.DotRGB,
    'o' : cf.WallRGB,
    'x' : (100,50,  0),
    '@' : cf.WallRGB,
    '-' : cf.WallRGB,
    '|' : cf.WallRGB,
    '.' : cf.DotRGB,
    '*' : (cf.PillR, cf.PillG, cf.PillB)
  }


  PacMaze[5].TypeList = {
    ' ' : 'dot',
    'o' : 'wall',
    'O' : 'wall',
    '@' : 'wall',
    'o' : 'wall',
    '-' : 'wall',
    '|' : 'wall',
    '.' : 'dot',
    '*' : 'pill'
  }



  PacMaze[5].map= (
    "ooooooooooooooooooooooooooooooooooooooooooo",
    "ooooooo. . . . .oxxxxxxxxxo. . . . .ooooooo",
    "oo. . . ooooooo ooooooooooo ooooooo . .  oo",
    "oo *ooo.oxxxxxo. . . * . . .oxxxxxo.ooo* oo",
    "oo. oxo oooooxo ooooo ooooo oxooooo oxo  oo",
    "oo .oxo. . .oxo.oxxxo oxxxo.oxo. . .oxo. oo",
    "oo. oxooooo oxo oxooo oooxo oxo oooooxo  oo",
    "oo .oxxxxxo.oxo.ooo. * .ooo.oxo.oxxxxxo. oo",
    "oo. oxooooo ooo . . . . . . ooo oooooxo  oo",
    "oo .oxo. . . . .ooooo ooooo. . . . .oxo. oo",
    "oo. ooo ooooooo oxxxo.oxxxo ooooooo ooo  oo",   
    "oo . * .oxxxxxo.oxooo oooxo.oxxxxxo. * . oo",
    "ooooooo ooooooo ooo  .  ooo ooooooo ooooooo",
    "ooxxxxo. . . . . . . . . . . . . . .oxxxxoo",
    "ooooooo ooooooo ooo  .  ooo ooooooo ooooooo",
    "oo . * .oxxxxxo.oxooo oooxo.oxxxxxo. * . oo",
    "oo. ooo ooooooo oxxxo.oxxxo ooooooo ooo  oo",   
    "oo .oxo. . . . .ooooo ooooo. . . . .oxo. oo",
    "oo. oxooooo ooo . . . . . . ooo oooooxo  oo",
    "oo .oxxxxxo.oxo.ooo  *  ooo.oxo oxxxxxo. oo",
    "oo. oxooooo oxo oxooo oooxo oxo oooooxo  oo",
    "oo .oxo. . .oxo.oxxxo oxxxo.oxo. . .oxo. oo",
    "oo. oxo oooooxo ooooo ooooo oxooooo oxo  oo",
    "oo *oxo.oxxxxxo. . . * . . .oxxxxxo.oxo* oo",
    "oo. ooo ooooooo ooooooooooo ooooooo ooo. oo",
    "ooo.  .  .  .  .oxxxxxxxxxo.  .  .  .  .ooo",
    "ooooooooooooooooooooooooooooooooooooooooooo"
)
 


  #Create Maze 6
  PacMaze.append(cf.Maze(
    h      = 18,
    v      = 0,
    width  = 43, 
    height = 27
    )
  )
  PacMaze[6].ColorList = {
    ' ' : cf.DotRGB,
    'o' : cf.WallRGB,
    'x' : (100,50,  0),
    '@' : cf.WallRGB,
    '-' : cf.WallRGB,
    '|' : cf.WallRGB,
    '.' : cf.DotRGB,
    '*' : (cf.PillR, cf.PillG, cf.PillB)
  }


  PacMaze[6].TypeList = {
    ' ' : 'dot',
    'o' : 'wall',
    'O' : 'wall',
    '@' : 'wall',
    'o' : 'wall',
    '-' : 'wall',
    '|' : 'wall',
    '.' : 'dot',
    '*' : 'pill'
  }



  PacMaze[6].map= (
    "ooooooooooooooooooooooooooooooooooooooooooo",
    "oo       . . . .           . . . . .     oo",
    "o . . . ooooooo             ooooooo . .   o",
    "o  *   .oxxxxxo. . . * . . .oxxxxxo.   *  o",
    "o .     ooooooo             ooooooo       o",
    "o  .   . .     .           .           .  o",
    "o .                                       o",
    "o  .           .   . *                 .  o",
    "o .             . . . . . .               o",
    "o          . . .           . . . . .   .  o",
    "o .     ooooooo      .      ooooooo       o",   
    "o  . * .oxxxxxo            .oxxxxxo. * .  o",
    "o       oooxooo      .      oooxooo       o",
    "o      . .oxo. . . . . . . . .oxo. .      o",
    "o       oooxooo      .      oooxooo       o",
    "o  . * .oxxxxxo.           .oxxxxxo. * .  o",
    "o .     ooooooo      .      ooooooo       o",   
    "o      . . . . .           . . . . .   .  o",
    "o .                                       o",
    "o  .                                      o",
    "o .                  *                    o",
    "o  .                                      o",
    "o .     ooooooo             ooooooo       o",
    "o  *   .oxxxxxo. . . * . . .oxxxxxo.      o",
    "o .     ooooooo             ooooooo       o",
    "oo .  .  .  .  .           .  .  .  .  . oo",
    "ooooooooooooooooooooooooooooooooooooooooooo"
)





  
  while 1 == 1:   

    #ThreeGhostPacSprite.HorizontalFlip()
    #ThreeGhostPacSprite.ScrollAcrossScreen(0,3,"left",gv.ScrollSleep)
    #ThreeGhostPacSprite.HorizontalFlip()

    #ThreeBlueGhostPacSprite.HorizontalFlip()
    #ThreeBlueGhostPacSprite.ScrollAcrossScreen(0,7,"right",gv.ScrollSleep)
    #ThreeBlueGhostPacSprite.HorizontalFlip()
    
#    ThreeGhostPacSprite.HorizontalFlip()
#    ThreeBlueGhostPacSprite.HorizontalFlip()
    
    
      

    LevelString = str(LevelCount)
   
    
    cf.ClearBigLED()
    #cf.ShowLevelCount(LevelCount)
    

    cf.CopySpriteToPixelsZoom(ClockSprite,      gv.ClockH,      gv.ClockV,      gv.ClockRGB,       gv.SpriteFillerRGB,1)
    cf.CopySpriteToPixelsZoom(DayOfWeekSprite,  gv.DayOfWeekH,  gv.DayOfWeekV,  gv.DayOfWeekRGB,   gv.SpriteFillerRGB,1)
    cf.CopySpriteToPixelsZoom(MonthSprite,      gv.MonthH,      gv.MonthV,      gv.MonthRGB,       gv.SpriteFillerRGB,1)
    cf.CopySpriteToPixelsZoom(CurrencySprite,   gv.CurrencyH,   gv.CurrencyV,   gv.CurrencyRGB,    gv.SpriteFillerRGB,1)


    
    #Reset Variables
    moves           = 0  
    PowerPillMoves  = 0
    PowerPillActive = 0
    PacStuckCount   = 0
    MovesSinceSmartSeekFlip  = 0
    PacDotSmartSeekMode  = 1



    gv.DotMatrix = [[0 for x in range(gv.HatWidth)] for y in range(gv.HatWidth)] 
    DotsRemaining = 0
    DotsEaten = 0
    Key       = ""
    ClosestX = 0
    ClosestY = 0
    
    #Keeping track of eating
    gv.MovesSinceSmartSeekFlip = 0
    MovesSinceEatingGhost  = 0
    gv.PacDotSmarkSeekMode = 1




    #Show clock
    m,r = divmod(moves,CheckClockSpeed)
    if (r == 0):
      CheckClockTimer(ClockSprite)
      cf.CopySpriteToPixelsZoom(ClockSprite,      gv.ClockH,      gv.ClockV,      gv.ClockRGB,       gv.SpriteFillerRGB,1)
      cf.CopySpriteToPixelsZoom(DayOfWeekSprite,  gv.DayOfWeekH,  gv.DayOfWeekV,  gv.DayOfWeekRGB,   gv.SpriteFillerRGB,1)
      cf.CopySpriteToPixelsZoom(MonthSprite,      gv.MonthH,      gv.MonthV,      gv.MonthRGB,       gv.SpriteFillerRGB,1)
      cf.CopySpriteToPixelsZoom(DayOfMonthSprite, gv.DayOfMonthH, gv.DayOfMonthV, gv.DayOfMonthRGB,  gv.SpriteFillerRGB,1)
  
    m,r = divmod(moves,gv.CheckCurrencySpeed)
    if (r == 0):  
      CurrencySprite = CreateCurrencySprite()
      cf.CopySpriteToPixelsZoom(CurrencySprite,   gv.CurrencyH,   gv.CurrencyV,   gv.CurrencyRGB,    gv.SpriteFillerRGB,1)


 

    #Set starting positions and Current Maze
    CurrentMaze = (random.randint(0,6))
    
    gv.DotMatrix,NumDots = PacMaze[CurrentMaze].LoadMap()
    (PacDotH, PacDotV), (Ghost1H, Ghost1V),  (Ghost2H, Ghost2V), (Ghost3H, Ghost3V), (Ghost4H, Ghost4V) = PacMaze[CurrentMaze].GetStartingPositions()

    #hard coding start of pacdot for maze5
    PacDotV = 23

    #we keep track of recent locations to help determine if PacDot is stuck or lost
    #priming it with 3 locations
    gv.PacDotRecentMoves.append((-1,-1))
    gv.PacDotRecentMoves.append((-1,-1))
    gv.PacDotRecentMoves.append((-1,-1))
    

    
    #DrawMaze()
    CurrentDirection1 = randint(1,4)
    CurrentDirection2 = randint(1,4)
    CurrentDirection3 = randint(1,4)
    CurrentDirection4 = randint(1,4)
    CurrentDirectionPacDot = randint(1,4)
    PowerPillActive = 0

    Ghost1Alive = 1
    Ghost2Alive = 1
    Ghost3Alive = 1 
    Ghost4Alive = 1 
   
    
    

    #decrement dots if PacDot starts out on one
    r,g,b = cf.getpixel(PacDotH,PacDotV)
    if r == cf.DotB and g == cf.DotG and b == cf.DotB:
      NumDots = NumDots -1
      #New method utilizesgv.DotMatrix
      gv.DotMatrix[PacDotH][PacDotV] = 0

    DotsRemaining = CountDotsRemaining(gv.DotMatrix)
   
      
    Ghost1H,Ghost1V = DrawGhost(Ghost1H,Ghost1V,cf.Ghost1R,cf.Ghost1G,cf.Ghost1B)
    Ghost2H,Ghost2V = DrawGhost(Ghost2H,Ghost2V,cf.Ghost2R,cf.Ghost2G,cf.Ghost2B)
    Ghost3H,Ghost3V = DrawGhost(Ghost3H,Ghost3V,cf.Ghost3R,cf.Ghost3G,cf.Ghost3B)
    Ghost4H,Ghost4V = DrawGhost(Ghost4H,Ghost4V,cf.Ghost4R,cf.Ghost4G,cf.Ghost4B)
    PacDotH,PacDotV = DrawPacDot(PacDotH,PacDotV,cf.PacR,cf.PacG,cf.PacB)

    #DrawPowerPills(PowerPills)

    #print ("moves: ",moves, "NumDots: ",NumDots," DotsEaten: ",DotsEaten," DotsRemaining: ",DotsRemaining, " ",end="\r")
    #sys.stdout.flush()
    
    
    
    while ((moves < MaxMoves) and (DotsRemaining > 0) and (PacStuckCount <= PacStuckMaxCount)):
      DotsRemaining = CountDotsRemaining(gv.DotMatrix)
      moves = moves + 1

      #Keeping track of eating
      gv.MovesSinceSmartSeekFlip = gv.MovesSinceSmartSeekFlip   + 1
      MovesSinceEatingGhost  = MovesSinceEatingGhost + 1
      


      PacOldH = PacDotH
      PacOldV = PacDotV
      #print ("moves: ",moves, "MaxMoves:",MaxMoves,"NumDots: ",NumDots," DotsEaten: ",DotsEaten," DotsRemaining: ",DotsRemaining, " ",end="\r")
      #sys.stdout.flush()

      #Check for keyboard input
      Key = ''
      m,r = divmod(moves,KeyboardSpeed)
      if (r == 0):
        Key = cf.PollKeyboard()
        ProcessKeypress(Key)
        if (Key == 'q'):
          moves = MaxMoves
          return
        if (Key == 'n'):
          PacStuckCount = PacStuckMaxCount
          


      #Show clock
      m,r = divmod(moves,CheckClockSpeed)
      if (r == 0):
        CheckClockTimer(ClockSprite)
        cf.CopySpriteToPixelsZoom(ClockSprite, gv.ClockH, gv.ClockV, gv.ClockRGB,gv.SpriteFillerRGB,1)


        
      if PowerPillActive == 1:
        PowerPillMoves = PowerPillMoves + 1
        GhostSpeed1 = BlueGhostSpeed
        GhostSpeed2 = BlueGhostSpeed
        GhostSpeed3 = BlueGhostSpeed
        GhostSpeed4 = BlueGhostSpeed

        if (Ghost1Alive == 0 and Ghost2Alive == 0 and Ghost3Alive == 0 and Ghost4Alive == 0):
          PowerPillActive = 0
          PowerPillMoves = 999
          


        if PowerPillMoves >= BlueGhostmoves:
          #Need to refresh dots
          DotsRemaining = CountDotsRemaining(gv.DotMatrix)
          PowerPillActive = 0
          PowerPillMoves = 0
          if (Ghost1Alive == 0):
            Ghost1Alive = 1
          if (Ghost2Alive == 0):
            Ghost2Alive = 1
          if (Ghost3Alive == 0):
            Ghost3Alive = 1
          if (Ghost4Alive == 0):
            Ghost4Alive = 1
          CurrentDirection1 = 4
          CurrentDirection2 = 1
          CurrentDirection3 = 2
          CurrentDirection4 = 3
          GhostSpeed1 = StartGhostSpeed1
          GhostSpeed2 = StartGhostSpeed2
          GhostSpeed3 = StartGhostSpeed3
          GhostSpeed4 = StartGhostSpeed4
          (IgnoreH, IgnoreV), (Ghost1H, Ghost1V),  (Ghost2H, Ghost2V), (Ghost3H, Ghost3V), (Ghost4H, Ghost4V) = PacMaze[CurrentMaze].GetStartingPositions()



      

          
      #If the ghost speed divides evenly into the moves, the ghost gets to move
      #The lower the ghost speed indicator, the more often it will move
      if Ghost1Alive == 1:
        m,r = divmod(moves,GhostSpeed1)
        if (r == 0):
        
          if (PowerPillActive == 1):
            CurrentDirection1 = TurnAwayFromDot4Way(Ghost1H,Ghost1V,CurrentDirection1,PacDotH,PacDotV)          
          else:
          #turn towards pacman now and then
            if (random.randint(1,3) == 1):
              CurrentDirection1 = TurnTowardsDot4Way(Ghost1H,Ghost1V,CurrentDirection1,PacDotH,PacDotV)          

          Ghost1H, Ghost1V, CurrentDirection1 = MoveGhost(Ghost1H, Ghost1V,CurrentDirection1,cf.Ghost1R,cf.Ghost1G,cf.Ghost1B)
          #CurrentDirection1 = cf.ChanceOfTurning(CurrentDirection1,50)
          Ghost1H,Ghost1V = DrawGhost(Ghost1H,Ghost1V,cf.Ghost1R,cf.Ghost1G,cf.Ghost1B)




      if Ghost2Alive == 1:
        m,r = divmod(moves,GhostSpeed2)
        if (r == 0):
          if (PowerPillActive == 1):
            CurrentDirection2 = TurnAwayFromDot4Way(Ghost2H,Ghost2V,CurrentDirection2,PacDotH,PacDotV)          
          else:
            #turn towards pacman now and then
            if (random.randint(1,4) == 1):
              CurrentDirection2 = TurnTowardsDot4Way(Ghost2H,Ghost2V,CurrentDirection2,PacDotH,PacDotV)          

          Ghost2H, Ghost2V, CurrentDirection2 = MoveGhost(Ghost2H,Ghost2V,CurrentDirection2,cf.Ghost2R,cf.Ghost2G,cf.Ghost2B)
          CurrentDirection2 = cf.ChanceOfTurning(CurrentDirection2,20)
          Ghost2H,Ghost2V = DrawGhost(Ghost2H,Ghost2V,cf.Ghost2R,cf.Ghost2G,cf.Ghost2B)

      if Ghost3Alive == 1:
        m,r = divmod(moves,GhostSpeed3)
        if (r == 0):
          if (PowerPillActive == 1):
            CurrentDirection3 = TurnAwayFromDot4Way(Ghost3H,Ghost3V,CurrentDirection3,PacDotH,PacDotV)          
          else:

            if (random.randint(1,4) == 1):
              CurrentDirection3 = TurnTowardsDot4Way(Ghost3H,Ghost3V,CurrentDirection3,PacDotH,PacDotV)          
          Ghost3H, Ghost3V, CurrentDirection3 = MoveGhost(Ghost3H, Ghost3V,CurrentDirection3,cf.Ghost3R,cf.Ghost3G,cf.Ghost3B)
          CurrentDirection3 = cf.ChanceOfTurning(CurrentDirection3,10)
          Ghost3H,Ghost3V = DrawGhost(Ghost3H,Ghost3V,cf.Ghost3R,cf.Ghost3G,cf.Ghost3B)

      if Ghost4Alive == 1:
        m,r = divmod(moves,GhostSpeed4)
        if (r == 0):
          if (PowerPillActive == 1):
            CurrentDirection4 = TurnAwayFromDot4Way(Ghost4H,Ghost4V,CurrentDirection4,PacDotH,PacDotV)          
          else:

            #turn towards pacman now and then
            if (random.randint(1,5) == 1):
              CurrentDirection4 = TurnTowardsDot4Way(Ghost4H,Ghost4V,CurrentDirection4,PacDotH,PacDotV)          
          Ghost4H, Ghost4V, CurrentDirection4 = MoveGhost(Ghost4H, Ghost4V,CurrentDirection4,cf.Ghost4R,cf.Ghost4G,cf.Ghost4B)
          CurrentDirection4 = cf.ChanceOfTurning(CurrentDirection2,10)
          Ghost4H,Ghost4V = DrawGhost(Ghost4H,Ghost4V,cf.Ghost4R,cf.Ghost4G,cf.Ghost4B)


          
          
      #Move Pacman
      m,r = divmod(moves,PacSpeed)
      if (r == 0):
        
        #Turn towards ghosts if they are blue
        # NOTE: this means pacdot always chases the ghosts in the same order
        #       we could change this to look for the closest ghost
        if (PowerPillActive == 1 and gv.PacDotSmartSeekMode == 1):
          if (random.randint(1,gv.TurnTowardsBlueGhostSpeed) == 1):
            if (Ghost1Alive == 1):
              CurrentDirectionPacDot = TurnTowardsDot4Way(PacDotH,PacDotV,CurrentDirectionPacDot,Ghost1H,Ghost1V)
            elif (Ghost2Alive == 1):
              CurrentDirectionPacDot = TurnTowardsDot4Way(PacDotH,PacDotV,CurrentDirectionPacDot,Ghost2H,Ghost2V)
            elif (Ghost3Alive == 1):
              CurrentDirectionPacDot = TurnTowardsDot4Way(PacDotH,PacDotV,CurrentDirectionPacDot,Ghost3H,Ghost3V)
            elif (Ghost4Alive == 1):
              CurrentDirectionPacDot = TurnTowardsDot4Way(PacDotH,PacDotV,CurrentDirectionPacDot,Ghost4H,Ghost4V)

        else:
        
          if (gv.PacDotSmartSeekMode == 1):
            #print (gv.DotMatrix)
            #print ("NumDots: ",NumDots)
            #unicorn.show()
            #time.sleep(.2)
            ClosestX, ClosestY = FindClosestDot(PacDotH,PacDotV,gv.DotMatrix)

            #print("BEFORE CurrentDirection:",CurrentDirectionPacDot,"PacDotHV:",PacDotH,PacDotV," ClosestXY:",ClosestX,ClosestY, "                      ")
            CurrentDirectionPacDot = TurnTowardsDot4Way(PacDotH,PacDotV,CurrentDirectionPacDot,ClosestX,ClosestY)        
            #print("AFTER  CurrentDirection:",CurrentDirectionPacDot,"PacDotHV:",PacDotH,PacDotV," ClosestXY:",ClosestX,ClosestY, "                      ")
          
        

        #else:
        #  cf.ChanceOfTurning(CurrentDirectionPacDot,1)

      
        #-------------------------------------------------
        # check to see if current location has been 
        # visited recently multiple times
        #-------------------------------------------------
        gv.PacDotRecentMoves.append((PacDotH,PacDotV))
        RecentMoves = 0
        for xy in gv.PacDotRecentMoves:
          if  xy == (PacDotH,PacDotV):
            RecentMoves = RecentMoves + 1
            #print ("recent moves:", RecentMoves)
            if(RecentMoves >= gv.MaxRecentMoves):
              gv.PacDotSmartSeekMode ^= 1

        if(len(gv.PacDotRecentMoves) >= 5):
          del gv.PacDotRecentMoves[0]
              

        CurrentDirectionPacDot = FollowScanner(PacDotH,PacDotV,CurrentDirectionPacDot)
        
        PacDotH, PacDotV, CurrentDirectionPacDot, DotsEaten = MovePacDot(PacDotH, PacDotV,CurrentDirectionPacDot,cf.PacR,cf.PacG,cf.PacB,DotsEaten)
        PacDotH,PacDotV = DrawPacDot(PacDotH,PacDotV,cf.PacR,cf.PacG,cf.PacB)
        
        
        


      #print ("MinDots:",MinDots,"MaxDots:",MaxDots,"MaxMoves:",MaxMoves,"moves:",moves,"NumDots:", NumDots,"Eaten:",DotsEaten,"Pmoves:",Pacmoves,"G1Alive:",Ghost1Alive,"PPActv:",PowerPillActive, end="\r")
      
      
      #RefreshScreen dots occasionally
      #if (random.randint(1,25) == 1):
      #  NumDots = DrawDotMatrix(gv.DotMatrix)

      #sys.stdout.flush()
      
      # If pacman is stuck, game over
      if (PacOldH == PacDotH and PacOldV == PacDotV):
        PacStuckCount = PacStuckCount + 1
      else:
        PacStuckCount = 0




      #put PacDot back into smart seek mode after X moves
      if (gv.MovesSinceSmartSeekFlip > gv.MaxMovesSinceSmartSeekFlip and gv.PacDotSmartSeekMode == 0):
        #print ("Current smart seek mode:",gv.PacDotSmartSeekMode, "MovesSinceSmartSeekFlip:",gv.MovesSinceSmartSeekFlip)
        gv.PacDotSmartSeekMode     = 1
        gv.MovesSinceSmartSeekFlip = 0
        #print ("Current smart seek mode:",gv.PacDotSmartSeekMode, "MovesSinceSmartSeekFlip:",gv.MovesSinceSmartSeekFlip)

      #-------------------------------------
      #display score
      #-------------------------------------
      #DigitSpriteList[int(c)],1)
      cf.DisplayScore(PacDotScore,(cf.MedGreen))




      #Count dots.  Sometimes the ghosts sit on a dot and it loses its color
      #if (CheckElapsedTime(5) == 1):
      #  DotsRemaining = CountDotsRemaining(gv.DotMatrix)

        
      #cf.ClearBigLED()
      #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
      time.sleep(gv.PacSleep)



        
    
    
    #Show Game over or level count
    if (Key !=  "q"):
      if (DotsRemaining == 0):
        ScoreString = str(PacDotScore) 
        #ScrollScreen('down',gv.ScrollSleep)
        #cf.ClearBigLED()
        #PacLeftAnimatedSprite.Scroll(gv.HatWidth,6,'left',20,gv.ScrollSleep)
        #cf.ShowScrollingBanner2("Score",(cf.MedCyan),gv.ScrollSleep  * 0.75)
        #cf.ShowScrollingBanner2(ScoreString,(cf.MedGreen),(gv.ScrollSleep  * 0.75))
        NumDots = randint(MinDots,MaxDots)
        DotsEaten = 0
        DotsRemaining = NumDots
        LevelCount = LevelCount + 1
 
        print ("End of level")
        print ("PacDotScore: ",PacDotScore," PacDotHighScore:",gv.PacDotHighScore)
        if (PacDotScore > int(gv.PacDotHighScore)):
          print ("** NEW HIGH SCORE: ",gv.PacDotHighScore)
          gv.PacDotHighScore = PacDotScore

        cf.SaveConfigData()
        
      else:
        #End of Game Display
        cf.FlashDot(Ghost1H,Ghost1V,0.05)
        cf.FlashDot(Ghost2H,Ghost2V,0.05)
        cf.FlashDot(Ghost3H,Ghost3V,0.05)
        cf.FlashDot(Ghost4H,Ghost4V,0.05)
        cf.FlashDot(PacDotH,PacDotV,0.05)



        gv.PacDotGamesPlayed = gv.PacDotGamesPlayed + 1
        ScoreString = 'SCORE ' + str(PacDotScore) 
        print ("PacDotScore:",PacDotScore," PacDotHighScore:",gv.PacDotHighScore)
        if (PacDotScore > int(gv.PacDotHighScore)):
          print ("** NEW HIGH SCORE: ",gv.PacDotHighScore)
          gv.PacDotHighScore = PacDotScore
        
       


        gv.TheMatrix.Clear()
        cf.ClearBuffers()
        cf.ShowGlowingText(CenterHoriz=True,h=0,v=1 ,Text= 'GAME',       RGB= cf.HighRed,    ShadowRGB= cf.ShadowRed,    ZoomFactor= 2,GlowLevels=150, DropShadow=True)
        cf.ShowGlowingText(CenterHoriz=True,h=0,v=12,Text= 'OVER',       RGB= cf.HighRed,    ShadowRGB= cf.ShadowRed,    ZoomFactor= 2,GlowLevels=150, DropShadow=True)
        cf.ShowGlowingText(CenterHoriz=True,h=0,v=26,Text= ScoreString,  RGB= cf.HighPurple, ShadowRGB= cf.ShadowPurple, ZoomFactor= 1,GlowLevels=150, FadeLevels=150,DropShadow=True)
        ThreeGhostSprite.ScrollAcrossScreen(0,26,'right',gv.ScrollSleep)


        gv.TheMatrix.Clear()
        cf.ClearBuffers()
        cf.ShowGlowingText(CenterHoriz=True,h=0,v=1 ,Text= 'HIGH SCORE',             RGB= cf.HighOrange, ShadowRGB= cf.ShadowOrange, ZoomFactor= 1,GlowLevels=50, DropShadow=True)
        cf.ShowGlowingText(CenterHoriz=True,h=0,v=8 ,Text= str(gv.PacDotHighScore),  RGB= cf.HighPurple, ShadowRGB= cf.ShadowPurple, ZoomFactor= 1,GlowLevels=100,FadeLevels=0,DropShadow=True)
        cf.ShowGlowingText(CenterHoriz=True,h=0,v=16,Text= 'GAMES PLAYED',           RGB= cf.HighOrange, ShadowRGB= cf.ShadowOrange, ZoomFactor= 1,GlowLevels=50, DropShadow=True)
        cf.ShowGlowingText(CenterHoriz=True,h=0,v=26,Text= str(gv.PacDotGamesPlayed),RGB= cf.HighPurple, ShadowRGB= cf.ShadowPurple, ZoomFactor= 1,GlowLevels=100,FadeLevels=0,DropShadow=True)
        cf.EraseMessageArea(6)
        ThreeGhostSprite.ScrollAcrossScreen(0,26,'left',gv.ScrollSleep)

        gv.TheMatrix.Clear()
        gv.Canvas.Clear()
        cf.ZoomScreen(gv.ScreenArray,32,256,0,Fade=True)

        PacDotScore = 0



        cf.SaveConfigData()
        return
        
        
    else:
      return

    








#--------------------------------------
# VirusWorld  / OUTBREAK             --
#--------------------------------------

# Ideas:
# - Mutations happen
# - if virus is mutating, track that in the object itself
# - possible mutations: speed, turning eraticly
# - aggression, defence can be new attributes
# - need a new object virus dot
# - when a virus conquers an area, remove part of the wall and scroll to the next area
# - areas may have dormant viruses that are only acivated once in a while
# - virus will slow down to eat


  

def SpreadInfection(Virus1,Virus2,direction):
  global ClumpingSpeed
  global ChanceOfSpeedup
  global InfectionChance
  global OriginalReplicationRate

  #print ("Spread Infection: ",Virus1.name, Virus2.name)
  
  #for some reason, my wall checks still let the odd wall slip past.  This will take care of it.
  if (Virus2.name == "WallBreakable"):
    #print ("Wallbreakable is immune from infections but does sustain damage",Virus2.lives)
    Virus2.lives = Virus2.lives -1
    Virus2.IncreaseBrightness(gv.FoodBrightnessSteps)
           
    #Trying something new here.  When the virus is eating, we still want it to be active (speed) but just not moving
    #until the food is gone
    Virus1.eating = True
    Virus1.clumping = True
    Virus1.AdjustSpeed(gv.EatingSpeedAdjustment)
    Virus1.replicationrate   = Virus1.replicationrate // 2   #floor division
    Virus1.mutationdeathrate = Virus1.mutationdeathrate + 1
   



    if (Virus2.lives <= 0):
      Virus2 = cf.EmptyObject
      Virus2.alive = 0
      #when virus finishes eating, it speeds up
      #Virus1.AdjustSpeed(-3)
      #if (Virus1.speed <= 1):
      #  Virus1.speed = 1
      
      #Done Eating?  Go faster little fella!
      Virus1.eating   = False
      Virus1.clumping = False
      Virus1.AdjustInfectionChance(-1)
      Virus1.AdjustSpeed(-3)
      Virus1.replicationrate = gv.OriginalReplicationRate


  else:

    if(random.randint(1,gv.InfectionChance) == 1):

      Virus2.name = Virus1.name
      Virus2.r    = Virus1.r   
      Virus2.g    = Virus1.g   
      Virus2.b    = Virus1.b   
      Virus2.direction      = direction
      Virus2.speed          = Virus1.speed
      Virus2.mutationtype   = Virus1.mutationtype
      Virus2.mutationrate   = Virus1.mutationrate
      Virus2.mutationfactor = Virus1.mutationfactor
      Virus2.eating         = Virus1.eating
      Virus2.clumping       = Virus1.clumping
      
      #Too slow.  Need another way to indicate mass infections spreading
      #if (cf.CheckBoundary(Virus2.h,Virus2.v) == 0):
      #  cf.FlashDot6(Virus2.h,Virus2.v)
      
      #Infected virus slows down, attempt to increase clumping
      Virus2.AdjustSpeed(+gv.ClumpingSpeed)
      
    
      

  
def ReplicateVirus(Virus,DinnerPlate):
  #global MaxReplications

  #         2 1 3
  #         5 x 6                              
  #           4   


  ItemList  = []
  h         = Virus.h
  v         = Virus.v
  ScanV     = 0
  ScanH     = 0
  direction = Virus.direction
  scandirection = 0


  if(Virus.replications <= gv.MaxReplications):
    ItemList               = cf.VirusWorldScanAround(Virus,DinnerPlate.Playfield)
  
    if (ItemList[5] == 'EmptyObject') or (ItemList[6] == 'EmptyObject'):
      VirusCopy              = copy.deepcopy(Virus)
      VirusCopy.replications +=1
      Virus.replications     +=1
    
      if (ItemList[5] == 'EmptyObject'):
        #print ("Open space to the left")
        scandirection  = cf.TurnLeft8Way(cf.TurnLeft8Way(direction))
        #print ("direction scandirection",direction,scandirection)

      elif (ItemList[6] == 'EmptyObject'):
        #print ("Open space to the right")
        scandirection = cf.TurnRight8Way(cf.TurnRight8Way(direction))


      ScanH,ScanV = cf.CalculateDotMovement8Way(h,v,scandirection)
      VirusCopy.v = ScanV
      VirusCopy.h = ScanH
      VirusCopy.AdjustSpeed(gv.ReplicationSpeed)
      DinnerPlate.Playfield[ScanV][ScanH] = VirusCopy
      return VirusCopy; 
  
  return cf.EmptyObject('EmptyObject');

  
  

def MoveVirus(Virus,Playfield):
  global VirusMoves
  global ChanceOfTurningIntoFood

  #print ("== MoveVirus : ",Virus.name," hv dh dv alive--",Virus.h,Virus.v,Virus.dh,Virus.dv,Virus.alive)
  
  #print ("")
  h = Virus.h
  v = Virus.v
  oldh  = h
  oldv  = v
  ScanH = 0
  ScanV = 0
  ItemList = []
  DoNothing = ""
  ScanDirection = 1
  WallInFront    = cf.EmptyObject('EmptyObject')
  VirusInFront   = cf.EmptyObject('EmptyObject')
  VirusInRear    = cf.EmptyObject('EmptyObject')
  VirusLeftDiag  = cf.EmptyObject('EmptyObject')
  VirusRightDiag = cf.EmptyObject('EmptyObject')
  
  #Infection / mutation modiefers
  #We need a random chance of mutation
  #  possibilities: 
  #  - mutate into another color
  #  - vastly increase/decrease speed
  #  - change direction
  #  - happens right before last move 
  
  InfectionSpeedModifier = -1
 
 

  #print("Current Virus vh direction:",v,h,Virus.direction)
  ItemList = cf.VirusWorldScanAround(Virus,Playfield)
  #print (ItemList)
  

  #Grab breakable wall object
  if (ItemList[1] == "WallBreakable"):
    ScanH,ScanV = cf.CalculateDotMovement8Way(h,v,Virus.direction)
    WallInFront = Playfield[ScanV][ScanH]


  #Grab potential viruses in scan zones NW N NE S
  #Grab Virus in front
  if (ItemList[1] != "Wall" and ItemList[1] != "WallBreakable" and ItemList[1] != 'EmptyObject'):
    ScanH,ScanV = cf.CalculateDotMovement8Way(h,v,Virus.direction)
    VirusInFront = Playfield[ScanV][ScanH]
    #print ("ScanFront    ",VirusInFront.name,VirusLeftDiag.name,VirusRightDiag.name,VirusInRear.name)

  #Grab Virus left diagonal
  if (ItemList[2] != "Wall" and ItemList[1] != "WallBreakable" and ItemList[2] != 'EmptyObject'):
    ScanDirection = cf.TurnLeft8Way(Virus.direction)
    ScanH,ScanV = cf.CalculateDotMovement8Way(h,v,ScanDirection)
    VirusLeftDiag = Playfield[ScanV][ScanH]
    #print ("ScanLeftDiag ",VirusInFront.name,VirusLeftDiag.name,VirusRightDiag.name,VirusInRear.name)

  #Grab Virus right diagonal
  if (ItemList[3] != "Wall" and ItemList[1] != "WallBreakable" and ItemList[3] != 'EmptyObject'):
    ScanDirection = cf.TurnRight8Way(Virus.direction)
    ScanH,ScanV = cf.CalculateDotMovement8Way(h,v,ScanDirection)
    VirusRightDiag = Playfield[ScanV][ScanH]
    #print ("ScanRightDiag",VirusInFront.name,VirusLeftDiag.name,VirusRightDiag.name,VirusInRear.name)
  
        
  if (ItemList[4] != "Wall" and ItemList[1] != "WallBreakable" and ItemList[4] != 'EmptyObject'):
    ScanDirection = cf.ReverseDirection8Way(Virus.direction)
    ScanH,ScanV   = cf.CalculateDotMovement8Way(h,v,ScanDirection)
    VirusInRear     = Playfield[ScanV][ScanH]
    #print ("ScanRear",VirusInFront.name,VirusLeftDiag.name,VirusRightDiag.name,VirusInRear.name)
  

  #Infect Virus
  #If different virus, take it over (test for chance)
  #else follow it


  #Add damage to breakable walls
  if (WallInFront.name == "WallBreakable"):
    #print ("Wall in front: ",WallInFront.name, WallInFront.lives)
    WallInFront.lives = WallInFront.lives -1
    Virus.eating = True
    WallInFront.IncreaseBrightness(gv.FoodBrightnessSteps)
    if (WallInFront.lives <= 0):
      Playfield[WallInFront.v][WallInFront.h] = cf.EmptyObject('EmptyObject')


  #print ("Thing in front:",VirusInFront.name, WallInFront.name)
        
  #Check front Virus
  if (VirusInFront.name != 'EmptyObject' and VirusInFront.name != 'WallBreakable'):
    if (VirusInFront.name != Virus.name):
      SpreadInfection(Virus,VirusInFront,Virus.direction)
      #VirusInFront.AdjustSpeed(InfectionSpeedModifier)

  #Check left diagonal Virus
  if (VirusLeftDiag.name != 'EmptyObject'):
    if (VirusLeftDiag.name != Virus.name):
      SpreadInfection(Virus,VirusLeftDiag,(cf.TurnLeft8Way(Virus.direction)))


  #Check right diagonal Virus
  if (VirusRightDiag.name != 'EmptyObject'):
    if (VirusRightDiag.name != Virus.name):
      SpreadInfection(Virus,VirusRightDiag,(cf.TurnRight8Way(Virus.direction)))


  #Check rear Virus
  if (VirusInRear.name != 'EmptyObject'):
    #If different virus, take it over 
    #make it follow
    if (VirusInRear.name != Virus.name):
      SpreadInfection(Virus,VirusInRear,Virus.direction)


  #We follow other virus of the same name
  if (VirusInFront.name == Virus.name):
    Virus.direction = VirusInFront.direction
  elif (VirusLeftDiag.name == Virus.name):
    Virus.direction = VirusLeftDiag.direction
  elif (VirusRightDiag.name == Virus.name):
    Virus.direction = VirusRightDiag.direction
  elif (VirusInRear.name == Virus.name):
    Virus.direction = VirusInRear.direction


  #If no viruses around, increase speed and wander around
  if (all('EmptyObject' == Item for Item in ItemList)):
    if (random.randint(1,gv.ChanceOfSpeedup) == 1):
      Virus.AdjustSpeed(-1)
  

  #print ("Viruss: ",Virus.name, VirusInFront.name, VirusLeftDiag.name, VirusRightDiag.name, VirusInRear.name)

  
  #If no viruses around, check for walls
  if (all('EmptyObject' == name for name in (VirusInFront.name, VirusLeftDiag.name, VirusRightDiag.name, VirusInRear.name))):
    

    if (ItemList[1] == "WallBreakable"):
      Virus.direction = cf.TurnLeftOrRight8Way(Virus.direction)


    elif((ItemList[1] == "Wall" or ItemList[1] == "WallBreakable") 
      and ItemList[2] == 'EmptyObject' 
      and ItemList[3] == 'EmptyObject'):
      Virus.direction = cf.TurnLeftOrRight8Way(Virus.direction)

    elif((ItemList[1] == "Wall" or ItemList[1] == "WallBreakable") 
      and(ItemList[2] == "Wall" or ItemList[2] == "WallBreakable") 
      and ItemList[3] == 'EmptyObject'):
      Virus.direction = cf.TurnRight8Way(Virus.direction)

    elif((ItemList[1] == "Wall" or ItemList[1] == "WallBreakable")
      and ItemList[2] == 'EmptyObject' 
      and(ItemList[3] == "Wall" or ItemList[3] == "WallBreakable")):
      Virus.direction = cf.TurnLeft8Way(Virus.direction)

    elif((ItemList[1] == "Wall" or ItemList[1] == "WallBreakable")
     and (ItemList[2] == "Wall" or ItemList[2] == "WallBreakable")
     and (ItemList[3] == "Wall" or ItemList[3] == "WallBreakable")):
      Virus.direction = cf.TurnLeftOrRightTwice8Way(cf.ReverseDirection8Way(Virus.direction))
 

  #-----------------------------------------
  #-- Mutations                           --
  #-----------------------------------------

  #Mutate virus
  #print ("MV - mutationrate type factor",Virus.mutationrate, Virus.mutationtype, Virus.mutationfactor)
  if (random.randint(0,Virus.mutationrate) == 1):
    Virus.Mutate()

    if (Virus.alive == 0):
      #print ("Accident during mutation. Virus died!")
      Virus.lives = 0
      Virus.speed = 1
      Virus.mutationtype   = 0
      Virus.mutationfactor = 0
      Playfield[Virus.v][Virus.h] = cf.EmptyObject('EmptyObject')


    #If after a mutation the virus dies, there is a small chance to turn into food or a wall
    if (random.randint(0,gv.ChanceOfTurningIntoFood) == 1):
      Playfield[Virus.v][Virus.h] = cf.Wall(Virus.h,Virus.v,cf.SDDarkWhiteR,cf.SDDarkWhiteG,(cf.SDDarkWhiteB + 60),1,gv.VirusFoodWallLives,'WallBreakable')
    elif (random.randint(0,gv.ChanceOfTurningIntoWall) == 1):
      Playfield[Virus.v][Virus.h] = cf.Wall(Virus.h,Virus.v,cf.SDDarkWhiteR,cf.SDDarkWhiteG,cf.SDDarkWhiteB,1,gv.VirusFoodWallLives,'Wall')
    else:
      Playfield[Virus.v][Virus.h] = cf.EmptyObject('EmptyObject')




  #apply directional mutations
  if (Virus.mutationtype in (1,2,8)):
    m,r = divmod(gv.VirusMoves,Virus.mutationfactor)
    if (r == 0):
      Virus.direction = cf.TurnLeft8Way(Virus.direction)

  elif(Virus.mutationtype in (3,4,9)):
    m,r = divmod(gv.VirusMoves,Virus.mutationfactor)
    if (r == 0):
      Virus.direction = cf.TurnRight8Way(Virus.direction)
  
  elif(Virus.mutationtype == 7):
    m,r = divmod(gv.VirusMoves,Virus.mutationfactor)
    if (r == 0):
      Virus.direction = cf.TurnRight8Way(Virus.direction)
      cf.TurnLeftOrRight8Way(Virus.direction)




  #A virus can be in eating mode, but another virus eats the food.  The first virus will stay in eating mode
  #as a work around, we will randomly tell the virus to stop eating
  if (random.randint(1,gv.ChanceToStopEating) == 1):
    Virus.eating = False


  if (Virus.alive == 1 and Virus.eating == False):  

    #Only move if the space decided upon is actually empty!
    ScanH,ScanV = cf.CalculateDotMovement8Way(h,v,Virus.direction)
    if (Playfield[ScanV][ScanH].name == 'EmptyObject'):
      #print ("Spot moving to is empty ScanV ScanH",ScanV,ScanH)
      #print ("Virus moved!!!!!!!!!!!!!")
      

      #If virus is in clumping mode, only move if the target space is bordering on a virus of the same name
      #If clumping mode but no nearby viruses, let the little fella keep going
      if (Virus.clumping == True):
        if (cf.IsThereAVirusNearby(ScanH, ScanV, Virus.direction,Virus.name,Playfield) == 1):
          Virus.h = ScanH
          Virus.v = ScanV
          Playfield[ScanV][ScanH] = Virus
          Playfield[oldv][oldh] = cf.EmptyObject('EmptyObject')

        elif(cf.CountVirusesBehind(Virus.h, Virus.v, Virus.direction,Virus.name,Playfield) == 0):
          Virus.h = ScanH
          Virus.v = ScanV
          Playfield[ScanV][ScanH] = Virus
          Playfield[oldv][oldh] = cf.EmptyObject('EmptyObject')

      else:
        Virus.h = ScanH
        Virus.v = ScanV
        Playfield[ScanV][ScanH] = Virus
        Playfield[oldv][oldh] = cf.EmptyObject('EmptyObject')



    else:
      #print ("spot moving to is not empty: ",Playfield[ScanV][ScanH].name, ScanV,ScanH)
      #Introduce some instability into the virus
      if (random.randint(0,InstabilityFactor) == 1):
        Virus.direction = cf.TurnLeftOrRight8Way(Virus.direction)
        Virus.AdjustSpeed(random.randint(-1,1))



  return 



def CreateDinnerPlate(MapLevel):
  global mutationrate
  
  print ("CreateDinnerPlate Map: ",MapLevel)


  TheMap = cf.TextMap(
    h      = 1,
    v      = 1,
    width  = 66, 
    height = 34
    )
  
  TheMap.ColorList = {
    ' ' : (0  ,0  ,0),
    '-' : ( 0 , 0 , 0),
    '.' : ( 5 , 5 , 5),
    'o' : (25 ,25 ,25),
    'O' : (65 ,65 ,65),
    '@' : (95 ,95 ,95),
    '#' : (125,125,125),
    '*' : (  5,  5,  5),
    '1' : (0  ,150,  0),
    '2' : (150,  0,  0),
    '3' : (150,100,  0),
    '4' : (  0,  0,100),
    '5' : (200,  0, 50),
    '6' : (125,185,  0),
    '7' : (200,  0,200),
    '8' : ( 50,150, 75)
  }

  TheMap.TypeList = {
    ' ' : 'EmptyObject',
    '-' : 'wall',
    '.' : 'wall',
    'o' : 'wall',
    'O' : 'wall',
    '@' : 'wall',
    '#' : 'wall',
    '*' : 'wallbreakable',
    '1' : 'virus',
    '2' : 'virus',
    '3' : 'virus',
    '4' : 'virus',
    '5' : 'virus',
    '6' : 'virus',
    '7' : 'virus',
    '8' : 'virus'
  }




  if (MapLevel == 1):
    
    DinnerPlate = cf.VirusWorld(name='TheCave',
                               width        = 66, #we want the playfield to be 1 pixel larger on all sides than the display
                               height       = 34,
                               Map          = [[]],
                               Playfield    = [[]],
                               CurrentRoomH = 1,
                               CurrentRoomV = 1,
                               DisplayH     = 1,
                               DisplayV     = 1,
                               mutationrate = mutationrate,
                               replicationrate = gv.replicationrate,
                               mutationdeathrate = mutationdeathrate,
                               VirusStartSpeed = gv.VirusStartSpeed)

    #Change food to blue for this map
    TheMap.ColorList['*']  =  (0,0,20)

    TheMap.map= (
      #0         1  .......2.........3.........4.........5.........6....65    
      "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO", #0  
      "O            -ooo.***********************************************O",
      "O            -OOo.****..oo***o***********************************O",
      "O            -@Oo.****..ooo**ooooooo*****************************O",
      "O            -3Oo.****..oooo**OOOOOooooo*************************O",
      "O            -OOo.***...oOOOO*****OOOOOooooo*********************O",
      "O            -ooo***....oO3333********OOOOOooooo*****************O",
      "O            -....**....oO3333            OOOOOooooo*************O",
      "O            -******.ooooO3333   111          OOOOOooooo***..... O", 
      "O            -*****..oOOOO       111              OOOOOoooo..... O", 
      "O            -***....oO          111                  OOOOo..... O", #10
      "O            - . ....oO          11           2          Oo......O",
      "O            - . ....oO          11     **    2          Oo......O",
      "O            - ......oOOOO       1    ******  2          Oo......O",
      "O            - ......ooooO          ********* 22222222   Oo......O",
      "O            -    ......oO        ******@*****22222222   Oo......O",
      "O            -      ....oO     ********@@*****2          Oo......O",
      "O            -     .....oO3333*********##******          Oo......O",    
      "O            -    ......oO3333********OOO********        Oo..... O",
      "O            -   .......oO3333*******OOOO*********    OOOOo..... O", 
      "O            -    ......oOOOOOO*****ooooo*********OOOOOoooo....  O", #20
      "O            -     .....ooooooO*****ooooo*****OOOOOooooooo.....  O",
      "O            -      ........ooO ***...... OOOOOooooooooo......   O",
      "O            -       ........oOOOO.......OOoooooooooo........    O",
      "O            -          ......oooo.......oo...............       O",
      "O            -            ..........................             O",
      "O            -               ..................                  O",
      "O            -                ...............                    O",
      "O            -                                                   O",
      "O            --------------------------                          O",
      "O                                     -                          O", #30
      "O                                     -                          O",
      "O                                     -                          O",
      "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO"  #33
    )








  if (MapLevel == 2):
    
    DinnerPlate = cf.VirusWorld(name='TheCave2',
                               width        = 66, #we want the playfield to be 1 pixel larger on all sides than the display
                               height       = 34,
                               Map          = [[]],
                               Playfield    = [[]],
                               CurrentRoomH = 1,
                               CurrentRoomV = 1,
                               DisplayH     = 1,
                               DisplayV     = 1,
                               mutationrate = mutationrate,
                               replicationrate = gv.replicationrate,
                               mutationdeathrate = mutationdeathrate,
                               VirusStartSpeed = gv.VirusStartSpeed)



  # TheMap.map= (
    # #0         1  .......2.........3.........4.........5.........6....65    
    # "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO", #0  
    # "O                                                                O",
    # "O                                                                O",
    # "O                                                                O",
    # "O                                                                O",
    # "O                                                                O",
    # "O                                                                O",
    # "O                                                                O",
    # "O                                                                O", 
    # "O                                                                O", 
    # "O                                                                O", #10
    # "O                                                                O",
    # "O                                                                O",
    # "O                                                                O",
    # "O                                                                O",
    # "O                                                                O",
    # "O                                                                O",
    # "O                                                                O",    
    # "O                                                                O",
    # "O                                                                O", 
    # "O                                                                O", #20
    # "O                                                                O",
    # "O                                                                O",
    # "O                                                                O",
    # "O                                                                O",
    # "O                                                                O",
    # "O                                                                O",
    # "O                                                                O",
    # "O                                                                O",
    # "O                                                                O",
    # "O                                                                O", #30
    # "O                                                                O",
    # "O                                                                O",
    # "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO"  #33
  # )

    TheMap.ColorList['*']  =  (0,0,20)

    TheMap.map= (
      #0         1  .......2.........3.........4.........5.........6....65    
      "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO", #0  
      "O            ....................................................O",
      "O            ..........................oooooo....................O",
      "O            .....oooooo..............oOOOOOOoo..................O",
      "O            ....oOOOOOOo............oOO22222OOoo................O",
      "O            ..ooO1*****Oo...........oO********OOoo..............O",
      "O            ..oO11*****OooooooooooooOO*********3OOo.............O",
      "O            ..oO1*******************************3Oo.............O",
      "O            ...oO1*****OooooooooooO*************3Oo.............O",
      "O            ....oOOOOOOo.........oO*************3Oo.............O",
      "O            .....oooooo...........oO444*********3Oo.............O", #10
      "O            ......................oO444*********3Oo.............O",
      "O            .......................oOOOO*******3Oo..............O",
      "O            ..oooooooo..............ooooOOO**OOOo...............O",
      "O            .ooOOOOOOOo.................ooO**Ooo................O",
      "O            ooO5555555Oo.................oO**Oo.....ooooo.......O",
      "O            oO555555***Oo................oO**Oo....oOOOOOo......O",
      "O            oO555*******Oo...............oO**Oo...oO*****Ooo....O",
      "O            oO55********Oo...............oO**Oo..oO*******OOo...O",
      "O            oO55********Oo...............oO**Oo.oO*********Oo...O",
      "O            oO**********Oo...............oO**Oo.oO*********Oo...O", #20
      "O            .oO**********Oo.........oooooOO**Oo.oO*********Oo...O",
      "O            ..oO***6******Oo....ooooOOOOOOO..OoooO*********Oo...O",
      "O            ...oOOO6*******OooooOOOOO**********************Oo...O",
      "O            ....oooO6*******OOOOO**************************Oo...O",
      "O            .......oO66************************************Oo...O",
      "O            ........oO666666*****************************88Oo...O",
      "O            .........oOOOOOO***************************888OOo...O",
      "O            ..........ooooooOO**********************8888OOoo....O",
      "O            ................ooO777777777777**88888888OOOoo......O",
      "O            ..................oOOOOOOOOOOOOOOOOOOOOOOOoo........O", #30
      "O            ...................ooooooooooooooooooooooo..........O",
      "O            ....................................................O",
      "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO"  #33
    )



  if (MapLevel == 3):
    
    DinnerPlate = cf.VirusWorld(name='BigFood',
                               width        = 66, #we want the playfield to be 1 pixel larger on all sides than the display
                               height       = 34,
                               Map          = [[]],
                               Playfield    = [[]],
                               CurrentRoomH = 1,
                               CurrentRoomV = 1,
                               DisplayH     = 1,
                               DisplayV     = 1,
                               mutationrate = mutationrate,
                               replicationrate = gv.replicationrate,
                               mutationdeathrate = mutationdeathrate,
                               VirusStartSpeed = gv.VirusStartSpeed)



    TheMap.ColorList['*']  =  (25,0,0)

    TheMap.map= (
      #0         1   ......2.........3.........4.........5.........6....65    
      "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO", #0  
      "O            --                                                  O",
      "O            --                                                  O",
      "O            --                                  ...             O",
      "O            --                   *           ....o....          O",
      "O            --                  *.*          ..ooOoo..          O",
      "O            --                 *.o.*        ...oO@Oo...         O",
      "O            --               *..ooo..*      ..oO@#@Oo..         O",
      "O            --              *..ooooo...*    ...oO@Oo...         O", 
      "O            --             *.ooooooooo.*     ..ooOoo..          O", 
      "O            --             *.oOOOOOOOo.*     ....o....          O", #10
      "O            --             *.oO@@@@@Oo.*        ...             O",
      "O            --             *.ooooooooo.*                        O",
      "O            --             *************                        O",
      "O            --             *.ooooooooo.*          8             O",
      "O            --             *.oO@@@@@Oo.*         8.8            O",
      "O            --             *.oOOOOOOOo.*        8ooo8           O",
      "O            --             *.ooooooooo.*       8OOOOO8          O",    
      "O            --             *...ooooo...*      8@@@@@@@8         O",
      "O            --               *..ooo..*       8#########8        O", 
      "O            --                 *.o.*          8@@@@@@@8         O", #20
      "O            --                  *.*            8OOOOO8          O",
      "O            --              ...  *              8ooo8           O",
      "O            --             .ooo.                 8.8            O",
      "O            --            .oOOOo.                 8             O",
      "O            --           .oO@@@Oo.                              O",
      "O            --          .oO@###@Oo.                             O",
      "O            --           .oO@@@Oo.                              O",
      "O            --            .oOOOo.                               O",
      "O            --             .ooo.                                O",
      "O            --              ...                                 O", #30
      "O            --                                                  O",
      "O                                                                O",
      "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO"  #33
    )





  if (MapLevel == 4):
    
    DinnerPlate = cf.VirusWorld(name='BigFood',
                               width        = 66, #we want the playfield to be 1 pixel larger on all sides than the display
                               height       = 34,
                               Map          = [[]],
                               Playfield    = [[]],
                               CurrentRoomH = 1,
                               CurrentRoomV = 1,
                               DisplayH     = 1,
                               DisplayV     = 1,
                               mutationrate = mutationrate,
                               replicationrate = gv.replicationrate,
                               mutationdeathrate = mutationdeathrate,
                               VirusStartSpeed = gv.VirusStartSpeed)

    DinnerPlate.walllives = random.randint(1,25) 
    TheMap.ColorList['*']  =  (5,5,5)

    TheMap.map= (
      #0         1   ......2.........3.........4.........5.........6....65    
      "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO", #0  
      "O            --**************************************************O",
      "O            --**************************************************O",
      "O            --**********************....************************O",
      "O            --**********************....************************O",
      "O            --**********************....************************O",
      "O            --**********************....************************O",
      "O            --**********************....************************O",
      "O            --****************................******************O",
      "O            --****************................******************O",
      "O            --****************................******************O", #10
      "O            --****************................******************O",
      "O            --**********************....************************O",
      "O            --**********************....************************O",
      "O            --**********************....************************O",
      "O            --**********************....************************O",
      "O            --**********************....************************O",
      "O            --**********************....************************O",
      "O            --**********************....************************O",
      "O            --**********************....************************O",
      "O            --**********************....************************O", #20
      "O            --**********************....************************O",
      "O            --**********************....************************O",
      "O            --**********************....************************O",
      "O            --**********************....************************O",
      "O            --**********************....************************O",
      "O            --**********************....************************O",
      "O            --**************************************************O",
      "O            --**************************************************O",
      "O            --**************************************************O",
      "O            --**************************************************O", #30
      "O            --**************************************************O",
      "O            --**************************************************O",
      "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO"  #33
    )

  

  
  if (MapLevel == 5):
    
    DinnerPlate = cf.VirusWorld(name='BigFood',
                               width        = 66, #we want the playfield to be 1 pixel larger on all sides than the display
                               height       = 34,
                               Map          = [[]],
                               Playfield    = [[]],
                               CurrentRoomH = 1,
                               CurrentRoomV = 1,
                               DisplayH     = 1,
                               DisplayV     = 1,
                               mutationrate = mutationrate,
                               replicationrate = gv.replicationrate,
                               mutationdeathrate = mutationdeathrate,
                               VirusStartSpeed = gv.VirusStartSpeed)

    DinnerPlate.walllives = random.randint(1,25) 
    TheMap.ColorList['.']  =  (0,10,0)
    TheMap.ColorList['*']  =  (0,10,0)

    TheMap.map= (
      #0         1   ......2.........3.........4.........5.........6....65    
      "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO", #0  
      "O            --**************************************************O",
      "O            --**************************************************O",
      "O            --**************************************************O",
      "O            --**************************************************O",
      "O            --**************************************************O",
      "O            --**************************************************O",
      "O            --**************************************************O",
      "O            --**************************************************O",
      "O            --**************************************************O",
      "O            --**************************************************O", #10
      "O            --**************************************************O",
      "O            --**************************************.***********O",
      "O            --*************************************...**********O",
      "O            --************************************.....*********O",
      "O            --***********************************.......********O",
      "O            --*****************.****************.........*******O",
      "O            --****************...**************...........******O",
      "O            --***************.....************.............*****O",
      "O            --**************.......**********...............****O",
      "O            --*************.........********.................***O", #20
      "O            --************...........******...................**O",
      "O            --***********.............****.....................*O",
      "O            --**********...............**.......................O",
      "O            --*********.........................................O",
      "O            --********..........................................O",
      "O            --*******...........................................O",
      "O            --**************************************************O",
      "O            --**************************************************O",
      "O            --**************************************************O",
      "O            --**************************************************O", #30
      "O            --**************************************************O",
      "O            --**************************************************O",
      "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO"  #33
    )


  if (MapLevel == 6):
    DinnerPlate = cf.VirusWorld(name='BigFood',
                               width        = 66, #we want the playfield to be 1 pixel larger on all sides than the display
                               height       = 34,
                               Map          = [[]],
                               Playfield    = [[]],
                               CurrentRoomH = 1,
                               CurrentRoomV = 1,
                               DisplayH     = 1,
                               DisplayV     = 1,
                               mutationrate = mutationrate,
                               replicationrate = gv.replicationrate,
                               mutationdeathrate = mutationdeathrate,
                               VirusStartSpeed = gv.VirusStartSpeed)

    DinnerPlate.walllives = random.randint(1,25) 
    TheMap.ColorList['*']  =  (0,15,0)

    TheMap.map= (
      #0         1   ......2.........3.........4.........5.........6....65    
      "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO", #0  
      "O            --**************************************************O",
      "O            --**************************************************O",
      "O            --**************************************************O",
      "O            --********************************.oO***************O",
      "O            --********************O***********.oO****........***O",
      "O            --*******************OoO**********.oO****.ooooooo***O",
      "O            --******************Oo.oO*********.oO****.oOOOOOO***O",
      "O            --*****************Oo.3.oO********.oO****.oO********O",
      "O            --****************Oo.333.oO*******.oO****.oO********O",
      "O            --***************Oo.33333.oO******.oO****.oO********O", #10
      "O            --**************Oo.........oO*****.oO****.oO********O",
      "O            --*************OoooooooooooooO****.oO****.oO********O",
      "O            --************OOOOOOOOOOOOOOOO****.oO***************O",
      "O            --********************************.oO***************O",
      "O            --********************************.oO***************O",
      "O            --*****************OOO************.oO***************O",
      "O            --****************Oo..************.oO*****.oO*******O",
      "O            --***************Oo..*************.oO*****.oO*******O",
      "O            --**************Oo..**************.oO*****.oO*******O",
      "O            --*************Oo..................oO*****.oO*******O", #20
      "O            --*************OooooooooooooooooooooO*****.oO*******O",
      "O            --**************OOOOOOOOOOOOOOOOOOOOO*****.oO*******O",
      "O            --****************************************.oO*******O",
      "O            --****************************************.oO*******O",
      "O            --******************************Oo.*******.oO*******O",
      "O            --******************************Oo.........oO*******O",
      "O            --******************************OoooooooooooO*******O",
      "O            --******************************OOOOOOOOOOOOO*******O",
      "O            --**************************************************O",
      "O            --**************************************************O", #30
      "O            --**************************************************O",
      "O            --**************************************************O",
      "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO"  #33
    )



  if (MapLevel == 7):
    DinnerPlate = cf.VirusWorld(name='BigFood',
                               width        = 66, #we want the playfield to be 1 pixel larger on all sides than the display
                               height       = 34,
                               Map          = [[]],
                               Playfield    = [[]],
                               CurrentRoomH = 1,
                               CurrentRoomV = 1,
                               DisplayH     = 1,
                               DisplayV     = 1,
                               mutationrate = mutationrate,
                               replicationrate = gv.replicationrate,
                               mutationdeathrate = mutationdeathrate,
                               VirusStartSpeed = gv.VirusStartSpeed)

    DinnerPlate.walllives = random.randint(1,25) 
    TheMap.ColorList['*']  =  (10,0,10)

    TheMap.map= (
      #0         1   ......2.........3.........4.........5.........6....65    
      "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO", #0  
      "O            --**************************************************O",
      "O            --*******OOOOOOOOOOOOOO*********OOOOOOOOOOOOOOOOO***O",
      "O            --******oOooooooooooooO********oOoooooooooooooooO***O",
      "O            --*****.oO...........oOOOOOOOOOOO..............oO***O",
      "O            --*****.oO**********.ooooooooooo**************.oO***O",
      "O            --*****.oO**********...........***************.oO***O",
      "O            --*****.oO************************************.oO***O",
      "O            --*****.oO************************************.oO***O",
      "O            --*****.oO**************OOOOOOOOO*************.oO***O",
      "O            --*****.oO*************oOoooooooO*************.oO***O", #10
      "O            --*****.oO************.oO......oO*************.oO***O",
      "O            --*****.oO************.oO*****.oOOOOOOOOOOOOOOOOO***O",
      "O            --*****.oO************.oO*****.ooooooooooooooooo****O",
      "O            --*****.oO************.oO*****.................*****O",
      "O            --*****.oO************.oO***************************O",
      "O            --*****.oO************.oO***************************O",
      "O            --*****.oOOOOO***OOOOOOOO***************************O",
      "O            --*****.ooooo***oooooooo****************************O",
      "O            --*****.....***........*****************************O",
      "O            --**************************************************O", #20
      "O            --**************************************************O",
      "O            --*****************************OOOO**OOOO***********O",
      "O            --****************************oOoo**ooooO***********O",
      "O            --***************************.oO.**....oO***********O",
      "O            --***************************.oO******.oO***********O",
      "O            --***************************.oOOOOOOOOOO***********O",
      "O            --***************************.oooooooooo************O",
      "O            --***************************..........*************O",
      "O            --**************************************************O",
      "O            --**************************************************O", #30
      "O            --**************************************************O",
      "O            --**************************************************O",
      "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO"  #33
    )

  if (MapLevel == 8):
    DinnerPlate = cf.VirusWorld(name='BigFood',
                               width        = 66, #we want the playfield to be 1 pixel larger on all sides than the display
                               height       = 34,
                               Map          = [[]],
                               Playfield    = [[]],
                               CurrentRoomH = 1,
                               CurrentRoomV = 1,
                               DisplayH     = 1,
                               DisplayV     = 1,
                               mutationrate = mutationrate,
                               replicationrate = gv.replicationrate,
                               mutationdeathrate = mutationdeathrate,
                               VirusStartSpeed = gv.VirusStartSpeed)

    DinnerPlate.walllives = random.randint(1,25) 
    TheMap.ColorList['*']  =  (15,0,0)

    TheMap.map= (
      #0         1   ......2.........3.........4.........5.........6....65    
      "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO", #0  
      "O            --**************************************************O",
      "O            --**************************************************O",
      "O            --**************************************************O",
      "O            --**************************************************O",
      "O            --**************************************************O",
      "O            --**************************************************O",
      "O            --**************************************************O",
      "O            --**************************************************O",
      "O            --**************************************************O",
      "O            --**************************************************O", #10
      "O            --**************************************************O",
      "O            --**************************************************O",
      "O            --**************************************************O",
      "O            --**************************************************O",
      "O            --**************************************************O",
      "O            --**************************************************O",
      "O            --**************************************************O",
      "O            --**************************************************O",
      "O            --**************************************************O",
      "O            --**************************************************O", #20
      "O            --**************************************************O",
      "O            --**************************************************O",
      "O            --**************************************************O",
      "O            --**************************************************O",
      "O            --**************************************************O",
      "O            --**************************************************O",
      "O            --**************************************************O",
      "O            --**************************************************O",
      "O            --**************************************************O",
      "O            --**************************************************O", #30
      "O            --**************************************************O",
      "O            --**************************************************O",
      "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO"  #33
    )



  DinnerPlate.CopyTextMapToPlayfield(TheMap)

  #we add random viruses to a plate of big food
  if(DinnerPlate.name == 'BigFood'):
    DinnerPlate.AddRandomVirusesToPlayfield(random.randint(1,gv.MaxRandomViruses))

  return DinnerPlate;



def FlashAllViruses(Viruses,VirusCount,DinnerPlate,CameraH,CameraV):
  x = 0
  r = 0
  g = 0
  b = 0
  highcolor = 0
  count = 0
  increment = 50
  H = 0
  V = 0
  name = ""

  for x in range (0,VirusCount):
    highcolor = max(DinnerPlate.Viruses[x].r, DinnerPlate.Viruses[x].g, DinnerPlate.Viruses[x].b)
    while (DinnerPlate.Viruses[x].r < 255  and DinnerPlate.Viruses[x].g < 255 and DinnerPlate.Viruses[x].b < 255):
      if (DinnerPlate.Viruses[x].r == highcolor):
        DinnerPlate.Viruses[x].r = min(255,DinnerPlate.Viruses[x].r + increment)
      elif (DinnerPlate.Viruses[x].g == highcolor):
        DinnerPlate.Viruses[x].g = min(255,DinnerPlate.Viruses[x].g + increment)
      elif (DinnerPlate.Viruses[x].b == highcolor):
        DinnerPlate.Viruses[x].b = min(255,DinnerPlate.Viruses[x].b + increment)

      highcolor = highcolor + increment

      #setpixel(DinnerPlate.Viruses[x].h,DinnerPlate.Viruses[x].v,DinnerPlate.Viruses[x].r,DinnerPlate.Viruses[x].g,DinnerPlate.Viruses[x].b)
      #unicorn.show()
      #time.sleep(0.01)
      
    DinnerPlate.DisplayWindow(CameraH,CameraV)
    #unicorn.show()



#-----------------------------
# Outbreak Global Variables --
#-----------------------------
InstabilityFactor = 50
ScrollSpeedLong   = 500
ScrollSpeedShort  = 5
MinBright         = 100
MaxBright         = 255


ScrollSpeedLong   = ScrollSpeedLong  * gv.CPUModifier
ScrollSpeedShort  = ScrollSpeedShort * gv.CPUModifier

    


def PlayOutbreak():      
 
  global mutationrate 
  global mutationdeathrate
  global OriginalMutationRate
  global OriginalReplicationRate
  global OriginalMutationDeathRate
  global VirusMoves
  global ClumpingSpeed
  global ReplicationSpeed
  global FreakoutReplicationRate
  global FreakoutMoves
  global MaxVirusMoves


  replicationrate   = gv.OriginalReplicationRate
  mutationrate      = gv.OriginalMutationRate
  mutationdeathrate = gv.OriginalMutationDeathRate


  finished      = 'N'
  gv.VirusMoves = 0
  LevelCount    = 0
  MaxLevel      = 8 #number of available mazes
  NameCount     = 0
  Viruses       = []
  VirusCount    = 0
  Virus         = cf.EmptyObject('EmptyObject')
  VirusDeleted        = 0
  DominanceCount      = 0
  ClockSprite         = cf.CreateClockSprite(12)
  DayOfWeekSprite     = cf.CreateDayOfWeekSprite()
  MonthSprite         = cf.CreateMonthSprite()
  DayOfMonthSprite    = cf.CreateDayOfMonthSprite()
  CurrencySprite      = CreateCurrencySprite()

  ClockSprite.on      = 0
  StrainCreated       = 0
  OldVirusTopSpeed    = gv.VirusTopSpeed
  OldVirusBottomSpeed = gv.VirusBottomSpeed
  NextMaze            = False  #Used to indicate if we skip to the next maze (keyboard input 'n')
  BigFoodAlive        = False

  #PathCount     = len(CameraPath)
  PathPosition  = 0
  PositionSpeed = 100

  CameraDirection = 0
  CameraSpeed     = 5
  VirusesInWindow = 0
  
  #CameraH, CameraV, CameraSpeed = CameraPath[0]
  
  cf.ShowGlowingText(CenterHoriz = True,h = -8,v = 1,   Text = 'UTBR8K', RGB = cf.HighOrange, ShadowRGB = cf.ShadowOrange, ZoomFactor = 8,GlowLevels=0,DropShadow=False)
  gv.TheMatrix.Clear()
  cf.ShowGlowingText(CenterHoriz = True,h = -8,v = 1,   Text = 'UTBR8K', RGB = cf.HighOrange, ShadowRGB = cf.ShadowOrange, ZoomFactor = 7,GlowLevels=0,DropShadow=False)
  gv.TheMatrix.Clear()
  cf.ShowGlowingText(CenterHoriz = True,h = -8,v = 1,   Text = 'UTBR8K', RGB = cf.HighOrange, ShadowRGB = cf.ShadowOrange, ZoomFactor = 6,GlowLevels=0,DropShadow=False)
  gv.TheMatrix.Clear()
  cf.ShowGlowingText(CenterHoriz = True,h = -8,v = 1,   Text = 'UTBR8K', RGB = cf.HighOrange, ShadowRGB = cf.ShadowOrange, ZoomFactor = 5,GlowLevels=0,DropShadow=False)
  gv.TheMatrix.Clear()
  cf.ShowGlowingText(CenterHoriz = True,h = -8,v = 1,   Text = 'UTBR8K', RGB = cf.HighOrange, ShadowRGB = cf.ShadowOrange, ZoomFactor = 4,GlowLevels=0,DropShadow=False)
  gv.TheMatrix.Clear()
  cf.ShowGlowingText(CenterHoriz = True,h = -8,v = 1,   Text = 'UTBR8K', RGB = cf.HighOrange, ShadowRGB = cf.ShadowOrange, ZoomFactor = 3,GlowLevels=0,DropShadow=False)

  gv.TheMatrix.Clear()
  cf.ClearBuffers()
  cf.ShowGlowingText(CenterHoriz = True,h = 0 ,v = 1,   Text = 'UTBR8K',      RGB = cf.HighYellow, ShadowRGB = cf.ShadowYellow, ZoomFactor = 2,GlowLevels=50, DropShadow=True)
  cf.ShowGlowingText(CenterHoriz = True,h = 0 ,v = 16,  Text = 'A VIRUS GAME',RGB = cf.HighRed,    ShadowRGB = cf.ShadowRed,    ZoomFactor = 1,GlowLevels=200,DropShadow=True)
  cf.ShowGlowingText(CenterHoriz = True,h = 0 ,v = 26,  Text = 'BY DATAGOD',  RGB = cf.HighGreen,  ShadowRGB = cf.ShadowGreen, ZoomFactor = 1,GlowLevels=100,FadeLevels=50,DropShadow=True)
  
  ThreeGhostPacSprite.ScrollAcrossScreen(0,26,'right',gv.ScrollSleep)
  ThreeBlueGhostPacSprite.ScrollAcrossScreen(gv.HatWidth,26,'left',gv.ScrollSleep)
  gv.TheMatrix.Clear()
  gv.Canvas.Clear()
  cf.ZoomScreen(gv.ScreenArray,32,1,0,Fade=True)
  time.sleep(1)
  gv.TheMatrix.Clear()







  #The map is an array of a lists.  You can address each element has VH e.g. [V][H]
  #Copying the map to the playfield needs to follow the exact same shape

  #----------------------
  #-- Prepare Level    --
  #----------------------
  cf.SaveConfigData()

  LevelCount = random.randint(1,MaxLevel)

  DinnerPlate = CreateDinnerPlate(LevelCount)


  VirusCount = len(DinnerPlate.Viruses)
  print("VirusCount: ",VirusCount)
  DominanceCount = 0
  CameraH        = DinnerPlate.DisplayH
  CameraV        = DinnerPlate.DisplayV

  print ("CameraHV: ",CameraH, CameraV)

  #af.ShowScrollingBanner("Outbreak!",cf.SDLowYellowR,cf.SDLowYellowG,cf.SDLowYellowB,gv.ScrollSleep *0.8)
  #DinnerPlate.DisplayWindowZoom(CameraH,CameraV,2,16,0.025)
  
  

  #--------------------------------
  #-- Main timing loop           --
  #--------------------------------

  NameCount = 1




  

  #Show Custom sprites
  DinnerPlate.CopySpriteToPlayfield(ClockSprite,      gv.ClockH +1,      gv.ClockV+1,      gv.ClockRGB,       ObjectType = 'Wall',  Filler = 'DarkWall')
  DinnerPlate.CopySpriteToPlayfield(DayOfWeekSprite,  gv.DayOfWeekH +1,  gv.DayOfWeekV+1,  gv.DayOfWeekRGB,   ObjectType = 'Wall',  Filler = 'DarkWall')
  DinnerPlate.CopySpriteToPlayfield(MonthSprite,      gv.MonthH +1,      gv.MonthV+1,      gv.MonthRGB,       ObjectType = 'Wall',  Filler = 'DarkWall')
  DinnerPlate.CopySpriteToPlayfield(DayOfMonthSprite, gv.DayOfMonthH +1, gv.DayOfMonthV+1, gv.DayOfMonthRGB , ObjectType = 'Wall',  Filler = 'DarkWall')
  DinnerPlate.CopySpriteToPlayfield(CurrencySprite,   gv.CurrencyH+1,   gv.CurrencyV+1,   gv.CurrencyRGB,    ObjectType = 'Wall',  Filler = 'DarkWall')



  #Zoom out, just a little bit too much then zoom back in.  Nice effect.
  DinnerPlate.DisplayWindowZoom(CameraH,CameraV,2,96,0)
  DinnerPlate.DisplayWindowZoom(CameraH,CameraV,96,32,0)



  while (finished == "N" and gv.VirusMoves < gv.MaxVirusMoves):
    gv.VirusMoves = gv.VirusMoves + 1
    
    #We will increase bottome speed X times over the course of a full game
    #OldVirusTopSpeed is the maximum speed we want to use no matter what
    m,r = divmod(gv.VirusMoves, (gv.MaxVirusMoves / gv.SpeedIncrements))
    if (r == 0):
      gv.VirusBottomSpeed = gv.VirusBottomSpeed -1
      gv.VirusTopSpeed    = gv.VirusTopSpeed -1
      if (gv.VirusTopSpeed < OldVirusTopSpeed):
        gv.VirusTopSpeed = OldVirusTopSpeed
      if (gv.VirusBottomSpeed < OldVirusTopSpeed):
        gv.VirusBottomSpeed = OldVirusTopSpeed

    #--------------------------------
    #Check for keyboard input      --
    #--------------------------------
    #If we do this too often, the terminal window (if using telnet) will flicker  (now been fixed, see cf.PollKeyboard function)
    m,r = divmod(gv.VirusMoves,KeyboardSpeed)
    if (r == 0):
      Key = cf.PollKeyboard()
      ProcessKeypress(Key)

      if (Key == 'q'):
        LevelFinished = 'Y'
        Finished      = 'Y'
        return
      elif (Key == 'm'):
        DinnerPlate.DebugPlayfield()
      elif (Key == 'n'):
        #skip to next maze
        NextMaze = True


      #update text window
      print ("Moves:",gv.VirusMoves," VirusCount:",VirusCount,"NameCount:",NameCount," gv.VirusTopSpeed:",gv.VirusTopSpeed," gv.VirusBottomSpeed:",gv.VirusBottomSpeed,"      ",end="\r")      


    

    #--------------------------------
    #-- Virus actions              --
    #--------------------------------

    firstname = DinnerPlate.Viruses[0].name
    NameCount = 1
    
        
    #It seems that Python determines the "VirusCount-1" value once, and does not re-evaluate.  When some of the virises die, 
    #this thorws off the loop and counts.  I will deal with this internally.
    #for x in range (0,VirusCount-1):

    #Changed the for loop to a while loop
    x = 0
    while (x < VirusCount):
      VirusDeleted = 0
      #Viruses freakout when near the end of max moves
      if (gv.VirusMoves == gv.FreakoutMoves):
        DinnerPlate.Viruses[x].replicationrate = gv.FreakoutReplicationRate


      #-------------------------
      #-- Check for dominance --  
      #-------------------------
      if (DinnerPlate.Viruses[x].name != firstname):
        NameCount = NameCount + 1

      
      #----------------------
      #-- Movement         --  
      #----------------------
      #print ("Speed:",DinnerPlate.Viruses[x].speed)
      m,r = divmod(gv.VirusMoves,DinnerPlate.Viruses[x].speed)
      if (r == 0):
        #print ("Virus name alive x:",DinnerPlate.Viruses[x].name,DinnerPlate.Viruses[x].alive,x)
        if (DinnerPlate.Viruses[x].alive == 1):
          MoveVirus(DinnerPlate.Viruses[x],DinnerPlate.Playfield)
        
      #After a move, we need to see if it is still alive, becaus a lot of things could have happened
      if (DinnerPlate.Viruses[x].alive == 0):
          #print ("Removing virus from the list: ",x)
          #print ("VirusCount:",VirusCount)
        VirusDeleted = 1
        DinnerPlate.Playfield[(DinnerPlate.Viruses[x].v)][(DinnerPlate.Viruses[x].h)] = cf.EmptyObject('EmptyObject')
        #DinnerPlate.Viruses[x] = cf.EmptyObject('EmptyObject')
        del DinnerPlate.Viruses[x]
        VirusCount = VirusCount -1
          


  
      #if virus not deleted, replicate
      if (VirusDeleted == 0):
        #----------------------
        #-- Replication      --  
        #----------------------
        #check virus internal replication rate, or if only one type of virus left check
        #the main rate as an override
        if ((random.randint(0,DinnerPlate.Viruses[x].replicationrate) == 1) or (VirusCount == 1 and (random.randint(0,replicationrate) == 1))):
          Virus = ReplicateVirus(DinnerPlate.Viruses[x],DinnerPlate)
          if (Virus.name != 'EmptyObject'):
            #print("Virus replicated")
            DinnerPlate.Viruses.append(Virus)
            VirusCount = len(DinnerPlate.Viruses)



        #-------------------------------
        #-- Move towards food         --
        #-------------------------------
        #
        if (random.randint(1,gv.ChanceOfHeadingToFood) == 1):
          #print("Chance to move towards food")
          FoodH = 0
          FoodV = 0
          FoodH,FoodV = DinnerPlate.FindClosestObject(
            SourceH    = DinnerPlate.Viruses[x].h,
            SourceV    = DinnerPlate.Viruses[x].v,
            Radius     = gv.FoodCheckRadius,
            ObjectType = 'WallBreakable' 
          )

          #print("Closest Object: ",FoodH, FoodV,"                    ")
          
          if (cf.CheckBoundary(FoodH,FoodV) == 0):
            #print("Move Towards food: ",FoodH, FoodV,"                    ")
            DinnerPlate.Viruses[x].direction = cf.PointTowardsObject8Way(DinnerPlate.Viruses[x].h,DinnerPlate.Viruses[x].v,FoodH,FoodV)



      #----------------------
      #-- Random Death     --  
      #----------------------
      #check virus internal death rate
      if (VirusDeleted == 0):

        #Too many strains?  Kick them in the butt.  Greater chance of dying, then reset
        if ((random.randint(0,DinnerPlate.Viruses[x].chanceofdying) == 1)):
          DinnerPlate.Viruses[x].alive = 0
          DinnerPlate.Viruses[x].lives = 0
          DinnerPlate.Viruses[x] = cf.EmptyObject('EmptyObject')
          del DinnerPlate.Viruses[x]
          VirusCount = VirusCount -1
          #print ("VirusCount:",VirusCount)
          VirusDeleted = 1


        else:
          if(NameCount >= gv.VirusNameSpeedupCount):
            DinnerPlate.Viruses[x].chanceofdying = gv.GreatChanceOfDying
            DinnerPlate.Viruses[x].chanceofdying = gv.ChanceOfDying




          




      #---------------------------
      #-- End Virus loop        --
      #---------------------------
      x = x + 1
      

      

      # #-------------------------------
      # #-- Move towards random spot  --
      # #-------------------------------
      # #
      # if (random.randint(1,gv.ChanceOfHeadingToHV) == 1):
        # RandomH = random.randint(0,DinnerPlate.width)
        # RandomV = random.randint(0,DinnerPlate.height)

        # for x in range(0,VirusCount):
          # #Center
          # #DinnerPlate.Viruses[x].direction = cf.PointTowardsObject8Way(DinnerPlate.Viruses[x].h,DinnerPlate.Viruses[x].v,(DinnerPlate.width/2),(DinnerPlate.height/2))

          # DinnerPlate.Viruses[x].direction = cf.PointTowardsObject8Way(DinnerPlate.Viruses[x].h,DinnerPlate.Viruses[x].v,RandomH,RandomV)
          # #DinnerPlate.Viruses[x].AdjustSpeed(10) 
          # DinnerPlate.Viruses[x].eating = 0
          # DinnerPlate.Viruses[x].clumping = True
          
        # print("Move Towards: ",RandomH,RandomV)



      #-------------------------------------------------
      #-- Random food appears!                        --
      #-------------------------------------------------
     
      #Point viruses towards the food
      if (random.randint(1,gv.ChanceOfRandomFood) == 1 and BigFoodAlive == False):
        BigFoodH,BigFoodV = 0,0
        r,g,b = gv.BigFoodRGB
        FreeSpotFound = False
        Tries         = 0
        
        while (FreeSpotFound == False and Tries <= 20):
          Tries = Tries + 1
          BigFoodH = random.randint(20,gv.HatWidth)
          BigFoodV = random.randint(5,gv.HatHeight - 8)

          if (DinnerPlate.Playfield[BigFoodV][BigFoodH].name == 'EmptyObject'):
            FreeSpotFound = True
            DinnerPlate.Playfield[BigFoodV][BigFoodH] = cf.Wall(BigFoodH,BigFoodV,r,g,b,1,gv.BigFoodLives,'WallBreakable')
            print ("Random food appears:",BigFoodH,BigFoodV)
            for x in range(0,VirusCount):
              DinnerPlate.Viruses[x].direction = cf.PointTowardsObject8Way(DinnerPlate.Viruses[x].h,DinnerPlate.Viruses[x].v,BigFoodH,BigFoodV)
              DinnerPlate.Viruses[x].AdjustSpeed(-1) 
              DinnerPlate.Viruses[x].eating = 0
              DinnerPlate.Viruses[x].clumping = True

              BigFoodAlive = True
      #if the big food is alive, we check to see if the spot is still occupied.  
      #If it is, turn all viruses towardsit
      if (BigFoodAlive == True and random.randint(1,50) == 1):
        if (DinnerPlate.Playfield[BigFoodV][BigFoodH].name == 'WallBreakable'):
            for x in range(0,VirusCount):
              DinnerPlate.Viruses[x].direction = cf.PointTowardsObject8Way(DinnerPlate.Viruses[x].h,DinnerPlate.Viruses[x].v,BigFoodH,BigFoodV)
              DinnerPlate.Viruses[x].AdjustSpeed(-5) 
              DinnerPlate.Viruses[x].eating = 0
              DinnerPlate.Viruses[x].clumping = False
        else:
          BigFoodAlive = False

      #-------------------------------------------------
      #-- Adjust parameters if too many viruses alive --
      #-------------------------------------------------

      #if too many virus strains, increase speed
      #otherwise reset to original speeds
      if(NameCount >= gv.VirusNameSpeedupCount):
        gv.VirusTopSpeed    = OldVirusTopSpeed
        gv.VirusBottomSpeed = OldVirusTopSpeed
        mutationdeathrate   = 1

    
    #----------------------
    #-- Audit Playfield  --  
    #----------------------
    #There seems to be a bug where an old dead virus is still on the playfield.
    #We will check periodically and remove them
    m,r = divmod(gv.VirusMoves,gv.AuditSpeed)
    if(r == 0):
      #DinnerPlate.DebugPlayfield()
      for v in range(0,DinnerPlate.height):
        for h in range(0,DinnerPlate.width):
          if (DinnerPlate.Playfield[v][h].alive == 0 and DinnerPlate.Playfield[v][h].name != 'EmptyObject'):
            DinnerPlate.Playfield[v][h] = cf.EmptyObject('EmptyObject')
            #print('Zombie detected:',v,h,DinnerPlate.Playfield[v][h].name)

















    #-------------------------------------------
    #-- Level ends when one virus dominates   --
    #-------------------------------------------
  
    if (NameCount == 1 or NextMaze == True):
      #Erase clock if present
      #DinnerPlate.DisplayWindow(CameraH, CameraV)
      DominanceCount = DominanceCount + 1
      #print ("NameCount:",NameCount,"DominanceCount:",DominanceCount,"DominanceMaxCount:",DominanceMaxCount)
     
      #one virus remains, increase chance of spreading
      replicationrate   = 1
      mutationdeathrate = mutationdeathrate * 25
      
      



      
      #This particular virus is a successful strain, we want to collect it to the center
      #Point viruses towards the center
      # if (StrainCreated == 0):
        # for x in range(0,VirusCount):
          # DinnerPlate.Viruses[x].direction = cf.PointTowardsObject8Way(DinnerPlate.Viruses[x].h,DinnerPlate.Viruses[x].v,(DinnerPlate.width/2),(DinnerPlate.height/2))
          # StrainCreated == 1

          

      #print ("DominanceCount:",DominanceCount,"DominanceMaxCount:",DominanceMaxCount,"VirusCount:",VirusCount,"gv.VirusMaxCount:",gv.VirusMaxCount)
      #if one virus dominates for X ticks, reset and load next level
      if (DominanceCount >= gv.DominanceMaxCount) or(VirusCount >= gv.VirusMaxCount) or (NextMaze == True):
        print ("VirusCount:",VirusCount)
        #print ("Flashdot hv: ",DinnerPlate.Viruses[0].h,DinnerPlate.Viruses[0].v)
        #FlashDot (DinnerPlate.Viruses[0].h - CameraH,DinnerPlate.Viruses[0].v + CameraV,0.5)
        time.sleep(1)
        #cf.ClearBigLED()
        FlashAllViruses(DinnerPlate.Viruses,VirusCount,DinnerPlate,CameraH,CameraV)
        DinnerPlate.DisplayWindowZoom(CameraH,CameraV,32,1,0.01)

        cf.ClearBuffers()
        cf.ShowGlowingText(h = -1,v = 2,  Text = 'STRAIN', RGB = cf.HighYellow,ShadowRGB = cf.DarkYellow,ZoomFactor=2)
        cf.ShowGlowingText(h = -1,v = 14,  Text = 'SECURE', RGB = cf.HighYellow,ShadowRGB = cf.DarkYellow,ZoomFactor=2)
        time.sleep(1)
        cf.ZoomScreen(gv.ScreenArray,32,1,0.01)
        


        #Prepare new level
        DominanceCount    = 0
        LevelCount        = random.randint(1,MaxLevel)
        replicationrate   = gv.OriginalReplicationRate
        mutationdeathrate = gv.OriginalMutationDeathRate
        gv.VirusTopSpeed    = OldVirusTopSpeed
        gv.VirusBottomSpeed = OldVirusBottomSpeed
        DinnerPlate         = CreateDinnerPlate(LevelCount)
        CameraH             = DinnerPlate.DisplayH
        CameraV             = DinnerPlate.DisplayV
        
        VirusCount          = len(DinnerPlate.Viruses)
        ClockSprite         = cf.CreateClockSprite(12)
        CurrencySprite      = CreateCurrencySprite()
        NextMaze            = False



        #Show Custom sprites
        DinnerPlate.CopySpriteToPlayfield(ClockSprite,      gv.ClockH +1,      gv.ClockV+1,      gv.ClockRGB,       ObjectType = 'Wall',  Filler = 'DarkWall')
        DinnerPlate.CopySpriteToPlayfield(DayOfWeekSprite,  gv.DayOfWeekH +1,  gv.DayOfWeekV+1,  gv.DayOfWeekRGB,   ObjectType = 'Wall',  Filler = 'DarkWall')
        DinnerPlate.CopySpriteToPlayfield(MonthSprite,      gv.MonthH +1,      gv.MonthV+1,      gv.MonthRGB,       ObjectType = 'Wall',  Filler = 'DarkWall')
        DinnerPlate.CopySpriteToPlayfield(DayOfMonthSprite, gv.DayOfMonthH +1, gv.DayOfMonthV+1, gv.DayOfMonthRGB , ObjectType = 'Wall',  Filler = 'DarkWall')
        DinnerPlate.CopySpriteToPlayfield(CurrencySprite,   gv.CurrencyH+1,   gv.CurrencyV+1,   gv.CurrencyRGB,    ObjectType = 'Wall',  Filler = 'DarkWall')

      

        ClockSprite.on      = 0
        DinnerPlate.DisplayWindowZoom(CameraH,CameraV,2,32,0.025)
      
        nextname = ""
    else:
      DominanceCount = 0
      StrainCreated  = 0
        
    
   


    #------------------
    #-- Main Display --
    #------------------

    # If it is time to show the clock, turn it on and show it
    # increment clock location if it is time to do so




    m,r = divmod(gv.VirusMoves,gv.CheckCurrencySpeed)
    if (r == 0):  
      CurrencySprite = CreateCurrencySprite()
      DinnerPlate.CopySpriteToPlayfield(CurrencySprite,   gv.CurrencyH+1,   gv.CurrencyV+1,   gv.CurrencyRGB,    ObjectType = 'Wall', Filler = 'DarkWall')

    
    m,r = divmod(gv.VirusMoves,CheckClockSpeed)
    if (r == 0):  
      #CheckClockTimer(ClockSprite)
      TheTime = cf.CreateClockSprite(12)

      #Show Custom sprites
      DinnerPlate.CopySpriteToPlayfield(ClockSprite,      gv.ClockH +1,      gv.ClockV +1,      gv.ClockRGB,       ObjectType = 'Wall',  Filler = 'DarkWall')
      DinnerPlate.CopySpriteToPlayfield(DayOfWeekSprite,  gv.DayOfWeekH +1,  gv.DayOfWeekV+1,  gv.DayOfWeekRGB,   ObjectType = 'Wall',  Filler = 'DarkWall')
      DinnerPlate.CopySpriteToPlayfield(MonthSprite,      gv.MonthH +1,      gv.MonthV+1,      gv.MonthRGB,       ObjectType = 'Wall',  Filler = 'DarkWall')
      DinnerPlate.CopySpriteToPlayfield(DayOfMonthSprite, gv.DayOfMonthH +1, gv.DayOfMonthV+1, gv.DayOfMonthRGB , ObjectType = 'Wall',  Filler = 'DarkWall')

  


      
      


    # #print ("Camera HV:",CameraH, CameraV)
    # if (ClockSprite.on == 1):
      # #print ("Clock on")
      # DinnerPlate.DisplayWindowWithSprite(CameraH, CameraV, ClockSprite)
      # MoveMessageSprite(gv.VirusMoves,ClockSprite)
    # # else:
    DinnerPlate.DisplayWindow(CameraH, CameraV)
    

      

    
    
    #-------------------------
    #-- Create Clock Sprite --
    #-------------------------
    # we want to display the clock ever X seconds, so we call the function CheckElapsedTime to see if that many
    # seconds have passed.  If so, create the clock and start sliding it onto the screen at a specific speed.
    # After X seconds, slide off screen and reset the timers.
   
    if (CheckElapsedTime(CheckTime) == 1):
      if (ClockSprite.on == 0):
        ClockSprite = cf.CreateClockSprite(12)
      
      
    #End game if all viruses dead
    VirusCount = len(DinnerPlate.Viruses)
    if (VirusCount == 0):
      finished = "Y"





  #let the display show the final results before clearing
  time.sleep(3)
  cf.ClearBigLED()
  DinnerPlate.DisplayWindowZoom(CameraH,CameraV,32,2,0.025)

  if(VirusCount == 0):
    cf.ShowScrollingBanner2("infection Cured!",(cf.MedYellow),gv.ScrollSleep *0.8)
    cf.ShowScrollingBanner2("Score: " + str(gv.VirusMoves) ,(cf.MedGreen),gv.ScrollSleep *0.8)
  else:
    cf.ShowScrollingBanner2("danger! pandemic protocols initiated",(cf.HighRed),gv.ScrollSleep *0.8)
    cf.ShowScrollingBanner2("game over",(cf.HighYellow),gv.ScrollSleep *0.8)


  cf.ClearBigLED()
  return





























#------------------------------------------------------------------------------
#    ___       _     _ _                                                     --
#   / _ \ _ __| |__ (_) |_ ___                                               --
#  | | | | '__| '_ \| | __/ __|                                              --
#  | |_| | |  | |_) | | |_\__ \                                              --
#   \___/|_|  |_.__/|_|\__|___/                                              --
#                                                                            --
#------------------------------------------------------------------------------

# Ideas:
# - particles have mass
# - particles can be bigger than one pixel
# - maybe have a sprite to display
# - store particles in a list 
# - all particles moved if it is their turn
# - particles have momentum, speed, heading
# - heading gets converted to an 8 way direction box when showing movement
# - start small, build a framework then build maps/games based on that


#

# Perhaps particles can be very tiny, even though they are drawn on one LED.
# Have a virtual grid of 1000x1000
# - Movements are tracked on virtual grid and then converted to 16x16 co-ordinates 
#   for drawing
# - it is important to draw each LED as an entire object
# - do we do collision detection on the playfield or in the virtual grid?
# - I am thinking virtual grid is only for calculating smooth movements, collision 
#   still takes place on the playfield
# - when drawing on the playfield we have to calculate the virtual destination
#   and use the turn towards 8 way functions to move on the playfield
# - smooth animation is essential
















class Particle(object):
  
  def __init__(self,h,v,r,g,b,direction,scandirection,alive,lives,name,score,exploding,radarrange,
               mass,
               velocity = 0,
               acceleration = 0,
               speed = 10
               ):

    self.h               = h              # location on playfield (e.g. 10,35)
    self.v               = v              # location on playfield (e.g. 10,35)
    self.r               = r
    self.g               = g
    self.b               = b
    self.direction       = direction      #direction of travel
    self.scandirection   = scandirection  #direction of scanners, if equipped
    self.alive           = 1
    self.lives           = 3
    self.name            = name
    self.exploding       = 0
    self.radarrange      = 20
    self.bottomspeed     = 50
    self.topspeed        = 1


    self.mass            = mass
    self.velocity        = velocity
    self.acceleration    = acceleration
    self.speed           = speed
    self.delta_h         = random.randint(-2, 2)
    self.delta_v         = random.randint(-2, 2)



  def Display(self):
    if (self.alive == 1):
      cf.setpixel(self.h,self.v,self.r,self.g,self.b)
     # print("display HV:", self.h,self.v)
      #unicorn.show()
      #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)
  
      
  def Erase(self):
    cf.setpixel(self.h,self.v,0,0,0)
    #unicorn.show()
    #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)


  #Lower is faster!
  def AdjustSpeed(self, increment):
    speed = self.speed
    speed = self.speed + increment
    if (speed > self.bottomspeed):
      speed = self.bottomspeed
    elif (speed < self.topspeed):
      speed = self.topspeed

    self.speed = speed
    return;



class ParticleWorld(object):
#A world that contains a playfield, a map, and a bunch of particles
#We will have one gravity source
  def __init__(self, 
               name, 
               width, 
               height, 
               Map, 
               Playfield, 
               CameraH, 
               CameraV, 
               DisplayH, 
               DisplayV, 
               GravityH = 7,
               GravityV = 7,
               Gravity  = 10):
    self.name      = name
    self.width     = width
    self.height    = height
    self.Map       = ([[]])
    self.Playfield = ([[]])
    self.CameraH   = CameraH
    self.CameraV   = CameraV
    self.DisplayH     = DisplayH
    self.DisplayV     = DisplayV

    self.Gravity   = Gravity   #Gravity of the world object, if required
    self.GravityH  = GravityH  #HV of the center of gravity
    self.GravityV  = GravityV  #HV of the center of gravity

    self.Map       = [[0 for i in range(self.width)] for i in range(self.height)]
    self.Playfield = [[ cf.EmptyObject('EmptyObject') for i in range(self.width)] for i in range(self.height)]



  def CopyMapToPlayfield(self):
    #This function is run once to populate the playfield with various objects (particles, walls, etc)
    #XY is actually implemented as YX.  Counter intuitive, but it works.

    width     = self.width 
    height    = self.height
    Particles = []
    print ("Map width height:",width,height)
    
   
    #print ("RD - CopyMapToPlayfield - Width Height: ", width,height)
    x = 0
    y = 0
    
    
    #print ("width height: ",width,height)
    
    for y in range (0,height):
      print (*self.Map[y])
  
      for x in range(0,width):
        #print ("RD xy color: ",x,y, self.Map[y][x])
        SDColor = self.Map[y][x]
  
        if (SDColor == 1):
          r = cf.SDDarkWhiteR
          g = cf.SDDarkWhiteG
          b = cf.SDDarkWhiteB
          self.Playfield[y][x] = Particle(x,y,r,g,b,1,1,1,1,1,1,'Wall',0,0,10)


        elif (SDColor == 2):
          r = cf.SDDarkWhiteR + 30
          g = cf.SDDarkWhiteG + 30
          b = cf.SDDarkWhiteB + 30
                                    #(h,v,r,g,b,alive,lives,name):
          self.Playfield[y][x] = Particle(x,y,r,g,b,1,1,1,1,1,1,'Wall',0,0,10)
          #print ("Copying wallbreakable to playfield hv: ",y,x)

        elif (SDColor == 3):
          r = cf.SDDarkWhiteR + 50
          g = cf.SDDarkWhiteG + 50
          b = cf.SDDarkWhiteB + 50
                                    #(h,v,r,g,b,alive,lives,name):
          self.Playfield[y][x] = Particle(x,y,r,g,b,1,1,1,1,1,1,'Wall',0,0,10)
          #print ("Copying wallbreakable to playfield hv: ",y,x)

        elif (SDColor == 4):
          r = cf.SDDarkWhiteR 
          g = cf.SDDarkWhiteG
          b = cf.SDDarkWhiteR + 60
                                    #(h,v,r,g,b,alive,lives,name):
          self.Playfield[y][x] = Particle(x,y,r,g,b,1,1,1,1,1,1,'WallBreakable',0,0,10)
          #print ("Copying wallbreakable to playfield hv: ",y,x)

        elif (SDColor >=5):
          r,g,b =  cf.ColorList[SDColor]
          
          
          #(h,v,r,g,b,direction,scandirection,mass,speed,alive,lives,name,score,exploding,radarrange):
          self.Playfield[y][x] = Particle(x,y,r,g,b,1,1,1,1,1,1,'Particle',0,0,10)
          Particles.append(self.Playfield[y][x])
          #self.Playfield[y][x].direction = cf.PointTowardsObject8Way(x,y,height/2,width/2)
          self.Playfield[y][x].direction = 1

        else:
          #print ('EmptyObject')
          self.Playfield[y][x] = cf.EmptyObject('EmptyObject')

    return Particles;




  def DisplayWindow(self,h,v):
    #This function accepts h,v coordinates for the entire map (e.g. 1,8  20,20,  64,64)    
    #Displays what is on the playfield currently, including walls, cars, etc.
    r = 0
    g = 0
    b = 0
    count = 0
        

    for V in range(0,gv.HatWidth):
      for H in range (0,gv.HatHeight):
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
          
        #Our map is an array of arrays [v][h] but we draw h,v
        cf.setpixel(H,V,r,g,b)
    
    #unicorn.show()
    #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)


            
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
        cf.setpixel(H,V,r,g,b)

    #Display clock at current location
    #Clock hv will allow external functions to slide clock all over screen

    #print ("Clock info  hv on: ",ClockSprite.h,ClockSprite.v,ClockSprite.on)
    ClockSprite.CopySpriteToBuffer(ClockSprite.h,ClockSprite.v)
        
    #unicorn.show()
    #SendBufferPacket(RemoteDisplay,gv.HatHeight,gv.HatWidth)




  def CountParticlesInWindow(self,h,v):
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





def calculate_single_body_acceleration(Particle):
    G_const  = 6.67408e-11 #m3 kg-1 s-2
    GravityH = 7
    GravityV = 32
    acceleration = point(0,0)
    
    r = (Particle.h - GravityH)**2 + (Particle.v - GravityV)**2  
    r = math.sqrt(r)
    tmp = G_const * external_body.mass / r**3
    acceleration.x += tmp * (GravityH - Particle.h)
    acceleration.y += tmp * (GravityV - Particle.v)
    

    return acceleration


    


def ParticleWorldScanAround(Particle,Playfield):
  # hv represent particle location
  # ScanH and ScanV is where we are scanning
  
  print ("== Scan in Front of Particle ==")
  
  ScanDirection = Particle.direction
  ScanH         = 0
  ScanV         = 0
  h             = Particle.h
  v             = Particle.v
  Item          = ''
  ItemList      = ['EmptyObject']
  count         = 0    #represents number of spaces to scan

#         2 1 3
#         5 x 6                              
#           4   
  
  #FlashDot2(h,v,0.005)

  #Scan in front
  ScanH, ScanV = cf.CalculateDotMovement8Way(h,v,Particle.direction)
  ItemList.append(Playfield[ScanV][ScanH].name)
  
  
  #Scan left diagonal
  ScanDirection = cf.TurnLeft8Way(Particle.direction)
  ScanH, ScanV = cf.CalculateDotMovement8Way(h,v,ScanDirection)
  ItemList.append(Playfield[ScanV][ScanH].name)
  
  #Scan right diagonal
  ScanDirection = cf.TurnRight8Way(Particle.direction)
  ScanH, ScanV = cf.CalculateDotMovement8Way(h,v,ScanDirection)
  print ("Scan right diaganol:",ScanH,ScanV)
  ItemList.append(Playfield[ScanV][ScanH].name)
  
  
  #Scan behind
  ScanDirection = cf.ReverseDirection8Way(Particle.direction)
  ScanH, ScanV = cf.CalculateDotMovement8Way(h,v,ScanDirection)
  ItemList.append(Playfield[ScanV][ScanH].name)
  
  #Scan left
  ScanDirection = cf.TurnLeft8Way(cf.TurnLeft8Way(Particle.direction))
  ScanH, ScanV = cf.CalculateDotMovement8Way(h,v,ScanDirection)
  ItemList.append(Playfield[ScanV][ScanH].name)


  #Scan right
  ScanDirection = cf.TurnRight8Way(cf.TurnRight8Way(Particle.direction))
  ScanH, ScanV = cf.CalculateDotMovement8Way(h,v,ScanDirection)
  ItemList.append(Playfield[ScanV][ScanH].name)


  return ItemList;
  




  

def MoveParticle(Particle,Playfield):
  print ("== MoveParticle : ",Particle.name," hv dh dv alive--",Particle.h,Particle.v,Particle.alive)
  
  #print ("")
  h = Particle.h
  v = Particle.v
  oldh  = h
  oldv  = v
  ScanH = 0
  ScanV = 0
  ItemList = []
  DoNothing = ""
  ScanDirection     = 1
  WallInFront       = cf.EmptyObject('EmptyObject')
  ParticleInFront   = cf.EmptyObject('EmptyObject')
  ParticleInRear    = cf.EmptyObject('EmptyObject')
  ParticleLeftDiag  = cf.EmptyObject('EmptyObject')
  ParticleRightDiag = cf.EmptyObject('EmptyObject')
  
  

  Particle.velocity = Particle.speed * Particle.mass


  #print("Current Particle vh direction:",v,h,Particle.direction)
  ItemList = ParticleWorldScanAround(Particle,Playfield)
  #print (ItemList)
  

  #Grab breakable wall object
  if (ItemList[1] == "WallBreakable"):
    ScanH,ScanV = cf.CalculateDotMovement8Way(h,v,Particle.direction)
    WallInFront = Playfield[ScanV][ScanH]


  #Grab potential Particles in scan zones NW N NE S
  #Grab Particle in front
  if (ItemList[1] != "Wall" and ItemList[1] != "WallBreakable" and ItemList[1] != 'EmptyObject'):
    ScanH,ScanV = cf.CalculateDotMovement8Way(h,v,Particle.direction)
    ParticleInFront = Playfield[ScanV][ScanH]
    #print ("ScanFront    ",ParticleInFront.name,ParticleLeftDiag.name,ParticleRightDiag.name,ParticleInRear.name)

  #Grab Particle left diagonal
  if (ItemList[2] != "Wall" and ItemList[1] != "WallBreakable" and ItemList[2] != 'EmptyObject'):
    ScanDirection = cf.TurnLeft8Way(Particle.direction)
    ScanH,ScanV = cf.CalculateDotMovement8Way(h,v,ScanDirection)
    ParticleLeftDiag = Playfield[ScanV][ScanH]
    #print ("ScanLeftDiag ",ParticleInFront.name,ParticleLeftDiag.name,ParticleRightDiag.name,ParticleInRear.name)

  #Grab Particle right diagonal
  if (ItemList[3] != "Wall" and ItemList[1] != "WallBreakable" and ItemList[3] != 'EmptyObject'):
    ScanDirection = cf.TurnRight8Way(Particle.direction)
    ScanH,ScanV = cf.CalculateDotMovement8Way(h,v,ScanDirection)
    ParticleRightDiag = Playfield[ScanV][ScanH]
    #print ("ScanRightDiag",ParticleInFront.name,ParticleLeftDiag.name,ParticleRightDiag.name,ParticleInRear.name)
  
        
  if (ItemList[4] != "Wall" and ItemList[1] != "WallBreakable" and ItemList[4] != 'EmptyObject'):
    ScanDirection = cf.ReverseDirection8Way(Particle.direction)
    ScanH,ScanV   = cf.CalculateDotMovement8Way(h,v,ScanDirection)
    ParticleInRear     = Playfield[ScanV][ScanH]
    #print ("ScanRear",ParticleInFront.name,ParticleLeftDiag.name,ParticleRightDiag.name,ParticleInRear.name)
  

  #Infect Particles
  #If different Particle, take it over
  #else follow it


  #Add damage to breakable walls
  if (WallInFront.name == "WallBreakable"):
    #print ("Wall in front: ",WallInFront.name, WallInFront.lives)
    WallInFront.lives = WallInFront.lives -1
    if (WallInFront.lives <= 0):
      Playfield[WallInFront.v][WallInFront.h] = cf.EmptyObject('EmptyObject')


  

  
  #If no Particles around, check for walls
  #if (all('EmptyObject' == name for name in (ParticleInFront.name, ParticleLeftDiag.name, ParticleRightDiag.name, ParticleInRear.name))):
   

  

  

  #temporary override
  Particle.h += Particle.delta_h
  Particle.v += Particle.delta_v
  
  if (Particle.v < 1 or Particle.v > 14):
    Particle.delta_v = Particle.delta_v *(-1)
 
  if (Particle.h < 1 or Particle.h > 14):
    Particle.delta_h = Particle.delta_h *(-1)
  
  Particle.h += Particle.delta_h
  Particle.v += Particle.delta_v
  

  if (Particle.v < 0):
    Particle.v = 0
  if (Particle.v > 15):
    Particle.v = 15

  if (Particle.h < 0):
    Particle.h = 0
  if (Particle.h > 15):
    Particle.h = 15




  if (Particle.alive == 1):  
    

    #Only move if the space decided upon is actually empty!
    ScanH,ScanV = cf.CalculateDotMovement8Way(h,v,Particle.direction)
    if (Playfield[ScanV][ScanH].name == 'EmptyObject'):
      #print ("Spot moving to is empty ScanV ScanH",ScanV,ScanH)
      #print ("Particle moved!!!!!!!!!!!!!")
      Particle.h = ScanH
      Particle.v = ScanV

      #print ("Making Empty oldv oldh vh ",oldv,oldh,v,h)
      Playfield[ScanV][ScanH] = Particle
      Playfield[oldv][oldh] = cf.EmptyObject('EmptyObject')
      #print ("Old spot:",Playfield[oldv][oldh].name)
    else:
      #print ("spot moving to is not empty: ",Playfield[ScanV][ScanH].name, ScanV,ScanH)
      #Introduce some instability into the Particle
      if (random.randint(0,InstabilityFactor) == 1):
        Particle.direction = cf.TurnLeftOrRight8Way(Particle.direction)
        Particle.AdjustSpeed(random.randint(-5,3))
  else:
    print ("Particle died during mutation.  No movement possible.")



  
  
  return 



def CreateParticleWorld(MapLevel):
  print ("Create Orbits Map: ",MapLevel)
  #def __init__(self, name, width, height, Map, Playfield, CameraH, CameraV, Gravity = 1):


  if (MapLevel == 1):
    Orbits = ParticleWorld(name='SolarSystem',
                           width        = 16,
                           height       = 16,
                           Map          = [[]],
                           Playfield    = [[]],
                           CameraH      = 1,
                           CameraV      = 1,
                           DisplayH     = 1,
                           DisplayV     = 1,
                           Gravity      = 1)

                                                        
    #                                         |  |
    Orbits.Map[0]  = ([  1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
    Orbits.Map[1]  = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1])
    Orbits.Map[2]  = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1])
    Orbits.Map[3]  = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1])
    Orbits.Map[4]  = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1])
    Orbits.Map[5]  = ([  1, 0, 0, 0, 0, 0, 0, 0,22, 0, 0, 0, 0, 0, 0, 1])
    Orbits.Map[6]  = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1])
    Orbits.Map[7]  = ([  1, 0, 0, 0, 0, 0, 0,11, 0, 0, 0, 0, 0, 0, 0, 1])
    Orbits.Map[8]  = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1])
    Orbits.Map[9]  = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1])
    Orbits.Map[10] = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1])
    Orbits.Map[11] = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1])
    Orbits.Map[12] = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1])
    Orbits.Map[13] = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1])
    Orbits.Map[14] = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1])
    Orbits.Map[15] = ([  1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])



  if (MapLevel == 2):
    Orbits = ParticleWorld(name='SolarSystem',
                           width        = 25,
                           height       = 25,
                           Map          = [[]],
                           Playfield    = [[]],
                           CameraH      = 1,
                           CameraV      = 1,
                           DisplayH     = 4,
                           DisplayV     = 4,
                           Gravity      = 1)
    #                                     |                    |  |                    |
    Orbits.Map[0]  = ([  1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ])
    Orbits.Map[1]  = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ])
    Orbits.Map[2]  = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ])
    Orbits.Map[3]  = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ])
    Orbits.Map[4]  = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ])
    Orbits.Map[5]  = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ])#
    Orbits.Map[6]  = ([  1, 0, 0, 0, 0, 0, 0,19, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ])
    Orbits.Map[7]  = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ])
    Orbits.Map[8]  = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ])
    Orbits.Map[9]  = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ])
    Orbits.Map[10] = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ])
    Orbits.Map[11] = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ])
    Orbits.Map[12] = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ])
    Orbits.Map[13] = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ])
    Orbits.Map[14] = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ])
    Orbits.Map[15] = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ])
    Orbits.Map[16] = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ])
    Orbits.Map[17] = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1 ])
    Orbits.Map[18] = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ])
    Orbits.Map[19] = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ]) #
    Orbits.Map[20] = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ])
    Orbits.Map[21] = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ])
    Orbits.Map[22] = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ])
    Orbits.Map[23] = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ])
    Orbits.Map[24] = ([  1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ])


    


  if (MapLevel == 98):
    Orbits = ParticleWorld(name='Template',
                           width        = 18,
                           height       = 18,
                           Map          = [[]],
                           Playfield    = [[]],
                           CameraH      = 1,
                           CameraV      = 1,
                           Gravity      = 1)

                                                         
    #                                                 |  |
    Orbits.Map[0]  = ([  1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ])
    Orbits.Map[1]  = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ])
    Orbits.Map[2]  = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ])
    Orbits.Map[3]  = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ])
    Orbits.Map[4]  = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ])
    Orbits.Map[5]  = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ])
    Orbits.Map[6]  = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ])
    Orbits.Map[7]  = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ])
    Orbits.Map[8]  = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ])
    Orbits.Map[9]  = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ])
    Orbits.Map[10] = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ])
    Orbits.Map[11] = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ])
    Orbits.Map[12] = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ])
    Orbits.Map[13] = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ])
    Orbits.Map[14] = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ])
    Orbits.Map[15] = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ])
    Orbits.Map[16] = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ])
    Orbits.Map[17] = ([  1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ])

  return Orbits;






  

def PlayOrbits():      


  
  finished     = 'N'
  moves        = 0
  LevelCount   = 1
  MaxLevel     = 1
  NameCount    = 0
  Particles      = []
  ParticleCount   = 0
  Particle        = cf.EmptyObject('EmptyObject')
  ParticleMaxCount  = 125 #if Particle count reaches 75%, end level
  ParticleDeleted   = 0
  ClockSprite       = cf.CreateClockSprite(12)
  ClockSprite.on    = 0
  MaxParticleMoves  = 100000
  
  


  #PathCount     = len(CameraPath)
  PathPosition  = 0
  PositionSpeed = 100

  CameraDirection = 0
  CameraSpeed     = 5
  ParticlesInWindow = 0
  
  #CameraH, CameraV, CameraSpeed = CameraPath[0]
  


  #The map is an array of a lists.  You can address each element has VH e.g. [V][H]
  #Copying the map to the playfield needs to follow the exact same shape

  #----------------------
  #-- Prepare Level    --
  #----------------------
  #LevelCount = random.randint(1,MaxLevel)
  LevelCount     = 1
  Orbits         = CreateParticleWorld(LevelCount)
  Particles      = Orbits.CopyMapToPlayfield()
  ParticleCount  = len(Particles)
  print("ParticleCount: ",ParticleCount)
  DominanceCount = 0
  CameraH        = Orbits.DisplayH
  CameraV        = Orbits.DisplayV

  print ("CameraHV: ",CameraH, CameraV)

  #ShowScrollingBanner("Outbreak!",cf.SDLowYellowR,cf.SDLowYellowG,cf.SDLowYellowB,gv.ScrollSleep *0.8)



  NameCount = 1

  while (finished == "N" and moves < MaxParticleMoves):
    moves = moves + 1
    

    #--------------------------------
    #Check for keyboard input      --
    #--------------------------------
    #If we do this too often, the terminal window (if using telnet) will flicker  (now been fixed, see cf.PollKeyboard function)
    m,r = divmod(moves,KeyboardSpeed)
    if (r == 0):
      Key = cf.PollKeyboard()
      if (Key == 'q'):
        LevelFinished = 'Y'
        Finished      = 'Y'
        return

      #print ("Moves:",moves,"                              ",end="\r")      


    

    #--------------------------------
    #-- Particle actions              --
    #--------------------------------

    firstname = Particles[0].name
    NameCount = 1
    
    
    
    #It seems that Python determines the "ParticleCount-1" value once, and does not re-evaluate.  When some of the virises die, 
    #this thorws off the loop and counts.  I will deal with this internally.
    #for x in range (0,ParticleCount-1):

    #Changed the for loop to a while loop
    x = 0
    while (x < ParticleCount):
      ParticleDeleted = 0

      #print ("Looping x ParticleCount: ",x,ParticleCount)

      #af.FlashDot(Particles[x].h,Particles[x].v,0.01)
      if (Particles[x].name != firstname):
        NameCount = NameCount + 1

      
      #----------------------
      #-- Movement         --  
      #----------------------
      #print ("Speed:",Particles[x].speed)
      m,r = divmod(moves,Particles[x].speed)
      if (r == 0):
        print ("Particle name alive x:",Particles[x].name,Particles[x].alive,x)
        if (Particles[x].alive == 1):
          MoveParticle(Particles[x],Orbits.Playfield)
        else:
          print ("*** Removing Particle from the list: ",x)
          del Particles[x]
          ParticleCount = ParticleCount -1
          #print ("ParticleCount:",ParticleCount)
          ParticleDeleted = 1
          
  


      #---------------------------
      #-- End Particle loop        --
      #---------------------------
      x = x + 1
      


      
      

    # #-------------------------------------------
    # #-- Level ends when one Particle dominates--
    # #-------------------------------------------
  
    # if (NameCount == 1):
      # #Erase clock if present
      # #Orbits.DisplayWindow(CameraH, CameraV)
      # DominanceCount = DominanceCount + 1
      # #print ("NameCount:",NameCount,"DominanceCount:",DominanceCount,"DominanceMaxCount:",DominanceMaxCount)
      
      

      # #print ("DominanceCount:",DominanceCount,"DominanceMaxCount:",DominanceMaxCount,"ParticleCount:",ParticleCount,"ParticleMaxCount:",ParticleMaxCount)
      # #if one Particle dominates for X ticks, reset and load next level
      # if (DominanceCount >= DominanceMaxCount) or(ParticleCount >= ParticleMaxCount):
        # print ("ParticleCount:",ParticleCount)
        # #print ("Flashdot hv: ",Particles[0].h,Particles[0].v)
        # #FlashDot (Particles[0].h - CameraH,Particles[0].v + CameraV,0.5)
        # time.sleep(1)
        # #cf.ClearBigLED()
        # FlashAllParticles(Particles,ParticleCount,Orbits,CameraH,CameraV)
        # #af.ShowScrollingBanner2("Strain # " + str(firstname) + " secured" ,(cf.MedGreen),gv.ScrollSleep)
        
        # #Prepare new level
        # DominanceCount  = 0
        # LevelCount      = random.randint(1,MaxLevel)
        # Orbits          = CreateParticleWorld(LevelCount)
        # CameraH         = Orbits.DisplayH
        # CameraV         = Orbits.DisplayV
        # Particles       = Orbits.CopyMapToPlayfield()
        # ParticleCount   = len(Particles)
        # ClockSprite     = cf.CreateClockSprite(12)
        # ClockSprite.on  = 0
      
        # nextname = ""
    # else:
      # DominanceCount = 0
        
    
    #------------------
    #-- Main Display --
    #------------------
    print ("Moves:",moves,"                              ",end="\r")      

    # If it is time to show the clock, turn it on and show it
    # increment clock location if it is time to do so
    
    m,r = divmod(moves,CheckClockSpeed)
    if (r == 0):  
      CheckClockTimer(ClockSprite)
        
    #print ("Camera HV:",CameraH, CameraV)
    if (ClockSprite.on == 1):
      #print ("Clock on")
      Orbits.DisplayWindowWithSprite(CameraH, CameraV, ClockSprite)
      MoveMessageSprite(moves,ClockSprite)
    else:
      Orbits.DisplayWindow(CameraH, CameraV)
    
    
    
    
    #-------------------------
    #-- Create Clock Sprite --
    #-------------------------
    # we want to display the clock ever X seconds, so we call the function CheckElapsedTime to see if that many
    # seconds have passed.  If so, create the clock and start sliding it onto the screen at a specific speed.
    # After X seconds, slide off screen and reset the timers.
   
    if (CheckElapsedTime(CheckTime) == 1):
      if (ClockSprite.on == 0):
        ClockSprite = cf.CreateClockSprite(12)
      
      
    #End game if all Particles dead
    ParticleCount = len(Particles)
    if (ParticleCount == 0):
      finished = "Y"


    

  #let the display show the final results before clearing
  time.sleep(3)
  cf.ClearBigLED()
  
  #af.ShowScrollingBanner2("Infection Cured!",(cf.MedYellow),gv.ScrollSleep *0.8)
  #af.ShowScrollingBanner2("Score: " + str(moves) ,(cf.MedGreen),gv.ScrollSleep *0.8)
  cf.ClearBigLED()
  return








#------------------------------------------------------------------------------
# REMOTE DISPLAY TEST                                                        --
#------------------------------------------------------------------------------


PacketString = ""
PreviousPacketString = ""

PacketWaitTime      = 1/30  # fractions of a second
FPSTooHighWaitTime  = 0.10
LastPacketTime      = time.time()
TimeSinceLastPacket = 0.000


#PacketTimeTotal = str(float(round((endTime - startTime ),3)))
#PacketFPS   = 0
#PacketCount = 0

def SendBufferPacket(RemoteDisplay,width,height):
  global PreviousPacketString
  global LastPacketTime
  global TimeSinceLastPacket


  
  PacketString = ""
  x = 0
  y = 0
  rgb = (0,0,0)
  gv.HatWidth  = width
  gv.HatHeight = height
  UnicornBuffer       = unicorn.get_pixels()
  FPS                 = 0
  Message             = "skipped"
  TotalTimeTaken      = 0
  
  
  #Rotate buffer to match web display
  NewUnicornBuffer = list(zip(*UnicornBuffer[::-1]))
   
  for x in range(0,gv.HatHeight):
    for y in range(0,gv.HatWidth):
      r,g,b = NewUnicornBuffer[x][y]
      PacketString = PacketString + '#%02x%02x%02x' % (r,g,b) + ","
   
  #trim last comma
  PacketString = PacketString[:-1]
 
 
  #send packet - but only if enough time has passed
  TimeSinceLastPacket = float(round((time.time() - LastPacketTime ),3))
  FPS = 1 / TimeSinceLastPacket
  #print ("TimeSinceLastPacket:",TimeSinceLastPacket, "FPS: ",FPS)
  
  
  try:
    
    if (PreviousPacketString == PacketString ):
      Message = "SKIPPED: duplicate packet"
    elif (TimeSinceLastPacket < PacketWaitTime):
      Message = "SKIPPED: FPS too high"
      #time.sleep(PacketWaitTime)
    else:
      startTime = time.time()
      RemoteDisplay.update([PreviousPacketString])
      PreviousPacketString = PacketString
      endTime = time.time()
      TotalTimeTaken = str(float(round((endTime - startTime ),3)))
      Message = "Sent PacketSendTime: " + TotalTimeTaken
      TimeSinceLastPacket = 0.000
      LastPacketTime = time.time()


      
    print ("TimeSinceLastPacket:",(str(TimeSinceLastPacket).ljust(5,'0'))," FPS:",str(round(FPS,4)).ljust(8,'0')," ",Message)

  except Exception as ErrorMessage:
    TheTrace = traceback.format_exc()
    print("`n`n--------------------------------------------------------------")
    print("ERROR")
    print(ErrorMessage)
    #print("EXCEPTION")
    #print(sys.exc_info())
    print("`n")
    print ("TRACE")
    print (TheTrace)
    print("--------------------------------------------------------------`n`n")
    



def ErrorHandler(ErrorMessage,TraceMessage,AdditionalInfo):
  CallingFunction =  inspect.stack()[1][3]
  #FinalCleanup(stdscr)
  print("")
  print("")
  print("--------------------------------------------------------------")
  print("ERROR - Function (",CallingFunction, ") has encountered an error. ")
  print(ErrorMessage)
  print("")
  print("")
  print("TRACE")
  print(TraceMessage)
  print("")
  print("")
  if (AdditionalInfo != ""):
    print("Additonal info:",AdditionalInfo)
    print("")
    print("")
  print("--------------------------------------------------------------")
  print("")
  print("")
  
  #cf.ShowScrollingBanner2("ERROR DETECTED!",cf.HighRed,0.01)
  #cf.ClearBigLED()
  Message = ("ERROR!")
  TheBanner = cf.CreateBannerSprite(Message)
  TheBanner.r = 255
  TheBanner.g = 0
  TheBanner.b = 0
  TheBanner.Display((gv.HatWidth / 2) - (TheBanner.width / 2) ,(gv.HatHeight / 2) -3)
  time.sleep(1)






def FinalCleanup(stdscr):
  stdscr.keypad(0)
  curses.echo()
  curses.nocbreak()
  curses.curs_set(1)
  curses.endwin()




  
#------------------------------------------------------------------------------
# R E T R O   C L O C K                                                      --
#------------------------------------------------------------------------------




  
#--------------------------------------
# M A I N   P R O C E S S I N G      --
#--------------------------------------


#server_url ="https://pixelsim.azurewebsites.net:443/displayHub/"
#display_name = "IGiveUp"
#RemoteDisplay = PixelSimDisplay(server_url, display_name)
#RemoteDisplay.connect()
#time.sleep(2)




TheRandomMessage = cf.random_message('IntroMessages.txt')

print ("--------------------------------------")
print ("WELCOME TO THE ARCADE RETRO CLOCK")
print ("")
print ("BY DATAGOD")
print ("--------------------------------------")
print ("")
print ("")

PadDotHighScore = 0
cf.LoadConfigData()

print("--start options--")
print("Gamma:",gv.Gamma)
print("-----------------")

#ScrollScreenShowChickenWormTime('up',gv.ScrollSleep)




#PlayOutbreak()





print(TheRandomMessage)
#af.ShowScrollingBanner(TheRandomMessage,cf.SDLowYellowR,cf.SDLowYellowG,cf.SDLowYellowB,gv.ScrollSleep )
#af.ShowScrollingBanner2(TheRandomMessage,cf.MedYellow,gv.ScrollSleep )
#ShowLongIntro(gv.ScrollSleep)


#ShowIPAddress()




# Check for time, show clock, or play games
while (1==1):
  now = datetime.now()
  hh  = now.hour
  print (" ")
  print ("--CurrentTime--")
  print ("",now, hh)
  print ("TinyClockStartHH TinyClockHours",gv.TinyClockStartHH,gv.TinyClockHours)
  print ("PacDotHighScore: ",gv.PacDotHighScore)

#  if (hh >= TinyClockStartHH and hh <= 24):
#    DrawTinyClock(TinyClockHours*60)
#  ShowBouncingSquare()


  try:











    #Draw the Big text
    #Clear only the LED matrix
    #Draw the next size down
    #When at the final zoom level
    #  - clear the LED Matrix
    #  - clear all buffers (canvas and ScreenArray[V][H])
    #  - draw the text at desired last zoom level
    #  - draw the rest of the text, at this point it is all written to ArrayBuffer
    #  - clear the LED Matrix
    #  - clear all buffers (canvas and ScreenArray[V][H])
    #Call the ZoomScreen function to redraw the display using ScreenArray[V][H] which at this point
    #contains the values last written to the screen.

    Message = cf.TronGetRandomMessage()

    cf.ShowGlowingText(CenterHoriz = True,h = -8,v = 0,   Text = 'ARCADE', RGB = cf.HighGreen, ShadowRGB = cf.DarkGreen, ZoomFactor = 8,GlowLevels=0,DropShadow=False)
    gv.TheMatrix.Clear()
    cf.ShowGlowingText(CenterHoriz = True,h = -7,v = 0,   Text = 'ARCADE', RGB = cf.HighGreen, ShadowRGB = cf.DarkGreen, ZoomFactor = 7,GlowLevels=0,DropShadow=False)
    gv.TheMatrix.Clear()
    cf.ShowGlowingText(CenterHoriz = True,h = -6,v = 0,   Text = 'ARCADE', RGB = cf.HighGreen, ShadowRGB = cf.DarkGreen, ZoomFactor = 6,GlowLevels=0,DropShadow=False)
    gv.TheMatrix.Clear()
    cf.ShowGlowingText(CenterHoriz = True,h = -5,v = 0,   Text = 'ARCADE', RGB = cf.HighGreen, ShadowRGB = cf.DarkGreen, ZoomFactor = 5,GlowLevels=0,DropShadow=False)
    gv.TheMatrix.Clear()
    cf.ShowGlowingText(CenterHoriz = True,h = -4,v = 0,   Text = 'ARCADE', RGB = cf.HighGreen, ShadowRGB = cf.DarkGreen, ZoomFactor = 4,GlowLevels=0,DropShadow=False)
    gv.TheMatrix.Clear()
    cf.ShowGlowingText(CenterHoriz = True,h = -3,v = 0,   Text = 'ARCADE', RGB = cf.HighGreen, ShadowRGB = cf.DarkGreen, ZoomFactor = 3,GlowLevels=0,DropShadow=False)

    gv.Canvas.Clear()
    gv.TheMatrix.Clear()
    cf.ClearBuffers()
    cf.ShowGlowingText(CenterHoriz = False,h = -1,v = 0,   Text = 'ARCADE', RGB = cf.HighGreen, ShadowRGB = cf.DarkGreen, ZoomFactor = 2)
    cf.ShowGlowingText(CenterHoriz = True,h = -1,v = 11,  Text = 'RETRO',  RGB = cf.HighRed,   ShadowRGB = cf.DarkRed,   ZoomFactor = 2)
    cf.ShowGlowingText(CenterHoriz = True,h = -1,v = 22,  Text = 'CLOCK',  RGB = cf.HighPurple,ShadowRGB = cf.DarkPurple,ZoomFactor = 2)
    time.sleep(1)
    gv.TheMatrix.Clear()
    gv.Canvas.Clear()



    cf.ZoomScreen(gv.ScreenArray,32,1,0,Fade=True)

    PlaySuperWorms()
    PlayPacDot(40)
    PlaySpaceDot()
    PlayOutbreak()
    #PlayDotZerk()
    #PlayRallyDot()
    #PlayDotInvaders()
    
    


      
  except Exception as ErrorMessage:
    TraceMessage = traceback.format_exc()
    AdditionalInfo = "Error in Main section" 
    ErrorHandler(ErrorMessage,TraceMessage,AdditionalInfo)
    cf.ClearBigLED()
    






















#------------------------------------------------------------------------------
#                                                                            --
#      _    ____   ____    _    ____  _____    ____ _     ___   ____ _  __   --
#     / \  |  _ \ / ___|  / \  |  _ \| ____|  / ___| |   / _ \ / ___| |/ /   --
#    / _ \ | |_) | |     / _ \ | | | |  _|   | |   | |  | | | | |   | ' /    --
#   / ___ \|  _ <| |___ / ___ \| |_| | |___  | |___| |__| |_| | |___| . \    --
#  /_/   \_\_| \_\\____/_/   \_\____/|_____|  \____|_____\___/ \____|_|\_\   --
#                                                                            --
#                                                                            --
#  Global Variables                                                           --
#                                                                            --
#------------------------------------------------------------------------------
#   Version: 1.0                                                             --
#   Date:    June 11, 2020                                                   --
#   Reason:  Initial Creation                                                --
#------------------------------------------------------------------------------





MainSleep        = 0
FlashSleep       = 0
PacSleep         = 0.01
ScrollSleep      = 0.03
TinyClockStartHH = 0
TinyClockHours   = 0
CPUModifier      = 0
Gamma            = 0
HatWidth         = 64
HatHeight        = 32
KeyboardPoll     = 10



#-----------------------------
# BIG LED                   --
#-----------------------------
#RGB Matrix
from rgbmatrix import graphics
from rgbmatrix import RGBMatrix, RGBMatrixOptions

import numpy
import time

#Initialize Matrix objects
options = RGBMatrixOptions()

options.rows       = HatHeight
options.cols       = HatWidth
options.brightness = 100
#stops sparkling 
options.gpio_slowdown = 5


#options.chain_length = self.args.led_chain
#options.parallel = self.args.led_parallel
#options.row_address_type = self.args.led_row_addr_type
#options.multiplexing = self.args.led_multiplexing
#options.pwm_bits = self.args.led_pwm_bits
#options.pwm_lsb_nanoseconds = self.args.led_pwm_lsb_nanoseconds
#options.led_rgb_sequence = self.args.led_rgb_sequence
#options.pixel_mapper_config = self.args.led_pixel_mapper
#if self.args.led_show_refresh:
#  options.show_refresh_rate = 1

#if self.args.led_no_hardware_pulse:
#  options.disable_hardware_pulsing = True


#The matrix object is what is used to interact with the LED display
TheMatrix    = RGBMatrix(options = options)

#Screen array is a copy of the matrix light layout because RGBMatrix is not queryable.  
ScreenArray  = ([[]])
ScreenArray  = [[ (0,0,0) for i in range(HatWidth)] for i in range(HatHeight)]

#Canvas is an object that we can paint to (setpixels) and then swap to the main display for a super fast update (vsync)
Canvas = TheMatrix.CreateFrameCanvas()
Canvas.Fill(0,0,0)


#-----------------------------
# Crypto                    --
#-----------------------------


CheckCurrencySpeed    = 250000 #How often to query Ethereum prices
DisplayCurrencySpeed  = 1000   #How often to refresh currency sprite on screen
CryptoBalance         = 0      #what is the current CryptoBalance
CryptoTimer           = 600    #only calculate crypto blance ever X seconds   


#-----------------------------
# Timers                    --
#-----------------------------

StartTime = time.time()


#-----------------------------
# Used in all games         --
#-----------------------------

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

EmptyObject = EmptyObject()


#-----------------------------
# Outbreak Global Variables --
#-----------------------------
VirusTopSpeed     = 1
VirusBottomSpeed  = 20
VirusStartSpeed   = 8  #starting speed of the viruses
MinBright         = 50
MaxBright         = 255

OriginalMutationRate      = 10000
OriginalMutationDeathRate = 500
MaxMutations              = 5      #Maximum number of mutations, if surpassed the virus dies
MutationTypes             = 10     #Number of different types of mutations
OriginalReplicationRate   = 5000
replicationrate           = OriginalReplicationRate
FreakoutReplicationRate   = 10     #new replication rate when a virus freaksout
MaxVirusMoves             = 100000 #after this many moves the level is over
FreakoutMoves             = 25000  #after this many moves, the viruses will replicate and mutate at a much greater rate
VirusMoves                = 0      #used to count how many times the viruses have moved
ClumpingSpeed             = 10     #This modifies the speed of viruses that contact each other
ReplicationSpeed          = 5      #When a virus replicates, it will be a bit slower.  This number is added to current speed.
ChanceOfSpeedup           = 10     #determines how often a lone virus will spontaneously speed up
SlowTurnMinMoves          = 2      #number of moves a mutated virus moves before turning
SlowTurnMaxMoves          = 40     #number of moves a mutated virus moves before turning
MaxReplications           = 5      #Maximum number of replications, if surpassed the virus dies
InfectionChance           = 20     #Chance of one virus infecting another, lower the number greater the chance
DominanceMaxCount         = 5000   #how many ticks with there being only one virus, when reached level over
VirusNameSpeedupCount     = 500    #when this many virus strains are on the board, speed them up
ChanceOfDying             = 1000   #random chance of a virus dying
GreatChanceOfDying        = 300    #random chance of a virus dying when too many straings are alive
ChanceOfHeadingToHV       = 50000  #random chance of all viruses being interested in the same location
ChanceOfHeadingToFood     = 50     #random chance of a virus heading towards the nearest food
FoodCheckRadius           = 5      #radius around the virus when looking for food
ChanceOfTurningIntoFood   = 5      #Random chance of a dying mutating virus to turn into food
ChanceOfTurningIntoWall   = 5      #Random chance of a dying mutating virus to turn into food
VirusFoodWallLives        = 5      #Lives of food before it gets eaten and disappears
AuditSpeed                = 100    #Every X tick, an audit text window is displayed for debugging purposes
EatingSpeedAdjustment     = -10    #When a virus eats, it gets full and slows down             
SpeedIncrements           = 50     #how many chunks the speed range is cut up into, for increasing gradually
FoodBrightnessSteps       = 5      #each time a food loses life, it gets brighter by this many units
ChanceToStopEating        = 100    #chance that a virus decides to stop eating and carry on with life
ChanceOfRandomFood        = 10000  #chance that random food will show up, which will draw the viruses to it
MapOffset                 = 20     #how many pixels from the left screen does the map really start (so we don't overwrite clocks and other things)
BigFoodLives              = 1000   #lives for the big food particle
BigFoodRGB                = (255,0,0)
MaxRandomViruses          = 5      #maximum number of random viruses to place on big food maps
VirusMaxCount             = 1000   #maximum number of unique virus strains allowed


#Sprite display locations
ClockH,      ClockV,      ClockRGB      = 0,0,  (0,150,0)
DayOfWeekH,  DayOfWeekV,  DayOfWeekRGB  = 0,6,  (150,0,0)
MonthH,      MonthV,      MonthRGB      = 0,12, (0,20,200)
DayOfMonthH, DayOfMonthV, DayOfMonthRGB = 2,18, (100,100,0)
CurrencyH,   CurrencyV,   CurrencyRGB   = 0,27, (0,150,0)

#Sprite filler tuple
SpriteFillerRGB = (0,4,0)



#----------------------------
#-- PacDot                 --
#----------------------------

PacDotScore       = 0
PacDotHighScore   = 0
PacDotGamesPlayed = 0

FindClosestDotSpeed = 1
TurnTowardsBlueGhostSpeed = 1
PacDotRecentMoves=[]

DotMatrix = [[0 for x in range(HatHeight)] for y in range(HatWidth)] 


MoveSinceSmartSeekFlip     = 0
MaxMovesSinceEatingGhost   = 10
MaxMovesSinceSmartSeekFlip = 2500
PacDotSmartSeekMode        = 0
MaxRecentMoves             = 3 #if pacdot visists the same space this many times in recent moves, flip into smart or seek mode

#----------------------------
#-- DotZerk                --
#----------------------------








#----------------------------
#-- SuperWorms             --
#----------------------------
SuperWormSleep = 0.015
EraseSpeed     = 0.001
SpeedUpSpeed   = 75              #The lower the number, the more often a speedup is applied  (e.g. every 1 out of 200 ticks)
StartSpeedHigh =  1              #the lower the number, the faster it goes (e.g. move every X ticks)
StartSpeedLow  =  7              #the lower the number, the faster it goes (e.g. move every X ticks)
ResurrectionChance  = 100000     #what is chance of new worm being added (1 in X)
ResurrectionTries   = 20         #maximum number of tries when trying to find an empty location for the resurrected superworm
MinSleepTime        = 0.001
ResurrectedMaxTrail = 3          #when resurected, you get this for the trail length
StartMaxTrail       = 50         #Trail length at the start of the round
IncreaseTrailLengthSpeed = 10    #how often to increase length of trail (1 in X chance)
MaxTrailLength           = 2048  #Maximum length of the trail
SuperWormCount           = 8     #maximum number of worms in the worm array
SuperWormStartMinH = 25
SuperWormStartMaxH = 63
SuperWormStartMinV = 0
SuperWormStartMaxV = 25
SuperWormLevels    = 3           #number of levels



#----------------------------
#-- SpaceDot               --
#----------------------------
SpaceDotWallLives   = 50
SpaceDotGroundLives = 25
PlanetSurfaceSleep  = 1000
DebrisCleanupSleep  = 2000 #make sure empty cells on playfield are displayed as empty (0,0,0) 

Playfield = ([[]])
Playfield = [[0 for i in range(HatWidth)] for i in range(HatHeight)]


#Wave
MinHomingMissileWave = 5 #homning missles / ufos only show up after this wave
MinBomberWave        = 3 #homning missles / ufos only show up after this wave


SpaceDotMinH = 25
SpaceDotMaxH = 63
SpaceDotMinV = 0
SpaceDotMaxV = 26

#Ground
GroundV = SpaceDotMaxV - 1

#Player
PlayerShipSpeed       = 200
PlayerShipMinSpeed    = 50
PlayerShipAbsoluteMinSpeed = 10
MaxPlayerMissiles     = 5
PlayerMissiles        = 2
PlayerMissileSpeed    = 25
PlayerMissileMinSpeed = 8
PlayerShipLives       = 3


#BomberShip
BomberShipSpeed       = 80
ChanceOfBomberShip    = 2000  #chance of a bomberhsip appearing
BomberRockSpeed       = 30   #how fast the bomber dropped asteroid falls

#UFO
UFOMissileSpeed = 50
UFOShipSpeed    = 50  #also known as the EnemeyShip
UFOShipMinSpeed = 25
UFOShipMaxSpeed = 100

#HomingMissile 
UFOFrameRate               = 50  #random animated homing missiles
HomingMissileFrameRate     = 50  #the white one that looks like satellite from astrosmash
HomingMissileInitialSpeed  = 75
HomingMissileLives         = 25
HomingMissileSprites       = 12    #number of different sprites that can be homing missiles
HomingMissileDescentChance = 3     #chance of homing missile  not descending, lower number greater chance of being slow
ChanceOfHomingMissile      = 10000  #chance of a homing missile appearing



#Points
SpaceDotScore        = 0
UFOPoints            = 10
BomberPoints         = 5
BomberHitPoints      = 1
HomingMissilePoints  = 5
AsteroidLandedPoints = 1
AsteroidPoints       = 5

#Asteroids
WaveStartV           = -5
WaveMinSpeed         = 5     #The fastest the wave of asteroids can fall
WaveSpeedRange       = 60    #how much variance in the wave speed min and max
AsteroidMinSpeed     = 30    #lower the number the faster the movement (based on ticks)
AsteroidMaxSpeed     = 60  
AsteroidSpawnChance  = 100  #lower the number the greater the chance
WaveDropSpeed        = 550  #how often the next chunk of the wave is dropped
MovesBetweenWaves    = 2000
AsteroidsInWaveMax   = 200
AsteroidsInWaveMin   = 5 
AsteroidsToDropMin   = 1     #Number of asteroids to drop at a time
AsteroidsToDropMax   = 5   #Number of asteroids to drop at a time




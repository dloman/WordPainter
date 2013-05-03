#!/usr/bin/python
#Red Bull Create Contest code for team Skeeze
#This code takes strings and a font file and converts it into servo
#commands to draw with a turret controlled spray gun

#Copyright (C) <2013>  <Daniel Loman> <www.github.com/dloman>
#based on work by Lawrence Glaister --Engrave.py v11
#                 John Thornton  -- GUI framwork from arcbuddy.py
#                 Ben Lipkowitz  (fenn)-- cxf2cnc.py v0.5 font parsing code

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

from math import *
import os, re, string, sys, serial
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

Serial = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
########################################################################
########################################################################
class Character:
    def __init__(self, key):
        self.key = key
        self.stroke_list = []

    def __repr__(self):
        return "%s" % (self.stroke_list)

    def get_xmax(self):
        try: return max([s.xmax for s in self.stroke_list[:]])
        except ValueError: return 0

    def get_ymax(self):
        try: return max([s.ymax for s in self.stroke_list[:]])
        except ValueError: return 0

########################################################################
########################################################################
class Line:

    def __init__(self, coords):
        self.xstart, self.ystart, self.xend, self.yend = coords
        self.xmax = max(self.xstart, self.xend)
        self.ymax = max(self.ystart, self.yend)

    def __repr__(self):
        return "Line([%s, %s, %s, %s])" % (self.xstart, \
                                           self.ystart, \
                                           self.xend, \
                                           self.yend)

########################################################################
def Sanitize(FontDict):
  for Key in FontDict.keys():
    if Key not in string.ascii_letters:
      FontDict.pop(Key)

########################################################################
def MakeCharacterBigger(Char,Scale=2.0):
  for Line in Char.stroke_list:
    Line.xstart *= Scale  
    Line.xend   *= Scale  

########################################################################
def Parse(file):
  font = {}
  key = None
  num_cmds = 0
  line_num = 0
  for text in file:
      #format for a typical letter (lowercase r):
      ##comment, with a blank line after it
      #
      #[r] 3
      #L 0,0,0,6
      #L 0,6,2,6
      #A 2,5,1,0,90
      #
      line_num += 1
      end_char = re.match('^$', text) #blank line
      if end_char and key: #save the character to our dictionary
          font[key] = Character(key)
          font[key].stroke_list = stroke_list
          font[key].xmax = xmax
          if (num_cmds != cmds_read):
            print "(warning: discrepancy in number of commands %s, \
                   line %s, %s != %s )" \
                   % (fontfile, line_num, num_cmds, cmds_read)

      new_cmd = re.match('^\[(.*)\]\s(\d+)', text)
      if new_cmd: #new character
          key = new_cmd.group(1)
          num_cmds = int(new_cmd.group(2)) #for debug
          cmds_read = 0
          stroke_list = []
          xmax, ymax = 0, 0

      line_cmd = re.match('^L (.*)', text)
      if line_cmd:
          cmds_read += 1
          coords = line_cmd.group(1)
          coords = [float(n) for n in coords.split(',')]
          stroke_list += [Line(coords)]
          xmax = max(xmax, coords[0], coords[2])

      arc_cmd = re.match('^A (.*)', text)
      if arc_cmd:
          cmds_read += 1
          coords = arc_cmd.group(1)
          coords = [float(n) for n in coords.split(',')]
          xcenter, ycenter, radius, start_angle, end_angle = coords
          # since font defn has arcs as ccw, we need some font foo
          if ( end_angle < start_angle ):
              start_angle -= 360.0
          # approximate arc with line seg every 20 degrees
          segs = int((end_angle - start_angle) / 20) + 1
          angleincr = (end_angle - start_angle)/segs
          xstart = cos(start_angle * pi/180) * radius + xcenter
          ystart = sin(start_angle * pi/180) * radius + ycenter
          angle = start_angle
          for i in range(segs):
              angle += angleincr
              xend = cos(angle * pi/180) * radius + xcenter
              yend = sin(angle * pi/180) * radius + ycenter
              coords = [xstart,ystart,xend,yend]
              stroke_list += [Line(coords)]
              xmax = max(xmax, coords[0], coords[2])
              ymax = max(ymax, coords[1], coords[3])
              xstart = xend
              ystart = yend
  return font

########################################################################
def R(x,y,z):
  return sqrt(x**2 + y**2 + z**2)
########################################################################
def CartesianToPolar(x,y,z):
  return R(x,y,z),acos(z/R(x,y,z)), atan(y/R(x,y,z))

########################################################################
def PolarToCartesian(R, Theta, Phi):
  return R*sin(Theta)*cos(Phi), R*sin(Theta)*sin(Phi), R*cos(Theta)

########################################################################
def DrawLetters(FontDict, \
                   String, \
                   Distance=69, \
                   InitialHeight=0, \
                   InitialOffset=0, \
                   LetterSpacing=5):
  y = Distance #Distance from the wall will not change
  xOrigin = InitialOffset
  zOrigin = InitialHeight

  #Move To Starting Position
  ROrigin, ThetaOrigin, PhiOrigin = CartesianToPolar(0,y,0)
  RStart, ThetaStart, PhiStart = CartesianToPolar(xOrigin,y,zOrigin)

  for Char in String:
    for Line in FontDict[Char].stroke_list:
      x = Line.xstart+xOrigin; z = Line.ystart +zOrigin
      RStart, ThetaStart, PhiStart = CartesianToPolar(x,y,z)

      x = Line.xend+xOrigin; z = Line.yend
      REnd, ThetaEnd, PhiEnd = CartesianToPolar(x,y,z)

      MoveServos(ThetaEnd-ThetaStart, PhiEnd-PhiStart, 1)
    xOrigin += LetterSpacing
  
    MoveServos(xOrigin-ThetaEnd, zOrigin-PhiEnd, 0)


########################################################################
def PlotWord(FontDict, String):
  fig = plt.figure()
  plt.clf()
  ax = fig.add_subplot(111)
  Origin = 0
  for Char in String:
    Origin+=10
    for Line in FontDict[Char].stroke_list:
      res = ax.plot([int(Origin+Line.xstart),\
                     int(Origin+Line.xend)],\
                     [int(Line.ystart),\
                     int(Line.yend)])
    Origin+=10
  plt.ylim(ymin=-5,ymax=15)
  plt.show()

########################################################################
def MoveServos(Theta,Phi,Trigger):
  print 'Theta = ',Theta, 'Phi = ', Phi, \
        'Trigger = ' ,Trigger
  #Serial.write(chr(int(100*Theta)))
  #Serial.write(chr(int(100*Phi)))
  #Serial.write(chr(Trigger))
  Done = Serial.readline()

########################################################################
########################################################################
if __name__ == "__main__":
  if len(sys.argv) < 2:
    print "USAGE: Control.py FontFile InputString"
    exit()
  FontFile = sys.argv[1]
  InputString = sys.argv[2]
  try:
    File = open(FontFile)
  except:
    print 'ERROR: couldnt open file'
    exit()
  FontDict = Parse(File)
  Sanitize(FontDict)
  print InputString
  print FontDict['i']
  PlotWord(FontDict, InputString)
  MakeCharacterBigger(FontDict['R'])
  DrawLetters(FontDict, InputString, LetterSpacing =2)

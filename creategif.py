###############################################################################
#
# Gif creater from ordered set of png files
# Created by Daniel Nagy
# Date: 15/07/2021
# Version: 1.0.1
# HDS Sonochemistry Research Group
#
###############################################################################
#
# Usage:
# use with python and imageio installed
# Argument 1: string of the input file folder (domain folder)
# Argument 2: string of the output folder where the png-s are saved
# Argument 3: Length of original scene
# --slowdown: Slowdown of the gif
# --fps: Framerate of the gif (target)
# --loop: Set the number of loops. Default 0: loop forever
# --shorter: Makes the animation shorter
# --omitpr: Omits the progress bar
#
###############################################################################



#import libraries
import imageio
import argparse
import os
from os import listdir
from os.path import isfile, join

#argument parser
parser = argparse.ArgumentParser(description='Creates gif animations')
parser.add_argument('inputfolder', metavar='inp', type=str, nargs=1, help='input folder')
parser.add_argument('outputfile', metavar='out', type=str, nargs=1, help='output filename')
parser.add_argument('length', metavar='len', type=float, help='length of original')
parser.add_argument('--slowdown',action='store', metavar='spd',  default=1.0, type=float, help='slowdown compared to the original')
parser.add_argument('--fps',action='store', metavar='fps', type=int, default=30, help='target framerate')
parser.add_argument('--loop',action='store', type=int, default=0, help='set the number of loops. Default 0: loop forever')
parser.add_argument('--shorter',action='store', type=float, default=1.0, help='makes the animation shorter only x.xx of original')
parser.add_argument('--omitpr',action='store_false', help='omits the progress bar')
parser.add_argument('--debug',action='store_true', help='debug mode')
parser.add_argument('--version',action='version', version='Gif Creater 1.0.1')

args = parser.parse_args()

#important parameters
originalLength = args.length
slowdown = args.slowdown
targetFps = args.fps
loop = args.loop
shorter = args.shorter
progress = args.omitpr
debug = args.debug


print("----------------------------------------------------------------------")
print("                    Running the gif creater")
print("----------------------------------------------------------------------")

print('Original length:\n   ',originalLength,'s')
print('GIF slowdown:\n   ',slowdown,'x')
print('Target framerate:\n   ',targetFps,'fps')
print('Loops (0 is forever):\n   ',loop)

#settings
workingDirectory = os.getcwd()

#print working folders
folderSource = workingDirectory + '/' +  args.inputfolder[0]
fileOutput = workingDirectory + '/' + args.outputfile[0] + '.gif'
print("Input folder: \n   ",folderSource)
print("Output file: \n   ",fileOutput)

#function to read all png files
def listallPNG(folder):
    files = [f for f in listdir(folder) if isfile(join(folder, f))]
    return [folderSource+'/'+i for i in files if '.png' in i]

#read all gifs from the source
files = listallPNG(folderSource)
files.sort()
if debug:
    print("Input files:")
    print("   ",files)
length = len(files)

#calculate stuff
targetNumberOfFrames = targetFps * slowdown * originalLength
samplingRate = int(round(length / targetNumberOfFrames))
if samplingRate == 0:
    samplingRate = 1
    print("WARNING: Sampling rate set to 1 from 0")

print("Number of files:\n   ",length)
print("Targetted number of frames:\n   ",targetNumberOfFrames*shorter)
print("Sampling rate from original files:\n   ",samplingRate)

#calculate more stuff
numberOfFrames = int(length / samplingRate)
fps = numberOfFrames / (slowdown * originalLength)
fullLength = numberOfFrames/fps

print("Number of frames:\n   ",int(numberOfFrames*shorter))
print("Framerate:\n   ",fps,'fps')
print("Length of gif:\n   ",fullLength*shorter,'s')

#create the gif
counter = 0
with imageio.get_writer(fileOutput, mode='I',fps=fps,loop=loop) as writer:
    for file in files[0:int(length*shorter):samplingRate]:
        image = imageio.imread(file)
        writer.append_data(image)
        if progress:
            print(counter,'/',numberOfFrames)
            counter = counter + 1

print("GIF saved at\n   ",fileOutput)
print("Framerate:\n   ",fps,'fps')
print("Length of gif:\n   ",fullLength*shorter,'s')

print("----------------------------------------------------------------------")
print("                 End of the gif creator code")
print("----------------------------------------------------------------------")

###############################################################################
#
# Postprocessor script for ALPACA outputs using Paraview
# Created by Daniel Nagy (nagyd@edu.bme.hu)
# Date: 07/01/2022
# Version: 3D 1.0
# HDS Sonochemistry Research Group
#
###############################################################################
#
# Usage:
# use with pvpython
# Argument 1     : String of the input file folder (domain folder)
# Argument 2     : String of the output file where the png-s are saved
# --debug        : Shows debug information
# --savewave     : Save standing wave data in y position (bottom/middle/top/all)
# --savepics     : Save every snapshots
# --pmin,--pmax  : Bottom and top color limit on snapshot
# --nosavedata   : Do not save the bubble data
# --version      : Prints the current version
# --help         : Prints out the help menu
#
###############################################################################

#import paraview
from paraview.simple import *

#file reader from a directory
import os
from os import listdir
from os.path import isfile, join
from sys import exit
import time
import argparse
import shutil
import numpy as np

################################################################################

#    Argument parser

################################################################################
parser = argparse.ArgumentParser(description='Calculates important data from bubble simulations')
parser.add_argument('inputfolder', metavar='inp', type=str, help='Input folder')
parser.add_argument('outputfile', metavar='out', type=str, help='Output file name')
parser.add_argument('--debug',action='store_const', default=0, const=1, help='Debugger (1) on, (0) off')
parser.add_argument('--savepics',action='store_const', default=0, const=1, help='Saves every screenshot')
parser.add_argument('--savewave',action='store', type=str, default='none', help='Saves the standing wave to every snapshot. Save at (top), (bottom), (middle) or (all)')
parser.add_argument('--nosavedata',action='store_const',  default=1, const=0, help='Saves the bubble and inlet data')
parser.add_argument('--pmin',action='store', type=float, default=0.9e5, help='Minimal pressure on the scale')
parser.add_argument('--pmax',action='store', type=float, default=1.1e5, help='Maximal pressure on the scale')
parser.add_argument('--version',action='version', version='Paraview postprocessor (3D) 1.0')

#get the data from the command line arguments arguments
args = parser.parse_args()
debug = args.debug
savepics = args.savepics
savewave = args.savewave
savedata = args.nosavedata
pmin = args.pmin
pmax = args.pmax

################################################################################

#    Function definitions

################################################################################
def initFile(name):
    file = open(name,'w')
    file.write("time/x,")
    for x in np.linspace(leftSide,rightSide,200):
        file.write("{:.8f},".format(x))
    file.write("\n")
    return file

def initFiles(names):
    fileP = initFile(names[0])
    fileD = initFile(names[1])
    fileV = initFile(names[2])
    return [fileP,fileD,fileV]

def closeFiles(names):
    names[0].close()
    names[1].close()
    names[2].close()

def writeFileLine(writer,lineData,field,format):
    lineDataLen = lineData.GetPointData().GetArray(field).GetNumberOfValues()
    writer.write("{:.10f},".format(timesteps[i]))
    for j in range(0,lineDataLen-5,5):
        writer.write((format+",").format(lineData.GetPointData().GetArray(field).GetValue(j)))
    writer.write("\n")

def writeAllLines(writers,lineData):
    writeFileLine(writers[0],lineData,'pressure',"{:6.2f}")
    writeFileLine(writers[1],lineData,'density',"{:5.7f}")

    #velocity is more complicated
    lineDataLen = lineData.GetPointData().GetArray('velocity').GetNumberOfValues()
    writers[2].write("{:.10f},".format(timesteps[i]))
    for j in range(0,lineDataLen-5,15):
        vel = lineData.GetPointData().GetArray('velocity').GetValue(j)
        writers[2].write(("{:3.6f},").format(vel))
    writers[2].write("\n")



################################################################################

#    Initialization: path generation, printing important infos

################################################################################
print("----------------------------------------------------------------------")
print("                Start of the postprocessor code")
print("----------------------------------------------------------------------")

if debug:
    print("   Debug mode is on")

#print working folders
workingDirectory = os.getcwd()
input = workingDirectory + '/' +  args.inputfolder + '/domain'
print("Input folder : \n   ",input)

#generate the output file names
outputFolder = workingDirectory + '/' + args.outputfile
outputFile = outputFolder + '/data.csv'
outputWaveT = [outputFolder + '/wavePressureTop.csv',outputFolder + '/waveDensityTop.csv',outputFolder + '/waveVelocityTop.csv']
outputWaveM = [outputFolder + '/wavePressureMiddle.csv',outputFolder + '/waveDensityMiddle.csv',outputFolder + '/waveVelocityMiddle.csv']
outputWaveB = [outputFolder + '/wavePressureBottom.csv',outputFolder + '/waveDensityBottom.csv',outputFolder + '/waveVelocityBottom.csv']
print("Output folder: \n   ",outputFolder,"Saving pictures here")
print("Output file  : \n   ",outputFile)

#create folder
if os.path.exists(outputFolder):
    print('Deleting old folder ...')
    #os.remove(outputFolder)
    shutil.rmtree(outputFolder)

print('Creating folder ...')
os.makedirs(outputFolder)

if savedata:
    print('Bubble data is saved ...')
else:
    print('Bubble data is *not* saved ...')

#saving the standing wave
saveBottom = False
saveMiddle = False
saveTop = False
if savewave == 'none':
    print("Standing wave will not be saved ...")
else:
    print("Standing wave will be saved ...")
    printFlag = False
    if savewave == 'bottom':
        print("   at the bottom")
        printFlag = True
        saveBottom = True
    if savewave == 'top':
        print("   at the top")
        printFlag = True
        saveTop = True
    if savewave == 'middle':
        print("   in the middle")
        printFlag = True
        saveMiddle = True
    if savewave == 'all':
        print("   at the bottom, top and in the middle")
        printFlag = True
        saveBottom = True
        saveMiddle = True
        saveTop = True
    if printFlag is False:
        print("error, command line option",savewave,'is invalid')
        exit()

#read all xdmf files from the folder
files = [f for f in listdir(input) if isfile(join(input, f))]
files = [input+'/'+i for i in files if '.xdmf' in i and 'data_time_series' not in i]
length = len(files)
if debug:
    #print("   All files: \n   ",files)
    print("   Number of files:\n   ",length)

#import to paraview
rawData = XDMFReader(registrationName='data',FileNames=files)
if debug:
    print("   XDMF reader setup")

#reader
reader = GetActiveSource()
timesteps = reader.TimestepValues
if debug:
    print("   Data read")

################################################################################

#    Get the parts of the flow area (bubble, inlet) and paraview setup

################################################################################
#get extreme points
QuerySelect(QueryString='(pointIsNear([(1000,1000,0),],2000, inputs))',FieldType="POINT",InsideOut=0)
topRight = ExtractSelection(registrationName="Top right",Input=rawData)
topRightData = paraview.servermanager.Fetch(topRight)
topRightCoord = topRightData.GetPoint(0)
ClearSelection()

SetActiveSource(rawData)
QuerySelect(QueryString='(pointIsNear([(-1000,-1000,0),],2000, inputs))',FieldType="POINT",InsideOut=0)
bottomLeft = ExtractSelection(registrationName="Bottom left",Input=rawData)
bottomLeftData = paraview.servermanager.Fetch(bottomLeft)
bottomLeftCoord = bottomLeftData.GetPoint(0)

#print extreme point data
print("Corners found:")
print("   Bottom left:  (",bottomLeftCoord[0],",",bottomLeftCoord[1],")")
print("   Top right  :  (",topRightCoord[0],",",topRightCoord[1],")")

middleCoord = (topRightCoord[1] + bottomLeftCoord[1])/2
bottomCoord = 0.01*topRightCoord[1] + 0.99*bottomLeftCoord[1]
topCoord = 0.99*topRightCoord[1] + 0.01*bottomLeftCoord[1]
leftSide = bottomLeftCoord[0]
rightSide = topRightCoord[0]
if saveTop:
    print("Top coordinate    y=",topCoord)
if saveMiddle:
    print("Middle coordinate y=",middleCoord)
if saveBottom:
    print("Bottom coordinate y=",bottomCoord)

#select the bubble from the picture
bubble = Threshold(registrationName='Water', Input=rawData)
bubble.Scalars = ['CELLS', 'levelset']
bubble.ThresholdRange = [-10, 0]
if debug:
    print("   Bubble found")


#select inlet from the picture
inlet = Clip(registrationName='Inlet', Input=rawData)
inlet.ClipType = 'Plane'
inlet.ClipType.Origin = [0.001, 0.01, 0.000]
if debug:
    print("   Inlet found")

#get the render view and turn off the axes
view = GetActiveViewOrCreate('RenderView')

#color the water by density
bubbleDisplay = GetDisplayProperties(bubble, view=view)
ColorBy(bubbleDisplay, ('CELLS', 'pressure'))
bubbleDisplay.SetScalarBarVisibility(view,True)

#change color bar
pressureLUT = GetColorTransferFunction('pressure')
pressureLUT.RGBPoints = [pmin,0.0,0.0,1.0,pmax,1.0,0.0,0.0]
if debug:
    print("   Colorbars setup")

#animation, and display ALL frames
animation = GetAnimationScene()
animation.NumberOfFrames = length
ResetCamera()
if debug:
    print("   Camera setup")

#open filewriter
file = open(outputFile,'w')
file.write("step,time,pressureB,densityB,volumeB,Rx,Ry,pressureI,densityI,massB\n")

fileT, fileM, fileB = 0, 0, 0
if saveTop:
    fileT = initFiles(outputWaveT)
if saveMiddle:
    fileM = initFiles(outputWaveM)
if saveBottom:
    fileB = initFiles(outputWaveB)
if debug:
    print("   Filewriters open")


################################################################################

#    Loop through each hdf5 file

################################################################################
counter = 0
for i in range(length):
    Show(bubble)
    if savepics:
        SaveScreenshot(outputFolder+'/pics_'+ '{:0>6}'.format(str(i))+'.png')
    animation.GoToNext()
    if i/length*100 > counter:
        counter = int(i/length*100) + 1
        print("{:d}".format(counter)+'%')

    if savedata:
        #calculate the pressure and density in the bubble
        integrateBubble = IntegrateVariables(registrationName="Integrate Bubble",Input=bubble)
        integrateBubble.DivideCellDataByVolume = 1
        integrateBubbleData = paraview.servermanager.Fetch(integrateBubble)
        bubbleData = paraview.servermanager.Fetch(bubble)
        pressureB = integrateBubbleData.GetCellData().GetArray('pressure').GetValue(0)
        densityB = integrateBubbleData.GetCellData().GetArray('density').GetValue(0)

        #get bubble datasets
        bubblePoints = paraview.servermanager.Fetch(bubble)
        bubblePointsNr = bubblePoints.GetNumberOfPoints()
        bubbleCellsNr = bubbleData.GetCellData().GetArray('density').GetNumberOfValues()
        cellSizes = paraview.servermanager.Fetch(CellSize(registrationName='Cell Sizes', Input=bubble))

        #calculate bubble mass and volume
        massB = 0
        volumeB = 0
        for j in range(bubbleCellsNr):
            vol = cellSizes.GetCellData().GetArray('Volume').GetValue(j)
            volumeB = volumeB + vol
            massB = massB + vol * bubbleData.GetCellData().GetArray('density').GetValue(j)

        #calculate bubble radius
        minX, maxX = 10000, 0
        minY, maxY = 10000, 0
        for j in range(bubblePointsNr):
            p = bubblePoints.GetPoint(j)
            x = p[0]
            y = p[1]
            if x > maxX:
                maxX = x
            if x < minX:
                minX = x
            if y > maxY:
                maxY = y
            if y < minY:
                minY = y

        rx = 0.5*(maxX-minX)
        ry = 0.5*(maxY-minY)

        #calculate the pressure and density at the inlet
        Show(inlet)
        integrateInlet = IntegrateVariables(registrationName="Integrate Inlet",Input=inlet)
        integrateInlet.DivideCellDataByVolume = 1
        integrateInletData = paraview.servermanager.Fetch(integrateInlet)
        pressureI = integrateInletData.GetCellData().GetArray('pressure').GetValue(0)
        densityI = integrateInletData.GetCellData().GetArray('density').GetValue(0)
        Hide(inlet)

        file.write("{:d},{:.10f},{:.20f},{:.20f},{:.20f},{:.20f},{:.20f},{:.20f},{:.20f},{:.20f}\n".format(i+1,timesteps[i],pressureB,densityB,volumeB,rx,ry,pressureI,densityI,massB))

    #save standing wave
    Show(rawData)
    if saveTop:
        pltOverLine = PlotOverLine(registrationName='Plot Top',Input=rawData)
        pltOverLine.Source.Point1 = [leftSide, topCoord, 0]
        pltOverLine.Source.Point2 = [rightSide, topCoord, 0]
        lineData = paraview.servermanager.Fetch(pltOverLine)
        writeAllLines(fileT,lineData)

    if saveMiddle:
        pltOverLine = PlotOverLine(registrationName='Plot Middle',Input=rawData)
        pltOverLine.Source.Point1 = [leftSide, middleCoord, 0]
        pltOverLine.Source.Point2 = [rightSide, middleCoord, 0]
        lineData = paraview.servermanager.Fetch(pltOverLine)
        writeAllLines(fileM,lineData)

    if saveBottom:
        pltOverLine = PlotOverLine(registrationName='Plot Bottom',Input=rawData)
        pltOverLine.Source.Point1 = [leftSide, bottomCoord, 0]
        pltOverLine.Source.Point2 = [rightSide, bottomCoord, 0]
        lineData = paraview.servermanager.Fetch(pltOverLine)
        writeAllLines(fileB,lineData)

    Hide(rawData)

#end of loop

################################################################################

#    End of script, close files

################################################################################
file.close()
if saveTop:
    closeFiles(fileT)
if saveMiddle:
    closeFiles(fileM)
if saveBottom:
    closeFiles(fileB)
if debug:
    print("   Filewriters closed")


print("----------------------------------------------------------------------")
print("                 End of the postprocessor code")
print("----------------------------------------------------------------------")

##------------------------------------------------##
## MONTAGES MODULE FOR PYTHON 3.X                 ##
##------------------------------------------------##
##                                                ##
## Release: 11/09/2019 (v 1.0)                    ##
## Git: https://github.com/vivien-walter/montages ##
##                                                ##
## Author: Vivien WALTER                          ##
## Contact: walter.vivien@gmail.com               ##
##------------------------------------------------##

import math
import os
import pims
import sys

import matplotlib.font_manager as fontman
import numpy as np

from glob import glob
from PIL import ImageFont, Image, ImageDraw
from skimage import io

##-\-\-\-\-\-\-\-\-\
## PRIVATE FUNCTIONS
##-/-/-/-/-/-/-/-/-/

#--------------------------------------------
# Check the last character of the folder path
def _checkPath(pathToFile, lastCharacter='/'):

    # Append the last character if it's missing
    if pathToFile[-1] != lastCharacter:
        pathToFile += lastCharacter

    return pathToFile

#--------------------------
# Calculate the time limits
def _time_limits(maxFrame, begin=0, end=None):

    # Correct the value of the first frame read
    if begin < 0:
        begin = 0
    elif begin >= maxFrame:
        begin = maxFrame - 1

    # Correct the value of the last frame read
    if end is None or end >= maxFrame:
        end = maxFrame
    if end <= begin:
        end = begin+1

    return begin, end

#-------------------------------
# Find the closes squared number
def _closest_square(number):

    # Initialise
    i = 0
    j = 1
    top_square = 0

    # Search for the pairs of numbers surrounding the reference
    while top_square < number:

        # Calculate the number
        i += 1
        j += 1
        bottom_square = i ** 2
        top_square = j ** 2

    # Select the one closest to the number
    if abs(number - i**2) < abs(number - j**2):
        return i
    else:
        return j

#-------------------
# Find font location
def _findFont(fontName = 'Arial.ttf'):

    # Look for the font location on the computer
    matches = list(filter(lambda path: fontName in os.path.basename(path), fontman.findSystemFonts()))

    return matches[0]

#-------------------------------------------
# Determine the font size for the image text
def _getFontSize(text, fontPath, sizeLimit):

    # Initialise the function
    fontSize = 1
    font = ImageFont.truetype(fontPath, fontSize)

    # Loop until the size is found
    while font.getsize(text)[0] < sizeLimit:
        fontSize += 1
        font = ImageFont.truetype(fontPath, fontSize)

    return fontSize - 1

#--------------------------------------------------
# Generate the text array associated with the image
def _textArray(text, imageSize, fontSize = None, fontPath = None, padding=10, position='bottom', color='white'):

    # Get the color values
    if color == 'white':
        backgroundColor = 0
        textColor = 255
    else:
        backgroundColor = 255
        textColor = 0

    # Generate the image to draw
    textImage = Image.new('L', imageSize, color=(backgroundColor))

    # Get the font size for the text and font path if required
    if fontPath is None:
        fontPath = _findFont()

    if fontSize is None:
        sizeLimit = imageSize[1] - 2*padding
        fontSize = _getFontSize(text, fontPath, sizeLimit)

    # Calculate the position from the top edge of the image
    textFont = ImageFont.truetype(fontPath, fontSize)
    textSize = textFont.getsize(text)

    if position == 'top':
        topPosition = padding

    else:
        topPosition = imageSize[1] - (padding + textSize[1])

    # Draw the text on the image
    textDrawing = ImageDraw.Draw(textImage)
    textDrawing.text((padding,topPosition), text, fill=(textColor), font=textFont)

    return np.array(textImage)

#-----------------------------------------------
# Generate the text array to write on the images
def _generateTextList(imageSize, fileNames = None, timeList = None, timeUnit = 'frame', textType = 'file', textSize = None, textFont= 'Arial.ttf', padding=10, position='bottom', color='white'):

    # Get the font path
    fontPath = _findFont(fontName = textFont)

    # Get the size limit
    sizeLimit = imageSize[1] - 2*padding

    # Generate text based on file name
    textList = []

    # CASE 1: Text type is file name
    if textType == 'file':

        # Calculate the text size
        if textSize is None:
            longestName = max(fileNames, key=len)
            textSize = _getFontSize(longestName, fontPath, sizeLimit)

        # Generate the array of text
        for name in fileNames:
            textArray = _textArray(name, imageSize, fontSize = textSize, fontPath = fontPath, padding = padding, position=position, color=color)
            textList.append( np.copy(textArray) )

    # CASE 2: Text type is the type stamp
    elif textType == 'time':

        # Generate the time stamp list
        timeStamps = [ str(x) + ' ' + timeUnit for x in timeList ]

        # Calculate the text size
        if textSize is None:
            longestName = max(timeStamps, key=len)
            textSize = _getFontSize(longestName, fontPath, sizeLimit)

        # Generate the array of text
        for stamp in timeStamps:
            textArray = _textArray(stamp, imageSize, fontSize = textSize, fontPath = fontPath, padding = padding, position=position, color=color)
            textList.append( np.copy(textArray) )

    return textList

##-\-\-\-\
## CLASSES
##-/-/-/-/

# Class to handle the single image object
class imageObject:

    def __init__(self, imageSequence, stack=True, filePath=None):

        # Initialise the arrays for the image
        self.raw = imageSequence
        self.treated = np.copy(np.array(self.raw))

        # Get the metadata
        frameNumber = len(self.treated)
        self.time = np.arange(frameNumber)

        # Generate the titles
        if stack:
            self.title = [filePath + ' frame ' + str(i) for i in range(frameNumber)]
        else:
            self.title = self.raw._filepaths

        # Initialise further arrays
        self.text = None

    # Reset the images
    def _reset(self):

        self.treated = np.copy(np.array(self.raw))

# Class to handle the stack
class imageStack:

    def __init__(self, objectPath, stack=True, filePath = None ):

        # Get the image and the relevant informations
        self.image = imageObject( pims.open(objectPath), stack=stack, filePath=objectPath )
        self.size = self.image.raw[0].shape
        self.type = self.image.raw[0].dtype
        self.totalFrame = len(self.image.raw)
        self.selectedFrame = self.totalFrame

        # Initialise the selection for the montage
        self.setSelection()
        self.setTimeScale()
        self.setMontage()

        # Initialise some inner variables
        self.isTextDisplayed = False

    # Rescale the intensity by a given factor
    def scaleIntensity(self, scaleFactor):

        self.image.treated = self.image.treated * scaleFactor

    # Create a selection for the montage
    def setSelection(self, begin=0, end=None, skip=0, maxFrame=None):

        # Get the time limits for the montage
        begin, end = _time_limits(self.totalFrame, begin=begin, end=end)
        skip += 1

        # Get the frame selection
        self.frameSelection = np.arange(int(begin), int(end), int(skip))

        # Adjust the selection
        if maxFrame is not None:
            if len(self.frameSelection) > maxFrame:
                self.frameSelection = self.frameSelection[0:int(maxFrame)]

        # Update the number of frames
        self.selectedFrame = self.frameSelection.shape[0]

    # Set the time scale of the stack
    def setTimeScale(self, scale=1, unit='frame'):

        # Scale the image selection
        self.image.time = np.arange(len(self.image.title)) * scale

        # Save the parameters
        self.timeScale = scale
        self.timeUnit = unit

    # Display text on the slides
    def setText(self, textType='file', textSize = None, textFont = 'Arial.ttf', padding=10, position = 'bottom', color='white', resetText=True):

        # Check if there is already text on the images
        if self.isTextDisplayed and resetText:
            self.image._reset()

        # Generate the text based on the type
        if textType == 'file':
            self.image.text = _generateTextList(self.size, fileNames = self.image.title, textType = textType, textSize = textSize, textFont= textFont, padding=padding, position=position)
        elif textType == 'time':
            self.image.text = _generateTextList(self.size, timeList = self.image.time, timeUnit = self.timeUnit, textType = textType, textSize = textSize, textFont= textFont, padding=padding, position=position)

        # Define the color
        if color == 'white':
            textColor = np.iinfo(self.type).max
        else:
            textColor = 0

        # Copy the text on the image
        for i, frameText in enumerate(self.image.text):
            self.image.treated[i][frameText == 255] = textColor

        self.isTextDisplayed = True

    # Set the montage properties
    def setMontage(self, column = None, row = None, margin=0, blackMargin=True):

        # Get the number of images in the selection
        imageNumber = self.selectedFrame

        # Calculate the number of columns and rows
        if column is None and row is None:
            column = _closest_square(imageNumber)
            row = math.ceil(imageNumber / column)
        elif row is None:
            row = math.ceil(imageNumber / column)
        elif column is None:
            column = math.ceil(imageNumber / row)

        # Calculate the size of the new array
        height = row * self.size[0] + (row-1) * margin
        width = column * self.size[1] + (column-1) * margin

        # Save the values
        self.montageSize = (height, width)
        self.montageTable = (row, column)
        self.montageMargin = margin
        self.blackMargin = blackMargin

##-\-\-\-\-\-\-\-\
## PUBLIC FUNCTIONS
##-/-/-/-/-/-/-/-/

#------------------------------------
# Load the image from the folder path
def loadImages(folder=None, stackFile=None):

    # Raise an error if the arguments are wrong
    if (folder is None and stackFile is None) or (folder is not None and stackFile is not None):
        sys.exit('ERROR: Exactly one argument is expected (folder= or stackFile=).')

    # Check and correct the input folder path if given
    elif folder is not None:
        input_folder = _checkPath(folder)+'/*'
        imageObject = imageStack(input_folder, stack=False)

    # Open the stack file if given
    elif stackFile is not None:
        imageObject = imageStack(stackFile)

    return imageObject

#-----------------
# Make the montage
def makeMontage(images):

    # Initialise a blank array
    montageArray = np.zeros(images.montageSize, images.type)

    # Change the type of margin
    if not images.blackMargin:
        montageArray[:] = np.iinfo(images.type).max

    # Populate the array
    for i, imageIndex in enumerate(images.frameSelection):

        # Stop if the number of images is greater than the size of the given table
        if i >= images.montageTable[0]*images.montageTable[1]:
            break

        # Get the index of the array in the table
        rowIndex = i // images.montageTable[1]
        columnIndex = i % images.montageTable[1]

        # Get the indices of the pixel in the wide array
        xPixelStart = columnIndex * (images.size[1] + images.montageMargin)
        xPixelStop = xPixelStart + images.size[1]
        yPixelStart = rowIndex * (images.size[0] + images.montageMargin)
        yPixelStop = yPixelStart + images.size[0]

        # Copy the images into the new array
        montageArray[yPixelStart:yPixelStop,xPixelStart:xPixelStop] = images.image.treated[imageIndex]

    return montageArray

#-----------------------------
# Save the montage into a file
def saveMontage(montage, fileName='untitled.tif'):

    io.imsave(fileName, montage)

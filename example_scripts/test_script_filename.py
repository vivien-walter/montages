# EXAMPLE SCRIPT
# Module montages
# 10/09/2019 - Vivien WALTER

# This example script presents how the module can be used to open images inside
# a folder, make a montage of the 25 first images and write the name of the file
# on each image of the montage.

# STEP 1: Import the module in your script at the top of it
import montages as mn

# STEP 2: Load the images from the folder
images = mn.loadImages(folder='test_folder/') # Always specify if you are loading a folder or a single file

# STEP 3 : Rescale the intensity of the image
images.scaleIntensity(10) # The intensity of all images is rescaled using the given factor

# STEP 4: Adjust the selection of frames

# NOTE: All of these settings are automatically generated in the previous step
# with all the images in the folder. We are just making specific choices here

images.setSelection(
                    begin=0, # (OPT.) Specify the index of the first frame
                    end=None, # (OPT.) Specify the index of the last frame - if set to None, auto-calculation
                    skip=0, # (OPT.) Select the number of frames to skip - if set to 0, all frames will be read
                    maxFrame=25 # (OPT.) Select the maximum number of frames to select for the montage - if set to None
                    )

# STEP 5: Edit the image to add the desired text

# We add here the name of the file at the bottom of the image

images.setText(
                textType='file', # (OPT.) Type of text to write, can chose between 'file' name and 'time' stamp - Default is 'file'
                textSize = None, # (OPT.) Size for the text - If not specified, the size is calculated automatically
                textFont = 'Arial.ttf', # (OPT.) Font to use for the text - Default is 'Arial.ttf'
                padding = 10, # (OPT.) Distance in pixel between the text and the edge of the image - Default is 10 px
                position = 'bottom', # (OPT.) Position of the text, can chose between 'top' and 'bottom' - Default is 'bottom'
                color = 'white' # (OPT.) Color of the text, can chose between 'black' and 'white' - Default is 'white'
                )

# STEP 6: Generate the image array for the montage

# 6.1 We set the parameters of the montage

# NOTE: The montage settings are automatically generated in the first step for
# all the images in the folder. We are just specifying here that we want a white
# 10px wide margin in between each frame.

images.setMontage(
                column=None, # (OPT.) Specify the number of columns - if not specified, it will be automatically calculated
                row=None, # (OPT.) Specify the number of rows - if not specified, it will be automatically calculated
                margin=10, # (OPT.) Specify the size of the margin between frames in the montage - if not specified, there will be no margin
                blackMargin = False
                )

# 6.2 We generate the montage array
montage = mn.makeMontage(images)

# STEP 7: Save the image in the destination folder

mn.saveMontage(montage, fileName='test_filename.tif')

# montages
Python 3 module to create montages of images taken from a folder or from a stack file (.tif)

## Instructions

### Standard functions

#### 1. Loading the images to make a montage with

All the images from a folder can be directly loaded into an object using the **loadImages** function of the module.

```python
import montages as mn

images = mn.loadImages(folder='test_folder/')
```

The module will load all files inside the folder, so be careful to not mix with non-image files or images from a different sequence.

Alternatively, you can load a stack file with the same function.

```python
import montages as mn

images = mn.loadImages(stackFile='test.tif')
```

#### 2. Creating the montage

When the images are loaded into an object, the module generates basic parameters for the montage so it can be used straight.
The montage can therefore be created using the function **makeMontage**.

```python
montageArray = mn.makeMontage(images)
```

The output of the function is a NumPy array containing all the pixel values of the montage.

To edit the parameters of the montage, please refer to the section *Setting the parameters for the montage* below.

#### 3. Saving the montage into a file

Once the pixel value array of the montage has been generated, it can be directly saved into an image file using the function **saveMontage**

```python
mn.saveMontage(montageArray, fileName='output_file.tif')
```

Alternatively, since the montage is here a simple NumPy array, it can be saved by using the method of your choice.

### Setting the parameters for the montage

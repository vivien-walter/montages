from setuptools import setup

setup(name='montages',
      version='1.0',
      description='Generation of images montages from a folder or an image stack',
      url='https://github.com/vivien-walter/montages',
      author='Vivien WALTER',
      author_email='walter.vivien@gmail.com',
      packages=['montages'],
      install_requires = [
      'numpy',
      'pims',
      'matplotlib',
      'pillow',
      'scikit-image'
      ])

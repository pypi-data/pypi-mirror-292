from setuptools import setup, find_packages
import os
from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

VERSION = '1.0.1' 
DESCRIPTION = 'GestureControlMouseScroll'
LONG_DESCRIPTION = 'Gesture Control of Mouse and Scroll using Mediapipe and OpenCV This code allows you to move your cursor and scroll the screen with your finger tips. The mediapipe library detects one of your hands and creates a map of landmarks. It then detects the number of fingers up. In case your index finger is up, your cursor will be moved according to your index finger tip. Clicking is realized via retracting your index finger. You can scroll down the screen by retracting your index and middle finger simultaneously.'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="gesturecontrolmousescroll", 
        version=VERSION,
        homepage="http://www.emanuelbierschneider.de/",
        author="Emanuel Bierschneider",
        author_email="<emanuel.bierschneider@gmx.de>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_reqs = required,
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'first package'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)
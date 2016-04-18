from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import *
import o3d3xx
import sys
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


imageWidth = 176
imageHeight = 132

class GrabO3D300():
    def __init__(self,data):
        self.data = data
        self.Amplitude = np.zeros((imageHeight,imageWidth))
        self.Distance = np.zeros((imageHeight,imageWidth))

    def readNextFrame(self):
        result = self.data.readNextFrame()
        self.Amplitude = np.frombuffer(result['amplitude'],dtype='uint16')
        self.Amplitude = self.Amplitude.reshape(imageHeight,imageWidth)
        self.Distance = np.frombuffer(result['distance'],dtype='uint16')
        self.Distance = self.Distance.reshape(imageHeight,imageWidth)
        self.illuTemp = 20.0

def updatefig(*args):
    g = args[1]
    g.readNextFrame();
    imAmp = args[2]
    amp_max = float(max(np.max(g.Amplitude),1));
    imAmp.set_array(g.Amplitude/ amp_max)
    axAmp = imAmp.get_axes()
    axAmp.set_title('Amplitude (Illu temp: %0.2f)'%(g.illuTemp))

    imDist = args[3]
    dist_max = float(max(np.max(g.Distance),1));
    imDist.set_array(g.Distance/ dist_max)
    axDist = imDist.get_axes()
    axDist.set_title('Distance')
    return imAmp,imDist,

def main():
    address = sys.argv[1]
    camData = o3d3xx.ImageClient(address, 50010)

    fig = plt.figure()
    grabber = GrabO3D300(camData)
    ax1 = fig.add_subplot(1, 2, 1)
    ax2 = fig.add_subplot(1, 2, 2)
    imAmplitude = ax1.imshow(np.random.rand(imageHeight,imageWidth))
    imDistance = ax2.imshow(np.random.rand(imageHeight,imageWidth))
    ani = animation.FuncAnimation(fig, updatefig, interval=50, blit=True, fargs = [grabber,imAmplitude,imDistance])
    plt.show()

if __name__ == '__main__':
    main()


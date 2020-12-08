from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import *
import o3d3xx
import sys
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


imageWidth = 224
imageHeight = 172

class GrabO3D300():
    def __init__(self,data):
        self.data = data
        self.Amplitude = np.zeros((imageHeight,imageWidth))
        self.Distance = np.zeros((imageHeight,imageWidth))

    def readNextFrame(self):
        result = self.data.readNextFrame()
        self.Amplitude = np.asarray(result['amplitude'])
        self.Amplitude = self.Amplitude.reshape(imageHeight,imageWidth)
        self.Distance = np.asarray(result['distance'])
        self.Distance = self.Distance.reshape(imageHeight,imageWidth)
        self.illuTemp = 20.0

def updatefig(*args):
    g = args[1]
    g.readNextFrame();
    imAmp = args[2]
    amp_max = float(max(np.max(g.Amplitude),1));
    imAmp.set_array(g.Amplitude/ amp_max)

    imDist = args[3]
    dist_max = float(max(np.max(g.Distance),1));
    imDist.set_array(g.Distance/ dist_max)
    return imAmp,imDist,

def main():
    address = sys.argv[1]
    camData = o3d3xx.ImageClient(address, 50010)

    fig = plt.figure()
    grabber = GrabO3D300(camData)
    ax1 = fig.add_subplot(1, 2, 1)
    ax1.set_title('Amplitude')
    ax2 = fig.add_subplot(1, 2, 2)
    ax2.set_title('Distance')
    imAmplitude = ax1.imshow(np.random.rand(imageHeight,imageWidth))
    imDistance = ax2.imshow(np.random.rand(imageHeight,imageWidth))
    ani = animation.FuncAnimation(fig, updatefig, interval=50, blit=True, fargs = [grabber,imAmplitude,imDistance])
    plt.show()

if __name__ == '__main__':
    main()


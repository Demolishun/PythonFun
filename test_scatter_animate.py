#!/usr/bin/env python
"""
    A fun little app that switches between plots.
    It uses a DSP low pass filter to gradually change a point from
    one value to another value.  This creates a smooth animation where points
    move from one position to another.

    Copyright 2018 Frank Carney
"""


import matplotlib
import matplotlib.pyplot as pyplot
import matplotlib.animation as animation
import numpy as np
import random
import time
from collections import OrderedDict

# encapsulate everything in an object for convenience
class ScatterAnim(object):
    def __init__(self, sleep=False):
        # determines tolerance of how close the values need to be to switch to next mode
        self.tol = 0.05 #0.1  #0.05

        # scale
        self.x = 1.0
        self.y = 1.0

        # number of sine cycles
        self.cycles = 4

        # number of data points
        self.points = 64 * self.cycles
        self.time = self.cycles * np.pi

        # create various function data sets for x and y
        self.x1 = np.linspace(0, self.time, self.points)
        self.y1 = np.sin(self.x1)
        self.y2 = np.cos(self.x1)
        self.y3 = self.y1 * self.y2
        self.y4 = self.y1 * self.y2 / (self.y1 - self.y2)
        self.y5 = np.tan(self.x1)/4
        self.x2 = np.sin(self.x1) * self.cycles + self.time/2
        self.y6 = np.cos(self.x1) * self.x1/(self.points/16)
        self.x3 = np.sin(self.x1) * self.x1/2 + self.time/2
        self.y7 = np.sin(2*np.sin(2*np.sin(2*np.sin(self.x1))))

        delta = np.pi/4.0
        a = 3
        b = 4
        tdiv = 4.0
        t = np.linspace(-self.time/tdiv,self.time/tdiv,self.points)
        self.x4 = np.sin(a * t + delta)*4.0+self.time/2.0
        self.y8 = np.sin(b * t)

        self.xwork = np.copy(self.x1)
        self.ywork = np.copy(self.y1)

        self.mode = 1
        self.ylist = OrderedDict([
            ("sin", (self.x1, self.y1)),
            ("cos", (self.x1, self.y2)),
            ("sin*cos", (self.x1, self.y3)),
            ("parabola",(self.x1, self.y4)),
            ("tan",(self.x1, self.y5)),
            ("circle",(self.x2, self.y2)),
            ("spiral",(self.x3, self.y6)),
            ("approx square",(self.x1, self.y7)),
            ("lissajous",(self.x4, self.y8)),
        ])
        #print len(self.ylist), self.ylist
        #self.ylist = [(self.x1, self.y1), (self.x1, self.y2), (self.x1, self.y3), (self.x1, self.y4), (self.x1, self.y5), (self.x2, self.y2), (self.x3, self.y6)]
        #self.ylist = [(self.x1, self.y1), (self.x2, self.y2),]

        # determine DSP filter value for each plot
        self.clist = [0.1, 0.1, 0.1, 0.2, 0.1, 0.1, 0.2, 0.1, 0.1]

        # create the figure
        self.fig = pyplot.figure()
        self.ax = self.fig.add_subplot(111)
        self.ax.grid()

        self.ani = animation.FuncAnimation(self.fig, self.update, interval=20,
            init_func=self.setup_plot, blit=True,
            repeat=False) #, frames=30) # limit frames

        # seed the random generator
        random.seed()

        # determine if a sleep is required before starting animation
        self.first = sleep

        #self.text1 = self.ax.text(0, 1.0,  "plot function")
        self.text1 = self.fig.text(0.05, 0.95,  "plot function")

    # prepare plot
    def setup_plot(self):
        self.ax.axis([-0.5, self.time+0.5, -self.y*1.1, self.y*1.1])
        self.scat = self.ax.scatter(self.xwork, self.ywork, c="tomato", s=20, animated=True)
        #self.scat, = self.ax.plot(self.xwork, self.ywork, linewidth=2.0, animated=True)

        return self.scat,

    def update(self, i):
        if self.first:
            time.sleep(20)
            self.first = False

        #self.x1 = self.analog_filter(self.x1, self.x2, 0.01)

        # get mode
        keys = self.ylist.keys()
        name = keys[self.mode]
        data = self.ylist[name]

        # filter values to next set of values
        self.xwork = self.analog_filter(self.xwork, data[0], self.clist[self.mode])
        self.ywork = self.analog_filter(self.ywork, data[1], self.clist[self.mode])

        # if values are "close" to each other within a tolerance then change modes
        if np.allclose((self.xwork, self.ywork), data, atol=self.tol):
            # randomly select mode from list
            #self.mode += 1
            #if self.mode > (len(self.ylist)-1):
            #    self.mode = 0
            mode = self.mode
            while mode == self.mode:
                mode = random.randrange(0, len(self.ylist), 1)
            self.mode = mode
            modetext = "changed mode: {0}".format(keys[self.mode])
            self.text1.set_text(modetext)
            #print modetext
            pyplot.draw()

        # perform animation update
        #self.scat = self.ax.scatter(self.xwork, self.ywork, c="tomato", s=20, animated=True)
        #self.scat.set_offsets(np.array([self.xwork,self.ywork]).transpose())
        #print type(self.scat)
        if isinstance(self.scat, matplotlib.lines.Line2D):
            self.scat.set_xdata(self.xwork)
            self.scat.set_ydata(self.ywork)
        elif isinstance(self.scat, matplotlib.collections.PathCollection):
            self.scat.set_offsets(np.array([self.xwork,self.ywork]).transpose())

        return self.scat,

    # get the ball rolling
    def show(self):
        try:
            pyplot.show()
        except AttributeError as e:
            # eat error from lib
            pass
            #print "Exception {0}".format(e)

    # DSP low pass filter
    def analog_filter(self, old, new, factor=0.1):
        old = old * (1.0 - factor) + new * factor
        return old

def main():

    # use this to delay for making a video
    #a = ScatterAnim(sleep=True)
    # use this for normal viewing
    a = ScatterAnim()

    # not plotting anything in movie
    # Don't try this, it is busted and does not work.  I used CamStudio to make the video on youtube.
    #a.ani.save('scatter_transform.mp4', fps=30, codec='libx264')

    a.show()

if __name__ == '__main__':
    main()


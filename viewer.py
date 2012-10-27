from pylab import *
try:
    from PIL import Image
except ImportError, exc:
    raise SystemExit("PIL must be installed to run this example")
import ImageOps
from tiledImage import TiledImage as TI
from time import time
import Image as im


class Viewer:
    def __init__(self, folder,topLayer):
        import os
        print os.getcwd()
        '''
        This is the viewer used to view a tiled image (Ti)
        
        '''
        self.topLayer = topLayer
        self.time1 = time()
        self.Ti = TI(folder)
        print self.Ti.picSize
        self.size = self.Ti.picSize
        self.lena = self.Ti.getBlock((00,00),(self.size[0],self.size[1]),self.topLayer)
        #self.lena.show()
        self.ul = self.Ti.UpperLeft
        self.lr = self.Ti.LowerRight
        self.zoom = self.topLayer
        self.coords = []
        
    
    def haveAllCoords(self):
        return len(self.coords)==8
    def show(self):
        self.figure()
    def figure(self):
        dpi = rcParams['figure.dpi']
        #rcParams['figure.dpi']
        figsize = 9,9
        #
        fig = figure(figsize=figsize)
        ax = axes([0,0,1,1], frameon=False)
        #ylim(self.lena.size[1],0)
        #ax.set_axis_off()
        def scaleCoordsUP(x,zoom):
            return int(x*2**(zoom-1))
        def FixYCoord(y):
            return self.lena.size[1]-y

        def onclick(event):
            t = time()
            print event.key
            print 'button=%d, x=%d, y=%d, xdata=%f, ydata=%f, time=%f'%(
                event.button, event.x, event.y, event.xdata, event.ydata,t-self.time1)
            x=scaleCoordsUP(event.xdata,self.zoom)+self.ul[0]
            y=scaleCoordsUP(FixYCoord(event.ydata),self.zoom)+self.ul[1]
            
            if (t-self.time1)<.6:##double click
                if event.button==1:    #Left Click zoom in
                    if self.zoom!=1:
                        if event.key =="alt":
                            self.zoom = 1
                        else:
                            self.zoom-=1
                        print "Zoomed into ", self.zoom
                    else:
                        print "at Base level"
                elif event.button==3:   #Right Click zoom out
                    if self.zoom==self.topLayer:
                        self.ul,self.lr = (0,0),(self.size[0],self.size[1])
                        self.lena = self.Ti.getBlock(self.ul,self.lr,self.zoom)
                        im = imshow(self.lena.convert("RGB"),origin='lower')
                        show()
                        self.time1 = t
                        return
                    else:
                        self.zoom+=1
                        print " now Zoomed Out to ",self.zoom
                #print "You Double Clicked!"
                #print "zoomed!",x,y,self.zoom
                coords = [x-512*2**(self.zoom-1) ,
                        y-512*2**(self.zoom-1)  ,
                        x+512*2**(self.zoom-1)  ,
                        y+512*2**(self.zoom-1)]
                for e in range(len(coords)):
                    if coords[e]<0:
                        coords[e]=0
                    if e%2==0:
                        if coords[e]>self.size[0]:
                            coords[e]=self.size[0] 
                    if e%2!=0:
                        if coords[e]>self.size[1]:
                            coords[e]=self.size[1]
                self.ul= coords[0:2]
                self.lr = coords[2:]
                print coords
                self.lena = self.Ti.getBlock(self.ul,self.lr,self.zoom)
                im = imshow(self.lena.convert("RGB"),origin='lower')
                show()
                self.time1 = t
                return
            else:
                if event.key=='shift' and event.button==1 and not self.haveAllCoords():
                    self.coords.append([x,y])
                    print "you selected",x,y," and added it to ", self.coords
            self.time1=t
        cid = fig.canvas.mpl_connect('button_press_event', onclick)
        im = imshow(self.lena.convert("RGB"), origin='lower')
        show()

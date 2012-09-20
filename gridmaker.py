#!/usr/bin/env python
import pylab
import numpy as np
import PIL
import Image as im
from tiledImage import TiledImage
import ImageDraw
import ImageFont


class GridMaker:##
    def __init__(self,coords,filename,ti):
        '''
        This constructs a matrix of the coordinates of the center of each well in the image
        
        coords == an Array of 8 coordinates that the user picked (first 3 wells in each direction and the final ones)
        filename == the name of the image
        ti == the Tiled Image object that allows for previewing wells with the "showWell(x,y)" Method
        
        '''
        self.Ti = ti
        self.filename = filename
        self.pic=im.open(filename)
        Coords= np.array(coords)

        AverageHX = ((Coords[2,0]-Coords[1,0])+(Coords[1,0]-Coords[0,0]))/2
        TotalHX = abs(int(round((Coords[3,0]-Coords[0,0])/AverageHX)))
        
        AverageHY = ((Coords[6,1]-Coords[5,1])+(Coords[5,1]-Coords[4,1]))/2
        TotalVY = abs(int(round((Coords[7,1]-Coords[4,1])/AverageHY)))
        
        Collumns =(abs(int(round(TotalHX))))+1
        Rows = abs(int(round(TotalVY)))+1
        self.Collumns = Collumns
        self.Rows = Rows
        print "The total number of Boxes in the Horizontal is: ", Collumns
        print "The Total number of Boxes in the Vertical is: ", Rows
        
        #Creats an empty numpy array of all of the wells
        self.AllCoords = np.ndarray(shape=(Collumns,Rows,2))
        
        AvgHX = int((Coords[3,0]-Coords[0,0])/int(round(TotalHX))) ## Average distance between 
        AvgHY = int((Coords[3,1]-Coords[0,1])/(TotalHX))
        AvgVX = int((Coords[7,0]-Coords[4,0])/TotalVY)
        AvgVY = int((Coords[7,1]-Coords[4,1])/int(round(TotalVY)))
    
        X = int(Coords[0,0])
        Y = int(Coords[0,1])
        
        for i in range(Collumns):
            for j in range(Rows):
                self.AllCoords[i,j,:] =[X+i*AvgHX+j*AvgVX,Y+AvgHY*i+j*AvgVY]
        self.Collumns =Collumns
        self.Rows = Rows
        wellSize = self.AllCoords[1,1]-self.AllCoords[0,0]
        self.wellHeight= wellSize[1]
        self.wellWidth = wellSize[0]
        self.randomGenerator(3)
        
    def randomGenerator(self,x):
        for i in range(x):
            self.showWell(int(np.random.randint(1,self.Collumns,1)),
                          int(np.random.randint(1,self.Rows,1)))
    
    def boxMaker(self,x,y):#Creates a box from the coords in matrix
        x-=1
        y-=1
        box = (int(self.AllCoords[x,y,0]-self.wellWidth/2) ,
               int(self.AllCoords[x,y,1]-self.wellHeight/2),
               int(self.AllCoords[x,y,0]+self.wellWidth/2) ,
               int(self.AllCoords[x,y,1]+self.wellHeight/2))
        for i in range(4):
            if i%2==0:
                if box[i]>self.pic.size[0]:
                    return None
            else:
                if box[i]>self.pic.size[1]:
                    return None
        return box

    def getWell(self,x,y):
        box = self.boxMaker(x,y)
        if box==None:
            return None
        well =self.pic.crop(box)
        return well
        
    def showWell(self,x,y):
        Position = '('+str(x)+","+str(y)+")"
        if self.boxMaker(x,y)==None:
            return "Selection Out of Range"
        l,u,r,lw = self.boxMaker(x,y)
        well = self.Ti.getBlock((l,u),(r,lw),1)
        draw = ImageDraw.Draw(well)
        draw.text((65,140),Position,fill = 200)
        well.show()
    
    def saveWell(self,x,y):
        if getWell(x,y)==None:
            return "Selection Out of Range"
        else:
            getWell(x,y).save("/Users/Willem/Desktop/temp/%d-%d.tif"%(x,y))
        
    def setTilesize(self,x,y):
        self.wellHeight = y
        self.wellWidth = x
    
    def decreaseTileSize(self,x):
        if x>1:
            return "Not possible: must be percent"
        else:
            self.setTilesize(self.wellHeight*x,self.wellWidth*x)
    #im.show()

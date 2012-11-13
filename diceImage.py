import Image as im
import numpy as np
#import os
import os.path as osp
import math
import json

#inputImage = 'ADGhts42_ControlWell_Initial_w1_15%25linear.tif'
#inputImage = 'ImagePick/SmallBF.tif'

#fileName = '/Users/willem/Desktop/test/ADGhts42_ControlWell_Initial_w1_15%linear.tif'

##osp.join('', inputImage) 
'''
{
    "width": 19500,
    "height": 18500,
    "levels": 5,
    "tileSize": 1024
    }
'''
class DiceImage:
    def __init__(self,filename):
        self.filename=filename
        folder = osp.split(filename)[0]
        print filename,folder
        self.folder=folder##is the folder of the picture
        #info = json.loads(osp.join(folder,'info.json'),'r').read()
        #print info
        self.tileSize=1024  #info['tileSize']
        
        self.width,self.height = 19500,18500 #info['width'],info['height']
        #self.folder = osp.join(self.folder,osp.split(filename)[1])
        self.viewFolder = self.makeBottomLayer(folder,filename)
        self.topLayer=5 #info['levels']
        print self.viewFolder
        #ensure_dir(nextfolder)
        for i in range(self.topLayer):
            self.scaleUp(self.viewFolder,i+1)
            print i+1,"done"

        #scaleUp(3,'/Users/willem/Documents/spectrum/',2,256)
        #scaleUp(2,'/Users/willem/Documents/spectrum/',3,256)
        
    
   
    
    def readTifChunk(self,fileName, box):
        
        '''Read a rectangular region from the image file'''
        dtypes = { 'L': np.uint8,
               'I;16B': np.int16,
               }
        img = im.open(fileName)
        print img.tile
        dtype = dtypes[img.tile[0][3][0]]
        dsize = np.dtype(dtype).itemsize
        
        headerSkip = img.tile[0][2] # get the header to skip assuming raw
    
        x,y,w,h = box # unpack box
    
        result = np.zeros((h,w), dtype=dtype)
    
        fp = file(fileName, 'rb')
    
        for row in xrange(h):
            fp.seek(headerSkip + ((row+y)*img.size[0]+x)*dsize)
            result[row] = np.fromfile(fp, dtype, w)
    
        result = result.astype(np.float)
    
        # this scaling should not be happening per chunk
        result = 255 * (result - result.min()) / float(result.max() - result.min())
    
        return result.astype(np.uint8)
    
    # w = 10000
    # h = 6000
    # dice = 8
    # cw = w/dice
    # ch = h/dice
    
    def ensure_dir(self,f):
        import os
        import shutil
        d = os.path.dirname(f)
        if os.path.exists(d):
            shutil.rmtree(d)
        os.makedirs(f)
        
    def makeBottomLayer(self,folder, filename):
        import math
        w,h = self.width,self.height
        ##newW =w/(2**(zoom-1))
        ##newH =h/(2**(zoom-1))
        size = self.tileSize
        tmp1 = im.open(filename)            ## opens main image
        diceX = int(math.ceil(float(w)/size))
        diceY = int(math.ceil(float(h)/size))
        print "dice: x, y ",diceX,diceY
        cw = size
        ch = size

        tmp = im.new(tmp1.mode,(diceX*size,diceY*size))  ## This creates a new image with same mode and
                                                        #   for extra space
        tmp.paste(tmp1,(0,0))
        
    #    tmp.save(newfile)
        tmpFolder = osp.join(folder,'.tempFolder')
        self.ensure_dir(tmpFolder)
        newfile= osp.join(tmpFolder,'tmp.tiff')
        tmp.save(newfile)
        print tmpFolder
        filename = newfile
        folder = osp.join(tmpFolder,'0')
        self.ensure_dir(folder)
        for row in xrange(diceY):
            for col in xrange(diceX):
                c = self.readTifChunk(newfile, (cw*col, ch*row, cw, ch))
                im.fromarray(c).save(folder+'%d-%d.tif' % (col,row))
    
        return tmpFolder
                                   ###This scales tiles up the image to the next level####
    def scaleUp(self,folder,zoom): 

        size=self.tilesize  ##this is the tilesize


        diceX = int(math.ceil(float(self.width)/(size*2**(zoom-1))))##This is how many tiles there are for the previous layer for x and y
        diceY = int(math.ceil(float(self.height)/(size*2**(zoom-1))))
        previousFolder = osp.join(folder,str(zoom-1))##This is the previous layer folder
        newfolder = osp.join(folder,str(zoom))##new folder
        self.ensure_dir(newfolder)
        import Image as im
        #print "diceX and diceY",diceX,diceY
        for y in range(0,diceY,2):## goes across every other tile in both directions
            for x in range(0,diceX,2):
                #print x , y
                tmp=im.new(im.open(folder+"0/0-0.tif").mode,(size*2,size*2))##new image for the four
                if (y==diceY-1):
                    if (x==diceX-1):
                        ##This is if the there is only one tile e.g. corner
                        tmp.paste(im.open( previousFolder+'%d-%d.tif' % (x,y)) ,(0,0))
                    else:
                        ##This is the bottom row if there are odd rows
                        tmp.paste( im.open( previousFolder+'%d-%d.tif' % (x,y)) ,(0,0))
                        tmp.paste( im.open( previousFolder+'%d-%d.tif' % (x+1,y)) ,(size,0))
                    
                elif (y!=diceY-1) and (x==diceX-1):
                    ##This is the last column if there is an odd number of columns
                    tmp.paste( im.open( previousFolder+'%d-%d.tif' % (x,y)) ,(0,0))
                    tmp.paste( im.open( previousFolder+'%d-%d.tif' % (x,y+1)) ,(0,size))
                    
                else:
                    ##Normal four tiles
                    tmp.paste( im.open( previousFolder+'%d-%d.tif' % (x,y)) ,(0,0))
                    tmp.paste( im.open( previousFolder+'%d-%d.tif' % (x,y+1)) ,(0,size))
                    tmp.paste( im.open( previousFolder+'%d-%d.tif' % (x+1,y)) ,(size,0))
                    tmp.paste( im.open( previousFolder+'%d-%d.tif' % (x+1,y+1)) ,(size,size))
                
                tmp = tmp.resize((size,size))
                tmp.save(newfolder+'%d-%d.tif'% ((x+2)/2-1,(y+2)/2-1))
    
    
    
    
    
    #BoxMaker('/Users/willem/Documents/spectrum/','spectrum.tif',256,2)
    ##BoxMaker('/Users/willem/Documents/spectrum/','spectrum.tif',256,3)
    #BoxMaker('/Users/willem/Documents/spectrum/','spectrum.tif',256,4)
    
    #
    #for row in xrange(dice):
    #    for col in xrange(dice):
    #        c = readTifChunk(fileName, (cw*col, ch*row, cw, ch))
    #        im.fromarray(c).save(nextfolder+'%d-%d.tif' % (row,col))

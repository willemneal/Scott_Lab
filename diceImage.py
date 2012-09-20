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

class DiceImage:
    def __init__(self,filename,folder):
        self.filename=filename
        info = json.loads(osp.join(folder,'info.json'),'r').read()
        self.tileSize=info['tileSize']
        self.folder=folder##is the folder of the picture
        self.width,self.height = info['width'],info['height']
        #self.folder = osp.join(self.folder,osp.split(filename)[1])
        self.tileMaker(folder,filename)
        self.topLayer=info['levels']
        #ensure_dir(nextfolder)
        for i in range(self.topLayer):
            self.scaleUp(self.folder,i+1)
            print i+1,"done"
        #
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
    
    w = 10000
    h = 6000
    dice = 8
    cw = w/dice
    ch = h/dice
    
    def ensure_dir(self,f):
        import os
        import shutil
        d = os.path.dirname(f)
        if os.path.exists(d):
            shutil.rmtree(d)
        os.makedirs(f)
        
    def tileMaker(self,folder, filename):
        ##folder = '/Users/willem/Desktop/TestFolder/'
        import math
        w,h = self.width,self.height
        ##newW =w/(2**(zoom-1))
        ##newH =h/(2**(zoom-1))
        
        tmp1 = im.open(filename)
        diceX = int(math.ceil(float(w)/size))
        diceY = int(math.ceil(float(h)/size))
        print "dice: x, y ",diceX,diceY
        cw = self.size
        ch = self.size
        tmp = im.new(tmp1.mode,(diceX*size,diceY*size))
        tmp.paste(tmp1,(0,0))
        newfile= osp.join(folder,osp.split(filename)[1])
        tmp.save(newfile)
        filename = newfile
        folder = osp.join(folder,'0')
        self.ensure_dir(folder)
        for row in xrange(diceY):
            for col in xrange(diceX):
                c = self.readTifChunk(filename, (cw*col, ch*row, cw, ch))
                im.fromarray(c).save(folder+'%d-%d.tif' % (col,row))
    
    
    
    
    def scaleUp(self,folder,zoom): ##This scales tiles up the image to the next level
        size=self.tileSize##this is the tilesize
        diceX = int(math.ceil(float(self.width)/(size*2**(zoom-1))))##This is how many tiles there are for the previous layer for x and y
        diceY = int(math.ceil(float(self.height)/(size*2**(zoom-1))))
        zfolder = osp.join(folder,str(zoom-1))##This is the previous layer folder
        newfolder = folder+str(zoom)+'/'##new folder
        self.ensure_dir(newfolder)
        import Image as im
        #print "diceX and diceY",diceX,diceY
        for y in range(0,diceY,2):##goes across every other tile in both directions
            for x in range(0,diceX,2):
                print x , y
                tmp=im.new(im.open(self.folder+"0/0-0.tif").mode,(size*2,size*2))##new image for the four
                if (y==diceY-1):
                    if (x==diceX-1):
                        ##This is if the there is only one tile e.g. corner
                        tmp.paste(im.open( zfolder+'%d-%d.tif' % (x,y)) ,(0,0))
                    else:
                        ##This is the bottom row if there are odd rows
                        tmp.paste( im.open( zfolder+'%d-%d.tif' % (x,y)) ,(0,0))
                        tmp.paste( im.open( zfolder+'%d-%d.tif' % (x+1,y)) ,(size,0))
                    
                elif (y!=diceY-1) and (x==diceX-1):
                    ##This is the last column if there is an odd number of columns
                    tmp.paste( im.open( zfolder+'%d-%d.tif' % (x,y)) ,(0,0))
                    tmp.paste( im.open( zfolder+'%d-%d.tif' % (x,y+1)) ,(0,size))
                    
                else:
                    ##Normal four tiles
                    tmp.paste( im.open( zfolder+'%d-%d.tif' % (x,y)) ,(0,0))
                    tmp.paste( im.open( zfolder+'%d-%d.tif' % (x,y+1)) ,(0,size))
                    tmp.paste( im.open( zfolder+'%d-%d.tif' % (x+1,y)) ,(size,0))
                    tmp.paste( im.open( zfolder+'%d-%d.tif' % (x+1,y+1)) ,(size,size))
                
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
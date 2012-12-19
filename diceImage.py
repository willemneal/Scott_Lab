import Image as im
import numpy as np
#import os
import os.path as osp
import math
import json
import pdb
import os

#inputImage = 'ADGhts42_ControlWell_Initial_w1_15%25linear.tif'
#inputImage = 'ImagePick/SmallBF.tif'

#fileName = '/Users/willem/Desktop/test/ADGhts42_ControlWell_Initial_w1_15%linear.tif'

##osp.join('', inputImage)

class DiceImage:
    '''
    This object takes a filename layers and tileSize from the json object.

    From this information it cuts up the large image into tiles of size given, it puts these into folder '0'
    located in the same directory as your input file. Then goes up a layer taking four tiles and condensing
    them into one tile, this folder is '1' and so on until the layer specified.
    '''
    def __init__(self,filename):
        self.filename=filename
        self.folder=osp.split(filename)[0] 
        print osp.join(self.folder,'info.json')
        Info = osp.join(self.folder,'info.json')
        info = json.loads(file(Info,'r').read())
        self.tileSize=info['tileSize']

        self.width,self.height = info['width'],info['height']
        
        self.makeBottom(self.folder,self.filename)  ## this creates the bottom layer of the tiles
        self.topLayer=info['levels']
        #ensure_dir(nextfolder)
        for i in range(self.topLayer):
            self.scaleUp(self.folder,i+1)

    def readTifChunk(self,fileName, box):
        
        '''Read a rectangular region from the image file
        by Gary Bishop
        '''
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
    
    
    def ensure_dir(self,f):
        '''checks if dir exists and if it does over writes it.'''
        import os
        import shutil
        d = os.path.dirname(f)
        if os.path.exists(d):
            shutil.rmtree(d)
        os.makedirs(f)
        
    def makeBottom(self,folder, filename):
        w,h = self.width,self.height
        size=self.tileSize  ##this is the tileSize
        originalImage = im.open(filename)##open original
        columns = int(math.ceil(float(w)/size))     #number of columns
        rows = int(math.ceil(float(h)/size))        #number of rows
        #print "dice: x, y ",columns,rows
        cellWidth = size                            #cell width is the same as tileSize
        cellHeight = size
        newfolder = osp.join(folder,'0')            #bottom layer folder '/0'
        if (self.checkDir(newfolder)):              #check if dir folder is full it returns true
            return
        tmp = im.new(originalImage.mode,(columns*size,rows*size))
        tmp.paste(originalImage,(0,0))
        newfile= osp.join(folder,"tmp.tif")
        tmp.save(newfile)
        filename = newfile
        ##pdb.set_trace()
        #self.ensure_dir(newfolder)
        for row in xrange(rows):            ## This cuts up the tiles!
            for col in xrange(columns):
                c = self.readTifChunk(filename, (cellWidth*col, cellHeight*row, cellWidth, cellHeight))
                im.fromarray(c).save(osp.join(newfolder,'%d-%d.tif' % (col,row)))
                                  
    def scaleUp(self,folder,zoom):
         ###This scales tiles up the image to the next level#### 

        size=self.tileSize  ##this is the tileSize

        columns = int(math.ceil(float(self.width)/(size*2**(zoom-1))))##This is how many tiles there are for the previous layer for x and y
        rows = int(math.ceil(float(self.height)/(size*2**(zoom-1))))
        previousFolder = osp.join(folder,str(zoom-1))##This is the previous layer folder
        newfolder = osp.join(folder,str(zoom))##new folder
        if (self.checkDir(newfolder)):
            return
        import Image as im
        #print "columns and rows",columns,rows
        for y in range(0,rows,2):## goes across every other tile in both directions
            for x in range(0,columns,2):
                #print x , y
                tmp=im.new(im.open(osp.join(previousFolder,"0-0.tif")).mode,(size*2,size*2))##new image for the four
                if (y==rows-1):
                    if (x==columns-1):
                        ##This is if the there is only one tile e.g. corner
                        tmp.paste(im.open( osp.join(previousFolder,'%d-%d.tif' % (x,y))) ,(0,0))
                    else:
                        ##This is the bottom row if there are odd rows
                        tmp.paste( im.open( osp.join(previousFolder,'%d-%d.tif' % (x,y))) ,(0,0))
                        tmp.paste( im.open( osp.join(previousFolder,'%d-%d.tif' % (x+1,y))) ,(size,0))
                    
                elif (y!=rows-1) and (x==columns-1):
                    ##This is the last column if there is an odd number of columns
                    tmp.paste( im.open( osp.join(previousFolder,'%d-%d.tif' % (x,y))) ,(0,0))
                    tmp.paste( im.open( osp.join(previousFolder,'%d-%d.tif' % (x,y+1))) ,(0,size))
                    
                else:
                    ##Normal four tiles
                    tmp.paste( im.open( osp.join(previousFolder,'%d-%d.tif' % (x,y))) ,(0,0))
                    tmp.paste( im.open( osp.join(previousFolder,'%d-%d.tif' % (x,y+1))) ,(0,size))
                    tmp.paste( im.open( osp.join(previousFolder,'%d-%d.tif' % (x+1,y))) ,(size,0))
                    tmp.paste( im.open( osp.join(previousFolder,'%d-%d.tif' % (x+1,y+1))) ,(size,size))
                tmp = tmp.resize((size,size))
                tmp.save(osp.join(newfolder,'%d-%d.tif'% ((x+2)/2-1,(y+2)/2-1)))

    def checkDir(self,newfolder):
        if os.path.exists(osp.join(newfolder,"0-0.tif")):
            return True
        elif not os.path.exists(newfolder):
            os.makedirs(newfolder)
            return False
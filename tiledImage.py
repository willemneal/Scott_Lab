import json
import os.path as osp
import Image as im

# folder given below contains a json format file with the info about the image
#{
#    width: 19500,
#    height: 18500,
#    levels: 5,
#    tileSize: 1024
#}

class TiledImage:
    def __init__(self, imageDir):
        self.imageDir = imageDir
        self.picSize = im.open(imageDir + "new.tif").size
        #print self.picSize
        ##self.info = json.loads(file(osp.path(imageDir, 'info.json'), 'r').read())
        self.width = 300
        self.height = 300
        self.tileSize = 1024
        self.size = 1200



    def getBlock(self, ul, lr, zoom):
        scale = 2**(zoom-1)##scale is used to make the units in terms of the bottom layer
        self.UpperLeft=ul
        self.LowerRight=lr
        width = (lr[0] - ul[0]) / scale
        height = (lr[1] - ul[1]) / scale
        res = im.new('L', (width,height))
        x0 = ul[0] / scale
        x1 = lr[0] / scale
        y0 = ul[1] / scale
        y1 = lr[1] / scale
        tSize = self.tileSize
        res = im.new('L',(width,height))
        #print x0,x1,y0,y1
        y = y0
        while y < y1:
            x = x0
            tR = y / tSize
            upper = (y - tR * tSize)
            if (upper+(y1-y)>tSize):
                lower = tSize
            else:
                lower = (y1-tR*tSize)
            while x < x1:
                tC = x / tSize
                fname = '%d/%d-%d.tif' % ( zoom-1, tC, tR)
                tile = im.open(self.imageDir+fname)
                #tile.show()
                #print self.imageDir+fname
                left = (x - tC * tSize)
                if (left+(x1-x))>tSize:
                    right = tSize
                else:
                    right = (x1-tC*tSize)
                #print "l,u,r,l",x,y
                #print left,upper,right,lower
                box = (int(left),int(upper),int(right),int(lower))
                region = tile.crop(box)
                box2 = (int(x-x0),int(y-y0))
                res.paste(region, box2)
                x = x+(right-left)
                #print "the new x is", x
                
            y = (lower-upper)+y
            #print "the new y is ", y
        #print res.size
        return res
    


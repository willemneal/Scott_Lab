#!/usr/bin/env python
## This is the main class for the program
import Image as im
from diceImage import DiceImage
from viewer import Viewer
from gridmaker import GridMaker
import os
import json
from tiledImage import TiledImage
from Tkinter import Tk#             For file selection gui
from tkFileDialog import askopenfilename
#

class Main:
    def __init__(self):
        self.filename, self.workfolder = self.selectFile()
        self.setUpInfo(self.filename,self.workfolder)
        Diced = DI(self.filename,self.workfolder)
        viewFolder = DI.viewFolder
        VI = Viewer(viewFolder,self.levels)
        VI.show()

    def setUpInfo(self,filename,workfolder):
        '''
        This creates a file info.json that contains 'width, height, levels, and tileSize
        '''
        info = os.path.join(os.path.split(filename)[0],os.path.join(workfolder,"info.json"))
        if not os.path.exists(info):
            os.makedirs(info)
        else:
            shutil.rmtree(info)
            os.makedirs(info)
        image = im.open(filename)
        width,height = image.size
        tileSize = 1024
        levels = self.levels(width,height,tileSize)
        self.levels = levels
        tmpinfo = json.dumps({
            "width": width,
            "height" : height,
            "levels": levels,
            "tileSize":tileSize
        })
        file(info,'w').write(tmpinfo)
        return
    def levels(self,width,height,tileSize):       
        '''
        This returns the number of levels given the tileSize, width and height.
        '''
        return int(max(math.log(width/tileSize,2),math.log(height/tileSize,2)))+1

    def selectFile(self):
        Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
        filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
        folder = os.path.split(filename)[0]
        return filename,folder

#filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
filename = '/Users/willem/Desktop/temp/ADGhts42_ControlWell_Initial_w2_10%linear.tif'
#main = Main(filename)

VI = Viewer('/Users/willem/Desktop/ADGhts42_ControlWell_Initial_Scans/',"k",5)
VI.show()
#Image = DI('/Users/willem/Documents/spectrum/','spectrum.tif',256)

#
coords =  [[260, 1185], [609, 1183], [971, 1185], [17418, 1260], [259, 1195], [267, 1544], [277, 1906], [192, 17650]]
Grid = GridMaker(coords,
    '/Users/willem/Desktop/ADGhts42_ControlWell_Initial_Scans/image1.tif',
    TiledImage('/Users/willem/Desktop/ADGhts42_ControlWell_Initial_Scans/'))
#
Grid.showWell(20,20)
Grid.saveWell(20,20)

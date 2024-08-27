import os
import colorsys
import numpy as np

from src.Model.Data_Storage.ConnGraph_Model import ConnGraph_Infos

class ParserFlut_Files:
    def __init__(self):
        
        # File Part
        self.fileName = None
        self.connGraph = ConnGraph_Infos()

        self.allLines = None

        self.areaInfos = {}  # {Name: {ID_Node, RGBA, Side, Wider_Area, ID_Opposite, 3D_Coos} List: [List Order]} -> FLUT File
        self.areasOrder = []  # Order of areas (with blanks)
        self.MajorRegions = []
        self.colorMajorRegions = {}

    def LoadFile(self):

        # Load the graph from the given file
        try:
            flutFile = open(os.path.abspath(self.fileName), 'r')
        except FileNotFoundError:
            raise Exception("Opening Error - {}".format(self.fileName))
        
        self.allLines = flutFile.readlines()

        # Handle Empty File
        if len(self.allLines) == 0:
            flutFile.close()
            raise Exception("Wrong Format Error - Empty Given File")
        
        flutFile.close()
        
    def DefineColorToMajorRegion(self):

        # Generate Distincs Color
        hues = np.linspace(0, 1, len(self.MajorRegions), endpoint=False)
        colors = [colorsys.hsv_to_rgb(hue, 0.7, 0.9) for hue in hues]

        for indexMajorRegion, majorRegion in enumerate(self.MajorRegions):
            self.colorMajorRegions[majorRegion] = colors[indexMajorRegion]
    
    # ==========================
    # Method to parse Flut Files
    # ==========================
    def Parser(self):
        print("\u27A2 Loading FLUT File")

        # For each line
        for line in self.allLines:

            lineSplit = line.split()

            if len(lineSplit) != 12 and len(lineSplit) != 9 \
                and len(lineSplit) != 8 and len(lineSplit) != 11:
                raise Exception ("Wrong Format - Wrong Column Number")

            if len(lineSplit) == 11 or len(lineSplit) == 8:
                removeIndex = 1
            else:
                removeIndex = 0

            idCurrent = int(lineSplit[0])
            nameCurrent = lineSplit[1]
            majorRegion = lineSplit[7 - removeIndex]
            
            if (idCurrent == 0 or nameCurrent.replace('x', '') == ''):

                self.areasOrder.append(("xxxx", idCurrent))
                continue  # Not Area -> blanc in the graph
            
            self.areasOrder.append((nameCurrent, idCurrent))

            try:
                # Fill the Area Infos Dictionary
                self.areaInfos[nameCurrent] = {}
                self.areaInfos[nameCurrent]["ID"] = idCurrent

                if len(lineSplit) == 9 or len(lineSplit) == 12:
                    if float(lineSplit[5]) == 0.0:
                        self.areaInfos[nameCurrent]["RGBA"] = (int(lineSplit[2]), int(lineSplit[3]), int(lineSplit[4]), 255)
                    else:
                        self.areaInfos[nameCurrent]["RGBA"] = (int(lineSplit[2]), int(lineSplit[3]), int(lineSplit[4]), float(lineSplit[5]))
                else:
                    self.areaInfos[nameCurrent]["RGBA"] = (int(lineSplit[2]), int(lineSplit[3]), int(lineSplit[4]), 255)
                    
                self.areaInfos[nameCurrent]["Side"] = int(lineSplit[6 - removeIndex])
                self.areaInfos[nameCurrent]["MajorRegion"] = majorRegion
                self.areaInfos[nameCurrent]["ID_Opposite"] = int(lineSplit[8 - removeIndex])

                # Limit to 14 major regions
                if len(self.MajorRegions) == 14:
                    raise Exception("Wrong Format - MAX 14 Major Regions")
                elif majorRegion not in self.MajorRegions:
                    self.MajorRegions.append(majorRegion)

                if len(lineSplit) == 12 or len(lineSplit) == 11:
                    self.areaInfos[nameCurrent]["3D_Coos"] = (int(lineSplit[9 - removeIndex]), int(lineSplit[10 - removeIndex]), int(lineSplit[11 - removeIndex]))

            except Exception as exception:
                raise Exception(exception.args[0])

    def FlutFile_Parser(self, fileName: str):

        self.fileName = fileName
        
        # Recovert and verify the file extension
        extension = os.path.splitext(self.fileName)[1]

        if extension != ".flut":
            raise Exception("Wrong Extension Error - Extension not allowed")

        # Load and Recovert All Lines from the File
        self.LoadFile()
        
        self.Parser()   

        self.DefineColorToMajorRegion()   

        # Complete the ConnGraph Object
        self.connGraph.areaInfos = self.areaInfos
        self.connGraph.numberOfNodes = len(self.areaInfos)
        self.connGraph.areasOrder = self.areasOrder
        self.connGraph.colorMajorRegions = self.colorMajorRegions








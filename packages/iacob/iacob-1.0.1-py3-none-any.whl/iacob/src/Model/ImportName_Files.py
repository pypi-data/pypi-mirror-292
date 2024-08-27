import os

from src.Model.Data_Storage.ConnGraph_Model import ConnGraph_Infos

class ParserName_Files:
    def __init__(self):
        
        # File Part
        self.fileName = None
        self.connGraph = ConnGraph_Infos()
        
        self.allLines = None

        self.idName = {}  # {ID_Node: Name}

    # ============================
    # Open - Read - Close the File
    # ============================
    def LoadFile(self):

        # Load the graph from the given file
        try:
            nameFile = open(os.path.abspath(self.fileName), 'r')
        except FileNotFoundError:
            raise Exception("Opening Error - {}".format(self.fileName))
        
        self.allLines = nameFile.readlines()

        # Handle Empty File
        if len(self.allLines) == 0:
            nameFile.close()
            raise Exception("Wrong Format Error - Empty Given File")
        
        nameFile.close()

    def OneLine_Parser(self):
        indexName = 0

        # Stock all Name with an abitratry ID
        for name in self.allLines[0].split():

            self.idName[indexName] = name
            indexName += 1

    def OneColumn_Parser(self):
        indexName = 0

        # Stock all Name with an abitratry ID
        for line in self.allLines:

            lineSplit = line.split()

            if lineSplit != []:
                self.idName[indexName] = "".join(lineSplit)
                indexName += 1

    # ==========================
    # Method to parse Name Files
    # ==========================
    def NameFile_Parser(self, fileName: str):
        
        self.fileName = fileName
        
        # Recovert and verify the file extension
        extension = os.path.splitext(self.fileName)[1]

        if extension != ".txt":
            raise Exception("Wrong Extension Error - Extension not allowed")

        # Load and Recovert All Lines from the File
        self.LoadFile()
        
        if len(self.allLines) == 1:
            self.OneLine_Parser()
        else:
            self.OneColumn_Parser()        

        # Complete the ConnGraph Object
        self.connGraph.idName = self.idName
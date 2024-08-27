import os
import json

from src.Model.Data_Storage.Filters_Model import Filters_Infos

class ParserFilters_Files:

    def __init__(self):
        
        # File Part
        self.fileName = None
        self.filters = Filters_Infos()

        self.filtersData = {}

    def Parser(self):
        
        try:

            if not isinstance(self.filtersData["thresholdPostFiltering"], (int, float)):
                raise Exception("Wrong Variable Type : Int / Float Expected")
            self.filters.thresholdPostFiltering = self.filtersData["thresholdPostFiltering"]

            if not isinstance(self.filtersData["WeightAndRank"]["Weight"]["discardWeight"], bool):
                raise Exception("Wrong Variable Type : Boolean Expected")
            self.filters.discardWeight = self.filtersData["WeightAndRank"]["Weight"]["discardWeight"]

            if not isinstance(self.filtersData["WeightAndRank"]["AbsWeight"]["discardAbsWeight"], bool):
                raise Exception("Wrong Variable Type : Boolean Expected")
            self.filters.discardAbsWeight = self.filtersData["WeightAndRank"]["AbsWeight"]["discardAbsWeight"]

            if not isinstance(self.filtersData["WeightAndRank"]["Rank"]["discardRank"], bool):
                raise Exception("Wrong Variable Type : Boolean Expected")
            self.filters.discardRank = self.filtersData["WeightAndRank"]["Rank"]["discardRank"]

            if not isinstance(self.filtersData["WeightAndRank"]["Weight"]["weightBetween_threshold"], list):
                raise Exception("Wrong Variable Type : List of Int / Float Expected") 
            if not all(isinstance(x, (int, float)) for x in self.filtersData["WeightAndRank"]["Weight"]["weightBetween_threshold"]):
                raise Exception("Wrong type of Variable elements : Int / Float Expected")
            self.filters.weightBetween_threshold = self.filtersData["WeightAndRank"]["Weight"]["weightBetween_threshold"]

            if not isinstance(self.filtersData["WeightAndRank"]["AbsWeight"]["absWeightBetween_threshold"], list):
                raise Exception("Wrong Variable Type : List of Int / Float Expected")
            if not all(isinstance(x, (int, float)) for x in self.filtersData["WeightAndRank"]["AbsWeight"]["absWeightBetween_threshold"]):
                raise Exception("Wrong type of Variable elements : Int / Float Expected")
            self.filters.absWeightBetween_threshold = self.filtersData["WeightAndRank"]["AbsWeight"]["absWeightBetween_threshold"]
            
            if not isinstance(self.filtersData["WeightAndRank"]["Rank"]["rankBetween_threshold"], list):
                raise Exception("Wrong Variable Type : List of Int Expected")
            if not all(isinstance(x, int) for x in self.filtersData["WeightAndRank"]["Rank"]["rankBetween_threshold"]):
                raise Exception("Wrong type of Variable elements : Int Expected")
            self.filters.rankBetween_threshold = self.filtersData["WeightAndRank"]["Rank"]["rankBetween_threshold"]

            if not isinstance(self.filtersData["ConnType"]["contralateral_connType"], bool):
                raise Exception("Wrong Variable Type : Boolean Expected")
            self.filters.contralateral_connType = self.filtersData["ConnType"]["contralateral_connType"]
            
            if not isinstance(self.filtersData["ConnType"]["homotopic_connType"], bool):
                raise Exception("Wrong Variable Type : Boolean Expected")
            self.filters.homotopic_connType = self.filtersData["ConnType"]["homotopic_connType"]
            
            if not isinstance(self.filtersData["ConnType"]["ipsilateral_connType"], bool):
                raise Exception("Wrong Variable Type : Boolean Expected")
            self.filters.ipsilateral_connType = self.filtersData["ConnType"]["ipsilateral_connType"]
            
            if not isinstance(self.filtersData["ConnType"]["other_connType"], bool):
                raise Exception("Wrong Variable Type : Boolean Expected")
            self.filters.other_connType = self.filtersData["ConnType"]["other_connType"]

        except Exception:
            raise Exception("Wrong Format Error - Missing Variable(s)")
        
        try:

            if not isinstance(self.filtersData["InterRegConn"], dict):
                raise Exception("Wrong Variable Type : Dictionary Expected")
            for names, value in self.filtersData["InterRegConn"].items():
                namesSplit = names.strip('()').split(',')
                namesSplitWithoutSpace = [name.strip() for name in namesSplit]

                if not isinstance(value, bool):
                    raise Exception("Wrong Variable Type : Boolean Expected")
                self.filters.discardInterRegConn[(namesSplitWithoutSpace[0], namesSplitWithoutSpace[1])] = value

        except Exception:
            raise Exception("Wrong Format Error - Missing Variable or Variable Composition")

    def LoadFile(self):

        # Load the graph from the given file
        try:
            nameFile = open(os.path.abspath(self.fileName), 'r')
        except FileNotFoundError:
            raise Exception("Opening Error - {}".format(self.fileName))
        
        self.filtersData = json.load(nameFile)

        # Handle Empty File
        if len(self.filtersData) == {}:
            nameFile.close()
            raise Exception("Wrong Format Error - Empty Given File")

        nameFile.close()

    def FiltersFile_Parser(self, filename):

        self.fileName = filename

        # Recovert and verify the file extension
        extension = os.path.splitext(self.fileName)[1]

        if extension != ".json":
            raise Exception("Wrong Extension Error - Extension not allowed")

        self.LoadFile()

        self.Parser()
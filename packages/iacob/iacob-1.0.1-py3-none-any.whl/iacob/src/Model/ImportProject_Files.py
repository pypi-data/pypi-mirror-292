import os
import json

from src.Model.Data_Storage.Project_Model import Project_Infos

class ParserProject_Files:

    def __init__(self):
        
        # File Part
        self.fileName = None
        self.project = Project_Infos()

        self.projectData = {}

    def Parser(self):
        
        try:

            if not isinstance(self.projectData["currentDataFile"], str):
                raise Exception("Wrong Variable Type : Str Expected")
            self.project.currentDataFile = self.projectData["currentDataFile"]

            if not isinstance(self.projectData["currentNameFile"], (str, bool)):
                raise Exception("Wrong Variable Type : Str / Bool Expected")
            self.project.currentNameFile = self.projectData["currentNameFile"]

            if not isinstance(self.projectData["currentFlutFile"], str):
                raise Exception("Wrong Variable Type : Str Expected")
            self.project.currentFlutFile = self.projectData["currentFlutFile"]

            if not isinstance(self.projectData["currentFiltersFile"], str):
                raise Exception("Wrong Variable Type : Str Expected")
            self.project.currentFiltersFile = self.projectData["currentFiltersFile"]

        except Exception:
            raise Exception("Wrong Format Error - Missing Variable or Variable Composition")

    def LoadFile(self):

        # Load the graph from the given file
        try:
            nameFile = open(os.path.abspath(self.fileName), 'r')
        except FileNotFoundError:
            raise Exception("Opening Error - {}".format(self.fileName))
        
        self.projectData = json.load(nameFile)

        # Handle Empty File
        if len(self.projectData) == {}:
            nameFile.close()
            raise Exception("Wrong Format Error - Empty Given File")

        nameFile.close()

    def ProjectFile_Parser(self, filename):

        self.fileName = filename

        # Recovert and verify the file extension
        extension = os.path.splitext(self.fileName)[1]

        if extension != ".json":
            raise Exception("Wrong Extension Error - Extension not allowed")

        self.LoadFile()

        self.Parser()

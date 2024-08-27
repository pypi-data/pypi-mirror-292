import os
import json

from src.Model.Data_Storage.DataSingleton_Model import DataSingleton
from src.Model.Data_Storage.Filters_Model import Filters_Infos

class Project_Infos(metaclass=DataSingleton):

    def __init__(self):
        
        self.filters = Filters_Infos()
        self.previousFiles = {"DataFiles": {}, "NameFiles": {}, "FlutFiles": [], "FiltersFiles": [], "ProjectFiles": []}
        
        self.InitReset()

    def InitReset(self):

        self.currentDataFile = None
        self.currentNameFile = None
        self.currentFlutFile = None
        self.currentFiltersFile = None

    def InitRestore(self, projectSave: 'Project_Infos'):

        self.currentDataFile = projectSave.currentDataFile
        self.currentNameFile = projectSave.currentNameFile
        self.currentFlutFile = projectSave.currentFlutFile

    def ExportToJSON(self, filePathFull):

        filePath = os.path.dirname(filePathFull)
        filePath_basename = ".".join(os.path.basename(filePathFull).split('.')[:-1])
        newFilePath = os.path.join(filePath, f"{filePath_basename}-Filters.json")
        self.filters.ExportToJSON(newFilePath)

        projectToJSON = {

            "currentDataFile": self.currentDataFile,
            "currentNameFile": self.currentNameFile,
            "currentFlutFile": self.currentFlutFile,
            "currentFiltersFile": newFilePath
        }

        with open(filePathFull, 'w', encoding='utf-8') as file:
            json.dump(projectToJSON, file, ensure_ascii=False, indent=4)
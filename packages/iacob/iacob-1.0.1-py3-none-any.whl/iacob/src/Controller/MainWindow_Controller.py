import os
import webbrowser
from pathlib import Path

import statistics
import csv
import json
import math
import numpy as np
import networkx as nx
from numpy import mean
from typing import List

from src.globals import version, release_date, colorPalettes

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QStandardPaths, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMenu, QAction, QTableWidgetItem, QSizePolicy, QCheckBox, QGridLayout, QSpacerItem, \
    QHBoxLayout, QPushButton, QFileDialog, QAbstractItemView, QHeaderView
from copy import deepcopy

from src.Controller.LoadingPopup import LoadingPopup

from src.Model.Data_Storage.ConnGraph_Model import ConnGraph_Infos
from src.Model.Data_Storage.Filters_Model import Filters_Infos
from src.Model.Data_Storage.FiltersSave_Model import FiltersSave_Infos
from src.Model.Data_Storage.Project_Model import Project_Infos

from src.Model.ImportPreviousFiles import ParserPrevious_Files
from src.Model.ExportPreviousFiles import ExportPrevious_Files
from src.Model.ImportProject_Files import ParserProject_Files
from src.Model.ImportFilters_Files import ParserFilters_Files
from src.Model.ImportData_Files import ParserData_Files
from src.Model.ImportName_Files import ParserName_Files
from src.Model.ImportFlut_Files import ParserFlut_Files

from src.View.CustomWidgets.CenteredWidget_Widget import CenteredWidget
from src.View.CustomWidgets.ConnGraphic_Widget import ConnGraphic_Widget
from src.View.CustomWidgets.FlowLayout_Layout import FlowLayout
from src.View.CustomWidgets.Graphic_Widget import GraphicWidget
from src.View.CustomWidgets.CheckGridLabel_Widget import CheckGridLabel_Widget
from src.View.CustomWidgets.TableWidgetItemCustom_Widget import NumericTableWidgetItem

from src.View.ImportFile_View import ImportFile_View


class MainWindow_Controller:
    connGraph: ConnGraph_Infos
    filters: Filters_Infos
    filtersSave : FiltersSave_Infos
    project: Project_Infos

    def __init__(self, mainWindow_view):

        self.mainWindow_view = mainWindow_view

        self.projectOpened = False
        self.newFilters = False

        self.connGraph = ConnGraph_Infos()
        self.filters = Filters_Infos()
        self.filtersSave = FiltersSave_Infos()
        self.project = Project_Infos()

        self.filtersToIgnore = [False, False, False, False, False, False, False]

        # Pie Part
        self.displayedPies = []

        # GT Part
        self.displayedLocalMeasures = []

        # Filter part
        self.checkGrid = []
        self.checkGridLabels = []
        self.checkAllGrid_button = None
        self.checkGridSpacers = []
        self.checkGridChecked = None

        self._InitActions()
        self._InitFilter()
        self._InitOther()

    def _InitActions(self):
        """
        
        
        
        
        
        
        
        """


        # ToolBar actions

        # ----- Projects -----

        self.createProject_action = QAction("Create New Project", self.mainWindow_view.menuBar)
        self.openProject_action = QAction("Open Existing Project", self.mainWindow_view.menuBar)
        self.closeProject_action = QAction("Close Project", self.mainWindow_view.menuBar)
        self.clearRecentProjects_action = QAction("Clear Menu", self.mainWindow_view.openRecentProjects_menu)
        self.exportProject_action = QAction("Export Project", self.mainWindow_view.menuBar)
        self.exportProject_action.setEnabled(False)

        self.createProject_action.triggered.connect(self.CreateNewProject_ToolBarFunction)
        self.openProject_action.triggered.connect(self.OpenExistingProject_ToolBarFunction)
        self.closeProject_action.triggered.connect(self.CloseProject_ToolBarFunction)
        self.clearRecentProjects_action.triggered.connect(self.ClearRecentProjects)
        self.exportProject_action.triggered.connect(self.ExportProjectToJSON_ToolBarFunction)

        # ----- Filters ------
        self.openFilters_action = QAction("Open Existing Filers", self.mainWindow_view.menuBar)
        self.openFilters_action.setEnabled(False)
        self.clearRecentFilters_action = QAction("Clear Menu", self.mainWindow_view.openRecentFilters_menu)
        self.exportFilters_action = QAction("Export Filers", self.mainWindow_view.menuBar)
        self.exportFilters_action.setEnabled(False)

        self.openFilters_action.triggered.connect(self.OpenExistingFilters_ToolBarFunction)
        self.clearRecentFilters_action.triggered.connect(self.ClearRecentFilters)
        self.exportFilters_action.triggered.connect(self.ExportFiltersToJSON_ToolBarFunction)

        # ----- Other ------

        self.help_action = QAction("Help", self.mainWindow_view.menuBar)
        self.about_action = QAction("About", self.mainWindow_view.menuBar)

        self.help_action.triggered.connect(self.Help_ToolBarFunction)
        self.about_action.triggered.connect(self.About_ToolBarFunction)

        # Action triggered when tab is changed in tabWidget
        self.mainWindow_view.mainTabWidget.currentChanged.connect(self.TabWidgetIndexChanged)

        # Filter actions

        # Reset filter
        self.resetFilter_action = QAction("Reset filter", self.mainWindow_view)
        self.resetGraphicFilter_action = QAction("Reset graphic filter", self.mainWindow_view)
        self.exportCircularGraphic_action = QAction("Export Circular graphic", self.mainWindow_view)
        self.exportList_action = QAction("Export List", self.mainWindow_view)

        self.resetFilter_action.triggered.connect(self.ResetFilter)
        self.resetGraphicFilter_action.triggered.connect(self.ResetGraphicFilter)
        # Warning, connGraph_widget need to be initialized
        self.exportCircularGraphic_action.triggered.connect(self.ExportCircularGraphic_Action)
        self.exportList_action.triggered.connect(self.ExportListToCSV)

        # Type filter
        self.mainWindow_view.homotopic_checkBox.stateChanged.connect(
            lambda: self.UpdateFilter_Event(self.mainWindow_view.homotopic_checkBox.objectName()))
        self.mainWindow_view.contralateral_checkBox.stateChanged.connect(
            lambda: self.UpdateFilter_Event(self.mainWindow_view.contralateral_checkBox.objectName()))
        self.mainWindow_view.ipsilateral_checkBox.stateChanged.connect(
            lambda: self.UpdateFilter_Event(self.mainWindow_view.ipsilateral_checkBox.objectName()))
        self.mainWindow_view.other_checkBox.stateChanged.connect(
            lambda: self.UpdateFilter_Event(self.mainWindow_view.other_checkBox.objectName()))

        # Discard weight/rank filter
        self.mainWindow_view.discardWeight_checkBox.stateChanged.connect(
            lambda: self.UpdateFilter_Event(self.mainWindow_view.discardWeight_checkBox.objectName()))
        self.mainWindow_view.discardWeight_spinBox.valueChanged.connect(
            lambda: self.UpdateFilter_Event(self.mainWindow_view.discardWeight_spinBox.objectName()))

        self.mainWindow_view.discardAbsWeight_checkBox.stateChanged.connect(
            lambda: self.UpdateFilter_Event(self.mainWindow_view.discardAbsWeight_checkBox.objectName()))
        self.mainWindow_view.discardAbsWeight_spinBox.valueChanged.connect(
            lambda: self.UpdateFilter_Event(self.mainWindow_view.discardAbsWeight_spinBox.objectName()))

        self.mainWindow_view.discardRank_checkBox.stateChanged.connect(
            lambda: self.UpdateFilter_Event(self.mainWindow_view.discardRank_checkBox.objectName()))
        self.mainWindow_view.discardRank_spinBox.valueChanged.connect(
            lambda: self.UpdateFilter_Event(self.mainWindow_view.discardRank_spinBox.objectName()))

        # Graphic settings
        self.mainWindow_view.widthCoefValue_spinBox.valueChanged.connect(
            lambda: self.UpdateFilter_Event(self.mainWindow_view.widthCoefValue_spinBox.objectName()))
        self.mainWindow_view.colorPalette_comboBox.currentIndexChanged.connect(
            lambda: self.UpdateFilter_Event(self.mainWindow_view.colorPalette_comboBox.objectName()))

        # GT settings 
        self.mainWindow_view.binaryThreshold_SpinBox.valueChanged.connect(self.BinaryGraphConstruction)
        self.mainWindow_view.binary_checkBox.stateChanged.connect(self.GTAfterFilters)
        
        # Action Creation - Open Project File
        self.toCsv_Qaction = QtWidgets.QAction('ExportToCSV', self.mainWindow_view)
        self.toCsv_Qaction.triggered.connect(self.ExportListToCSV)

    def _InitFilter(self):

        # Set value for weight and conn infos labels
        self.mainWindow_view.weightSumValue_label.setText('...')
        self.mainWindow_view.weightMeanValue_label.setText('...')
        self.mainWindow_view.connNumValue_label.setText('...')

    def _InitOther(self):

        self._InitPie()
        self._InitList()
        self._InitGT()

        try:
            # Previous File Initialization
            parserPreviousFiles = ParserPrevious_Files()
            self.project.previousFiles = parserPreviousFiles.LoadFile()

        except Exception as exception:
            print("[ERROR]", exception.args[0])
            self.mainWindow_view.ErrorLoading("[ERROR]" + exception.args[0])

    def _InitToolBar(self):

        self.UpdatePreviousFilters()
        self.UpdatePreviousProject()
        
        self.mainWindow_view.openRecentFilters.setEnabled(False)

    # --------- Menu bar actions ---------

    def CreateNewProject_ToolBarFunction(self):
        self.OpenImportWindows_ToolBarFunction()

    def OpenExistingProject_ToolBarFunction(self):

        self.CloseProject_ToolBarFunction()

        userDirectory = QStandardPaths.writableLocation(QStandardPaths.HomeLocation)
        fileName, _ = QFileDialog.getOpenFileName(self.mainWindow_view,
                                                "Open Existing Project File",
                                                userDirectory,
                                                "Supported Files (*.json)")

        if fileName:
            self.OpenProjectFile(fileName)

    def CloseProject_ToolBarFunction(self):
        
        self.filters.InitReset()
        self.connGraph.InitReset()
        self.project.InitReset()

        self.projectOpened = False
        self.HideItems()
        self.RemoveDataMainWindow()

    def ExportProjectToJSON_ToolBarFunction(self):

        userDirectory = QStandardPaths.writableLocation(QStandardPaths.HomeLocation)
        filePath, _ = QFileDialog.getSaveFileName(self.mainWindow_view,
                                                  "Export Project Files",
                                                  userDirectory,
                                                  "JSON Files (*.json)")

        if filePath:

            if not filePath.endswith(".json"):
                filePath += ".json"

            self.project.ExportToJSON(filePath)

    def OpenExistingFilters_ToolBarFunction(self):

        userDirectory = QStandardPaths.writableLocation(QStandardPaths.HomeLocation)
        fileName, _ = QFileDialog.getOpenFileName(self.mainWindow_view,
                                                "Open Existing Filters File",
                                                userDirectory,
                                                "Supported Files (*.json)")

        if fileName:
            self.OpenFiltersFile(fileName)

    def ExportFiltersToJSON_ToolBarFunction(self):

        userDirectory = QStandardPaths.writableLocation(QStandardPaths.HomeLocation)
        filePath, _ = QFileDialog.getSaveFileName(self.mainWindow_view,
                                                  "Export Filters Files",
                                                  userDirectory,
                                                  "JSON Files (*.json)")

        if filePath:

            if not filePath.endswith(".json"):
                filePath += ".json"

            self.filters.ExportToJSON(filePath)

    def Help_ToolBarFunction(self):
        
        resourcedir = Path(__file__).parent.parent.parent / 'resources'
        pdf_path = os.path.join(resourcedir, "help_pdf.pdf")

        pdf_url = 'file://' + os.path.abspath(pdf_path)

        webbrowser.open(pdf_url)

    def About_ToolBarFunction(self):
        about = f"""
--------------------------------------------------------------
pyIACOB v{version} : {release_date}

Authors :
- enzo.creuzet@univ-tours.fr
- thibaud.scribe@univ-tours.fr

Supervisors : 
- frederic.andersson@univ-tours.fr
- barthelemy.serres@univ-tours.fr
--------------------------------------------------------------
    """
        
        print(about)

    # ---------- Interface Initialization ----------

    def TabWidgetIndexChanged(self, tabIndex: int):

        # Update view based on the current tab
        # Hide the dock widget for the "FileInfo" tab only
        match tabIndex:
            case 0:   # tab File info
                self.mainWindow_view.dockWidget.hide()

            case 1:  # tab Circular
                self.mainWindow_view.gtView_groupBox.hide()
                self.mainWindow_view.edgeView_groupBox.show()
                self.mainWindow_view.edgeColor_groupBox.show()

                self.mainWindow_view.exportCircular_button.show()
                self.mainWindow_view.exportList_button.hide()

                self.mainWindow_view.dockWidget.show()

            case 2:  # tab Pie
                self.mainWindow_view.gtView_groupBox.hide()
                self.mainWindow_view.edgeView_groupBox.hide()
                self.mainWindow_view.edgeColor_groupBox.hide()

                self.mainWindow_view.exportCircular_button.hide()
                self.mainWindow_view.exportList_button.hide()

                self.mainWindow_view.dockWidget.show()

            case 3:  # tab List
                self.mainWindow_view.gtView_groupBox.hide()
                self.mainWindow_view.edgeView_groupBox.hide()
                self.mainWindow_view.edgeColor_groupBox.hide()

                self.mainWindow_view.exportCircular_button.hide()
                self.mainWindow_view.exportList_button.show()

                self.mainWindow_view.dockWidget.show()

            case 4:  # tab GT
                self.mainWindow_view.edgeView_groupBox.hide()
                self.mainWindow_view.edgeColor_groupBox.hide()
                self.mainWindow_view.gtView_groupBox.show()

                self.mainWindow_view.exportCircular_button.hide()
                self.mainWindow_view.exportList_button.hide()

                self.mainWindow_view.dockWidget.show()

    def OpenImportWindows_ToolBarFunction(self):

        ImportFileWindow = ImportFile_View(parent=self.mainWindow_view)
        ImportFileWindow.setWindowTitle("ImportFile Window")
        
        resourcedir = Path(__file__).parent.parent.parent / 'resources'
        icon_path = os.path.join(resourcedir, "images", "chat_pixel.jpg")
        ImportFileWindow.setWindowIcon(QIcon(icon_path))

        with open(os.path.join(resourcedir, "Style_Application.qss"), 'r') as file:
            stylesheet = file.read()
            ImportFileWindow.setStyleSheet(stylesheet)

        ImportFileWindow.show()

    def UpdatePreviousProject(self):

        actions = self.mainWindow_view.openRecentProjects_menu.actions()

        for action in actions:
            if action != self.mainWindow_view.separatorRecentProject and action != self.clearRecentProjects_action:
                self.mainWindow_view.openRecentProjects_menu.removeAction(action)
                action.deleteLater()

        for project in self.project.previousFiles["ProjectFiles"]:

            addRecentProjects_action = QAction(os.path.basename(project), self.mainWindow_view.openRecentProjects_menu)
            addRecentProjects_action.setData(project)
            addRecentProjects_action.triggered.connect(self.OpenRecentProject)
            self.mainWindow_view.openRecentProjects_menu.insertAction(self.mainWindow_view.separatorRecentProject, addRecentProjects_action)

    def OpenRecentProject(self):

        self.CloseProject_ToolBarFunction()

        action = self.mainWindow_view.sender()
        self.OpenProjectFile(action.data())

    def ClearRecentProjects(self):

        actions = self.mainWindow_view.openRecentProjects_menu.actions()

        for action in actions:
            if action != self.mainWindow_view.separatorRecentProject and action != self.clearRecentProjects_action:
                self.mainWindow_view.openRecentProjects_menu.removeAction(action)
                action.deleteLater()

        self.project.previousFiles["ProjectFiles"] = []

    def UpdatePreviousFilters(self):

        actions = self.mainWindow_view.openRecentFilters_menu.actions()

        for action in actions:
            if action != self.mainWindow_view.separatorRecentFilters and action != self.clearRecentFilters_action:
                self.mainWindow_view.openRecentFilters_menu.removeAction(action)
                action.deleteLater()

        for filters in self.project.previousFiles["FiltersFiles"]:

            addRecentFilters_action = QAction(os.path.basename(filters), self.mainWindow_view.openRecentFilters_menu)
            addRecentFilters_action.setData(filters)
            addRecentFilters_action.triggered.connect(self.OpenRecentFilters)
            self.mainWindow_view.openRecentFilters_menu.insertAction(self.mainWindow_view.separatorRecentFilters, addRecentFilters_action)

    def OpenRecentFilters(self):

        action = self.mainWindow_view.sender()
        self.OpenFiltersFile(action.data())

    def ClearRecentFilters(self):

        actions = self.mainWindow_view.openRecentFilters_menu.actions()

        for action in actions:
            if action != self.mainWindow_view.separatorRecentFilters and action != self.clearRecentFilters_action:
                self.mainWindow_view.openRecentFilters_menu.removeAction(action)
                action.deleteLater()

        self.project.previousFiles["FiltersFiles"] = []


    # Open / Coherence Project (Data / Name / FLUT Files)
    def OpenProjectFile(self, fileName):

        try:

            # Parser Files
            parserProjectFile = ParserProject_Files()
            parserProjectFile.ProjectFile_Parser(fileName)

            parserDataFile = ParserData_Files()
            parserDataFile.GraphCreation(self.project.currentDataFile)
            self.InitConnGraph()

            if self.project.currentNameFile:
                self.parserNameFile = ParserName_Files()
                self.parserNameFile.NameFile_Parser(self.project.currentNameFile)
                self.CoherenceVerification_NAMEDATA()

            # Parser the File
            parserFlutFile = ParserFlut_Files()
            parserFlutFile.FlutFile_Parser(self.project.currentFlutFile)

            # Verify the coherence between Data and FLUT Files
            if not self.CoherenceVerification_NAMEFLUT():

                # Popup for warning
                self.mainWindow_view.WarningPopUpValidation()

                if not self.validation:
                    return

            if len(self.connGraph.areasOrder) > 150:
                self.mainWindow_view.WarningPopUpNumberRegion()

            # If the coherence are OK
            self.connGraph.SetTypeConnexion()

        except Exception as exception:
            print("[ERROR]", exception.args[0])
            self.mainWindow_view.ErrorLoading("[ERROR]" + exception.args[0])
            return

        # Update Recent Project Files
        if fileName not in self.project.previousFiles["ProjectFiles"]:
            if len(self.project.previousFiles["ProjectFiles"]) == 5:
                self.project.previousFiles["ProjectFiles"].pop()

            self.project.previousFiles["ProjectFiles"].append(fileName)

            self.UpdatePreviousProject()

        self.OpenFiltersFile(self.project.currentFiltersFile)

        self.loadingPopup = LoadingPopup(self.mainWindow_view)
        self.loadingPopup.show()
        QTimer.singleShot(100, self.LoadingExecute)

    def LoadingExecute(self):
        self.UpdateConnGraphAfterFilter()
        self.LoadDataMainWindow()
        self.loadingPopup.accept()

    def InitConnGraph(self):

        self.graphValues = list(self.connGraph.GetAllValues())
        self.connGraph.allGraphValues = self.graphValues
        self.sortedGraphValues = sorted(self.graphValues, key=abs)

        nbValues = len(self.graphValues)
        self.valuesRank = {value: nbValues - rank for rank, value in enumerate(self.sortedGraphValues)}
        self.connGraph.valuesRank = self.valuesRank

        self.connGraph.minMax = (min(self.graphValues), max(self.graphValues))

        self.plotMinMax = (min(self.graphValues, key=abs), max(self.graphValues, key=abs))
        self.connGraph.plotMinMax = self.plotMinMax

        self.absMinMax = (abs(self.plotMinMax[0]), abs(self.plotMinMax[1]))
        self.connGraph.absMinMax = self.absMinMax

        difference = self.absMinMax[1] - self.absMinMax[0]

        if difference < 2:
            self.valueRound = 5
        elif difference < 5:
            self.valueRound = 4
        elif difference < 20:
            self.valueRound = 3
        elif difference < 50:
            self.valueRound = 2
        elif difference < 100:
            self.valueRound = 1
        else:
            self.valueRound = 0

    def UpdateConnGraphAfterFilter(self):

        self.valueRank = self.filters.rankBetween_threshold[1]
        for value, rank in self.connGraph.valuesRank.items():
            if rank == self.filters.rankBetween_threshold[1]:
                self.valueRank = value 
                break
            elif rank > self.filters.rankBetween_threshold[1]:
                self.valueRank = value 
                break

        if self.filters.thresholdPostFiltering < self.valueRank:
            sortedBy = self.filters.thresholdPostFiltering
        else:
            sortedBy = self.valueRank

        nxGraph = nx.Graph()
        for areaInfoName in self.connGraph.areaInfos.keys():
            nxGraph.add_node(areaInfoName)

        edgesValuesCopy = deepcopy(self.connGraph.edgesValues)
        for id_source, DestValue in edgesValuesCopy.items():
                
            for id_dest, value in DestValue.items():

                if abs(value) < sortedBy:
                    del self.connGraph.edgesValues[id_source][id_dest]
                    continue

            if len(self.connGraph.edgesValues[id_source]) == 0:
                del self.connGraph.edgesValues[id_source]

        self.connGraph.SetGraph(nxGraph)

        edgesValues_withoutDuplicataCopy = deepcopy(self.connGraph.edgesValues_withoutDuplicata)
        for nodeIDnodeDest, value in edgesValues_withoutDuplicataCopy.items():
            if abs(value) < sortedBy:
                del self.connGraph.edgesValues_withoutDuplicata[nodeIDnodeDest]

        self.connGraph.numberOfEdges = len(self.connGraph.edgesValues_withoutDuplicata)

    def CoherenceVerification_NAMEDATA(self):

        # Verify the correct relation between the Connectivity Matrix and Names
        if self.connGraph.numberOfNodesInData != len(self.connGraph.idName):
            raise Exception("Wrong Format - Different Number of Name/Nodes")
        
    def CoherenceVerification_NAMEFLUT(self):

        # Verify the Correlation between Name and Flut (Name and Number of Name)
        areaInfo_idName = {str(ID['ID']): name for name, ID in self.connGraph.areaInfos.items()}
        self.limitedAreaInfo = {}
        self.dataToRemove = []

        # For each Name, compare with Flut Name
        for id, nameOrID in self.connGraph.idName.items():

            if nameOrID in self.connGraph.areaInfos:
                self.limitedAreaInfo[nameOrID] = self.connGraph.areaInfos[nameOrID]

                continue

            elif nameOrID in areaInfo_idName:
                newName = areaInfo_idName[nameOrID]
                self.connGraph.idName[id] = newName
                self.limitedAreaInfo[newName] = self.connGraph.areaInfos[newName]
                continue

            print("This ID or Name is different between DATA and FLUT", nameOrID)
            self.dataToRemove.append(id)

        return self.dataToRemove == []

    def IgnoreValidationIncoherences(self):

        for id_source in self.dataToRemove:

            del self.connGraph.idName[id_source]

            if id_source in self.connGraph.edgesValues:
                for id_dest in self.connGraph.edgesValues[id_source]:
                    del self.connGraph.edgesValues[id_dest][id_source]


                    minMax = (min(id_source, id_dest), max(id_source, id_dest))
                    if minMax in self.connGraph.edgesValues_withoutDuplicata:
                        del self.connGraph.edgesValues_withoutDuplicata[minMax]
                    else:
                        del self.connGraph.edgesValues_withoutDuplicata[(minMax[1], minMax[0])]

                del self.connGraph.edgesValues[id_source]

        self.validation = True

    def CancelValidation(self):

        self.validation = False

    def HideRegions(self):

        idName_Inversed = {str(name): ID for ID, name in self.connGraph.idName.items()}
        newAreaOrder = []

        # Delete unused area between Data File and Flut File
        for item in self.connGraph.areasOrder:
            if item[0] in idName_Inversed or str(item[1]) in idName_Inversed:
                newAreaOrder.append(item)
            elif item[0] == 'xxxx':
                newAreaOrder.append(item)

        self.connGraph.areasOrder = newAreaOrder
        self.connGraph.areaInfos = self.limitedAreaInfo

        self.connGraph.numberOfNodes = len(self.connGraph.areaInfos)

    def DisplayAllRegions(self):
        # Display All regions
        pass


    # Open / Coherence Filters

    def OpenFiltersFile(self, fileName):

        self.filters.InitReset()

        try:
            parserFiltersFile = ParserFilters_Files()
            parserFiltersFile.FiltersFile_Parser(fileName)

        except Exception as exception:
            print("[ERROR]", exception.args[0])
            self.mainWindow_view.ErrorLoading("[ERROR]" + exception.args[0])
            return
        
        # Update Recent Filters Files
        if fileName not in self.project.previousFiles["FiltersFiles"]:

            if len(self.project.previousFiles["FiltersFiles"]) == 5:
                self.project.previousFiles["FiltersFiles"].pop()

            self.project.previousFiles["FiltersFiles"].append(fileName)

            self.UpdatePreviousFilters()

        # Verify the coherence between Data and FLUT Files
        if not self.CoherenceVerification_DATAFILTERS():

            # Popup for warning
            self.mainWindow_view.WarningPopUpFilters()

            if not self.filtersIgnored:
                return
        
        if self.projectOpened:
            self.LoadFilter()
            self.UpdateFileInfo()

    def CoherenceVerification_DATAFILTERS(self):

        minABSEdgeFiltered = min(self.connGraph.edgesValues_withoutDuplicata.values(), key=abs)
        minEdgeFiltered = min(self.connGraph.edgesValues_withoutDuplicata.values())

        # Coherence Verification between data and threshold
        if self.filters.thresholdPostFiltering < abs(minABSEdgeFiltered):
            self.filtersToIgnore[0] = True

        if self.filters.weightBetween_threshold[0] < minEdgeFiltered:
            self.filtersToIgnore[1] = True

        if self.filters.weightBetween_threshold[1] != self.connGraph.minMax[1]:
            self.filtersToIgnore[2] = True

        if self.filters.absWeightBetween_threshold[0] < abs(minABSEdgeFiltered):
            self.filtersToIgnore[3] = True
        else:
            if not self.filtersToIgnore[0]:
                if self.filters.absWeightBetween_threshold[0] < self.filters.thresholdPostFiltering:
                    self.filtersToIgnore[3] = True

        if self.filters.absWeightBetween_threshold[1] != self.connGraph.absMinMax[1]:
            self.filtersToIgnore[4] = True

        if self.filters.rankBetween_threshold[1] > self.connGraph.numberOfEdges:
            self.filtersToIgnore[5] = True

        allInterRegConnCorrect = True
        allRegionsNames = []

        for namesPair in self.filters.discardInterRegConn.keys():
            for name in namesPair:

                if name not in self.connGraph.colorMajorRegions:
                    allInterRegConnCorrect = False
                    self.filtersToIgnore[6] = True
                    break

            allRegionsNames.append(name)

            if not allInterRegConnCorrect:
                break

        allRegionsNames = list(set(allRegionsNames))
        if len(allRegionsNames) != len(self.connGraph.colorMajorRegions):
            self.filtersToIgnore[6] = True

        for region1 in allRegionsNames:
            for region2 in allRegionsNames:
                if (region1, region2) not in self.filters.discardInterRegConn:
                    self.filters.discardAbsWeight[(region1, region2)] = True

        return self.filtersToIgnore == [False, False, False, False, False, False, False]

    def IgnoreFiltersIncoherences(self):

        self.filtersIgnored = True

        for indexFilter, toIgnore in enumerate(self.filtersToIgnore):
            if toIgnore:
                match indexFilter:
                    case 0:
                        self.filters.thresholdPostFiltering = self.connGraph.absMinMax[0]
                    case 1:
                        self.filters.weightBetween_threshold[0] = self.connGraph.minMax[0]
                    case 2:
                        self.filters.weightBetween_threshold[1] = self.connGraph.minMax[1]
                    case 3:
                        self.filters.absWeightBetween_threshold[0] = self.filters.thresholdPostFiltering
                    case 4:
                        self.filters.absWeightBetween_threshold[1] = self.connGraph.absMinMax[1]
                    case 5:
                        self.filters.rankBetween_threshold[1] = self.connGraph.numberOfEdges
                    case 6:
                        self.filters.discardInterRegConn = {}

    def CancelFilters(self):

        self.filtersIgnored = False
        self.filters.LoadSaveFilters(self.filtersSave.RecovertFiltersSave())

        if not self.filtersSave.Save:
            # Initialize correctly the filters
            self.filters.valueRound = self.valueRound
            self.filters.thresholdPostFiltering = self.connGraph.absMinMax[0]

            self.filters.SetWeightMax(self.connGraph.minMax[1])
            self.filters.SetWeightMin(self.connGraph.minMax[0])

            self.filters.SetAbsWeightMin(self.connGraph.absMinMax[0])
            self.filters.SetAbsWeightMax(self.connGraph.absMinMax[1])

            self.filters.SetRankMax(self.connGraph.numberOfEdges)

        
    # ---------- Interface Update ----------

    def LoadDataMainWindow(self):

        self.RemoveDataMainWindow()
        self.ShowItems()
    
        self.UpdateGraph()

        self.projectOpened = True

        self.UpdateFileInfo()
        self.LoadFilter()

        self.UpdatePreviousFilters()

    def RemoveDataMainWindow(self):

        self.projectOpened = False

        # ==== Circular graph ====
        circularLayout = self.mainWindow_view.circularTabSupport_Frame.layout()
        self.ClearLayout(circularLayout)

        # ==== GT graph ====
        # Clear the FlowLayout
        if self.displayedLocalMeasures:
            self.mainWindow_view.region_scroll_layout_GT.clear()
            self.displayedLocalMeasures = []

        self.mainWindow_view.gtList_tableWidget.setRowCount(0)

        # ==== Pie Part ====

        # Clear the FlowLayout
        if self.displayedPies:
            self.mainWindow_view.region_scroll_layout.clear()
            self.mainWindow_view.region_scroll_layout2.clear()
            self.mainWindow_view.region_scroll_layout3.clear()
            self.mainWindow_view.region_scroll_layout4.clear()
            self.mainWindow_view.region_scroll_layout5.clear()
            self.displayedPies = []

        self.mainWindow_view.region_menu.clear()

        # ==== List Part ====

        # Clear the tableWidget before inserting data
        self.mainWindow_view.infoList_tableWidget.setRowCount(0)

        # ==== Filter part ====

        # Clear the checkBoxes grid
        self.ClearLayout(self.mainWindow_view.connSelection_groupBox.layout())
        self.checkGrid = []
        self.checkGridLabels = []
        self.checkAllGrid_button = None
        self.checkGridSpacers = []
        self.checkGridChecked = None
        self.UpdateFilterView()

    def ClearLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.ClearLayout(item.layout())

    def HideItems(self):

        # Tab1 : File Infos
        self.mainWindow_view.fileInfosSupport_Frame.hide()
        self.mainWindow_view.noInfoTab1_Label.show()

        # Tab2 : Graph Circular
        self.mainWindow_view.circularTabSupport_Frame.hide()
        self.mainWindow_view.noInfoTab2_Label.show()

        # Tab3 : Pie
        self.mainWindow_view.pieTabWidget.hide()
        self.mainWindow_view.noInfoTab3_Label.show()

        # Tab4 : List
        self.mainWindow_view.listSupport_Frame.hide()
        self.mainWindow_view.noInfoTab4_Label.show()

        # Tab5 : GT
        self.mainWindow_view.tabGTWidget.hide()
        self.mainWindow_view.noInfoTab5_Label.show()

        # Actions (Filters)
        self.exportFilters_action.setEnabled(False)
        self.exportProject_action.setEnabled(False)
        self.openFilters_action.setEnabled(False)
        self.mainWindow_view.openRecentFilters.setEnabled(False)

    def ShowItems(self):

        # Tab1 : File Infos
        self.mainWindow_view.fileInfosSupport_Frame.show()
        self.mainWindow_view.noInfoTab1_Label.hide()

        # Tab2 : Graph Circular
        self.mainWindow_view.circularTabSupport_Frame.show()
        self.mainWindow_view.noInfoTab2_Label.hide()

        # Tab3 : Pie
        self.mainWindow_view.pieTabWidget.show()
        self.mainWindow_view.noInfoTab3_Label.hide()

        # Tab4 : List
        self.mainWindow_view.listSupport_Frame.show()
        self.mainWindow_view.noInfoTab4_Label.hide()

        # Tab5 : GT
        self.mainWindow_view.tabGTWidget.show()
        self.mainWindow_view.noInfoTab5_Label.hide()

        # Actions (Filters)
        self.exportFilters_action.setEnabled(True)
        self.exportProject_action.setEnabled(True)
        self.openFilters_action.setEnabled(True)
        self.mainWindow_view.openRecentFilters.setEnabled(True)

    def CreateFileInfo(self, filePathFull, ExportType):

        filePath = os.path.dirname(filePathFull)
        filePath_basename = ".".join(os.path.basename(filePathFull).split('.')[:-1])
        newFilePath = os.path.join(filePath, "".join([filePath_basename, "-", ExportType, "_INFO.txt"]))

        with open(newFilePath, 'w', newline='') as file:
            file.write(f"Data File: {self.project.currentDataFile}\n")
            
            if self.project.currentNameFile:
                file.write(f"Name File: {self.project.currentNameFile}\n")
                
            file.write(f"Flut File: {self.project.currentFlutFile}\n")
            
            # Convert Filters in to JSON and write in the file
            filters_json = json.dumps(self.filters.PreparationToJSON(), indent=4)
            file.write(f"Filters File:\n{filters_json}\n")

    # ---------- Filter Initialization / Loading --------
    
    def LoadFilter(self):

        # Init inter regional connection checkboxes grid
        self.checkGrid: list[QCheckBox]
        self.checkGridLabels: list[list[CheckGridLabel_Widget]]
        self.checkAllGrid_button: QPushButton

        interRegNames = self.connGraph.GetAllInterRegionalName()

        if not self.filters.discardInterRegConn:
            self.filters.InitInterRegConnDict(interRegNames)

        if not self.checkGrid :
            self.checkGrid, self.checkGridLabels, self.checkAllGrid_button, self.checkGridSpacers = self.CreateInterRegGrid(interRegNames)

            self.checkGridChecked = True

        # Init filters
        self.filtersSave.LoadCurrentFilters(self.filters.SaveCurrentFilters())

        self.newFilters = True
        self.UpdateFilterView()
        self.newFilters = False

    def UpdateFilterView(self):

        self.BlockFilterSignals(True)

        # Connection types
        self.mainWindow_view.homotopic_checkBox.setChecked(self.filters.homotopic_connType)
        self.mainWindow_view.contralateral_checkBox.setChecked(self.filters.contralateral_connType)
        self.mainWindow_view.ipsilateral_checkBox.setChecked(self.filters.ipsilateral_connType)
        self.mainWindow_view.other_checkBox.setChecked(self.filters.other_connType)

        # Grid
        for checkBox in self.checkGrid:
            # TODO : faire des accesseurs pour éviter ces lignes de code redondantes
            names = checkBox.objectName().split(",")
            nameRow = names[0]
            nameColumn = names[1]
            state = self.filters.InterRegConnEnabled(nameRow, nameColumn)

            if state is not None:
                checkBox.setChecked(state)

        # Thresholds
        if self.filters.discardWeight:
            self.mainWindow_view.discardWeight_checkBox.setChecked(True)
            self.mainWindow_view.discardAbsWeight_checkBox.setChecked(False)
            self.mainWindow_view.discardRank_checkBox.setChecked(False)
        elif self.filters.discardAbsWeight:
            self.mainWindow_view.discardWeight_checkBox.setChecked(False)
            self.mainWindow_view.discardAbsWeight_checkBox.setChecked(True)
            self.mainWindow_view.discardRank_checkBox.setChecked(False)
        elif self.filters.discardRank:
            self.mainWindow_view.discardWeight_checkBox.setChecked(False)
            self.mainWindow_view.discardAbsWeight_checkBox.setChecked(False)
            self.mainWindow_view.discardRank_checkBox.setChecked(True)
        else:
            self.mainWindow_view.discardWeight_checkBox.setChecked(False)
            self.mainWindow_view.discardAbsWeight_checkBox.setChecked(False)
            self.mainWindow_view.discardRank_checkBox.setChecked(False)

        self.mainWindow_view.discardWeight_spinBox.setSingleStep(math.pow(10, - self.filters.valueRound))
        self.mainWindow_view.discardWeight_spinBox.setDecimals(self.filters.valueRound)
        weightMin = self.filters.WeightMin()
        weightMax = self.filters.WeightMax()
        self.mainWindow_view.discardWeight_spinBox.setRange(weightMin, weightMax)
        self.mainWindow_view.discardWeight_spinBox.setValue(self.filters.WeightMin())

        self.mainWindow_view.discardAbsWeight_spinBox.setSingleStep(math.pow(10, - self.filters.valueRound))
        self.mainWindow_view.discardAbsWeight_spinBox.setDecimals(self.filters.valueRound)
        absWeightMin = self.filters.AbsWeightMin()
        absWeightMax = self.filters.AbsWeightMax()
        self.mainWindow_view.discardAbsWeight_spinBox.setRange(absWeightMin, absWeightMax)
        self.mainWindow_view.discardAbsWeight_spinBox.setValue(self.filters.AbsWeightMin())

        self.mainWindow_view.discardRank_spinBox.setRange(0, self.filters.RankMax())
        self.mainWindow_view.discardRank_spinBox.setValue(self.filters.RankMax())

        self.mainWindow_view.binaryThreshold_SpinBox.setRange(self.filters.absWeightBetween_threshold[0], 
                                                              self.filters.absWeightBetween_threshold[1])
        self.mainWindow_view.binaryThreshold_SpinBox.setSingleStep(math.pow(10, - self.filters.valueRound))
        self.mainWindow_view.binaryThreshold_SpinBox.setDecimals(self.filters.valueRound)
        self.mainWindow_view.binaryThreshold_SpinBox.setValue(self.filters.AbsWeightMin())

        if not self.projectOpened:
            self.mainWindow_view.widthCoefValue_spinBox.setRange(1, 20)
            self.mainWindow_view.widthCoefValue_spinBox.setValue(5)
            self.mainWindow_view.widthCoefValue_spinBox.setSingleStep(1)
            self.mainWindow_view.widthCoefValue_spinBox.setDecimals(0)

        if self.projectOpened:
            self.UpdateCheckGridState_Action()

        self.BlockFilterSignals(False)

        # If a project is already loaded, then we trigger a filter event for all tabs
        if self.projectOpened:
            self.UpdateFilter_Action(True)

    def BlockFilterSignals(self, block: bool):

        self.mainWindow_view.homotopic_checkBox.blockSignals(block)
        self.mainWindow_view.ipsilateral_checkBox.blockSignals(block)
        self.mainWindow_view.contralateral_checkBox.blockSignals(block)
        self.mainWindow_view.other_checkBox.blockSignals(block)

        self.mainWindow_view.discardWeight_checkBox.blockSignals(block)
        self.mainWindow_view.discardAbsWeight_checkBox.blockSignals(block)
        self.mainWindow_view.discardRank_checkBox.blockSignals(block)

        self.mainWindow_view.discardWeight_spinBox.blockSignals(block)
        self.mainWindow_view.discardAbsWeight_spinBox.blockSignals(block)
        self.mainWindow_view.discardRank_spinBox.blockSignals(block)

        self.mainWindow_view.binaryThreshold_SpinBox.blockSignals(block)

        # Checkboxes grid
        for checkBox in self.checkGrid:
            checkBox.blockSignals(block)

        for label in self.checkGrid:
            label.blockSignals(block)

        self.mainWindow_view.widthCoefValue_spinBox.blockSignals(block)

        if self.checkAllGrid_button:
            self.checkAllGrid_button.blockSignals(block)

    def ResetFilter(self):

        self.filters.LoadSaveFilters(self.filtersSave.RecovertFiltersSave())

        # Faster than applying the new filter to the graph
        self.connGraph_widget.connGraphicView.ResetFilter()

        self.newFilters = True
        self.UpdateFilterView()
        self.newFilters = False

    # =========================
    #       Tab File Info
    # =========================
    def UpdateFileInfo(self):

        self.InformationsInitialization()
        self.DisplayInitialGraphCurves()
        self.UpdateGraphCurves(self.filters.thresholdPostFiltering)

    def RoundInitialization(self, value):

        if math.isnan(value):
            return "..."
        
        return round(value) if self.filters.valueRound == 0 else round(value, self.filters.valueRound)

    def InformationsInitialization(self):

        if self.project.currentNameFile:
            self.mainWindow_view.currentDataFile_Label.setText("".join(
                [os.path.basename(self.project.currentDataFile), "\n",
                 os.path.basename(self.project.currentNameFile)]))
        else:
            self.mainWindow_view.currentDataFile_Label.setText(os.path.basename(self.project.currentDataFile))

        self.mainWindow_view.currentFlutFile_Label.setText(os.path.basename(self.project.currentFlutFile))

        graphCurveValues = self.connGraph.edgesValues_withoutDuplicata.values()

        # Nb Nodes / Connections
        self.mainWindow_view.nbNodesValue_Label.setText(str(self.connGraph.numberOfNodes))
        self.mainWindow_view.nbConnectionsValue_Label.setText(str(self.connGraph.numberOfEdges))

        # ABS Mean / ABS Sum
        if len(graphCurveValues) < 2:
                self.mainWindow_view.meanAbsValue_Label.setText("None")
                self.mainWindow_view.sumAbsValue_Label.setText("None")
        else:
            meanAbs = statistics.fmean(map(abs, graphCurveValues))
            sumAbs = sum(map(abs, graphCurveValues))

            self.mainWindow_view.meanAbsValue_Label.setText(str(self.RoundInitialization(meanAbs)))
            self.mainWindow_view.sumAbsValue_Label.setText(str(self.RoundInitialization(sumAbs)))

        if self.filters.valueRound == 0:
            roundMinValue = round(self.connGraph.plotMinMax[0])
        else:
            roundMinValue = round(self.connGraph.plotMinMax[0], self.filters.valueRound) - math.pow(10, -(
                self.filters.valueRound))
        self.mainWindow_view.minValue_Label.setText(str(roundMinValue))
        self.mainWindow_view.maxValue_Label.setText(str(self.RoundInitialization(self.connGraph.plotMinMax[1])))

        if self.filters.valueRound == 0:
            roundMinRelValue = round(self.connGraph.minMax[0])
        else:
            roundMinRelValue = round(self.connGraph.minMax[0], self.filters.valueRound) - math.pow(10, -(
                self.filters.valueRound))
        self.mainWindow_view.minRelValue_Label.setText(str(roundMinRelValue))
        self.mainWindow_view.maxRelValue_Label.setText(str(self.RoundInitialization(self.connGraph.minMax[1])))

        # Standard Deviation
        if len(graphCurveValues) < 2:
            self.mainWindow_view.standardDeviationValue_Label.setText("None")
        else:   
            stddev = statistics.stdev(map(abs, graphCurveValues))
            self.mainWindow_view.standardDeviationValue_Label.setText(str(self.RoundInitialization(stddev)))

        # Threshold
        if self.filters.valueRound == 0:
            roundThreshold = round(self.filters.thresholdPostFiltering)
        else:
            roundThreshold = round(self.filters.thresholdPostFiltering, self.filters.valueRound)
        self.mainWindow_view.thresholdValue_Label.setText(str(roundThreshold))

    def DisplayInitialGraphCurves(self):

        # Clear the previous plot and Create a new one
        self.mainWindow_view.graph_curve.clear()
        self.graph_curve = self.mainWindow_view.graph_curve.add_subplot(111)

        # Sort Values -> Initial value
        positiveValues = [value for value in self.connGraph.allGraphValues if value > 0]
        negativeValues = [value for value in self.connGraph.allGraphValues if value < 0]

        sortedValues = sorted(negativeValues, reverse=True) + sorted(positiveValues, reverse=True)

        x_coords = list(range(len(sortedValues)))
        y_coords = [abs(val) for val in sortedValues]

        self.graph_curve.plot(x_coords, y_coords, label='Initial Curve')

        # Limited plot (initially empty)
        self.limitedCurve, = self.graph_curve.plot([], [], label='Limited Curve')

        # Set the y-axis to logarithmic scale
        self.graph_curve.set_yscale('log')

        # Add title and labels
        self.graph_curve.set_title('Values in Curve', fontsize=20)
        self.graph_curve.set_xlabel('Value', fontsize=15)
        self.graph_curve.set_ylabel('Absolute Value', fontsize=15)

        # Remove x-tick labels
        self.graph_curve.set_xticks([])
        self.graph_curve.set_xticklabels([])

        self.graph_curve.tick_params(axis='y', which='major', labelsize=10)
        self.graph_curve.legend(fontsize=15)

        # Add min and max value annotations outside the plot area
        minValue = min(self.connGraph.allGraphValues, key=abs)
        maxValue = max(self.connGraph.allGraphValues, key=abs)

        # Add min and max value annotations outside the plot area
        if self.filters.valueRound == 0:
            roundMinValue = round(minValue)
        else:
            roundMinValue = round(minValue, self.filters.valueRound) - math.pow(10, -(self.filters.valueRound))

        roundMaxValue = round(maxValue, self.filters.valueRound)

        # Add min and max value outside the plot area with a white background
        self.graph_curve.text(
            -0.05, -0.05,  # Position near the bottom of the plot
            f'Min: {abs(roundMinValue)}',
            fontsize=9, color='black',
            verticalalignment='bottom',
            horizontalalignment='left',
            bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'),
            transform=self.graph_curve.transAxes
        )

        self.graph_curve.text(
            -0.05, 1.05,
            f'Max: {abs(roundMaxValue)}',
            fontsize=9, color='black',
            verticalalignment='top',
            horizontalalignment='left',
            bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'),
            transform=self.graph_curve.transAxes
        )

        # Draw the canvas
        self.mainWindow_view.canvas.draw()

    def UpdateGraphCurves(self, newValue: float):

        graphCurveValues = self.connGraph.allGraphValues

        # Update the limited curve data
        positiveValuesLimited = [value for value in graphCurveValues if value > 0]
        negativeValuesLimited = [value for value in graphCurveValues if value < 0]

        sortedValuesLimited = sorted(negativeValuesLimited, reverse=True) + sorted(positiveValuesLimited, reverse=True)

        x_coordsLimited = list(range(len(sortedValuesLimited)))
        y_coordsLimited = [abs(value) if abs(value) > newValue - math.pow(10, -(self.filters.valueRound))
                           else None for value in sortedValuesLimited]

        self.limitedCurve.set_data(x_coordsLimited, y_coordsLimited)

        # Update the canvas
        self.graph_curve.relim()
        self.graph_curve.autoscale_view()
        self.mainWindow_view.canvas.draw()

    # =========================
    #       Tab Circular
    # =========================
    def UpdateGraph(self):

        # Create graph widget
        self.connGraph_widget = ConnGraphic_Widget()
        self.connGraph_widget.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        # Add it to the connGraphicView

        centeredWidget = CenteredWidget(self.connGraph_widget)

        self.mainWindow_view.circularTabSupport_Frame.layout().addWidget(centeredWidget)

        self.mainWindow_view.mainTabWidget.setCurrentIndex(0)

    # =========================
    #       Tab Pie
    # =========================
    def _InitPie(self):

        # Init a flow layout to enhance the scroll area
        self.mainWindow_view.region_scroll_layout = FlowLayout(self.mainWindow_view.regionScrollContent)
        self.mainWindow_view.regionScrollContent.setContentsMargins(10, 10, 10, 10)

        self.mainWindow_view.region_scroll_layout2 = FlowLayout(self.mainWindow_view.regionScrollContent2)
        self.mainWindow_view.regionScrollContent2.setContentsMargins(10, 10, 10, 10)

        self.mainWindow_view.region_scroll_layout3 = FlowLayout(self.mainWindow_view.regionScrollContent3)
        self.mainWindow_view.regionScrollContent3.setContentsMargins(10, 10, 10, 10)

        self.mainWindow_view.region_scroll_layout4 = FlowLayout(self.mainWindow_view.regionScrollContent4)
        self.mainWindow_view.regionScrollContent4.setContentsMargins(10, 10, 10, 10)

        self.mainWindow_view.region_scroll_layout5 = FlowLayout(self.mainWindow_view.regionScrollContent5)
        self.mainWindow_view.regionScrollContent5.setContentsMargins(10, 10, 10, 10)

        # Create context menu for the "add graphic" button
        self.mainWindow_view.region_menu = QMenu(self.mainWindow_view, triggered=self.AddGraphics_PieTab)

        self.mainWindow_view.addGraphic_button.setMenu(self.mainWindow_view.region_menu)
        self.mainWindow_view.addGraphic2_button.setMenu(self.mainWindow_view.region_menu)
        self.mainWindow_view.addGraphic3_button.setMenu(self.mainWindow_view.region_menu)
        self.mainWindow_view.addGraphic4_button.setMenu(self.mainWindow_view.region_menu)
        self.mainWindow_view.addGraphic5_button.setMenu(self.mainWindow_view.region_menu)

    def PieAfterFilter(self):

        # Clear the FlowLayout
        if self.displayedPies:
            self.mainWindow_view.region_scroll_layout.clear()
            self.mainWindow_view.region_scroll_layout2.clear()
            self.mainWindow_view.region_scroll_layout3.clear()
            self.mainWindow_view.region_scroll_layout4.clear()
            self.mainWindow_view.region_scroll_layout5.clear()
            self.displayedPies = []

        self.mainWindow_view.region_menu.clear()

        self.UpdatePie()

    def UpdatePie(self):

        # Build menu with each region name
        for regionName in self.connGraph.GetAllNameWithConnectivity_PieChart():
            self.mainWindow_view.region_menu.addAction(QAction(regionName, self.mainWindow_view.region_menu))

    def AddGraphics_PieTab(self, action: QAction):

        if action is not None and action.text() not in self.displayedPies:

            # Avoid Same Graph Repetition
            self.displayedPies.append(action.text())

            graphicConnections_widget = GraphicWidget(self, action.text(), "Connections")
            self.mainWindow_view.region_scroll_layout.addWidget(graphicConnections_widget)

            graphicMajorRegions_widget = GraphicWidget(self, action.text(), "MajorRegions")
            self.mainWindow_view.region_scroll_layout2.addWidget(graphicMajorRegions_widget)

            graphicMajorRegions_widgetBar = GraphicWidget(self, action.text(), "MajorRegionsBar")
            self.mainWindow_view.region_scroll_layout3.addWidget(graphicMajorRegions_widgetBar)

            graphicConnectionType_widget = GraphicWidget(self, action.text(), "ConnectionType")
            self.mainWindow_view.region_scroll_layout4.addWidget(graphicConnectionType_widget)

            graphicConnectionType_widgetBar = GraphicWidget(self, action.text(), "ConnectionTypeBar")
            self.mainWindow_view.region_scroll_layout5.addWidget(graphicConnectionType_widgetBar)

    def DeleteGraphics_PieTab(self, name):

        self.displayedPies.remove(name)

        # Remove widget based on the name on each region scroll layout
        for item in range(self.mainWindow_view.region_scroll_layout.count()):
            graphicWidget = self.mainWindow_view.region_scroll_layout.itemAt(item).widget()

            if graphicWidget.name == name:
                # Delete the Widget from the layout
                self.mainWindow_view.region_scroll_layout.removeWidget(graphicWidget)

                # Destroye the Widget and free the resources
                graphicWidget.setParent(None)
                graphicWidget.deleteLater()

                # Update the FlowLayout
                self.mainWindow_view.region_scroll_layout.update()

                break  # don't need to iterate more

        for item in range(self.mainWindow_view.region_scroll_layout2.count()):
            graphicWidget = self.mainWindow_view.region_scroll_layout2.itemAt(item).widget()

            if graphicWidget.name == name:
                # Delete the Widget from the layout
                self.mainWindow_view.region_scroll_layout2.removeWidget(graphicWidget)

                # Destroye the Widget and free the resources
                graphicWidget.setParent(None)
                graphicWidget.deleteLater()

                # Update the FlowLayout
                self.mainWindow_view.region_scroll_layout2.update()

                break  # don't need to iterate more

        for item in range(self.mainWindow_view.region_scroll_layout3.count()):
            graphicWidget = self.mainWindow_view.region_scroll_layout3.itemAt(item).widget()

            if graphicWidget.name == name:
                # Delete the Widget from the layout
                self.mainWindow_view.region_scroll_layout3.removeWidget(graphicWidget)

                # Destroye the Widget and free the resources
                graphicWidget.setParent(None)
                graphicWidget.deleteLater()

                # Update the FlowLayout
                self.mainWindow_view.region_scroll_layout3.update()

                break  # don't need to iterate more

        for item in range(self.mainWindow_view.region_scroll_layout4.count()):
            graphicWidget = self.mainWindow_view.region_scroll_layout4.itemAt(item).widget()

            if graphicWidget.name == name:
                # Delete the Widget from the layout
                self.mainWindow_view.region_scroll_layout4.removeWidget(graphicWidget)

                # Destroye the Widget and free the resources
                graphicWidget.setParent(None)
                graphicWidget.deleteLater()

                # Update the FlowLayout
                self.mainWindow_view.region_scroll_layout4.update()

                break  # don't need to iterate more

        for item in range(self.mainWindow_view.region_scroll_layout5.count()):
            graphicWidget = self.mainWindow_view.region_scroll_layout5.itemAt(item).widget()

            if graphicWidget.name == name:
                # Delete the Widget from the layout
                self.mainWindow_view.region_scroll_layout5.removeWidget(graphicWidget)

                # Destroye the Widget and free the resources
                graphicWidget.setParent(None)
                graphicWidget.deleteLater()

                # Update the FlowLayout
                self.mainWindow_view.region_scroll_layout5.update()

                break  # don't need to iterate more

    # =========================
    #       Tab List
    # =========================

    def _InitList(self):

        # Hide vertical header of the list
        self.mainWindow_view.infoList_tableWidget.verticalHeader().setVisible(False)

        # Disable cell editing and column resizing by user
        self.mainWindow_view.infoList_tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.mainWindow_view.infoList_tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.mainWindow_view.infoList_tableWidget.setSelectionBehavior(
            QAbstractItemView.SelectRows)  # Action when Row clicked
        self.mainWindow_view.infoList_tableWidget.resizeColumnsToContents()
        self.mainWindow_view.infoList_tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)  # Action when Row clicked

        # Set sorting based on the first column
        self.mainWindow_view.infoList_tableWidget.setSortingEnabled(True)

    def ListAfterFilter(self):
        
        # If the table widget is empty, update the list
        if self.mainWindow_view.infoList_tableWidget.rowCount() == 0:
            self.UpdateList()
            return  
        else:

            self.mainWindow_view.infoList_tableWidget.setUpdatesEnabled(False)

            try:
                edges_filtered = self.connGraph.edgesValuesFiltered
                
                # Iterate through all the rows in the table
                for indexRowItem in range(self.mainWindow_view.infoList_tableWidget.rowCount()):
                    # Fetch both source and destination IDs once
                    id_source = int(self.mainWindow_view.infoList_tableWidget.item(indexRowItem, 0).text())
                    id_dest = int(self.mainWindow_view.infoList_tableWidget.item(indexRowItem, 1).text())
                    
                    # Determine whether to hide the row based on conditions
                    hide_row = not (id_source in edges_filtered and id_dest in edges_filtered[id_source])

                    # Apply the visibility flag only once
                    self.mainWindow_view.infoList_tableWidget.setRowHidden(indexRowItem, hide_row)
            finally:

                # Re-enable updates to the table widget after processing
                self.mainWindow_view.infoList_tableWidget.setUpdatesEnabled(True)

    def UpdateList(self):

        # Build a list of edges with each information needed
        edges = np.array(self.connGraph.GetEdgesDetails_List())

        self.mainWindow_view.infoList_tableWidget.setUpdatesEnabled(False)

        self.mainWindow_view.infoList_tableWidget.setRowCount(len(edges))

        # Create each row with edges info
        for rowIndex, edge in enumerate(edges):
            node1 = int(edge[0])
            node2 = int(edge[1])
            area1 = str(edge[2])
            area2 = str(edge[3])
            region1 = str(edge[4])
            region2 = str(edge[5])
            connType = str(edge[6])
            value = float(self.RoundInitialization(float(edge[7])))
            rank = int(edge[8])

            rowRowData = [
            NumericTableWidgetItem(node1),
            NumericTableWidgetItem(node2),
            QTableWidgetItem(area1),
            QTableWidgetItem(area2),
            QTableWidgetItem(region1),
            QTableWidgetItem(region2),
            QTableWidgetItem(connType),
            NumericTableWidgetItem(value),
            NumericTableWidgetItem(rank)
            ]

            # Alignement pour chaque item
            for item in rowRowData:
                item.setTextAlignment(Qt.AlignHCenter)

            # Insertion des éléments préparés
            for columnIndex, item in enumerate(rowRowData):
                self.mainWindow_view.infoList_tableWidget.setItem(rowIndex, columnIndex, item)

        self.mainWindow_view.infoList_tableWidget.setUpdatesEnabled(True)
        self.mainWindow_view.infoList_tableWidget.resizeColumnsToContents()

        # Force the resize for area Name
        header = self.mainWindow_view.infoList_tableWidget.horizontalHeader()

        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)

    def ExportListToCSV(self):

        if self.projectOpened:
            userDirectory = QStandardPaths.writableLocation(QStandardPaths.HomeLocation)
            filePath, _ = QFileDialog.getSaveFileName(self.mainWindow_view, "Save List in CSV", userDirectory,
                                                    "CSV Files (*.csv)")

            if filePath:

                if not filePath.endswith(".csv"):
                    filePath += ".csv"

                with open(filePath, 'w', newline='') as file:
                    writer = csv.writer(file)
                    field = ["Node1", "Node2", "Label1", "Label2", "Region1", "Region2", "ConnectionType", "Connectivity",
                            "Value"]

                    writer.writerow(field)

                    for row in range(self.mainWindow_view.infoList_tableWidget.rowCount()):
                        rowData = []
                        for col in range(self.mainWindow_view.infoList_tableWidget.columnCount()):
                            rowData.append(self.mainWindow_view.infoList_tableWidget.item(row, col).text().replace(' ', ''))

                        writer.writerow(rowData)

                self.CreateFileInfo(filePath, "CSV")

    # =========================
    #       Tab GT
    # =========================
    def _InitGT(self):

        # ----- Init Graph (Local Measures) Part -----

        # Init a flow layout to enhance the scroll area
        self.mainWindow_view.region_scroll_layout_GT = FlowLayout(self.mainWindow_view.regionScrollContentGT)
        self.mainWindow_view.regionScrollContentGT.setContentsMargins(10, 10, 10, 10)

        # Create context menu for the "add graphic" button
        self.mainWindow_view.region_menu_GT = QMenu(self.mainWindow_view, triggered=self.AddGTGraph_GTTab)
        self.mainWindow_view.addGraphGT_button.setMenu(self.mainWindow_view.region_menu_GT)

        # ----- Init List (Global Measures) Part -----

        # Hide vertical header of the list
        self.mainWindow_view.gtList_tableWidget.verticalHeader().setVisible(False)

        # Disable cell editing and column resizing by user
        self.mainWindow_view.gtList_tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.mainWindow_view.gtList_tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.mainWindow_view.gtList_tableWidget.setSelectionBehavior(
            QAbstractItemView.SelectRows)  # Action when Row clicked
        self.mainWindow_view.gtList_tableWidget.resizeColumnsToContents()
        self.mainWindow_view.gtList_tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)  # Action when Row clicked

        # Set sorting based on the first column
        self.mainWindow_view.gtList_tableWidget.setSortingEnabled(True)

    def DisplayWeightedMeasures(self):
        
        self.mainWindow_view.region_menu_GT.clear()
        weightedLocalMeasures = [
            "degree (weighted)",
            "cluster coef (weighted)",
            "local efficiency (weighted)",
            "betweenness centrality (weighted)",
            "eigenvector centrality (weighted)",
            "eccentricity (weighted)",
        ]

        for weightedlocalmeasures in weightedLocalMeasures:
            self.mainWindow_view.region_menu_GT.addAction(QAction(weightedlocalmeasures, self.mainWindow_view.region_menu_GT))

        globalMeasures = {
            "Density": nx.density(self.connGraph.nxGraph),
            "Clustering Coeff Average (weighted)": nx.average_clustering(self.connGraph.nxGraph, weight='weight'),
            "Transitivity (weighted)": nx.transitivity(self.connGraph.nxGraph),
            "Network Characteristic Path Length (weighted)": 0,
            "Global Efficiency (weighted)": nx.global_efficiency(self.connGraph.nxGraph),
            "Diameter of Graph (weighted)": float('inf'),  # Infini pour un graphe déconnecté
            "Radius of Graph (weighted)": float('inf'),  # Infini pour un graphe déconnecté
            "Assortativity Coefficient (weighted)": nx.degree_assortativity_coefficient(self.connGraph.nxGraph, weight='weight'),
        }

        # Calculer la longueur caractéristique du chemin pour le graphe entier
        try:
            globalMeasures["Network Characteristic Path Length (weighted)"] = nx.average_shortest_path_length(self.connGraph.nxGraph, weight='weight')
        except nx.NetworkXError:
            globalMeasures["Network Characteristic Path Length (weighted)"] = float('inf')  # Pour les graphes déconnectés

        # Calculer le diamètre et le rayon pour les composants connexes seulement
        if nx.is_connected(self.connGraph.nxGraph):
            globalMeasures["Diameter of Graph (weighted)"] = nx.diameter(self.connGraph.nxGraph, e=None, usebounds=False)
            globalMeasures["Radius of Graph (weighted)"] = nx.radius(self.connGraph.nxGraph)
        else:
            # Graphe déconnecté : définir le diamètre et le rayon à 'inf'
            globalMeasures["Diameter of Graph (weighted)"] = float('inf')
            globalMeasures["Radius of Graph (weighted)"] = float('inf')


        self.mainWindow_view.gtList_tableWidget.setHorizontalHeaderLabels(["Global Measures (Weighted)", "Values (ABS Graph)"])

        return globalMeasures

    def BinaryGraphConstruction(self):

        if not self.mainWindow_view.binary_checkBox.isChecked():
            return
        
        # Clear the FlowLayout
        if self.displayedLocalMeasures:
            self.mainWindow_view.region_scroll_layout_GT.clear()
            self.displayedLocalMeasures = []
        
        threshold = self.mainWindow_view.binaryThreshold_SpinBox.value()

        self.connGraph.nxGraphBinary = nx.Graph()

        for node in self.connGraph.nxGraph.nodes():
            self.connGraph.nxGraphBinary.add_node(node)

        for node1, node2, data in self.connGraph.nxGraph.edges(data=True):
            if data['weight'] >= threshold:
                self.connGraph.nxGraphBinary.add_edge(node1, node2)

    def DisplayBinaryMeasures(self):

        self.mainWindow_view.region_menu_GT.clear()
        binaryLocalMeasures = [
            "degree (binary)",
            "cluster coef (binary)",
            "local efficiency (binary)",
            "betweenness centrality (binary)",
            "eigenvector centrality (binary)",
            "eccentricity (binary)",
        ]

        for binarylocalmeasures in binaryLocalMeasures:
            self.mainWindow_view.region_menu_GT.addAction(QAction(binarylocalmeasures, self.mainWindow_view.region_menu_GT))

        binaryMeasures = {

            "Density": nx.density(self.connGraph.nxGraphBinary),
            "Clustering Coeff Average (binary)": nx.average_clustering(self.connGraph.nxGraphBinary),
            "Transitivity (binary)": nx.transitivity(self.connGraph.nxGraphBinary),
            "Network Characteristic Path Length (binary)": 0,
            "Global Efficiency (binary)": nx.global_efficiency(self.connGraph.nxGraphBinary),
            "Diameter of Graph (binary)": 0,
            "Radius of Graph (binary)": 0,
            "Assortativity Coefficient (binary)": nx.degree_assortativity_coefficient(self.connGraph.nxGraphBinary),

        }

        components = list(nx.connected_components(self.connGraph.nxGraph))
        numComponents = len(components)

        for component in components:
            subgraph = self.connGraph.nxGraph.subgraph(component)

            binaryMeasures["Network Characteristic Path Length (binary)"] += \
                nx.average_shortest_path_length(subgraph)
            
            if nx.is_connected(subgraph):
                binaryMeasures["Diameter of Graph (binary)"] = \
                    max(binaryMeasures["Diameter of Graph (binary)"], nx.diameter(subgraph))
                binaryMeasures["Radius of Graph (binary)"] = \
                    max(binaryMeasures["Radius of Graph (binary)"], nx.radius(subgraph))

        # Ajout des autres mesures au dictionnaire des mesures globales
        binaryMeasures["Network Characteristic Path Length (binary)"] /= numComponents

        self.mainWindow_view.gtList_tableWidget.setHorizontalHeaderLabels(["Global Measures (Binary)", "Values (ABS Graph)"])
        
        return binaryMeasures
    
    def GTAfterFilters(self):

        # Clear the FlowLayout
        if self.displayedLocalMeasures:
            self.mainWindow_view.region_scroll_layout_GT.clear()
            self.displayedLocalMeasures = []

        self.UpdateGTList_GTTab()

    def AddGTGraph_GTTab(self, action: QAction):

        if action is not None and action.text() not in self.displayedLocalMeasures:

            self.displayedLocalMeasures.append(action.text())
            graphicGT_widget = GraphicWidget(self, action.text(), "GTGraph")
            self.mainWindow_view.region_scroll_layout_GT.addWidget(graphicGT_widget)

    def UpdateGTList_GTTab(self):

        self.mainWindow_view.gtList_tableWidget.setRowCount(0)

        if self.mainWindow_view.binary_checkBox.isChecked():
            self.BinaryGraphConstruction()
            measures = self.DisplayBinaryMeasures()
        else:
            measures = self.DisplayWeightedMeasures()
      
        for indexMeasure, (measure, value) in enumerate(measures.items()):
            self.mainWindow_view.gtList_tableWidget.insertRow(indexMeasure)
            
            itemMeasures = QTableWidgetItem(f"{measure}")
            itemMeasures.setTextAlignment(Qt.AlignCenter)
            self.mainWindow_view.gtList_tableWidget.setItem(indexMeasure, 0, itemMeasures)

            itemValue = QTableWidgetItem(str(value))
            itemValue.setTextAlignment(Qt.AlignCenter)
            self.mainWindow_view.gtList_tableWidget.setItem(indexMeasure, 1, itemValue)


        # Force the resize for area Name
        header = self.mainWindow_view.gtList_tableWidget.horizontalHeader()

        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)

    def DeleteGraphic_GTTab(self, name):

        self.displayedLocalMeasures.remove(name)

        # Remove widget based on the name on each region scroll layout
        for item in range(self.mainWindow_view.region_scroll_layout_GT.count()):
            graphicWidget = self.mainWindow_view.region_scroll_layout_GT.itemAt(item).widget()

            if graphicWidget.name == name:
                # Delete the Widget from the layout
                self.mainWindow_view.region_scroll_layout_GT.removeWidget(graphicWidget)

                # Destroye the Widget and free the resources
                graphicWidget.setParent(None)
                graphicWidget.deleteLater()

                # Update the FlowLayout
                self.mainWindow_view.region_scroll_layout_GT.update()

                break  # don't need to iterate more
    
    
    # --------- Filter actions ---------

    # ----- Update -----

    def UpdateFilter_Event(self, name: str = None):

        if name not in [None, "widthCoefValue_spinBox", "colorPalette_comboBox"] and self.projectOpened:
            if (name == "contralateral_checkBox" or
                    name == "homotopic_checkBox" or
                    name == "ipsilateral_checkBox" or
                    name == "other_checkBox"):
                self.UpdateConnectionType_Filter()

            if name == "checkGrid_checkBox":
                self.UpdateInterRegionalConnection_Filter()

            if (name == "discardWeight_checkBox" or
                    name == "discardAbsWeight_checkBox" or
                    name == "discardWeight_spinBox" or
                    name == "discardAbsWeight_spinBox"):
                
                discardWeight = self.mainWindow_view.discardWeight_checkBox.isChecked()
                discardAbsWeight = self.mainWindow_view.discardAbsWeight_checkBox.isChecked()

                if discardWeight == False and discardAbsWeight == False:
                    return
                
                self.filters.discardWeight = discardWeight 
                self.filters.discardAbsWeight = discardAbsWeight   

                self.filters.SetWeightMin(self.mainWindow_view.discardWeight_spinBox.value())
                self.filters.SetAbsWeightMin(self.mainWindow_view.discardAbsWeight_spinBox.value())

                # Keep only one check box checked at the same time
                if name == "discardWeight_checkBox" and discardWeight:
                    self.mainWindow_view.discardAbsWeight_checkBox.setChecked(False)
                    self.mainWindow_view.discardRank_checkBox.setChecked(False)
                elif name == "discardAbsWeight_checkBox" and discardAbsWeight:
                    self.mainWindow_view.discardWeight_checkBox.setChecked(False)
                    self.mainWindow_view.discardRank_checkBox.setChecked(False)

            if (name == "discardRank_checkBox" or
                    name == "discardRank_spinBox"):
                
                discardRank = self.mainWindow_view.discardRank_checkBox.isChecked()
                if discardRank == False:
                    return

                self.filters.discardRank = discardRank
                self.filters.SetRankMax(self.mainWindow_view.discardRank_spinBox.value())

                if name == "discardRank_checkBox" and discardRank:
                    self.mainWindow_view.discardWeight_checkBox.setChecked(False)
                    self.mainWindow_view.discardAbsWeight_checkBox.setChecked(False)

            absThreshold = self.filters.absWeightBetween_threshold[0]
            relThreshold = self.filters.weightBetween_threshold[0] if self.filters.weightBetween_threshold[0] > self.filters.absWeightBetween_threshold[0] else self.filters.absWeightBetween_threshold[0]
            valueRank = None
            for value, rank in self.connGraph.valuesRank.items():
                if rank == self.filters.rankBetween_threshold[1]:
                    valueRank = value 
                    break
                elif rank < self.filters.rankBetween_threshold[1]:
                    valueRank = value 
                    break

            sortedBy = min(absThreshold, relThreshold, abs(valueRank))
            self.mainWindow_view.binaryThreshold_SpinBox.setRange(sortedBy,
                                                          self.filters.absWeightBetween_threshold[1])
            
            if sortedBy > self.mainWindow_view.binaryThreshold_SpinBox.value():

                # Update Binary Threshold
                if self.mainWindow_view.binary_checkBox.isChecked():
                    self.mainWindow_view.binaryThreshold_SpinBox.setValue(sortedBy)
                else:
                    self.mainWindow_view.binaryThreshold_SpinBox.blockSignals(True)
                    self.mainWindow_view.binaryThreshold_SpinBox.setValue(sortedBy)
                    self.mainWindow_view.binaryThreshold_SpinBox.blockSignals(False)

            self.UpdateFilter_Action(True)

        elif name in ["widthCoefValue_spinBox", "colorPalette_comboBox"] and self.projectOpened:

            if name == "widthCoefValue_spinBox":
                self.filters.coefWidthEdges = self.mainWindow_view.widthCoefValue_spinBox.value()

            if name == "colorPalette_comboBox":
                edgeColorData = self.mainWindow_view.colorPalette_comboBox.currentData()
                self.filters.colorEdges = edgeColorData[0]
                self.mainWindow_view.displayColorPalette_Label.setStyleSheet(edgeColorData[1])

            self.UpdateFilter_Action(False)

    def UpdateFilter_Action(self, filtersToAllOnglet):

        if self.newFilters:
            self.filters.InitReset()
            self.connGraph_widget.connGraphicView.filtersSave.LoadCurrentFilters(self.filters.SaveCurrentFilters())
            self.filters.LoadSaveFilters(self.filtersSave.RecovertFiltersSave())
        
        self.connGraph_widget.connGraphicView.Filter()

        if filtersToAllOnglet:
            self.connGraph.SetEdgesValuesFiltered()
            self.PieAfterFilter()
            self.ListAfterFilter()
            self.GTAfterFilters()
            self.UpdateInfo_Filter()

    def UpdateInfo_Filter(self):
            
        visibleEdgesState = self.connGraph_widget.connGraphicView.GetVisibleEdgesInfos()

        visibleCount = 0
        visibleWeightList = []
        for (_, _), infos in visibleEdgesState.items():
            visible = infos["visible"]
            value = abs(infos["value"])

            if visible:
                visibleCount += 1
                visibleWeightList.append(value)

        if visibleCount != 0:
            visibleWeightSum = round(sum(visibleWeightList), self.filters.valueRound)
            visibleWeightMean = round(mean(visibleWeightList), self.filters.valueRound)
        else:
            visibleWeightSum = "..."
            visibleWeightMean = "..."

        self.mainWindow_view.weightSumValue_label.setText(str(visibleWeightSum))
        self.mainWindow_view.weightMeanValue_label.setText(str(visibleWeightMean))
        self.mainWindow_view.connNumValue_label.setText(str(visibleCount))

    def UpdateConnectionType_Filter(self):

        self.filters.homotopic_connType = self.mainWindow_view.homotopic_checkBox.isChecked()
        self.filters.contralateral_connType = self.mainWindow_view.contralateral_checkBox.isChecked()
        self.filters.ipsilateral_connType = self.mainWindow_view.ipsilateral_checkBox.isChecked()
        self.filters.other_connType = self.mainWindow_view.other_checkBox.isChecked()

    def UpdateInterRegionalConnection_Filter(self):

        for checkBox in self.checkGrid:
            names = checkBox.objectName().split(",")
            nameRow = names[0]
            nameColumn = names[1]
            state = checkBox.isChecked()

            self.filters.SetInterRegConnEnabled(nameRow, nameColumn, state)

        self.UpdateCheckGridState_Action()

        # ----- Reset -----

    def ResetGraphicFilter(self):

        if self.projectOpened:

            self.BlockFilterSignals(True)
            self.mainWindow_view.widthCoefValue_spinBox.setValue(5)
            self.filters.coefWidthEdges = 5

            self.mainWindow_view.colorPalette_comboBox.setCurrentIndex(0)
            self.filters.colorEdges = colorPalettes["Red -> White -> Blue"][0]
            self.mainWindow_view.displayColorPalette_Label.setStyleSheet(colorPalettes["Red -> White -> Blue"][1])
            self.BlockFilterSignals(True)

            self.connGraph_widget.connGraphicView.Filter()
            self.connGraph_widget.connGraphicView.ResetGraphicFilter()

    # ----- CheckBoxes grid -----

    def InterRegConnLabelClick_Action(self, name: str):

        self.BlockFilterSignals(True)
        infos = name.split(",")
        orientation = infos[0]
        name = infos[1]

        label = self.GetCheckGridLabelWithName(name, orientation)

        check = not label.checked

        for checkBox in self.checkGrid:
            names = checkBox.objectName().split(",")
            nameRow = names[0]
            nameColumn = names[1]
            if orientation == "row" and nameRow == name:
                checkBox.setChecked(check)
            if orientation == "column" and nameColumn == name:
                checkBox.setChecked(check)
        
        self.BlockFilterSignals(False)
        self.UpdateFilter_Event("checkGrid_checkBox")

    def UpdateCheckGridState_Action(self):
        
        # Update row labels state
        for label in self.checkGridLabels[0]:
            name = label.name
            for checkBox in self.checkGrid:
                checkBox: QCheckBox
                names = checkBox.objectName().split(",")
                nameRow = names[0]

                if nameRow == name and checkBox.isChecked() is True:
                    label.checked = True
                    break
                elif nameRow == name:
                    label.checked = False

        # Update columns labels state
        for label in self.checkGridLabels[1]:
            name = label.name
            for checkBox in self.checkGrid:
                checkBox: QCheckBox
                names = checkBox.objectName().split(",")
                nameColumn = names[1]
                if nameColumn == name and checkBox.isChecked() is True:
                    label.checked = True
                    break
                elif nameColumn == name:
                    label.checked = False

        states = []
        for checkBox in self.checkGrid:
            states.append(checkBox.isChecked())

        allChecked = all(states)
        allUnchecked = not any(states)

        if allChecked:
            self.checkGridChecked = True
            self.checkAllGrid_button.setText("uncheck all")

        if allUnchecked:
            self.checkGridChecked = False
            self.checkAllGrid_button.setText("check all")

    def GetCheckGridLabelWithName(self, name: str, orientation: str):
        labels = self.checkGridLabels[0] + self.checkGridLabels[1]

        for label in labels:
            label: CheckGridLabel_Widget
            if label.name == name and label.orientation == orientation:
                return label

        return None

    def CreateInterRegGrid(self, names) -> tuple[list[QCheckBox | QCheckBox], list[list[CheckGridLabel_Widget]], QPushButton, list[QSpacerItem]]:
        """
        Create the inter-regional connections grid with checkboxes
        :param names:
        """

        """
        grid shape :
                    □ name 1
                □   □ name 2
            □   □   □ name 3
        □   □   □   □ name 4
        n1  n2  n3  n4 
        """
        checkGrid = []
        labels = []
        rowLabels = []
        nameNum = len(names)

        gridLayout: QGridLayout = self.mainWindow_view.connSelection_groupBox.layout()
        gridLayout.setAlignment(Qt.AlignCenter)

        for posY in range(0, nameNum):
            for posX in range(nameNum - posY - 1, nameNum):
                # Create layout for the checkbox
                layout = QHBoxLayout()
                layout.setAlignment(Qt.AlignCenter)
                layout.setContentsMargins(0, 0, 0, 0)

                # Create checkBox and add it to the list
                checkBox = QCheckBox(self.mainWindow_view.connSelection_groupBox)
                checkGrid.append(checkBox)

                # Set checkBox params
                name = f"{names[posY]},{names[nameNum - posX - 1]},{posY},{posX}"
                checkBox.setObjectName(name)
                checkBox.setProperty("class", "blackCheckBox")
                checkBox.setChecked(True)

                checkBox.stateChanged.connect(lambda: self.UpdateFilter_Event("checkGrid_checkBox"))

                # Add the layout to the grid
                #gridLayout.addWidget(widget, posY, posX + 1)
                gridLayout.addLayout(layout, posY, posX + 1)
                gridLayout.addWidget(checkBox, posY, posX + 1)

            # Create row title label (clickable)
            labelName = f"row,{names[posY]},1"
            labelColor = self.connGraph.colorMajorRegions[names[posY]]
            label = CheckGridLabel_Widget(names[posY], "row", labelColor)
            label.setObjectName(labelName)

            label.clicked.connect(self.InterRegConnLabelClick_Action)

            label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            gridLayout.addWidget(label, posY, nameNum + 1)

            rowLabels.append(label)

        columnLabels = []
        for posX in range(0, nameNum):
            # Create column title label (clickable)

            namePos = nameNum - posX - 1
            labelName = f"column,{names[namePos]},1"
            labelColor = self.connGraph.colorMajorRegions[names[namePos]]
            label = CheckGridLabel_Widget(names[namePos], "column", labelColor, rotation=90)
            label.setObjectName(labelName)

            label.clicked.connect(self.InterRegConnLabelClick_Action)

            label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            gridLayout.addWidget(label, nameNum, posX + 1)

            columnLabels.append(label)

        # Update labels list
        labels.append(rowLabels)
        labels.append(columnLabels)

        # Create check/uncheck all checkboxes button
        checkAllButton = QPushButton("uncheck all", self.mainWindow_view.connSelection_groupBox)
        checkAllButton.setProperty("class", "grayRoundedButton")
        checkAllButton.clicked.connect(self.ToggleAllGrid_Action)

        gridLayout.addWidget(checkAllButton, nameNum, nameNum + 1)
        gridLayout.setAlignment(checkAllButton, Qt.AlignTop)

        spacers = []
        # Add spacer around the grid to center it
        for posX in range(nameNum + 1):
            spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding)
            spacers.append(spacer)
            gridLayout.addItem(spacer, posX, 0)
            gridLayout.addItem(spacer, posX, nameNum + 3)
        for posY in range(nameNum + 1):
            spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding)
            spacers.append(spacer)
            gridLayout.addItem(spacer, 0, posY)
            gridLayout.addItem(spacer, nameNum + 3, posY)

        gridLayout.setAlignment(Qt.AlignCenter)
        return checkGrid, labels, checkAllButton, spacers

    def ToggleAllGrid_Action(self):

        self.BlockFilterSignals(True)

        checked = not self.checkGridChecked
        for checkBox in self.checkGrid:
            checkBox.setChecked(checked)

        self.BlockFilterSignals(False)
        self.UpdateFilter_Event("checkGrid_checkBox")

    def ExportCircularGraphic_Action(self):
        if self.projectOpened and self.connGraph_widget:
            self.connGraph_widget.connGraphicView.ShowExportDialog()

    def SaveData(self):

        # Save Previous Files
        exportPreviousFiles = ExportPrevious_Files()
        exportPreviousFiles.SaveFile(self.project.previousFiles)

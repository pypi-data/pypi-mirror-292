import os
from pathlib import Path

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon, QGuiApplication
from PyQt5.QtWidgets import QDesktopWidget, QMessageBox, QPushButton

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from src.View.ui.ImportWindow_ui import Ui_ImportWindow
from src.Controller.ImportFile_Controller import ImportFile_Controller


class ImportFile_View(QtWidgets.QMainWindow, Ui_ImportWindow):

    def __init__(self, parent=None):
        super(ImportFile_View, self).__init__(parent=parent)

        self.setupUi(self)

        # Load Controler File
        self.importFile_Controller = ImportFile_Controller(self)

        # Action Configuration
        self._InitAction()

        # Hidden Elements
        self._HiddenElements()

        # Images Loading
        self._InitLoadingImages()

        # Graph Preparation
        self._InitGraphPreparation()



    # =====================================================================
    # Method to associate all actions to each winget when the app is opened
    # =====================================================================
    def _InitAction(self):

        # Resize the Window (80%)
        self.ResizeWindow()

        # Display Full Path when the mouse entered the item
        self.previousDataFiles_List.setMouseTracking(True)
        self.previousFlutFiles_List.setMouseTracking(True)
        self.previousFiltersFiles_List.setMouseTracking(True)

        # Asssociate Action to ToolButton
        self.importDataFile_Button.setDefaultAction(self.importFile_Controller.OpenDataFile_Qaction)
        self.importNameFile_Button.setDefaultAction(self.importFile_Controller.OpenNameFile_Qaction)
        self.importFlutFile_Button.setDefaultAction(self.importFile_Controller.OpenFlutFile_Qaction)
        self.importFiltersFile_Button.setDefaultAction(self.importFile_Controller.OpenFiltersFile_Qaction)
        self.validation_Button.setDefaultAction(self.importFile_Controller.Validation_Qaction)

    # ==============================================
    # Method to hide elements when the app is opened
    # ==============================================
    def _HiddenElements(self):

        # Label / Button to import Name File
        self.openedNameFile_Label.hide()
        self.importNameFile_Button.hide()

        self.errorDataNameFile_Label.hide()
        self.errorFlutFile_Label.hide()
        self.errorFiltersFile_Label.hide()

        # Graph Section
        self.graphSection_Widget.hide()

    # =======================================
    # Method to associate image to ToolButton
    # =======================================
    def _InitLoadingImages(self):

        resourcedir = Path(__file__).parent.parent.parent / 'resources'
        imagePath = os.path.join(resourcedir, "images", "folder.png")

        # Load image using the variable path
        pixmap = QPixmap(imagePath)
        pixmap = pixmap.scaled(self.importDataFile_Button.width(), self.importDataFile_Button.height(),
                               Qt.KeepAspectRatioByExpanding)

        # Check if pixmap loaded successfully
        if not pixmap.isNull():

            # Set pixmap as icon for the tool button
            icon_Qicon = QIcon(pixmap)

            self.importDataFile_Button.setIcon(icon_Qicon)
            self.importDataFile_Button.setIconSize(pixmap.size())
            self.importNameFile_Button.setIcon(icon_Qicon)
            self.importNameFile_Button.setIconSize(pixmap.size())
            self.importFlutFile_Button.setIcon(icon_Qicon)
            self.importFlutFile_Button.setIconSize(pixmap.size())
            self.importFiltersFile_Button.setIcon(icon_Qicon)
            self.importFiltersFile_Button.setIconSize(pixmap.size())

        else:
            print("Image Not Correctly Loaded")

    # =======================================================
    # Method to create Figure and Canvas to display Histogram
    # =======================================================
    def _InitGraphPreparation(self):

        # Create a Matplotlib figure and a canvas to display it
        self.graph = Figure()
        self.canvas = FigureCanvas(self.graph)
        self.graphDisplay_Layout.addWidget(self.canvas)

    # ==================================================
    # Method to resize the window when the app is opened
    # ==================================================
    def ResizeWindow(self):

        # Obtain the Screen Size
        screen = QGuiApplication.primaryScreen().geometry()
        screenWidth = screen.width()
        screenHeight = screen.height()

        # Define the Window Size (80%)
        widthPercentage = 0.9
        heightPercentage = 0.9

        # Compute the new Window Size
        newWidth = int(screenWidth * widthPercentage)
        newHeight = int(screenHeight * heightPercentage)

        startX = int((screenWidth * (1 - widthPercentage)) / 2)
        startY = int((screenHeight * (1 - widthPercentage)) / 2)

        # Apply new Value
        #self.resize(newWidth, newHeight)
        self.setGeometry(startX, startY, newWidth, newHeight)

    def LoadIcon(self, iconType):

        resourcedir = Path(__file__).parent.parent.parent / 'resources'
        imagePath = os.path.join(resourcedir, "images", iconType + ".png")

        return QIcon(imagePath)
    
    def WarningPopUpFilters(self, filtersToIgnore):

        msgBox = QMessageBox(self)
        msgBox.setWindowTitle("Coherence Filters")

        if filtersToIgnore.count(True) > 1:
            text = "Data and FLUT files are not coherent. \
                        \nDo you want ignore Incoherences ?"
        else:
            match filtersToIgnore.index(False)[0]:
                case 0:
                    text = "Data and FLUT files are not coherent. \
                        \nDo you want ignore Pre-Filter Threshold Incoherence ?"
                case 1:
                    text = "Data and FLUT files are not coherent. \
                        \nDo you want ignore Relative Threshold Incoherence ?"
                case 2:
                    text = "Data and FLUT files are not coherent. \
                        \nDo you want ignore Relative Threshold Incoherence ?"
                case 3:
                    text = "Data and FLUT files are not coherent. \
                        \nDo you want ignore Absolu Threshold Incoherence ?"
                case 4:
                    text = "Data and FLUT files are not coherent. \
                        \nDo you want ignore Absolu Threshold Incoherence ?"
                case 5:
                    text = "Data and FLUT files are not coherent. \
                        \nDo you want ignore Rank Threshold Incoherence ?"
                case 6:
                    text = "Data and FLUT files are not coherent. \
                        \nDo you want ignore Inter-Region Incoherence(s) ?"
                    
        msgBox.setText(text)
        msgBox.setWindowIcon(self.LoadIcon("warning"))
        
        ignoreButton = QPushButton("Ignore")
        cancelButton = QPushButton("Cancel")

        msgBox.addButton(ignoreButton, QMessageBox.ActionRole)
        msgBox.addButton(cancelButton, QMessageBox.ActionRole)

        ignoreButton.clicked.connect(self.importFile_Controller.IgnoreFiltersIncoherences)
        cancelButton.clicked.connect(self.importFile_Controller.CancelFilters)

        msgBox.exec_()

    def WarningPopUpNumberRegion(self):

        msgBox = QMessageBox(self)
        msgBox.setWindowTitle("Region Number")
        msgBox.setText("The number of regions is higher than the recommended number (150 with blanks). \
                       \nDo you want to DISPLAY all regions, or HIDE regions not present in data file ?")
        msgBox.setWindowIcon(self.LoadIcon("warning"))
        
        displayButton = QPushButton("Display")
        hideButton = QPushButton("Hide")

        msgBox.addButton(displayButton, QMessageBox.ActionRole)
        msgBox.addButton(hideButton, QMessageBox.ActionRole)

        displayButton.clicked.connect(self.importFile_Controller.DisplayAllRegions)
        hideButton.clicked.connect(self.importFile_Controller.HideRegions)

        msgBox.exec_() 
    
    def WarningPopUpDATAFLUT(self):

        msgBox = QMessageBox(self)
        msgBox.setWindowTitle("Coherence Verification")
        msgBox.setText("Data and FLUT files are not coherent. \
                       \nDo you want ignore Incoherence(s) ?")
        msgBox.setWindowIcon(self.LoadIcon("warning"))
        
        ignoreButton = QPushButton("Ignore")
        cancelButton = QPushButton("Cancel")

        msgBox.addButton(ignoreButton, QMessageBox.ActionRole)
        msgBox.addButton(cancelButton, QMessageBox.ActionRole)

        ignoreButton.clicked.connect(self.importFile_Controller.IgnoreValidationIncoherences)
        cancelButton.clicked.connect(self.importFile_Controller.CancelValidation)

        msgBox.exec_()

    # =======================================
    # Method called when the window is closed
    # =======================================
    def closeEvent(self, event):
        
        # when the application is closed, called the control to save some data
        if hasattr(self, 'importFile_Controller'):
            self.importFile_Controller.CloseImportWithoutValidation()

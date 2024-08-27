import os
from pathlib import Path

from src.globals import colorPalettes

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QPushButton, QLabel

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from src.Controller.MainWindow_Controller import MainWindow_Controller
from src.View.ui.MainWindow_ui import Ui_IACOB


class MainWindowView(QMainWindow, Ui_IACOB):

    def __init__(self):
        super().__init__()

        self.setupUi(self)

        self.openRecentProjects_menu = None
        self.openRecentFilters_menu = None

        self.mainWindow_controller = MainWindow_Controller(self)
        self.menuBar.setNativeMenuBar(False)

        self._InitView()
        self._InitActions()
        self._InitLoadingImages()
        self._InitGraphPreparation()
        self._InitColorPaletteChoice()

    def _InitView(self):

        # Hide the dock widget for the "FileInfo" tab only
        if self.mainTabWidget.currentIndex() == 0:
            self.dockWidget.hide()
        else:
            self.dockWidget.show()

        # Tab1 : File Infos
        self.fileInfosSupport_Frame.hide()
        self.noInfoTab1_Label.show()

        # Tab2 : Circular
        self.circularTabSupport_Frame.hide()
        self.noInfoTab2_Label.show()

        # Tab3 : Pie
        self.pieTabWidget.hide()
        self.noInfoTab3_Label.show()

        # Tab4 : List
        self.listSupport_Frame.hide()
        self.noInfoTab4_Label.show()

        # Tab5 : GT
        self.tabGTWidget.hide()
        self.noInfoTab5_Label.show()

    # =======================================================
    # Method to create Figure and Canvas to display Histogram
    # =======================================================
    def _InitGraphPreparation(self):

        # Create a Matplotlib figure and a canvas to display it
        self.graph_curve = Figure()
        self.canvas = FigureCanvas(self.graph_curve)
        self.graphDisplay_Layout.addWidget(self.canvas)

        # Add two custom QLineEdit for discardWeight and discardAbsWeight inputs
    
    def _InitActions(self):

        # ===== Project / Filters Files ======

        # ----- Project Files -----

        # & define a quick key to jump to this menu by pressing alt+F
        self.file_toolBarMenu = self.menuBar.addMenu("&Files")
        self.file_toolBarMenu.addAction(self.mainWindow_controller.createProject_action)
        self.file_toolBarMenu.addAction(self.mainWindow_controller.openProject_action)

        # Open Recent Project
        self.openRecentProjects_menu = self.file_toolBarMenu.addMenu("Open Recent Project")

        self.separatorRecentProject = self.openRecentProjects_menu.addSeparator()
        self.openRecentProjects_menu.addAction(self.mainWindow_controller.clearRecentProjects_action)

        self.file_toolBarMenu.addAction(self.mainWindow_controller.exportProject_action)
        self.file_toolBarMenu.addAction(self.mainWindow_controller.closeProject_action)

        # ----- Filters Files -----
        self.separator = self.file_toolBarMenu.addSeparator()
        self.openFilters = self.file_toolBarMenu.addAction(self.mainWindow_controller.openFilters_action)

        # Open Recent Filters
        self.openRecentFilters = self.openRecentFilters_menu = self.file_toolBarMenu.addMenu("Open Recent Filters")

        self.separatorRecentFilters = self.openRecentFilters_menu.addSeparator()
        self.exportFilters = self.openRecentFilters_menu.addAction(self.mainWindow_controller.clearRecentFilters_action)

        self.file_toolBarMenu.addAction(self.mainWindow_controller.exportFilters_action)

        # ===== Other Buttons ======
        self.help_toolBarAction = self.menuBar.addAction(self.mainWindow_controller.help_action)
        self.about_toolBarAction = self.menuBar.addAction(self.mainWindow_controller.about_action)

        self.resetFilter_button.setDefaultAction(self.mainWindow_controller.resetFilter_action)
        self.resetGraphicFilter_button.setDefaultAction(self.mainWindow_controller.resetGraphicFilter_action)
        self.exportCircular_button.setDefaultAction(self.mainWindow_controller.exportCircularGraphic_action)
        self.exportList_button.setDefaultAction(self.mainWindow_controller.exportList_action)

        self.mainWindow_controller._InitToolBar()

    def _InitLoadingImages(self):

        resourcedir = Path(__file__).parent.parent.parent / 'resources'
        imagePath = os.path.join(resourcedir, "images", "plus.png")

        # Load image using the variable path
        pixmap_plus = QPixmap(imagePath)
        pixmap_plus = pixmap_plus.scaled(self.addGraphic_button.width(), self.addGraphic_button.height(),
                               Qt.KeepAspectRatioByExpanding)

        # Check if pixmap loaded successfully
        if not pixmap_plus.isNull():

            # Set pixmap as icon for the tool button
            icon_Qicon = QIcon(pixmap_plus)

            self.addGraphic_button.setIcon(icon_Qicon)
            self.addGraphic_button.setIconSize(pixmap_plus.size())
            self.addGraphic2_button.setIcon(icon_Qicon)
            self.addGraphic2_button.setIconSize(pixmap_plus.size())
            self.addGraphic3_button.setIcon(icon_Qicon)
            self.addGraphic3_button.setIconSize(pixmap_plus.size())
            self.addGraphic4_button.setIcon(icon_Qicon)
            self.addGraphic4_button.setIconSize(pixmap_plus.size())
            self.addGraphic5_button.setIcon(icon_Qicon)
            self.addGraphic5_button.setIconSize(pixmap_plus.size())
            self.addGraphGT_button.setIcon(icon_Qicon)
            self.addGraphGT_button.setIconSize(pixmap_plus.size())

        else:
            print("Image Not Correctly Loaded")

    def _InitColorPaletteChoice(self):

        for palette_name, colors in colorPalettes.items():
            # Ajouter le texte et associer les couleurs comme data
            self.colorPalette_comboBox.addItem(palette_name, colors)

        self.displayColorPalette_Label.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, \
                                                     stop:0 rgba(255, 0, 0, 255), \
                                                     stop:0.5 rgba(200, 200, 200, 255), \
                                                     stop:1 rgba(0, 0, 255, 255));")

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

        displayButton.clicked.connect(self.mainWindow_controller.DisplayAllRegions)
        hideButton.clicked.connect(self.mainWindow_controller.HideRegions)

        msgBox.exec_() 
    
    def WarningPopUpValidation(self):

        msgBox = QMessageBox(self)
        msgBox.setWindowTitle("Coherence Verification")
        msgBox.setText("Data and FLUT files are not coherent. \
                       \nDo you want ignore Incoherence(s) ?")
        msgBox.setWindowIcon(self.LoadIcon("warning"))

        ignoreButton = QPushButton("Ignore")
        cancelButton = QPushButton("Cancel")

        msgBox.addButton(ignoreButton, QMessageBox.ActionRole)
        msgBox.addButton(cancelButton, QMessageBox.ActionRole)

        ignoreButton.clicked.connect(self.mainWindow_controller.IgnoreValidationIncoherences)
        cancelButton.clicked.connect(self.mainWindow_controller.CancelValidation)

        msgBox.exec_()

    def ErrorLoading(self, text):

        msgBox = QMessageBox(self)
        msgBox.setWindowTitle("Error Display")
        msgBox.setText(text)
        msgBox.setWindowIcon(self.LoadIcon("error"))

        okButton = QPushButton("OK")
        msgBox.addButton(okButton, QMessageBox.ActionRole)
        okButton.clicked.connect(msgBox.accept)

        msgBox.exec_()
    
    # =======================================
    # Method called when the window is closed
    # =======================================
    def closeEvent(self, event):

        # when the application is closed, called the control to save some data
        if hasattr(self, 'mainWindow_controller'):
            self.mainWindow_controller.SaveData()
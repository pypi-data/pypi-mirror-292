import os
import csv
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon

import numpy as np

from PyQt5.QtCore import QSize, QStandardPaths
from PyQt5.QtWidgets import QWidget, QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from src.View.ui.GraphWidget_ui import Ui_GraphWidget
from src.Model.Data_Storage.ConnGraph_Model import ConnGraph_Infos


class GraphicWidget(QWidget):
    connGraph: ConnGraph_Infos

    def __init__(self, mainWindow_Controller, name, graphicType):
        super().__init__()

        # Setup widget UI
        self.graphWidget_ui = Ui_GraphWidget()
        self.graphWidget_ui.setupUi(self)

        self._InitLoadingImages()

        self.connGraph = ConnGraph_Infos()
        self.graphicType = graphicType

        if self.graphicType == "GTGraph":
            self.widthValue = 4.8
            self.dpiValue = 100
        else:
            self.widthValue = 4.8
            self.heightValue = 3
            self.dpiValue = 100

        self.mainWindow_Controller = mainWindow_Controller

        self.name = name
        self.data = None  # Get in 'match graphicType'

        self.plot = None
        self.graphWidget_ui.title_label.setText(name)
        
        # Separate each graphic Type
        match self.graphicType:

            case "Connections":
                
                self.data = self.connGraph.GetAllConnectivityWithName_PieChart(self.name)
                # Colors define in the Flut File

                self._InitConnectionsPie()
                self.graphWidget_ui.toCsv_button.clicked.connect(self.ExportToCsvTupleVersion)

            case "MajorRegions":

                self.data = self.connGraph.GetAllMajorRegionsWithName_PieChart(self.name)
                self.colorMajorRegions = self.connGraph.colorMajorRegions

                self._InitMajorRegionsPie()
                self.graphWidget_ui.toCsv_button.clicked.connect(self.ExportToCsv)

            case "MajorRegionsBar":

                self.data = self.connGraph.GetAllMajorRegionsWithName_PieChart(self.name)
                self.colorMajorRegions = self.connGraph.colorMajorRegions

                self._InitMajorRegionsBar()
                self.graphWidget_ui.toCsv_button.clicked.connect(self.ExportToCsv)

            case "ConnectionType":

                self.data = self.connGraph.GetAllConnectionTypeWithName_PieChart(self.name)
                # Color For Connection Type (Ipsilateral, Contralateral, Homotopic, Other)
                self.ConnectionsTypeColor = ["skyblue", "#556B2F", "darkkhaki", "lightgray"]

                self._InitConnectionTypePie()
                self.graphWidget_ui.toCsv_button.clicked.connect(self.ExportToCsv)

            case "ConnectionTypeBar":
                
                self.data = self.connGraph.GetAllConnectionTypeWithName_PieChart(self.name)
                # Color For Connection Type (Ipsilateral, Contralateral, Homotopic, Other)
                self.ConnectionsTypeColor = ["skyblue", "#556B2F", "darkkhaki", "lightgray"]

                self._InitConnectionTypeBar()
                self.graphWidget_ui.toCsv_button.clicked.connect(self.ExportToCsv)

            case "GTGraph":

                self.data = self.connGraph.GetLocalMeasures(name)
                self._InitGTGraph()

        self.graphWidget_ui.closeButton.clicked.connect(self.CloseWindow)
        self.graphWidget_ui.toImage_button.clicked.connect(self.ExportToImage)
    
    def _InitLoadingImages(self):

        resourcedir = Path(__file__).parent.parent.parent.parent / 'resources'
        imagePath = os.path.join(resourcedir, "images", "close.png")

        # Load image using the variable path
        pixmap_close = QPixmap(imagePath)
        pixmap_close = pixmap_close.scaled(self.graphWidget_ui.closeButton.width(), self.graphWidget_ui.closeButton.height(),
                               Qt.KeepAspectRatioByExpanding)

        # Check if pixmap loaded successfully
        if not pixmap_close.isNull():

            # Set pixmap as icon for the tool button
            icon_Qicon = QIcon(pixmap_close)

            self.graphWidget_ui.closeButton.setIcon(icon_Qicon)
            self.graphWidget_ui.closeButton.setIconSize(pixmap_close.size())

        else:
            print("[ERROR] Image Not Correctly Loaded")

        resourcedir = Path(__file__).parent.parent.parent.parent / 'resources'
        imagePath = os.path.join(resourcedir, "images", "csv.png")

        # Load image using the variable path
        pixmap_csv = QPixmap(imagePath)
        pixmap_csv = pixmap_csv.scaled(self.graphWidget_ui.toCsv_button.width() - 5, self.graphWidget_ui.toCsv_button.height() - 5,
                               Qt.KeepAspectRatioByExpanding)

        # Check if pixmap loaded successfully
        if not pixmap_csv.isNull():

            # Set pixmap as icon for the tool button
            icon_Qicon = QIcon(pixmap_csv)

            self.graphWidget_ui.toCsv_button.setIcon(icon_Qicon)
            self.graphWidget_ui.toCsv_button.setIconSize(pixmap_csv.size())

        else:
            print("[ERROR] Image Not Correctly Loaded")

        resourcedir = Path(__file__).parent.parent.parent.parent / 'resources'
        imagePath = os.path.join(resourcedir, "images", "image.png")

        # Load image using the variable path
        pixmap_image = QPixmap(imagePath)
        pixmap_image = pixmap_image.scaled(self.graphWidget_ui.toImage_button.width() - 5, 
                                           self.graphWidget_ui.toImage_button.height() - 5,
                                           Qt.KeepAspectRatioByExpanding)

        # Check if pixmap loaded successfully
        if not pixmap_image.isNull():

            # Set pixmap as icon for the tool button
            icon_Qicon = QIcon(pixmap_image)

            self.graphWidget_ui.toImage_button.setIcon(icon_Qicon)
            self.graphWidget_ui.toImage_button.setIconSize(pixmap_image.size())

        else:
            print("[ERROR] Image Not Correctly Loaded")

    def _InitConnectionsPie(self):

        self.figure = Figure(figsize=(self.widthValue, self.heightValue), dpi=self.dpiValue)
        self.canvas = FigureCanvas(self.figure)
        
        self.plot = self.figure.add_subplot(111)

        sortedAreas = sorted(list(self.data.items()), key=lambda item: item[1][0], reverse=True)
        sortedAreas_dict = dict(sortedAreas)
        
        sortedAreaValue = []
        sortedAreaRGBA = []
        for areaInfo in sortedAreas_dict.values():
            sortedAreaValue.append(abs(areaInfo[0]))
            sortedAreaRGBA.append((areaInfo[1][0] / 255, areaInfo[1][1] / 255, areaInfo[1][2] / 255, areaInfo[1][3] / 255))

        totalValue_threshold = sum(sortedAreaValue) * 0.05

        def autopct_func(pct):
            # Display percentage > 5%
            return ('%1.0f%%' % pct) if pct > (totalValue_threshold * 100.0 / sum(sortedAreaValue)) else ''
    
        # Display the Pie Graph
        wedges, _, autotexts = self.plot.pie(sortedAreaValue, startangle=90, colors=sortedAreaRGBA,
                                  autopct=autopct_func, pctdistance=0.80)

        for autotext in autotexts:
            autotext.set_fontsize(8)  # Adjust the font size here
        
        # Recovert threshold label (to print in the legend)
        legendLabels = []
        legendColor = []

        indexLabel = 0
        namesListe = list(sortedAreas_dict.keys())
        while indexLabel < 14 and indexLabel < len(namesListe):

            label = namesListe[indexLabel]
            legendLabels.append(label)
            legendColor.append(wedges[indexLabel])

            indexLabel += 1


        self.plot.legend(legendColor, legendLabels, loc="upper center", bbox_to_anchor=(0.5, 0), 
                         ncol=2, fontsize='x-small')

        self.plot.axis('equal')
        self.figure.subplots_adjust(bottom=0.4)

        # Draw the canvas
        self.graphWidget_ui.plot_widget.layout().addWidget(self.canvas)

    def _InitMajorRegionsPie(self):

        self.figure = Figure(figsize=(self.widthValue, self.heightValue), dpi=self.dpiValue)
        self.canvas = FigureCanvas(self.figure)
        
        self.plot = self.figure.add_subplot(111)

        allMajorRegions = {}
        for majorRegion in self.colorMajorRegions.keys():
            
            if majorRegion in self.data:
                allMajorRegions[majorRegion] = self.data[majorRegion]
            else:
                allMajorRegions[majorRegion] = 0.0
        
        totalValue_threshold = sum(allMajorRegions.values()) * 0.05

        def autopct_func(pct):
            return ('%1.0f%%' % pct) if pct > (totalValue_threshold * 100.0 / sum(allMajorRegions.values())) else ''

        # Display the Pie Graph
        wedges, _, autotexts = self.plot.pie(allMajorRegions.values(), startangle=90, 
                                             colors=self.colorMajorRegions.values(), autopct=autopct_func, pctdistance=0.80)

        for autotext in autotexts:
            autotext.set_fontsize(8)  # Adjust the font size here

        self.plot.legend(wedges, allMajorRegions.keys(), 
                         loc="upper center", bbox_to_anchor=(0.5, 0), ncol=2, fontsize='x-small')

        self.plot.axis('equal')
        self.figure.subplots_adjust(bottom=0.4)

        # Draw the canvas
        self.graphWidget_ui.plot_widget.layout().addWidget(self.canvas)

    def _InitMajorRegionsBar(self):
        
        self.figure = Figure(figsize=(self.widthValue, self.heightValue), dpi=self.dpiValue)
        self.canvas = FigureCanvas(self.figure)
        
        self.plot = self.figure.add_subplot(111)

        allMajorRegions = {}
        for majorRegion in self.colorMajorRegions.keys():
            
            if majorRegion in self.data:
                allMajorRegions[majorRegion] = self.data[majorRegion]
            else:
                allMajorRegions[majorRegion] = 0.0

        # Calculate the bar width dynamically based on the number of bars
        num_bars = len(allMajorRegions)
        bar_positions = np.arange(num_bars)

        total = sum(allMajorRegions.values())
        MajorRegion_PercentageValue = [(value / total) * 100 for value in allMajorRegions.values()]

        # Display the Bar Graph
        bars = self.plot.bar(bar_positions, MajorRegion_PercentageValue, 
                             color=self.colorMajorRegions.values(), width=0.8)

        self.plot.legend(bars, allMajorRegions.keys(), 
                     loc="upper center", bbox_to_anchor=(0.5, 0), ncol=2, fontsize='x-small')
        
        self.plot.set_xticks([])
        self.plot.set_ylabel('Major Region Values (%)')
        self.plot.set_title('Major Regions')

        self.figure.subplots_adjust(bottom=0.4)

        # Draw the canvas
        self.graphWidget_ui.plot_widget.layout().addWidget(self.canvas)

    def _InitConnectionTypePie(self):

        self.figure = Figure(figsize=(self.widthValue, self.heightValue), dpi=self.dpiValue)
        self.canvas = FigureCanvas(self.figure)
        
        self.plot = self.figure.add_subplot(111)

        ConnectionsType_dict = self.data
        
        totalValue_threshold = sum(ConnectionsType_dict.values()) * 0.05

        def autopct_func(pct):
            return ('%1.0f%%' % pct) if pct > (totalValue_threshold * 100.0 / sum(ConnectionsType_dict.values())) else ''

        # Display the Pie Graph
        wedges, _, _ = self.plot.pie(ConnectionsType_dict.values(), startangle=90, colors=self.ConnectionsTypeColor,
                                  autopct=autopct_func, pctdistance=0.80)

        self.plot.legend(wedges, ConnectionsType_dict.keys(), 
                         loc="upper center", bbox_to_anchor=(0.5, 0), ncol=2, fontsize='small')

        self.plot.axis('equal')
        self.figure.subplots_adjust(bottom=0.3)

        # Draw the canvas
        self.graphWidget_ui.plot_widget.layout().addWidget(self.canvas)

    def _InitConnectionTypeBar(self):

        self.figure = Figure(figsize=(self.widthValue, self.heightValue), dpi=self.dpiValue)
        self.canvas = FigureCanvas(self.figure)
        
        self.plot = self.figure.add_subplot(111)

        ConnectionsType_dict = self.data
        total = sum(ConnectionsType_dict.values())
        ConnectionsType_PercentageValue = [(value / total) * 100 for value in ConnectionsType_dict.values()]

        # Display the Bar Graph
        self.plot.bar(ConnectionsType_dict.keys(), ConnectionsType_PercentageValue, 
                      color=self.ConnectionsTypeColor)

        self.plot.set_ylabel('Connections Values (%)')
        self.plot.set_title('Connections Type')

        # Draw the canvas
        self.graphWidget_ui.plot_widget.layout().addWidget(self.canvas)

    def _InitGTGraph(self):

        # Number of labels (names)
        num_labels = len(self.data)
        
        # Calculate the figure height based on the number of labels
        height_per_label = 0.15
        figure_height = max(self.widthValue, num_labels * height_per_label)
        
        # Create the figure with the new calculated height
        self.figure = Figure(figsize=(self.widthValue, figure_height), dpi=self.dpiValue)
        self.canvas = FigureCanvas(self.figure)
        
        self.plot = self.figure.add_subplot(111)

        self.plot.set_xlabel('Values')
        self.plot.set_title('GT Local Measures')

        labels = list(self.data.keys())
        colorLabels = []
        for label in labels:
            rgba = self.connGraph.areaInfos[label]['RGBA']
            normalized_rgba = tuple([x / 255.0 for x in rgba])
            colorLabels.append(normalized_rgba)

        values = list(self.data.values())

        # Create the horizontal bar chart
        bar_container = self.plot.barh(labels, values, color=colorLabels)

        for bar in bar_container:
            bar.set_height(bar.get_height() * 0.8)

        self.plot.set_yticks(range(len(labels)))    
        self.plot.set_yticklabels(labels, rotation=30, fontsize=6)

        # Adjust the margins based on the number of labels
        self.figure.subplots_adjust(left=0.3, right=0.95, top=0.9, bottom=0.1)

        # Draw the canvas
        self.graphWidget_ui.plot_widget.layout().addWidget(self.canvas)


    def ExportToCsvTupleVersion(self):
        
        userDirectory = QStandardPaths.writableLocation(QStandardPaths.HomeLocation)
        defaultPath = os.path.join(userDirectory, self.name)

        filePath, _ = QFileDialog.getSaveFileName(self, "Save Pie Graph (CSV)", defaultPath, "CSV Files (*.csv)")

        if filePath:

            if not filePath.endswith(".csv"):
                filePath += ".csv"

            with open(filePath, 'w', newline='') as file:
                writer = csv.writer(file)
                field = ["Source", "Destination", "Value", "Percentage"]

                writer.writerow(field)
                totalValue = sum(value[0] for value in self.data.values())

                for destination, value in self.data.items():
                    elements = [self.name, destination, value[0], value[0] / totalValue * 100]
                    writer.writerow(elements)

        self.mainWindow_Controller.CreateFileInfo(filePath, "CSV")

    def ExportToCsv(self):
        
        userDirectory = QStandardPaths.writableLocation(QStandardPaths.HomeLocation)
        defaultPath = os.path.join(userDirectory, self.name)

        filePath, _ = QFileDialog.getSaveFileName(self, "Save Pie Graph (CSV)", defaultPath, "CSV Files (*.csv)")

        if filePath:
            
            if not filePath.endswith(".csv"):
                filePath += ".csv"

            with open(filePath, 'w', newline='') as file:
                writer = csv.writer(file)
                field = ["Source", "Destination", "Value", "Percentage"]

                writer.writerow(field)
                totalValue = sum(self.data.values())

                for destination, value in self.data.items():
                    elements = [self.name, destination, value, value / totalValue * 100]
                    writer.writerow(elements)

        self.mainWindow_Controller.CreateFileInfo(filePath, "CSV")
        
    def ExportToImage(self):
        
        userDirectory = QStandardPaths.writableLocation(QStandardPaths.HomeLocation)
        defaultPath = os.path.join(userDirectory, self.name)

        filePath, _ = QFileDialog.getSaveFileName(self, "Save Graph (Image)", defaultPath, "(*.png)")
        
        if filePath:

            if not filePath.endswith(".png"):
                filePath += ".png"

            high_dpi = 300
            self.plot.figure.savefig(filePath, bbox_inches='tight', dpi=high_dpi)

        self.mainWindow_Controller.CreateFileInfo(filePath, "IMAGE")

    def CloseWindow(self):

        # Call a controller function to remove all widget with the name
        if self.graphicType == "GTGraph":
            self.mainWindow_Controller.DeleteGraphic_GTTab(self.name)
        else:
            self.mainWindow_Controller.DeleteGraphics_PieTab(self.name)


import math
import math
import random
import sys
from copy import deepcopy
from math import comb
from typing import Union

import numpy as np
import pyqtgraph as pg
from PyQt5.QtCore import QPointF, Qt, QSize
from PyQt5.QtGui import QFont, QColor, QPainter, QTransform, QImage, QPainterPath, QFontMetrics
from PyQt5.QtWidgets import QGraphicsBlurEffect, QWidget, QVBoxLayout
from matplotlib.path import Path

from src.Model.Data_Storage.ConnGraph_Model import ConnGraph_Infos
from src.Model.Data_Storage.Filters_Model import Filters_Infos


class RegionLabelItem_GTGraphic(pg.ImageItem):

    def __init__(self, text: str, coordinates, color: QColor = QColor(0, 0, 0), **kargs):
        # Init label attributes
        self.text = text
        self.coordinates = coordinates
        self.color = color
        self.shaded = False
        self.distance = 1  # TODO : à voir quel réglage est préférable

        size_min, size_max = 8, 12
        self.size = self.ComputeTextSize(size_min, size_max)
        self.rotation, self.anchor = self.ComputeTextRotation()

        np_image = self._InitText()
        super().__init__(np_image, **kargs)

        self._InitImage()

    def _InitText(self):
        # Initialisation de la police pour calculer la taille de la zone de texte
        font = QFont("Arial", self.size, weight=QFont.Bold)
        self.text_width = QFontMetrics(font).width(self.text, len(self.text))
        self.text_height = QFontMetrics(font).height() + 6

        # width, height = self.size * len(self.text), self.size + 6
        image = QImage(self.text_width, self.text_height, QImage.Format_ARGB32)
        image.fill(Qt.transparent)

        # On utilise QPainter et QPainterPath pour afficher le texte
        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        painter.setFont(font)

        path = QPainterPath()
        path.addText(0, self.size + 3, font, self.text)

        painter.fillPath(path, self.color)
        painter.end()

        # On convertit ensuite ce texte en matrice pour initialiser l'ImageItem
        np_image = self.ImageToNpArray(image)

        return np_image

    def _InitImage(self):
        self.setPos(self.ComputeTextCoordinates(self.distance))

        self.setTransform(self.ComputeTextTransform())

        blurEffect = QGraphicsBlurEffect(blurRadius=1.01)
        self.setGraphicsEffect(blurEffect)

    def ImageToNpArray(self, image: QImage):
        width, height = image.width(), image.height()

        buffer = image.bits().asstring(width * height * 4)
        np_array = np.frombuffer(buffer, dtype=np.uint8).reshape((height, width, 4))

        return np_array

    def ComputeTextSize(self, size_min: int, size_max: int):

        # Compute text size based on the width of text area
        size = int(math.dist(self.coordinates[2], self.coordinates[3]))
        # To guarantee that text size is beetween given min and max size
        size = min(size_max, size)
        size = max(size_min, size)

        return size

    def ComputeTextRotation(self):
        if self.coordinates[2, 1] - self.coordinates[3, 1] < 0:
            x = -np.mean(self.coordinates[:, 0])
            y = -np.mean(self.coordinates[:, 1])
            anchor = (1, 0.5)
        else:
            x = np.mean(self.coordinates[:, 0])
            y = np.mean(self.coordinates[:, 1])
            anchor = (0, 0.5)

        angle = -np.arctan2(x, y)

        return np.degrees(angle), anchor

    def ComputeTextCoordinates(self, distance):
        p1, p2 = self.coordinates[2], self.coordinates[3]

        # Calculate the normal vector to the longer side
        dx, dy = p2 - p1
        normal_vector = np.array([-dy, dx])
        normal_vector = normal_vector / np.linalg.norm(normal_vector) * distance

        # Determine the direction to place the point outside the region
        midpoint = (p1 + p2) / 2
        point = midpoint + normal_vector

        text_coordinates = QPointF(point[0], point[1])

        # Now the position is defined, we translate the text depending on the anchor settings

        x = text_coordinates.x()
        text_coordinates.setX(x)
        return text_coordinates

    def ComputeTextTransform(self):
        tr = QTransform()
        tr.scale(0.3, 0.3)
        tr.rotate(self.rotation)

        xt = -self.anchor[1] * self.text_height
        # We use text_len to put the anchor at the end of the text if it is reversed
        yt = -self.anchor[0] * self.text_width + self.distance
        tr.translate(xt, yt)

        return tr

    """
    Si les connexions ne sont pas affichées : gris
    Si les connexions sont partiellement affichées : gris
    Si les connexions sont toutes affichées : noir
    """

    def SetTextShaded(self, shaded: bool):
        self.shaded = shaded
        if shaded:
            self.setOpacity(0.7)
        else:
            self.setOpacity(1)

    def IsPointInTextPolygon(self, x, y):
        polygon = np.array([
            self.coordinates[0],
            self.coordinates[1],
            self.coordinates[2],
            self.coordinates[3]
        ])
        path = Path(polygon)

        return path.contains_point((x, y))


class RegionItem_GTGraphic:
    outside: pg.PlotDataItem  # Outer line of the region
    inside: pg.FillBetweenItem  # Colored part of the region

    interRegionOutside: pg.PlotDataItem  # Outer line of the region
    interRegionInside: pg.FillBetweenItem  # InterRegional colored part (between the region and text area)

    gtValueOutside : pg.PlotDataItem  # Outer line of the value polygon
    gtValueInside : pg.FillBetweenItem  # Value polygon colored part

    text: RegionLabelItem_GTGraphic  # Text label

    def __init__(self, code: int, name: str, value : float, maxValue : float,
                 coordinates,  # coordinates of each item : region, interRegion, label, gtValue
                 circlePoints,  # 4 list of corresponding circle coords for each item
                 precision=20,
                 regionColor=QColor(255, 255, 255, 255),  # inside color of a region, white by default
                 outlineColor=QColor(0, 0, 0, 255),  # outline color of a region, black by default
                 interRegionColor=QColor(255, 255, 255, 255),  # color of an inter-region associated to a region
                 *args):
        """
        :param coordinates: 4 coordinates points which define the polygon to draw
        """
        self.code = code  # Code of the region
        self.name = name  # Name of the region
        self.value = value
        self.maxValue = maxValue

        self.coordinates = coordinates  # Coordinates of region, interRegion and label
        self.regionColor = regionColor  # Region color
        self.outlineColor = outlineColor  # Region color (outline)
        self.interRegionColor = interRegionColor  # Inter region color
        self.precision = precision  # Precision value. WARING : Greatly affect performances
        self.allCircles = circlePoints  # Circles points for drawing region, interRegion and label

        self._ComputePolygons()
        self._DrawRegion()
        self._DrawInterRegion()
        self._DrawLabel()
        self._DrawGtValue()

        super().__init__(*args)

    def _ComputePolygons(self):
        # Compute polygon lines
        # regions
        self.innerCoords = self.LineToCircleArc(self.allCircles[0][0], self.coordinates[0][0])
        self.outerCoords = self.LineToCircleArc(self.allCircles[0][1], self.coordinates[0][3])

        # inter regions
        self.innerInterRegCoords = self.LineToCircleArc(self.allCircles[1][0], self.coordinates[1][0])
        self.outerInterRegCoords = self.LineToCircleArc(self.allCircles[1][1], self.coordinates[1][3])

        # value
        coeff = 1 - (self.value / self.maxValue)
        self.outerGtValueCoords = self.LineToCircleArc(self.allCircles[3][1], self.coordinates[3][1])
        self.innerGtValueCoords = self.outerGtValueCoords * coeff

        # For gtValues polygons which begins at the center of the graph
        """circleCoords = self.allCircles[3][1] * (1 - coeff)
        self.innerGtValueCoords = np.array([[0, 0], [0, 0]])
        self.outerGtValueCoords = self.LineToCircleArc(circleCoords, self.coordinates[3][1])"""

    def _DrawRegion(self):
        x_coords = np.append(np.append(self.innerCoords[:, 0],
                                       self.outerCoords[::-1, 0]),
                             self.innerCoords[0, 0])

        y_coords = np.append(np.append(self.innerCoords[:, 1],
                                       self.outerCoords[::-1, 1]),
                             self.innerCoords[0, 1])

        # Draw the outline of the polygon
        # TODO : width
        self.outside = pg.PlotDataItem(x_coords, y_coords, pen=pg.mkPen(color=self.outlineColor, width=1))

        # Color the inside of the polygon
        innerLine = pg.PlotDataItem(self.innerCoords[:, 0], self.innerCoords[:, 1])
        outerLine = pg.PlotDataItem(self.outerCoords[:, 0], self.outerCoords[:, 1])

        self.inside = pg.FillBetweenItem(innerLine, outerLine, brush=pg.mkBrush(self.regionColor))

    def _DrawInterRegion(self):

        x_coords = np.append(np.append(self.innerInterRegCoords[:, 0],
                                       self.outerInterRegCoords[::-1, 0]),
                             self.innerInterRegCoords[0, 0])

        y_coords = np.append(np.append(self.innerInterRegCoords[:, 1],
                                       self.outerInterRegCoords[::-1, 1]),
                             self.innerInterRegCoords[0, 1])


        # Draw the outline of the polygon
        self.interRegionOutside = pg.PlotDataItem(x_coords, y_coords, pen=pg.mkPen(color=self.interRegionColor, width=1))


        # Color the inside of the polygon
        innerLine = pg.PlotDataItem(self.innerInterRegCoords[:, 0], self.innerInterRegCoords[:, 1])
        outerLine = pg.PlotDataItem(self.outerInterRegCoords[:, 0], self.outerInterRegCoords[:, 1])

        self.interRegionInside = pg.FillBetweenItem(innerLine, outerLine, brush=pg.mkBrush(self.interRegionColor))

    def _DrawGtValue(self):
        x_coords = np.append(np.append(self.innerGtValueCoords[:, 0],
                                       self.outerGtValueCoords[::-1, 0]),
                             self.innerGtValueCoords[0, 0])

        y_coords = np.append(np.append(self.innerGtValueCoords[:, 1],
                                       self.outerGtValueCoords[::-1, 1]),
                             self.innerGtValueCoords[0, 1])

        # Draw the outline of the polygon
        #self.gtOutlineColor = QColor(150, 150, 150)
        self.gtValueOutside = pg.PlotDataItem(x_coords, y_coords, pen=pg.mkPen(color=self.outlineColor, width=1))


        # Color the inside of the polygon
        innerLine = pg.PlotDataItem(self.innerGtValueCoords[:, 0], self.innerGtValueCoords[:, 1])
        outerLine = pg.PlotDataItem(self.outerGtValueCoords[:, 0], self.outerGtValueCoords[:, 1])

        """color = self.regionColor
        color.setAlpha(int(color.alpha() * 0.6))"""

        self.gtValueInside = pg.FillBetweenItem(innerLine, outerLine, brush=pg.mkBrush(self.regionColor))

    def _DrawLabel(self):
        # Draw text next to the polygon
        self.text = RegionLabelItem_GTGraphic(self.name, self.coordinates[2])

    # Function used for rouding region borders
    def LineToCircleArc(self, circlePoints, start):
        # Find the two points on the circle closest to the start and end points
        startDistances = np.linalg.norm(circlePoints - start, axis=1)

        startIndex = np.argmin(startDistances)
        endIndex = startIndex + self.precision

        return circlePoints[startIndex:endIndex + 1]

    #TODO : exemple de commentaire pour la doc ici !!
    def IsPointInRegionPolygon(self, x, y):
        """
        Compute if the given point is inside the polygon region

        Parameters
        ----------
        x : int
            x coordinate of the point
        y : int
            y coordinate of the point

        Returns
        -------
        bool
            True if inside else False
        """
        # Create matplotlib Path object
        polygonPoints = np.vstack((self.innerCoords, self.outerCoords[::-1]))
        polygonPath = Path(polygonPoints)

        # Check if the point is inside the polygon
        return polygonPath.contains_point((x, y))


class ConnGraphicView(pg.ViewBox):
    graph_info: ConnGraph_Infos
    filters: Filters_Infos
    regions: list[Union[RegionItem_GTGraphic, None]]  # Can contain both None or RegionItem_GTGraphic
    colors: list[QColor]
    graphicFilter: bool  # True if a region is highlighted or hidden by a click on the chart
    highlightedRegions: bool

    graph_info: ConnGraph_Infos

    # TODO : Modifier les paramètres d'initialisation pour passer le graphe complet
    def __init__(self, colorSet: list[QColor], parent=None):

        super().__init__(parent)

        self.graph_info = ConnGraph_Infos()
        filters = Filters_Infos()

        numPoints = len(self.graph_info.areasOrder) + 2  # For blank at begin and end

        # Init regions list
        self.regions = [None for i in range(numPoints)]
        self.highlightedRegions = False

        # Init class attributes
        self.filters = deepcopy(filters)  # Save the current state of the filter
        self.graphicFilter = False
        self.numPoints = numPoints
        self.maxAbsConnValue = self.graph_info.absMinMax[1]
        self.colorSet = colorSet

        self._InitViewSettings()
        self._InitGraphSettings()
        self._GenerateGraphValues()
        self._InitGraph_Regions()

    def _InitViewSettings(self):

        self.disableAutoRange()
        self.setMouseEnabled(False, False)  # Disable mouse interactions
        self.setBackgroundColor("w")

        XRange = 100
        YRange = 100
        self.setRange(xRange=(-XRange, XRange), yRange=(-YRange, YRange))

    def _InitGraphSettings(self):

        self.radius = 50  # Radius in pyqtgraph unit of the text on the plot

        self.regionThickness = 300 / self.numPoints  # The more regions on the graph, the less the thickness of the donut will be

        self.interRegionThickness = self.regionThickness / 2
        self.interRegionDistance = self.regionThickness + 1  # Distance between region polygon and interRegion polygon

        self.textDistance = self.interRegionDistance + self.interRegionThickness + 0  # Distance between interRegion polygon and regionLabel item
        self.textLength = 20  # Lenght in pyqtgraph unit of the text on the plot

        self.gtValueDistance = 1  # Distance beetween region polygon and gtValue polygon

        # IMPORTANT : GREATLY AFFECT PERFORMANCES, but improves region smoothing
        self.precision = 20

        # Changing the font can make the text too long and go outside the plotting area
        self.font = QFont("Arial", pointSize=25, weight=QFont.ExtraBold)

    def _GenerateGraphValues(self):
        angles = np.linspace(0.5 * np.pi, 2.5 * np.pi, self.numPoints, endpoint=False)

        # coordinates of each region
        self.innerPoints = (np.vstack((np.cos(angles), np.sin(angles))).T
                            * self.radius)
        self.innerPoints = np.concatenate((self.innerPoints, [self.innerPoints[0]]))

        self.outerPoints = (np.vstack((np.cos(angles), np.sin(angles))).T
                            * (self.radius + self.regionThickness))
        self.outerPoints = np.concatenate((self.outerPoints, [self.outerPoints[0]]))

        # coordinates of each interRegion polygon
        self.interRegionInnerPoints = (np.vstack((np.cos(angles), np.sin(angles))).T
                                       * (self.radius + self.interRegionDistance))
        self.interRegionInnerPoints = np.concatenate((self.interRegionInnerPoints, [self.interRegionInnerPoints[0]]))

        self.interRegionOuterPoints = (np.vstack((np.cos(angles), np.sin(angles))).T
                                       * (self.radius + self.interRegionDistance + self.interRegionThickness))
        self.interRegionOuterPoints = np.concatenate((self.interRegionOuterPoints, [self.interRegionOuterPoints[0]]))

        # coordinates of each label
        self.innerTextPoints = (np.vstack((np.cos(angles), np.sin(angles))).T
                                * (self.radius + self.textDistance))
        self.innerTextPoints = np.concatenate((self.innerTextPoints, [self.innerTextPoints[0]]))

        self.outerTextPoints = (np.vstack((np.cos(angles), np.sin(angles))).T
                                * (self.radius + self.textDistance + self.textLength))
        self.outerTextPoints = np.concatenate((self.outerTextPoints, [self.outerTextPoints[0]]))

        # coordinates of each value triangle
        self.gtValueOuterPoints = (np.vstack((np.cos(angles), np.sin(angles))).T
                                       * (self.radius - self.gtValueDistance))
        self.gtValueOuterPoints = np.concatenate((self.gtValueOuterPoints, [self.gtValueOuterPoints[0]]))


        # create two circle for the inner and outer line of the donut
        circleAngle = np.linspace(0.5 * np.pi, 2.5 * np.pi, self.numPoints * self.precision, endpoint=False)
        circleAngle = np.append(circleAngle, circleAngle[0])

        circlesPoints = np.vstack((np.cos(circleAngle), np.sin(circleAngle))).T

        # Region polygon circles
        innerRegionCirclePoints = circlesPoints * self.radius
        outerRegionCirclePoints = circlesPoints * (self.radius + self.regionThickness)

        # InterRegion polygon circles
        innerInterRegionCirclePoints = circlesPoints * (self.radius + self.interRegionDistance)
        outerInterRegionCirclePoints = circlesPoints * (self.radius + self.interRegionDistance + self.interRegionThickness)

        # Text circles
        innerCircleTextPoints = circlesPoints * (self.radius + self.textDistance)
        outerCircleTextPoints = circlesPoints * (self.radius + self.textDistance + self.textLength)

        innerGtValuePoint = (0, 0)
        outerGtValueCirclePoints = circlesPoints * (self.radius - self.gtValueDistance)

        self.allCircles = ((innerRegionCirclePoints, outerRegionCirclePoints),
                           (innerInterRegionCirclePoints, outerInterRegionCirclePoints),
                           (innerCircleTextPoints, outerCircleTextPoints),
                           (innerGtValuePoint, outerGtValueCirclePoints))

    def _InitGraph_Regions(self):

        pos = 1
        for region in self.graph_info.areasOrder:
            pos += 1

            # TODO : maybe use region code == 0 instead
            region_name = region[0]
            if region_name == "xxxx":
                continue

            region_info = self.graph_info.areaInfos[region_name]

            # TODO : get inter region color here
            interRegionColor = self.graph_info.colorMajorRegions[region_info["MajorRegion"]]
            interRegionColor = [int(color * 255) for color in interRegionColor]

            self.CreateRegionOnGraph(self.graph_info.GetRegionIDWithName(region_name),
                                     region_name, region_info["RGBA"], interRegionColor, pos)

    # Get a region of the graph with its code
    def GetRegion(self, code):
        for region in self.regions:
            if region is not None:
                if region.code == code:
                    return region
        return None


    # ---------- Accessors ----------

    # create a new RegionItem at a given position in RegionList (beetween 1 and numPoints)
    def CreateRegionOnGraph(self, code, name, regionColor, interRegionColor, pos):
        pos -= 1

        # Get coordinates on the inner/outer circle of the graph
        regionCoordinates = np.array([
            [self.outerPoints[pos][0], self.outerPoints[pos][1]],
            [self.outerPoints[pos + 1][0], self.outerPoints[pos + 1][1]],
            [self.innerPoints[pos + 1][0], self.innerPoints[pos + 1][1]],
            [self.innerPoints[pos][0], self.innerPoints[pos][1]]
        ])

        interRegionCoordinates = np.array([
            [self.interRegionOuterPoints[pos][0], self.interRegionOuterPoints[pos][1]],
            [self.interRegionOuterPoints[pos + 1][0], self.interRegionOuterPoints[pos + 1][1]],
            [self.interRegionInnerPoints[pos + 1][0], self.interRegionInnerPoints[pos + 1][1]],
            [self.interRegionInnerPoints[pos][0], self.interRegionInnerPoints[pos][1]]
        ])

        textCoordinates = np.array([
            [self.outerTextPoints[pos][0], self.outerTextPoints[pos][1]],
            [self.outerTextPoints[pos + 1][0], self.outerTextPoints[pos + 1][1]],
            [self.innerTextPoints[pos + 1][0], self.innerTextPoints[pos + 1][1]],
            [self.innerTextPoints[pos][0], self.innerTextPoints[pos][1]]
        ])

        gtValueCoordinates = np.array([
            [self.gtValueOuterPoints[pos + 1][0], self.gtValueOuterPoints[pos + 1][1]],
            [self.gtValueOuterPoints[pos][0], self.gtValueOuterPoints[pos][1]]
        ])

        allCoordinates = (regionCoordinates, interRegionCoordinates, textCoordinates, gtValueCoordinates)

        # Create region
        # TODO : add transparency if needed

        # Convert RGB color values to QColor object
        regionColor = QColor(regionColor[0], regionColor[1], regionColor[2])
        interRegionColor = QColor(interRegionColor[0], interRegionColor[1], interRegionColor[2])

        #outlineColor = QColor(color[2], color[1], color[0])

        # TODO : delete this
        value = random.randint(0, 68000)
        maxValue = 68000

        self.regions[pos] = RegionItem_GTGraphic(code, name,
                                                 value, maxValue,
                                                 allCoordinates,
                                                 self.allCircles,
                                                 precision=self.precision,
                                                 regionColor=regionColor,
                                                 interRegionColor=interRegionColor)
        self.AddRegion(self.regions[pos], pos)

    def AddRegion(self, region: RegionItem_GTGraphic, pos=None):

        # TODO : à revoir une fois le graphe implémenté
        if pos is None:
            self.regions.append(region)
        else:
            self.regions[pos] = region

        # Add region polygon the gtGraphicView
        self.addItem(region.inside)
        self.addItem(region.outside)

        # Add interRegion polygon to the gtGraphicView
        self.addItem(region.interRegionInside)
        self.addItem(region.interRegionOutside)

        # Add label to the gtGraphicView
        self.addItem(region.text)

        # Add value polygon to the gtGraphicView
        self.addItem(region.gtValueInside)
        self.addItem(region.gtValueOutside)

    # ---------- Click methods ----------

    def mouseClickEvent(self, ev):
        #super().mouseClickEvent(ev) open context menu with right click, so we need to override it
        # Keep the menu enabled, but with a different button
        if ev.button() == Qt.MouseButton.MiddleButton and self.menuEnabled():
            ev.accept()  # Indicate that the event will be handled so the parent won't receive it
            self.raiseContextMenu(ev)
        else:
            # Convert pixel position into scene position
            p = self.mapSceneToView(ev.scenePos())  # QPointF

            # Search for a region under clicked point
            for region in self.regions:
                if region is not None and (region.IsPointInRegionPolygon(p.x(), p.y()) or
                                           region.text.IsPointInTextPolygon(p.x(), p.y())):
                    ev.accept()
                    self.RegionClickEvent(ev, region)
                    break

    def RegionClickEvent(self, ev, region):
        if ev.button() == Qt.MouseButton.LeftButton:
            self.graphicFilter = True
            print("Region click event 1")
        elif ev.button() == Qt.MouseButton.RightButton:
            self.graphicFilter = True
            print("Region click event 2")


class GTGraphic_Widget(QWidget):
    connGraphicView: ConnGraphicView
    graph_info: ConnGraph_Infos

    def __init__(self, parent=None):
        super().__init__(parent)

        self.graph_info = ConnGraph_Infos()

        self.setContentsMargins(0, 0, 0, 0)

        self.setStyleSheet("border: 1px solid black")

        # red, white, blue
        colorSet = [QColor(255, 0, 0), QColor(200, 200, 200), QColor(0, 0, 255)]

        self.connGraphicView = ConnGraphicView(colorSet)

        self.graphic = pg.GraphicsView()
        self.graphic.setCentralItem(self.connGraphicView)

        QVBoxLayout(self)
        self.layout().addWidget(self.graphic)

    # To force the widget to stay square
    def resizeEvent(self, event):
        size = min(event.size().width(), event.size().height())

        self.resize(QSize(size, size))


# Print iterations progress
# (from https://stackoverflow.com/questions/3173320/text-progress-bar-in-terminal-with-block-characters)
def PrintProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    sys.stdout.write(f'\r{prefix} |{bar}| {percent}% {suffix}')
    # Print New Line on Complete
    if iteration == total:
        print()


#TODO : remove it later
def printCoordinates(coordinates):
    i = 0
    for point in coordinates:
        print(f"Point {i} : ({point[0]}, {point[1]})")
        i += 1

import math
import math
import sys
from copy import deepcopy
from math import comb
from typing import Union

import numpy as np
import pyqtgraph as pg
import pyqtgraph.exporters as exporters
from PyQt5.QtCore import QPointF, Qt, QSize
from PyQt5.QtGui import QFont, QColor, QPainter, QTransform, QImage, QPainterPath, QFontMetrics
from PyQt5.QtWidgets import QGraphicsBlurEffect, QWidget, QVBoxLayout
from matplotlib.path import Path

from src.Model.Data_Storage.ConnGraph_Model import ConnGraph_Infos
from src.Model.Data_Storage.Filters_Model import Filters_Infos
from src.Model.Data_Storage.FiltersSave_Model import FiltersSave_Infos


class RegionLabelItem_ConnGraphic(pg.ImageItem):

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


class RegionItem_ConnGraphic:
    outside: pg.PlotDataItem  # Outer line of the region
    inside: pg.FillBetweenItem  # Colored part of the region

    interRegionOutside: pg.PlotDataItem  # Outer line of the region
    interRegionInside: pg.FillBetweenItem  # InterRegional colored part (between the region and text area)

    text: RegionLabelItem_ConnGraphic  # Text label
    edgesVisible: bool = True

    def __init__(self, code: int, name: str,
                 coordinates,  # coordinates of each item : region, interRegion, label
                 circlePoints,  # 3 list of corresponding circle coords for each item
                 precision=1,
                 regionColor=QColor(255, 255, 255, 255),  # inside color of a region, white by default
                 outlineColor=QColor(0, 0, 0, 255),  # outline color of a region, black by default
                 interRegionColor=QColor(255, 255, 255, 255),  # color of an inter-region associated to a region
                 *args):
        """
        :param coordinates: 4 coordinates points which define the polygon to draw
        """
        self.code = code  # Code of the region
        self.name = name  # Name of the region
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

        super().__init__(*args)

    def _ComputePolygons(self):
        # Compute polygon lines
        # regions
        self.innerCoords = self.LineToCircleArc(self.allCircles[0][0], self.coordinates[0][0])
        self.outerCoords = self.LineToCircleArc(self.allCircles[0][1], self.coordinates[0][3])

        # inter regions
        self.innerInterRegCoords = self.LineToCircleArc(self.allCircles[1][0], self.coordinates[1][0])
        self.outerInterRegCoords = self.LineToCircleArc(self.allCircles[1][1], self.coordinates[1][3])

    def _DrawRegion(self):
        x_coords = np.append(np.append(self.innerCoords[:, 0],
                                       self.outerCoords[::-1, 0]),
                             self.innerCoords[0, 0])

        y_coords = np.append(np.append(self.innerCoords[:, 1],
                                       self.outerCoords[::-1, 1]),
                             self.innerCoords[0, 1])

        # Draw the outline of the polygon
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
        self.interRegionOutside = pg.PlotDataItem(x_coords, y_coords,
                                                  pen=pg.mkPen(color=self.interRegionColor, width=1))

        # Color the inside of the polygon
        innerLine = pg.PlotDataItem(self.innerInterRegCoords[:, 0], self.innerInterRegCoords[:, 1])
        outerLine = pg.PlotDataItem(self.outerInterRegCoords[:, 0], self.outerInterRegCoords[:, 1])

        self.interRegionInside = pg.FillBetweenItem(innerLine, outerLine, brush=pg.mkBrush(self.interRegionColor))

    def _DrawLabel(self):
        # Draw text next to the polygon
        self.text = RegionLabelItem_ConnGraphic(self.name, self.coordinates[2])

    # Function used for rouding region borders
    def LineToCircleArc(self, circlePoints, start):
        """

        :param circlePoints:
        :param start:
        :return:
        """
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


class EdgeItem_ConnGraphic(pg.PlotCurveItem):
    value = 0
    node1: int
    node2: int
    typeFiltered: bool
    regionFiltered: bool
    weightRankFiltered: bool

    def __init__(self, node1, node2, value, node1_x, node1_y, node2_x, node2_y,
                 color: QColor = QColor(0, 0, 0), width=1, precision=20, plotRadius=0.0,
                 *args, **kargs):
        self.node1 = node1
        self.node2 = node2
        self.node1_x = node1_x
        self.node1_y = node1_y
        self.node2_x = node2_x
        self.node2_y = node2_y
        self.precision = precision
        self.value = value
        self.typeFiltered = False
        self.regionFiltered = False
        self.weightRankFiltered = False

        # For drawing
        self.color = color
        self.width = width

        x, y = self.computeBezierCurve(plotRadius)

        pen = pg.mkPen(color=self.color, width=self.width)

        super().__init__(x=x, y=y, pen=pen, *args, **kargs)

    def computeBezierCurve(self, plotRadius=0.0):
        p0 = np.array([self.node1_x, self.node1_y])
        p1 = np.array([self.node2_x, self.node2_y])
        midpoint = (p0 + p1) / 2

        dist = np.linalg.norm(p1 - p0)

        curvatureFactor = (plotRadius - dist) / plotRadius if plotRadius > 0.0 else 0.0

        controlPoint = curvatureFactor * midpoint

        controlPoints = np.array([p0, controlPoint, p1])
        n = len(controlPoints) - 1

        values = np.linspace(0, 1, self.precision)
        bezierPoints = np.array(
            [sum(comb(n, i) * (t ** i) * ((1 - t) ** (n - i)) * controlPoints[i]
                 for i in range(n + 1)) for t in values])

        return bezierPoints[:, 0], bezierPoints[:, 1]

    def SetColor(self, color: QColor):
        pen = pg.mkPen(color=color, width=self.width)
        self.setPen(pen)

    def SetWidth(self, width: float):

        self.width = width
        pen = pg.mkPen(color=self.color, width=width)
        self.setPen(pen)

    def updateVisible(self):
        visible = not self.typeFiltered or not self.regionFiltered or not self.weightRankFiltered
        super().setVisible(visible)

    def setVisible(self, visible):
        filtered = self.typeFiltered or self.regionFiltered or self.weightRankFiltered
        visible = visible and not filtered  # Can be true only if the edge is not filtered

        super().setVisible(visible)

    def forceVisible(self, visible):
        super().setVisible(visible)


class ConnGraphicView(pg.ViewBox):
    graph_info: ConnGraph_Infos
    filters: Filters_Infos
    filtersSave: FiltersSave_Infos
    regions: list[Union[RegionItem_ConnGraphic, None]]  # Can contain both None or RegionItem_ConnGraphic
    colors: list[QColor]
    edges: list[EdgeItem_ConnGraphic]
    radius: float  # Used to compute edges curvature
    edgesVisible: bool
    graphicFilter: bool  # True if a region is highlighted or hidden by a click on the chart
    highlightedRegions: bool

    # TODO : Modifier les paramètres d'initialisation pour passer le graphe complet
    def __init__(self, colorSet: list[QColor], parent=None):
        super().__init__(parent)

        self.graph_info = ConnGraph_Infos()
        self.filters = Filters_Infos()

        numPoints = len(self.graph_info.areasOrder) + 2  # For blank at begin and end

        # Init regions and edges list
        self.regions = [None for i in range(numPoints)]
        self.edges = []
        self.edgesVisible = True
        self.highlightedRegions = False

        # Init class attributes

        self.filtersSave = FiltersSave_Infos()  # Save the current state of the filter
        self.filtersSave.LoadCurrentFilters(self.filters.SaveCurrentFilters())

        self.graphicFilter = False
        self.numPoints = numPoints
        self.maxAbsConnValue = self.graph_info.absMinMax[1]
        self.edgeThicknessFactor = 5
        self.colorSet = colorSet

        # Image exporter
        self.imageExporter = None

        # Zoom
        self.XRange = self.YRange = 100

        self._InitViewSettings()
        self._InitGraphSettings()
        self._GenerateGraphValues()
        self._InitGraph_Regions()
        self._InitGraph_Edges()
        

    def _InitViewSettings(self):

        self.disableAutoRange()
        #self.setMouseEnabled(False, False)  # Disable mouse interactions
        self.setBackgroundColor("w")

        self.setRange(xRange=(-self.XRange, self.XRange), yRange=(-self.YRange, self.YRange))

    def ResetZoom(self):
        self.setRange(xRange=(-self.XRange, self.XRange), yRange=(-self.YRange, self.YRange))

    def _InitGraphSettings(self):

        self.radius = 50  # Radius in pyqtgraph unit of the text on the plot
        self.regionThickness = 300 / self.numPoints  # The more regions on the graph, the less the thickness of the donut will be
        self.interRegionThickness = self.regionThickness / 2
        self.interRegionDistance = self.regionThickness + 1  # Distance between region item and interRegion polygon
        self.textDistance = self.interRegionDistance + self.interRegionThickness + 0  # Distance between interRegion polygon and regionLabel item
        self.textLength = 20  # Lenght in pyqtgraph unit of the text on the plot

        # IMPORTANT : GREATLY AFFECT PERFORMANCES, but improves edge and region smoothing
        self.precision = 20  # Nb of lines which compose an edge

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

        # create two circle for the inner and outer line of the donut
        circleAngle = np.linspace(0.5 * np.pi, 2.5 * np.pi, self.numPoints * self.precision, endpoint=False)
        circleAngle = np.append(circleAngle, circleAngle[0])

        circlesPoints = np.vstack((np.cos(circleAngle), np.sin(circleAngle))).T

        # Region item circles
        innerRegionCirclePoints = circlesPoints * self.radius
        outerRegionCirclePoints = circlesPoints * (self.radius + self.regionThickness)

        # InterRegion polygon circles
        innerInterRegionCirclePoints = circlesPoints * (self.radius + self.interRegionDistance)
        outerInterRegionCirclePoints = circlesPoints * (
                    self.radius + self.interRegionDistance + self.interRegionThickness)

        # Text circles
        innerCircleTextPoints = circlesPoints * (self.radius + self.textDistance)
        outerCircleTextPoints = circlesPoints * (self.radius + self.textDistance + self.textLength)

        self.allCircles = ((innerRegionCirclePoints, outerRegionCirclePoints),
                           (innerInterRegionCirclePoints, outerInterRegionCirclePoints),
                           (innerCircleTextPoints, outerCircleTextPoints))

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

    def _InitGraph_Edges(self):
        edges = []

        for nodes, value in self.graph_info.edgesValues_withoutDuplicata.items():
            node1, node2 = nodes[0], nodes[1]

            edges.append([value, node1, node2])

        # For layering edges based on their absolute values
        edges.sort(key=lambda edge: abs(edge[0]))
        for edge in edges:
            self.CreateEdge(edge[1], edge[2], edge[0])

    # Get a region of the graph with its code
    def GetRegion(self, code):
        for region in self.regions:
            if region is not None:
                if region.code == code:
                    return region
        return None

    def CreateEdge(self, node1, node2, value):

        region1 = self.GetRegion(node1)
        region2 = self.GetRegion(node2)

        # Standardize edge value with the absolute value
        maxAbsConnValue = self.graph_info.plotMinMax[1]

        if region1 is not None and region2 is not None:
            # Compute edge ends
            region1Coordinates = region1.coordinates[0]
            region2Coordinates = region2.coordinates[0]

            color = self.ComputeEdgeColor(value)

            edgeW = abs(value / maxAbsConnValue * self.edgeThicknessFactor)

            # Get coordinate of each region border
            x1 = np.mean([region1Coordinates[2, 0], region1Coordinates[3, 0]])
            y1 = np.mean([region1Coordinates[2, 1], region1Coordinates[3, 1]])
            x2 = np.mean([region2Coordinates[2, 0], region2Coordinates[3, 0]])
            y2 = np.mean([region2Coordinates[2, 1], region2Coordinates[3, 1]])

            # Create the Edge
            edge = EdgeItem_ConnGraphic(node1, node2,
                                        value,
                                        x1, y1,
                                        x2, y2,
                                        color,
                                        width=edgeW,
                                        precision=self.precision,
                                        plotRadius=self.radius)

            self.AddEdge(edge)

    def ComputeEdgeColor(self, value):
        color_count = len(self.colorSet)
        bornes = self.graph_info.absMinMax[1]
        
        # Normalize the value to a ratio between 0 and 1
        ratio = abs(value) / bornes
        ratio = max(0, min(ratio, 1))  # Clamp ratio between 0 and 1

        def interpolate_color(c1, c2, ratio):
            r = int(c1.red() + (c2.red() - c1.red()) * ratio)
            g = int(c1.green() + (c2.green() - c1.green()) * ratio)
            b = int(c1.blue() + (c2.blue() - c1.blue()) * ratio)
            return QColor(r, g, b)

        if color_count == 2:
            # Interpolate between two colors
            return interpolate_color(self.colorSet[0], self.colorSet[1], ratio)
        
        elif color_count == 3:
            # Interpolate between three colors
            if value < 0:
                return interpolate_color(self.colorSet[1], self.colorSet[0], ratio)
            else:
                return interpolate_color(self.colorSet[1], self.colorSet[2], ratio)
        
        elif color_count == 7:
            if value < 0:
                # Negative value range
                segment = (-value / bornes) * 3  # Map to the range [0, 3]
                lower_index = int(segment)
                upper_index = min(lower_index + 1, 3)
                segment_ratio = segment - lower_index

                # Clamp indices to be within valid range
                lower_index = max(0, min(3, lower_index))
                upper_index = max(0, min(3, upper_index))
                lower_color_index = 3 - lower_index
                upper_color_index = 3 - upper_index
                # Ensure indices do not exceed the bounds of colorSet
                lower_color_index = max(0, min(6, lower_color_index))
                upper_color_index = max(0, min(6, upper_color_index))
                return interpolate_color(self.colorSet[lower_color_index], self.colorSet[upper_color_index], segment_ratio)
            else:
                # Positive value range
                segment = (value / bornes) * 3  # Map to the range [0, 3]
                lower_index = int(segment)
                upper_index = min(lower_index + 1, 3)
                segment_ratio = segment - lower_index

                # Clamp indices to be within valid range
                lower_index = max(0, min(3, lower_index))
                upper_index = max(0, min(3, upper_index))
                lower_color_index = 4 + lower_index
                upper_color_index = 4 + upper_index
                # Ensure indices do not exceed the bounds of colorSet
                lower_color_index = max(0, min(6, lower_color_index))
                upper_color_index = max(0, min(6, upper_color_index))
                return interpolate_color(self.colorSet[lower_color_index], self.colorSet[upper_color_index], segment_ratio)

        # Handle cases where color_count is not recognized
        return QColor(0, 0, 0)  # Default color or error handling

    def UpdateEdgesColorSet(self, colorSet : list[QColor]):
        self.colorSet = colorSet

        for edge in self.edges:
            if edge:
                color = self.ComputeEdgeColor(edge.value)
                edge.SetColor(color)


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

        allCoordinates = (regionCoordinates, interRegionCoordinates, textCoordinates)

        # Create region
        # TODO : add transparency

        # Convert RGB color values to QColor object
        regionColor = QColor(regionColor[0], regionColor[1], regionColor[2])
        interRegionColor = QColor(interRegionColor[0], interRegionColor[1], interRegionColor[2])

        #outlineColor = QColor(color[2], color[1], color[0])
        self.regions[pos] = RegionItem_ConnGraphic(code, name,
                                                   allCoordinates,
                                                   self.allCircles,
                                                   precision=self.precision,
                                                   regionColor=regionColor,
                                                   interRegionColor=interRegionColor)
        self.AddRegion(self.regions[pos], pos)

    def AddRegion(self, region: RegionItem_ConnGraphic, pos=None):

        # TODO : à revoir une fois le graphe implémenté
        if pos is None:
            self.regions.append(region)
        else:
            self.regions[pos] = region

        # Add region polygon the connGraphicView
        self.addItem(region.inside)
        self.addItem(region.outside)

        # Add interRegion polygon to the connGraphicView
        self.addItem(region.interRegionInside)
        self.addItem(region.interRegionOutside)

        # Add label to the connGraphicView
        self.addItem(region.text)

    def AddEdge(self, edge: EdgeItem_ConnGraphic):
        if edge is not None:
            self.edges.append(edge)

            # Add edge to the connGraphicView
            self.addItem(edge)

    # Get an edge of the graph with its two nodes
    def GetEdge(self, node1, node2):
        for edge in self.edges:
            if edge is not None:
                if edge.node1 == node1 and edge.node2 == node2:
                    return edge
        return None

    def GetRegionEdges(self, code):
        edges = []
        for edge in self.edges:
            if edge is not None:
                if edge.node1 == code or edge.node2 == code:
                    edges.append(edge)
        return edges

    def GetSortedEdgeList(self, reverse: bool):
        # TODO : check if edge is not None
        # True mean descending, False mean ascending
        return sorted(self.edges, key=lambda edge: abs(edge.value), reverse=reverse)

    def GetVisibleEdgesInfos(self):
        # TODO : peut être améliorer les performances en utilisant le dico dans toute la classe
        edges = {}

        for edge in self.edges:
            infos = {"visible": edge.isVisible(), "value": edge.value}
            edges[(edge.node1, edge.node2)] = infos

        return edges

   
    # ---------- Click methods ----------

    def mouseClickEvent(self, ev):
        #super().mouseClickEvent(ev) open context menu with right click, so we need to override it
        if ev.button() == Qt.MouseButton.LeftButton or ev.button() == Qt.MouseButton.RightButton:
            # Convert pixel position into scene position
            p = self.mapSceneToView(ev.scenePos())  # QPointF

            # Search for a region under clicked point
            for region in self.regions:
                if region is not None and (region.IsPointInRegionPolygon(p.x(), p.y()) or
                                           region.text.IsPointInTextPolygon(p.x(), p.y())):
                    ev.accept()  # Indicate that the event will be handled so the parent won't receive it
                    self.RegionClickEvent(ev, region)
                    break

    def RegionClickEvent(self, ev, region):
        if ev.button() == Qt.MouseButton.LeftButton and not region.edgesVisible:
            self.graphicFilter = True
            self.SetRegionEdgesVisible(region, True)
        elif ev.button() == Qt.MouseButton.LeftButton and region.edgesVisible:
            self.graphicFilter = True
            self.HighlightRegionEdges(region)
        elif ev.button() == Qt.MouseButton.RightButton:
            self.graphicFilter = True
            self.SetRegionEdgesVisible(region, False)

    def ShowExportDialog(self):
        if self.imageExporter is None:
            self.imageExporter = exporters.ImageExporter(self)

            dpi = 300
            current_size = self.imageExporter.parameters()['width']
            scaling_factor = dpi / 72.0
            self.imageExporter.parameters()['width'] = current_size * scaling_factor

            self.imageExporter.export()


    # ---------- Filter methods ----------

    def Filter(self):

        """
        Filter graph edges based on the give filter object.

        Actually, there are 4 filter applicable to the edges :
        - Connexion type
        - Inter-regional connexion type
        - Weight
        - Absolute weight
        - Rank of the edges

        NB : If you want to add a new filter, it's important to keep this hierarchy,
             and to add in EdgeItem_ConnGraphic class a boolean to manage the hierarchy.
        :param filters:
        :return:
        """

        if not (self.filters.discardWeight or self.filters.discardAbsWeight or self.filters.discardRank):
            for edge in self.edges:
                edge.weightRankFiltered = False
            self.ToggleAllEdges(True)

        newFiltersDiscard = [self.filters.discardWeight, self.filters.discardAbsWeight, self.filters.discardRank]
        oldFiltersDiscard = [self.filtersSave.discardWeight, self.filtersSave.discardAbsWeight, self.filtersSave.discardRank]
        forceChange = not (newFiltersDiscard == oldFiltersDiscard)

        # Weight filter
        if self.filters.discardWeight:
            if self.filtersSave.weightBetween_threshold != self.filters.weightBetween_threshold or forceChange:
                self.KeepEdgesBetweenWeight(self.filters.WeightMin(), self.filters.WeightMax())

        # Absolute weight filter
        if self.filters.discardAbsWeight:
            if self.filtersSave.absWeightBetween_threshold != self.filters.absWeightBetween_threshold or forceChange:
                self.KeepAbsEdgesBetweenWeight(self.filters.AbsWeightMin(), self.filters.AbsWeightMax())

        if self.filters.discardRank:
            if self.filtersSave.rankBetween_threshold != self.filters.rankBetween_threshold or forceChange:
                self.KeepEdgesBetweenRank(self.filters.RankMin(), self.filters.RankMax())

        # Connexion type filter
        if self.filtersSave.contralateral_connType != self.filters.contralateral_connType:
            self.ToggleConnType("Contralateral", self.filters.contralateral_connType)

        if self.filtersSave.homotopic_connType != self.filters.homotopic_connType:
            self.ToggleConnType("Homotopic", self.filters.homotopic_connType)

        if self.filtersSave.ipsilateral_connType != self.filters.ipsilateral_connType:
            self.ToggleConnType("Ipsilateral", self.filters.ipsilateral_connType)

        if self.filtersSave.other_connType != self.filters.other_connType:
            self.ToggleConnType("Other", self.filters.other_connType)

        # Inter-regional connexion type filter
        for (name1, name2), visible in self.filters.discardInterRegConn.items():
            # Check if the state have changed since the last call of Filter function
            if self.filtersSave.InterRegConnEnabled(name1, name2) != visible:
                self.FilterBetweenAreas()
                break

        if self.filtersSave.coefWidthEdges != self.filters.coefWidthEdges:
            self.ToggleCoefWithEdges(self.filters.coefWidthEdges)

        if self.filtersSave.colorEdges != self.filters.colorEdges:
            self.UpdateEdgesColorSet(self.filters.colorEdges)

        self.UpdateRegionsEdgesVisibleState()

        # As soon a filter is detected, turn off the graphic filter
        if self.graphicFilter:
            self.ResetGraphicFilter()

        # Save the current state of the filter
        self.filtersSave.LoadCurrentFilters(self.filters.SaveCurrentFilters())

    def ToggleAllRegions(self, visible: bool):
        for region in self.regions:
            self.SetRegionEdgesVisible(region, visible)

    def ToggleAllEdges(self, visible: bool, force: bool = False):

        self.ResetGraphicFilter()

        # Toggle edges
        for edge in self.edges:
            if edge is not None:
                if force:
                    edge.forceVisible(visible)
                else:
                    edge.setVisible(visible)

        # Update edgesVisible state and text color
        for region in self.regions:
            if region is not None:
                region.edgesVisible = visible
                region.text.SetTextShaded(not visible)

        self.edgesVisible = visible

    def ResetFilter(self):
        
        self.ToggleAllEdges(True, True)

    def ResetGraphicFilter(self):
        
        self.graphicFilter = False
        for region in self.regions:
            if region is not None:
                if region.text.shaded:
                    self.SetRegionEdgesVisible(region, True)

        self.ResetZoom()

        self.highlightedRegions = False

    def SetRegionEdgesVisible(self, region, visible):
        if region is not None:
            edges = self.GetRegionEdges(region.code)

            # Toggle edges
            for edge in edges:
                edge.setVisible(visible)

            region.text.SetTextShaded(not visible)

            region.edgesVisible = visible

    # Set region.edgesVisible to False if all of its edges are hidden
    def UpdateRegionsEdgesVisibleState(self):
        for region in self.regions:
            if region is not None:
                edges = self.GetRegionEdges(region.code)
                region.edgesVisible = False

                for edge in edges:
                    if edge.isVisible():
                        region.edgesVisible = True
                        break

    def HighlightRegionEdges(self, region):
        if region is not None:
            if not self.highlightedRegions:
                self.highlightedRegions = True
                self.ToggleAllRegions(False)

            self.SetRegionEdgesVisible(region, True)

    def FilterBetweenAreas(self):
        filters = Filters_Infos()
        for edge in self.edges:
            # Get edge areas names
            edgeRegion1 = self.GetRegion(edge.node1).name
            edgeRegion2 = self.GetRegion(edge.node2).name
            edgeArea1 = self.graph_info.areaInfos[edgeRegion1]["MajorRegion"]
            edgeArea2 = self.graph_info.areaInfos[edgeRegion2]["MajorRegion"]

            visible = filters.InterRegConnEnabled(edgeArea1, edgeArea2)

            edge.regionFiltered = not visible
            edge.setVisible(visible)

    def ToggleConnType(self, connType, visible):
        for edge in self.edges:
            edgeType = self.graph_info.edgesTypeConnexion[edge.node1][edge.node2]
            if edgeType == connType:
                edge.typeFiltered = not visible
                edge.setVisible(visible)
       
    def ToggleCoefWithEdges(self, newWidthCoef):
        self.edgeThicknessFactor = newWidthCoef

        for edge in self.edges:
            newWidth = abs(edge.value / self.graph_info.plotMinMax[1] * self.edgeThicknessFactor)
            edge.SetWidth(newWidth)

    def KeepEdgesBetweenWeight(self, inf, sup):
        # Hide each edge outside weight range
        for edge in self.edges:
            if edge is not None:
                visible = inf <= edge.value <= sup  # Boolean

                edge.weightRankFiltered = not visible
                edge.setVisible(visible)

    def KeepAbsEdgesBetweenWeight(self, inf, sup):
        #TODO : manage exception if inf or sup is negative ?

        # Hide each edge outside weight range
        for edge in self.edges:
            if edge is not None:
                visible = inf <= abs(edge.value) <= sup

                edge.weightRankFiltered = not visible
                edge.setVisible(visible)

    def KeepEdgesBetweenRank(self, inf, sup):
        edges = self.GetSortedEdgeList(True)

        for i in range(0, len(edges)):
            visible = inf <= i < sup

            edges[i].weightRankFiltered = not visible
            edges[i].setVisible(visible)


# TODO : set a parent
class ConnGraphic_Widget(QWidget):
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

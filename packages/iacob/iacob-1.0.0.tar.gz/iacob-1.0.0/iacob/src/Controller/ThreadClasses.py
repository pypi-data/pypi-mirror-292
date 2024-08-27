import numpy as np

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QTableWidgetItem

class RecovertListData_Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(list)

    def __init__(self, connGraph, filters):
        super().__init__()

        self.connGraph = connGraph
        self.filters = filters

    def run(self):

        # Build a list of edges with each information needed
        edges = np.array(self.connGraph.GetEdgesDetails())

        # Prepare formatting for int/float values in the tableWidget
        # Note : It is important to not convert int values into str() values without .format
        #        otherwise sorting will not work properly for these values
        intMax = max(np.concatenate((edges[:, 0], edges[:, 1])))
        intFormat = "{:" + str(intMax) + "d}"
        floatFormat = "{:10." + str(self.filters.valueRound) + "f}"

        # Create each row with edges info
        for edge in edges:

            node1 = intFormat.format(int(edge[0]))
            node2 = intFormat.format(int(edge[1]))
            area1 = str(edge[2])
            area2 = str(edge[3])
            region1 = str(edge[4])
            region2 = str(edge[5])
            connType = str(edge[6])
            value = floatFormat.format(float(edge[7]))
            rank = intFormat.format(int(edge[8]))
            newRow = [node1, node2, area1, area2, region1, region2, connType, value, rank]
            self.progress.emit(newRow)

        self.finished.emit()
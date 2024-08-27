from copy import deepcopy
import networkx as nx

from src.Model.Data_Storage.Filters_Model import Filters_Infos
from src.Model.Data_Storage.DataSingleton_Model import DataSingleton

class ConnGraph_Infos(metaclass=DataSingleton):

    def __init__(self):

        self.filters = Filters_Infos()
        self.InitReset()

    def InitReset(self):

        self.nxGraph = None
        self.nxGraphBinary = None
        self.dictGraph = None

        self.allGraphValues = []

        self.idName = {}  # Link between ID and Name of each area -> {ID_Node: Name}
        self.areaInfos = {}  # Area Informations
                             # {Name: {ID, RGBA, Side, MajorRegion, ID_Opposite, 3D_Coos}} -> FLUT File
        self.areasOrder = []  # Order of areas (with blanks)
        self.colorMajorRegions = {}
        self.numberOfNodes = None
        
        self.valuesRank = {}
        self.numberOfNodesInData = None
        self.edgesValues = {}  # Value of each edge in the graph -> {ID_Node: {ID_Next: Value}}
        self.edgesValuesFiltered = {}
        self.edgesValues_withoutDuplicata = {}
        self.edgesTypeConnexion = {}  # Connexion Type -> ID_Node: {ID_Next: Value}
                                      # Value in ("Contralateral", "Homotopic", "Ipsilateral", "Other")
        self.edgesTypeConnexionFiltered = {}
        self.numberOfEdges = 0

        self.minMax = None
        self.plotMinMax = None
        self.absMinMax = None

        self.adjacencyMatrix = []

    def SaveCurrentConnGraph(self):

        return {
            "nxGraph": deepcopy(self.nxGraph),
            "dictGraph": deepcopy(self.dictGraph),

            "allGraphValues": deepcopy(self.allGraphValues),
            "idName": deepcopy(self.idName),
            "areaInfos": deepcopy(self.areaInfos),
            "areasOrder": deepcopy(self.areasOrder),
            "colorMajorRegions": deepcopy(self.colorMajorRegions),

            "valuesRank": deepcopy(self.valuesRank),
            "edgesValues": deepcopy(self.edgesValues),
            "edgesValues_withoutDuplicata": deepcopy(self.edgesValues_withoutDuplicata),
            "edgesTypeConnexion": deepcopy(self.edgesTypeConnexion),

            "minMax": deepcopy(self.minMax),
            "plotMinMax": deepcopy(self.plotMinMax),
            "absMinMax": deepcopy(self.absMinMax),

            "numberOfNodes": self.numberOfNodes,
            "numberOfEdges": self.numberOfEdges,
            "adjacencyMatrix": deepcopy(self.adjacencyMatrix)
        }

    def LoadSaveConnGraph(self, connGraphSave: dict):

        self.nxGraph = connGraphSave["nxGraph"]
        self.dictGraph = connGraphSave["dictGraph"]

        self.allGraphValues = connGraphSave["allGraphValues"]
        self.idName = connGraphSave["idName"]
        self.areaInfos = connGraphSave["areaInfos"]
        self.areasOrder = connGraphSave["areasOrder"]
        self.colorMajorRegions = connGraphSave["colorMajorRegions"]

        self.valuesRank = connGraphSave["valuesRank"]
        self.edgesValues = connGraphSave["edgesValues"]
        self.edgesValues_withoutDuplicata = connGraphSave["edgesValues_withoutDuplicata"]
        self.edgesTypeConnexion = connGraphSave["edgesTypeConnexion"]

        self.minMax = connGraphSave["minMax"]
        self.plotMinMax = connGraphSave["plotMinMax"]
        self.absMinMax = connGraphSave["absMinMax"]

        self.numberOfNodes = connGraphSave["numberOfNodes"]
        self.numberOfEdges = connGraphSave["numberOfEdges"]
        self.adjacencyMatrix = connGraphSave["adjacencyMatrix"]

        self.SetEdgesValuesFiltered()
    
    # ----- Set Variables -----

    def SetGraph(self, nxGraph: nx.Graph):

        self.nxGraph = nxGraph
        self.dictGraph = nx.to_dict_of_dicts(self.nxGraph)

        if nx.empty_graph(self.nxGraph):
            self.adjacencyMatrix = nx.adjacency_matrix(self.nxGraph).todense()

    def SetTypeConnexion(self):

        for edge_source, edgesDestValue in self.edgesValues.items():

            name_source = self.idName[edge_source]
            if edge_source not in self.edgesTypeConnexion:
                self.edgesTypeConnexion[edge_source] = {}

            for edge_dest in edgesDestValue.keys():

                name_dest = self.idName[edge_dest]

                # Ipsilateral Connexion
                if self.areaInfos[name_source]["Side"] == self.areaInfos[name_dest]["Side"]:
                    self.edgesTypeConnexion[edge_source][edge_dest] = "Ipsilateral"

                elif self.areaInfos[name_source]["Side"] != self.areaInfos[name_dest]["Side"]:

                    # 2 -> 0 or 0 -> 2 => Other Connexion
                    if self.areaInfos[name_source]["Side"] == 0 or self.areaInfos[name_dest]["Side"] == 0:
                        self.edgesTypeConnexion[edge_source][edge_dest] = "Other"

                    # Contralateral or Homotopic Connexion
                    else:
                        if self.areaInfos[name_source]["ID_Opposite"] == self.areaInfos[name_dest]["ID"]:
                            self.edgesTypeConnexion[edge_source][edge_dest] = "Homotopic"
                        else:
                            self.edgesTypeConnexion[edge_source][edge_dest] = "Contralateral"

    # ----- Get Values -----

    # ====================================
    # Return a list of all weight of edges
    # ====================================
    def GetAllValues(self):
        return list(self.edgesValues_withoutDuplicata.values())

    # =============================================
    # Return a list of all absolute weight of edges
    # =============================================
    def GetAllAbsValues(self):
        return [abs(value) for value in list(self.edgesValues_withoutDuplicata.values())]


    # ----- Get Values With Name / ID -----

    # ============================================
    # Return the name corresponding to a region ID
    # ============================================
    def GetRegionNameWithID(self, ID: int):
        
        return self.idName[ID]

    # ============================================
    # Return the ID corresponding to a region name
    # ============================================
    def GetRegionIDWithName(self, name: str):
        for regionID, regionName in self.idName.items():
            if regionName == name:
                return regionID
        return None

    def GetAreasInWiderArea(self, widerAreaName : str):
        areas = []
        for areaName, areaDetails in self.areaInfos.items():
            if widerAreaName == areaDetails["MajorRegion"]:
                areas.append(areaName)

        return areas

    def GetAllInterRegionalName(self):

        interRegionalNames = []
        for _, info in self.areaInfos.items():
            name = info["MajorRegion"]
            if name not in interRegionalNames :
                interRegionalNames.append(name)


        return interRegionalNames

    # ----- Update Filter
    
    def SetEdgesValuesFiltered(self):
        self.edgesValuesFiltered = {}
        self.edgesTypeConnexionFiltered = {}
        
        if self.nxGraph:
            self.nxGraph.remove_edges_from(list(self.nxGraph.edges))

        # Sort element respecting filters
        for idEdge_source, destValue in self.edgesValues.items():

            nameEdge_source = self.GetRegionNameWithID(idEdge_source)
            for idEdge_dest, valueEdge in destValue.items():

                # Sorted with the Weight / Rank
                if self.filters.discardWeight:
                    if valueEdge < self.filters.weightBetween_threshold[0] or \
                        valueEdge > self.filters.weightBetween_threshold[1]:
                        continue

                elif self.filters.discardAbsWeight:
                    if abs(valueEdge) < self.filters.absWeightBetween_threshold[0] or \
                        abs(valueEdge) > self.filters.absWeightBetween_threshold[1]:
                        continue

                elif self.filters.discardRank:
                    if self.valuesRank[valueEdge] < self.filters.rankBetween_threshold[0] or \
                        self.valuesRank[valueEdge] > self.filters.rankBetween_threshold[1]:
                        continue

                nameEdge_dest = self.GetRegionNameWithID(idEdge_dest)

                # Sorted with Major Regions
                majorRegion_source = self.areaInfos[nameEdge_source]["MajorRegion"]
                majorRegion_dest = self.areaInfos[nameEdge_dest]["MajorRegion"]

                if not self.filters.discardInterRegConn[(majorRegion_source, majorRegion_dest)]:
                    continue

                # Sorted with Connection Type
                connType_sourceDest = self.edgesTypeConnexion[idEdge_source][idEdge_dest]

                if not self.filters.contralateral_connType:
                    if connType_sourceDest == "Contralateral":
                        continue

                if not self.filters.homotopic_connType:
                    if connType_sourceDest == "Homotopic":
                        continue
                
                if not self.filters.ipsilateral_connType:
                    if connType_sourceDest == "Ipsilateral":
                        continue

                if not self.filters.other_connType:
                    if connType_sourceDest == "Other":
                        continue


                if idEdge_source not in self.edgesValuesFiltered:
                    self.edgesValuesFiltered[idEdge_source] = {} 
                    self.edgesTypeConnexionFiltered[idEdge_source] = {} 

                self.edgesValuesFiltered[idEdge_source][idEdge_dest] = valueEdge
                self.edgesTypeConnexionFiltered[idEdge_source][idEdge_dest] = connType_sourceDest
                self.nxGraph.add_weighted_edges_from([(nameEdge_source, nameEdge_dest, abs(valueEdge))])

    # ----- List Part -----

    # =========================================================
    # Return a list of all edges with detailed infos about them
    # =========================================================
    def GetEdgesDetails_List(self):

        edgesDetails = []

        for edge_source, nextEdgeValues in self.edgesValuesFiltered.items():
            for edge_dest, value in nextEdgeValues.items():

                area_1 = self.GetRegionNameWithID(edge_source)
                area_2 = self.GetRegionNameWithID(edge_dest)

                region_1 = self.areaInfos[area_1]["MajorRegion"]
                region_2 = self.areaInfos[area_2]["MajorRegion"]

                connectionType = self.edgesTypeConnexion[edge_source][edge_dest]

                rank = self.valuesRank[value]

                details = [edge_source, edge_dest, area_1, area_2, region_1, region_2, connectionType, value, rank]

                edgesDetails.append(details)

        return edgesDetails


    # ----- Pie Chart Part -----    

    # ============================================================================
    # Return the list of name with connectivity (remove name without connectivity)
    # ============================================================================
    def GetAllNameWithConnectivity_PieChart(self):

        namesWithConnectivity = []
        for id in self.edgesValuesFiltered.keys():
            namesWithConnectivity.append(self.GetRegionNameWithID(id))

        return namesWithConnectivity

    # ====================================================================
    # Return a dict of all connectivity (nextNodeName, weight) from a node
    # ====================================================================
    def GetAllConnectivityWithName_PieChart(self, name: str):

        id_name = self.GetRegionIDWithName(name)

        connectivities = {}
        for edge_dest, value in self.edgesValuesFiltered[id_name].items():
            nextName = self.GetRegionNameWithID(edge_dest)
            connectivities[nextName] = (abs(value), self.areaInfos[nextName]["RGBA"])

        return connectivities

    # =====================================================
    # Return a dict of sum of all Major Regions from a node
    # =====================================================
    def GetAllMajorRegionsWithName_PieChart(self, name: str):

        id_name = self.GetRegionIDWithName(name)

        majorRegions = {}
        for edge_dest, edge_value in self.edgesValuesFiltered[id_name].items():

            majorRegion = self.areaInfos[self.GetRegionNameWithID(edge_dest)]["MajorRegion"]
            if majorRegion not in majorRegions:
                majorRegions[majorRegion] = 0.0

            majorRegions[majorRegion] += abs(edge_value)

        return majorRegions

    # =======================================================
    # Return a dict of sum of all Connection Type from a node
    # =======================================================
    def GetAllConnectionTypeWithName_PieChart(self, name: str):

        id_name = self.GetRegionIDWithName(name)

        connectionsType = {"Ipsilateral": 0.0, "Contralateral": 0.0, "Homotopic": 0.0, "Other": 0.0}
        for edge_dest, connectionType in self.edgesTypeConnexionFiltered[id_name].items():
            connectionsType[connectionType] += abs(self.edgesValues[id_name][edge_dest])

        return connectionsType


    # ----- GT Measures -----

    def local_efficiency(self, graph):

        efficiency = {}
        for node in graph.nodes():
            neighbors = list(graph.neighbors(node))
            if len(neighbors) < 2:
                efficiency[node] = 0
            else:
                subgraph = graph.subgraph(neighbors)
                efficiency[node] = nx.global_efficiency(subgraph)
        return efficiency

    def eccentricity(self, graphe, weight):

        eccentricity = {}
        
        # Parcourir chaque composant connexe du graphe
        for component in nx.connected_components(graphe):
            subgraph = graphe.subgraph(component)
            
            # Calculer les longueurs des chemins les plus courts avec les poids
            path_lengths = dict(nx.all_pairs_dijkstra_path_length(subgraph, weight=weight))
            
            # Calculer l'excentricité pour le sous-graphe
            subgraph_eccentricity = {}
            for node in subgraph.nodes():
                # Excentricité est la distance maximale depuis un nœud vers tous les autres nœuds
                max_distance = max(path_lengths[node].values(), default=0)
                subgraph_eccentricity[node] = max_distance
            
            # Mettre à jour l'excentricité globale
            eccentricity.update(subgraph_eccentricity)
        
        return eccentricity
    
    def GetLocalMeasures(self, localMeasure):

        match localMeasure:
            # ---- Weighted ----

            case "degree (weighted)":
                return dict(self.nxGraph.degree(weight='weight'))
            case "cluster coef (weighted)":
                return nx.clustering(self.nxGraph, weight='weight')
            case "local efficiency (weighted)":
                return self.local_efficiency(self.nxGraph)
            case "betweenness centrality (weighted)":
                return nx.betweenness_centrality(self.nxGraph, weight='weight', normalized=False)
            case "eigenvector centrality (weighted)":
                try:
                    return nx.eigenvector_centrality(self.nxGraph, max_iter=1000, tol=1e-5, weight='weight')
                except nx.PowerIterationFailedConvergence:
                    return nx.eigenvector_centrality_numpy(self.nxGraph, weight='weight')
                
            case "eccentricity (weighted)":
                return self.eccentricity(self.nxGraph, "weight")

            # ---- Binary ----
            case "degree (binary)":
                return dict(self.nxGraphBinary.degree())
            case "cluster coef (binary)":
                return nx.clustering(self.nxGraphBinary)
            case "local efficiency (binary)":
                return self.local_efficiency(self.nxGraphBinary)
            case "betweenness centrality (binary)":
                return nx.betweenness_centrality(self.nxGraphBinary, normalized=False)
            case "eigenvector centrality (binary)":
                return nx.eigenvector_centrality(self.nxGraphBinary)
            case "eccentricity (binary)":
                return self.eccentricity(self.nxGraphBinary, None)
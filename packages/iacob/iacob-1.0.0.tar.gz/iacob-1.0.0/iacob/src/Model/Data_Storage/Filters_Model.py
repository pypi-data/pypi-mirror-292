import json
from copy import deepcopy

from PyQt5.QtGui import QColor

from src.Model.Data_Storage.DataSingleton_Model import DataSingleton

class Filters_Infos(metaclass=DataSingleton):

    def __init__(self):

        self.InitReset()

    def InitReset(self):

        self.valueRound: int = 0
        self.thresholdPostFiltering: float = 0.0

        # Connection types
        self.contralateral_connType: bool = True
        self.homotopic_connType: bool = True
        self.ipsilateral_connType: bool = True
        self.other_connType: bool = True

        # Inter regional connections -> {(name1, name2) : visible}
        self.discardInterRegConn: dict[(str, str), bool] = {}

        # Thresholds
        self.discardWeight: bool = False
        self.discardAbsWeight: bool = False
        self.discardRank: bool = False

        self.weightBetween_threshold: list[float] = [0.0, 0.0]
        self.absWeightBetween_threshold: list[float] = [0.0, 0.0]
        self.rankBetween_threshold: list[int] = [0, 0]

        self.coefWidthEdges: int  = 5
        self.colorEdges: list[QColor] = []

    def SaveCurrentFilters(self):

        return {
            
            "thresholdPostFiltering": self.thresholdPostFiltering,
            
            "WeightAndRank": {

                "Weight": {
                    "discardWeight": self.discardWeight,
                    "weightBetween_threshold": deepcopy(self.weightBetween_threshold),
                },

                "AbsWeight": {

                    "discardAbsWeight": self.discardAbsWeight,
                    "absWeightBetween_threshold": deepcopy(self.absWeightBetween_threshold),
                },

                "Rank": {

                    "discardRank": self.discardRank,
                    "rankBetween_threshold": deepcopy(self.rankBetween_threshold),
                }
            },

            "InterRegConn": deepcopy(self.discardInterRegConn),

            "ConnType": {

                "contralateral_connType": self.contralateral_connType,
                "homotopic_connType": self.homotopic_connType,
                "ipsilateral_connType": self.ipsilateral_connType,
                "other_connType": self.other_connType,
            },

            "coefWidthEdges": self.coefWidthEdges,
            "colorEdges": deepcopy(self.colorEdges)
        }

    def LoadSaveFilters(self, filtersSave: dict):

        self.thresholdPostFiltering = filtersSave["thresholdPostFiltering"]

        conn_types = filtersSave["ConnType"]
        self.contralateral_connType = conn_types["contralateral_connType"]
        self.homotopic_connType = conn_types["homotopic_connType"]
        self.ipsilateral_connType = conn_types["ipsilateral_connType"]
        self.other_connType = conn_types["other_connType"]

        self.discardInterRegConn = filtersSave["InterRegConn"]

        weight_and_rank = filtersSave["WeightAndRank"]

        weight = weight_and_rank["Weight"]
        self.discardWeight = weight["discardWeight"]
        self.weightBetween_threshold = weight["weightBetween_threshold"]

        abs_weight = weight_and_rank["AbsWeight"]
        self.discardAbsWeight = abs_weight["discardAbsWeight"]
        self.absWeightBetween_threshold = abs_weight["absWeightBetween_threshold"]

        rank = weight_and_rank["Rank"]
        self.discardRank = rank["discardRank"]
        self.rankBetween_threshold = rank["rankBetween_threshold"]

        self.coefWidthEdges = filtersSave["coefWidthEdges"]
        self.colorEdges = filtersSave["colorEdges"]

    def InitInterRegConnDict(self, names: list[str]):
        for name1 in names:
            for name2 in names:
                self.discardInterRegConn[(name1, name2)] = True

    # Weight threshold
    def WeightMin(self) -> float:
        return self.weightBetween_threshold[0]

    def WeightMax(self) -> float:
        return self.weightBetween_threshold[1]

    def SetWeightMin(self, weightMin: float):
        self.weightBetween_threshold[0] = weightMin

    def SetWeightMax(self, weightMax: float):
        self.weightBetween_threshold[1] = weightMax

    # Abs weight threshold
    def AbsWeightMin(self) -> float:
        return self.absWeightBetween_threshold[0]

    def AbsWeightMax(self) -> float:
        return self.absWeightBetween_threshold[1]

    def SetAbsWeightMin(self, absWeightMin: float):
        self.absWeightBetween_threshold[0] = absWeightMin

    def SetAbsWeightMax(self, absWeightMax: float):
        self.absWeightBetween_threshold[1] = absWeightMax

    # Rank threshold
    def RankMin(self) -> int:
        return self.rankBetween_threshold[0]

    def RankMax(self) -> int:
        return self.rankBetween_threshold[1]

    def SetRankMin(self, rankMin: int):
        self.rankBetween_threshold[0] = rankMin

    def SetRankMax(self, rankMax: int):
        self.rankBetween_threshold[1] = rankMax

    def InterRegConnEnabled(self, name1: str, name2: str) -> bool:
        if (name1, name2) in self.discardInterRegConn:
            return self.discardInterRegConn[(name1, name2)]

    def SetInterRegConnEnabled(self, name1: str, name2: str, state: bool):
        self.discardInterRegConn[(name1, name2)] = state
        self.discardInterRegConn[(name2, name1)] = state

    def PreparationToJSON(self):

        interRegConn_str = {f"{k[0]},{k[1]}": v for k, v in self.discardInterRegConn.items()}

        filtersToJSON = {
            
            "thresholdPostFiltering": self.thresholdPostFiltering,
            
            "WeightAndRank": {

                "Weight": {
                    "discardWeight": self.discardWeight,
                    "weightBetween_threshold": self.weightBetween_threshold,
                },

                "AbsWeight": {

                    "discardAbsWeight": self.discardAbsWeight,
                    "absWeightBetween_threshold": self.absWeightBetween_threshold,
                },

                "Rank": {

                    "discardRank": self.discardRank,
                    "rankBetween_threshold": self.rankBetween_threshold,
                }
            },

            "InterRegConn": interRegConn_str,

            "ConnType": {

                "contralateral_connType": self.contralateral_connType,
                "homotopic_connType": self.homotopic_connType,
                "ipsilateral_connType": self.ipsilateral_connType,
                "other_connType": self.other_connType,
            }
        }

        return filtersToJSON

    def ExportToJSON (self, filePath):

        with open(filePath, 'w', encoding='utf-8') as file:
            json.dump(self.PreparationToJSON(), file, ensure_ascii=False, indent=4)

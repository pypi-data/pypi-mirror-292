from enum import Enum
from p1afempy.data_structures import CoordinatesType
import numpy as np
from dataclasses import dataclass


@dataclass
class WeightsAndIntegrationPoints:
    weights: np.ndarray
    integration_points: CoordinatesType


class CubatureRuleEnum(Enum):
    MIDPOINT = 1
    LAUFFER_LINEAR = 2
    SMPLX1 = 3


@dataclass
class CubatureRule:
    weights_and_integration_points: WeightsAndIntegrationPoints
    degree_of_exactness: int
    name: str

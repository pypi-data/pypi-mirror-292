from p1afempy.data_structures import \
    CoordinatesType, ElementsType
from triangle_cubature.cubature_rule \
    import CubatureRuleEnum
from triangle_cubature.transformations import \
    transform_weights_and_integration_points
from triangle_cubature.rule_factory import get_rule
from typing import Callable
import numpy as np


def integrate_on_triangle(
        f: Callable[[CoordinatesType], np.ndarray],
        triangle: CoordinatesType,
        cubature_rule: CubatureRuleEnum) -> float:
    """
    approximates the integral of the function provided
    on the triangle at hand using the specified cubature rule

    parameters
    ----------
    f: Callable[[CoordinatesType], np.ndarray]
        the function to be integrated
    triangle: CoordinatesType
        the coordinates of the triangle's vertices
        in counter-clockwise order
    cubature_rule: CubatureRuleEnum
        the cubature rule to be used

    returns
    -------
    float: the approximated value of the integral

    notes
    -----
    - the function f must be able to
      handle inputs of shape (N, 2), i.e.
      coordinates as array
    """
    waip = get_rule(rule=cubature_rule).weights_and_integration_points
    transformed = transform_weights_and_integration_points(
        weights_and_integration_points=waip,
        physical_triangle=triangle)
    return np.dot(transformed.weights, f(transformed.integration_points))


def integrate_on_mesh(
        f: Callable[[CoordinatesType], np.ndarray],
        coordinates: CoordinatesType,
        elements: ElementsType,
        cubature_rule: CubatureRuleEnum) -> float:
    """
    approximates the integral of the function provided
    over the mesh at hand using the specified cubature rule

    parameters
    ----------
    f: Callable[[CoordinatesType], np.ndarray]
        the function to be integrated
    coordinates: CoordinatesType
        vrtices of the mesh
    elements: ElementsType
        the elements of the mesh
    cubature_rule: CubatureRuleEnum
        the cubature rule to be used

    returns
    -------
    float: the approximated value of the integral

    notes
    -----
    - the function f must be able to
      handle inputs of shape (N, 2), i.e.
      coordinates as array
    """

    # fully vectorized midpoint integration,
    # based on ideas found in the following paper:
    # --------------------------------------------------------------------
    # Funken, Stefan, Dirk Praetorius, and Philipp Wissgott.
    # Efficient Implementation of Adaptive P1-FEM in Matlab.
    # Computational Methods in Applied Mathematics 11,
    # no. 4 (1 January 2011): 460–90. https://doi.org/10.2478/cmam-2011-0026.
    c1 = coordinates[elements[:, 0]]
    d21 = coordinates[elements[:, 1]] - c1
    d31 = coordinates[elements[:, 2]] - c1

    # vector of element areas 2*|T|
    areas_2 = (d21[:, 0]*d31[:, 1] - d21[:, 1] * d31[:, 0])

    waip = get_rule(rule=cubature_rule).weights_and_integration_points
    weights = waip.weights
    integration_points = waip.integration_points

    sum = 0.
    for weight, integration_point in zip(weights, integration_points):
        x_hat, y_hat = integration_point
        transformed_integration_points = c1 + x_hat * d21 + y_hat * d31
        f_on_integration_points = f(transformed_integration_points)
        sum += weight * np.dot(f_on_integration_points, areas_2)
    return sum

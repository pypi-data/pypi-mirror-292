import numpy as np
from p1afempy.data_structures import CoordinatesType
from triangle_cubature.cubature_rule \
    import WeightsAndIntegrationPoints


def transform_weights_and_integration_points(
    weights_and_integration_points: WeightsAndIntegrationPoints,
    physical_triangle: CoordinatesType
) -> WeightsAndIntegrationPoints:
    reference_weights = weights_and_integration_points.weights
    reference_integration_points = \
        weights_and_integration_points.integration_points

    jacobian = get_jacobian(physical_triangle=physical_triangle)

    transformed_weights = transform_weights(
        reference_weights=reference_weights,
        jacobian=jacobian)
    transformed_integration_points = transform_integration_points(
        reference_integration_points=reference_integration_points,
        p1=physical_triangle[0, :],
        jacobian=jacobian)

    return WeightsAndIntegrationPoints(
        weights=transformed_weights,
        integration_points=transformed_integration_points)


def transform_weights(reference_weights: np.ndarray,
                      jacobian: np.ndarray) -> np.ndarray:
    jacobian_determinant = np.linalg.det(jacobian)
    return jacobian_determinant * reference_weights


def transform_integration_points(
        reference_integration_points: CoordinatesType,
        p1: np.ndarray,
        jacobian: np.ndarray) -> CoordinatesType:

    transformed_integration_points = p1 \
        + reference_integration_points.dot(jacobian.T)

    return np.array(transformed_integration_points)


def get_jacobian(physical_triangle: CoordinatesType) -> np.ndarray:
    p1 = physical_triangle[0, :]
    p2 = physical_triangle[1, :]
    p3 = physical_triangle[2, :]
    return np.column_stack((p2 - p1, p3 - p1))

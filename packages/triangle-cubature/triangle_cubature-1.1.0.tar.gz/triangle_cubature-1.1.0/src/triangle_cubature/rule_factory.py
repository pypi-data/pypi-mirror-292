import numpy as np
from triangle_cubature.cubature_rule \
    import CubatureRule, CubatureRuleEnum, WeightsAndIntegrationPoints


def get_rule(rule: CubatureRuleEnum) -> CubatureRule:
    """
    given a cubature rule, returns the corresponding
    weight(s) and integration point(s)

    Notes
    -----
    - the rules correspond to the rules as specified in [1]

    References
    ----------
    - [1] Stenger, Frank.
      'Approximate Calculation of Multiple Integrals (A. H. Stroud)'.
      SIAM Review 15, no. 1 (January 1973): 234-35.
      https://doi.org/10.1137/1015023. p. 306-315
    """
    if rule == CubatureRuleEnum.MIDPOINT:
        weights = np.array([1./2.])
        integration_points = np.array([1./3., 1./3.]).reshape(1, 2)
        weights_and_integration_points = WeightsAndIntegrationPoints(
            weights=weights,
            integration_points=integration_points)
        name = 'midpoint'
        degree_of_exactness = 1

        return CubatureRule(
            weights_and_integration_points=weights_and_integration_points,
            degree_of_exactness=degree_of_exactness,
            name=name)

    if rule == CubatureRuleEnum.LAUFFER_LINEAR:
        integration_points = np.array([
            [0., 0.],
            [1., 0.],
            [0., 1.]
        ])
        weights = np.array([
            1/3 * 0.5,
            1/3 * 0.5,
            1/3 * 0.5
        ])
        weights_and_integration_points = WeightsAndIntegrationPoints(
            weights=weights,
            integration_points=integration_points)
        name = 'lauffer-linear'
        degree_of_exactness = 1

        return CubatureRule(
            weights_and_integration_points=weights_and_integration_points,
            degree_of_exactness=degree_of_exactness,
            name=name)

    if rule == CubatureRuleEnum.SMPLX1:
        r = (1.)/(6.)
        s = 2./3.
        integration_points = np.array([
            [r, r],
            [r, s],
            [s, r]
        ])
        weights = np.array([
            1/3 * 0.5,
            1/3 * 0.5,
            1/3 * 0.5
        ])
        weights_and_integration_points = WeightsAndIntegrationPoints(
            weights=weights,
            integration_points=integration_points)
        name = 'SMPLX1'
        degree_of_exactness = 2

        return CubatureRule(
            weights_and_integration_points=weights_and_integration_points,
            degree_of_exactness=degree_of_exactness,
            name=name)

    raise ValueError('specified rule does not exist.')

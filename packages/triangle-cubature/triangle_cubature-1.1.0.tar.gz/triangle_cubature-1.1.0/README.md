# Triangle Cubature Rules
This repo serves as a collection of well-tested triangle cubature rules,
i.e. numerical integration schemes for integrals of the form

$$
\int_K f(x, y) ~\mathrm{d}x ~\mathrm{d}y,
$$

where $K \subset \mathbb{R}^2$ is a triangle.
All cubature rules are based on [1].

## Usage
Using the cubature schemes is fairly simple.

```python
from triangle_cubature.cubature_rule import CubatureRuleEnum
from triangle_cubature.integrate import integrate_on_mesh
from triangle_cubature.integrate import integrate_on_triangle
import numpy as np

# specifying the mesh
coordinates = np.array([
  [0., 0.],
  [1., 0.],
  [1., 1.],
  [0., 1.]
])

elements = np.array([
  [0, 1, 2],
  [0, 2, 3]
], dtype=int)


# defining the function to be integrated
# NOTE the function must be able to handle coordinates as array
# of shape (N, 2)
def constant(coordinates: np.ndarray):
    """returns 1"""
    return np.ones(coordinates.shape[0])


# integrating over the whole mesh
integral_on_mesh = integrate_on_mesh(
    f=constant,
    coordinates=coordinates,
    elements=elements,
    cubature_rule=CubatureRuleEnum.MIDPOINT)

# integrating over a single triangle, e.g.
# in this case, the "first" element of the mesh
integral_on_triangle = integrate_on_triangle(
    f=constant,
    triangle=coordinates[elements[0], :],
    cubature_rule=CubatureRuleEnum.MIDPOINT)

print(f'Integral value on mesh: {integral_on_mesh}')
print(f'Integral value on triangle: {integral_on_triangle}')

```

## Available Rules
The available cubature rules can be found in `triangle_cubature/cubature_rule.py`.

- `CubatureRuleEnum.MIDPOINT`
  - degree of exactness: 1
  - Ref: [1]
- `CubatureRuleEnum.LAUFFER_LINEAR`
  - degree of exactness: 1
  - Ref: [1]
- `CubatureRuleEnum.SMPLX1`
  - degree of exactness: 2
  - Ref: [1]

## (Unit) Tests
To run auto tests, you do
```sh
python -m unittest discover tests/auto/
```

> The unit tests use `sympy` to verify the degree of exactness of the
> implemented cubature rules, i.e. creates random polynomials $p_d$ of the 
> expected degree of exactness $d$ and compares the exact result of
> $\int_K p_d(x, y) ~\mathrm{d}x ~\mathrm{d}y$ to the value obtained
> with the cubature rule at hand.

## References
- [1] Stenger, Frank.
    'Approximate Calculation of Multiple Integrals (A. H. Stroud)'.
    SIAM Review 15, no. 1 (January 1973): 234-35.
    https://doi.org/10.1137/1015023. p. 306-315
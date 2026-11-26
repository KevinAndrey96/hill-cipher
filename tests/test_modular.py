from math import gcd

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from hill import SingularMatrixError, adjugate, determinant, inverse_mod
from hill.modular import Matrix, as_matrix, minor, multiply, transpose


def laplace(matrix: Matrix) -> int:
    if len(matrix) == 1:
        return matrix[0][0]

    return sum((-1) ** c * matrix[0][c] * laplace(minor(matrix, 0, c)) for c in range(len(matrix)))


def identity(size: int) -> Matrix:
    return tuple(tuple(int(r == c) for c in range(size)) for r in range(size))


@st.composite
def square_matrices(draw: st.DrawFn, max_size: int = 4) -> Matrix:
    size = draw(st.integers(min_value=1, max_value=max_size))
    values = st.integers(min_value=-30, max_value=30)

    return tuple(tuple(draw(values) for _ in range(size)) for _ in range(size))


@pytest.mark.parametrize(
    ("matrix", "expected"),
    [
        (((5,),), 5),
        (((3, 3), (2, 5)), 9),
        (((0, 1), (1, 0)), -1),
        (((2, 0, 1), (1, 3, 2), (1, 1, 1)), 0),
        (((0, 0), (0, 4)), 0),
        (((6, 24, 1), (13, 16, 10), (20, 17, 15)), 441),
    ],
)
def test_determinant_of_known_matrices(matrix: Matrix, expected: int) -> None:
    assert determinant(matrix) == expected


@given(square_matrices())
def test_bareiss_matches_laplace_expansion(matrix: Matrix) -> None:
    assert determinant(matrix) == laplace(matrix)


@given(square_matrices())
def test_adjugate_identity(matrix: Matrix) -> None:
    size = len(matrix)
    product = tuple(
        tuple(sum(matrix[r][k] * adjugate(matrix)[k][c] for k in range(size)) for c in range(size))
        for r in range(size)
    )
    det = determinant(matrix)

    assert product == tuple(tuple(det * value for value in row) for row in identity(size))


@given(square_matrices())
def test_inverse_mod_26(matrix: Matrix) -> None:
    assume(gcd(determinant(matrix) % 26, 26) == 1)

    assert multiply(matrix, inverse_mod(matrix, 26), 26) == identity(len(matrix))


def test_rejects_matrices_sharing_a_factor_with_the_modulus() -> None:
    with pytest.raises(SingularMatrixError, match="determinant 2 shares a factor with 26"):
        inverse_mod(((2, 0), (0, 1)), 26)


@pytest.mark.parametrize("rows", [[], [[1, 2]], [[1, 2], [3]]])
def test_as_matrix_requires_square_input(rows: list[list[int]]) -> None:
    with pytest.raises(ValueError, match="square"):
        as_matrix(rows)


def test_transpose() -> None:
    assert transpose(((1, 2), (3, 4))) == ((1, 3), (2, 4))

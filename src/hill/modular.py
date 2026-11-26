"""Exact integer matrix arithmetic modulo m."""

from __future__ import annotations

from collections.abc import Sequence
from math import gcd

type Matrix = tuple[tuple[int, ...], ...]


class SingularMatrixError(ValueError):
    """Raised when a matrix has no inverse modulo m."""


def as_matrix(rows: Sequence[Sequence[int]]) -> Matrix:
    matrix = tuple(tuple(int(value) for value in row) for row in rows)
    size = len(matrix)
    if size == 0 or any(len(row) != size for row in matrix):
        raise ValueError("matrix must be square and non empty")

    return matrix


def determinant(matrix: Matrix) -> int:
    """Exact determinant by fraction free Bareiss elimination."""
    rows = [list(row) for row in matrix]
    size = len(rows)
    sign, previous = 1, 1
    for pivot in range(size - 1):
        if rows[pivot][pivot] == 0:
            swap = next((r for r in range(pivot + 1, size) if rows[r][pivot] != 0), None)
            if swap is None:
                return 0
            rows[pivot], rows[swap] = rows[swap], rows[pivot]
            sign = -sign
        for r in range(pivot + 1, size):
            for c in range(pivot + 1, size):
                rows[r][c] = (
                    rows[r][c] * rows[pivot][pivot] - rows[r][pivot] * rows[pivot][c]
                ) // previous
        previous = rows[pivot][pivot]

    return sign * rows[-1][-1]


def minor(matrix: Matrix, row: int, column: int) -> Matrix:
    return tuple(
        tuple(value for c, value in enumerate(values) if c != column)
        for r, values in enumerate(matrix)
        if r != row
    )


def adjugate(matrix: Matrix) -> Matrix:
    """Transpose of the cofactor matrix, so that A adj(A) = det(A) I."""
    size = len(matrix)
    if size == 1:
        return ((1,),)

    return tuple(
        tuple((-1) ** (r + c) * determinant(minor(matrix, c, r)) for c in range(size))
        for r in range(size)
    )


def inverse_mod(matrix: Matrix, modulus: int) -> Matrix:
    """A^-1 = det(A)^-1 adj(A) (mod m), defined only when gcd(det A, m) = 1."""
    det = determinant(matrix) % modulus
    if gcd(det, modulus) != 1:
        raise SingularMatrixError(
            f"determinant {det} shares a factor with {modulus}, the matrix is not invertible"
        )
    det_inverse = pow(det, -1, modulus)

    return tuple(tuple(det_inverse * value % modulus for value in row) for row in adjugate(matrix))


def multiply(left: Matrix, right: Matrix, modulus: int) -> Matrix:
    return tuple(
        tuple(
            sum(a * b for a, b in zip(row, column, strict=True)) % modulus
            for column in zip(*right, strict=True)
        )
        for row in left
    )


def transpose(matrix: Matrix) -> Matrix:
    return tuple(zip(*matrix, strict=True))

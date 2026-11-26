"""Hill cipher (Lester S. Hill, 1929): C = K P (mod 26) on blocks of n letters."""

from __future__ import annotations

import math
import unicodedata
from collections.abc import Sequence
from dataclasses import dataclass

from hill.modular import Matrix, as_matrix, inverse_mod, multiply

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
MODULUS = len(ALPHABET)
FILLER = "X"


class InvalidKeyError(ValueError):
    """Raised when a key matrix cannot be used to encrypt and decrypt."""


def normalize(text: str) -> str:
    """Uppercase letters only, with accents removed (á -> A, ñ -> N)."""
    decomposed = unicodedata.normalize("NFD", text.upper())

    return "".join(char for char in decomposed if char in ALPHABET)


def to_numbers(text: str) -> list[int]:
    return [ALPHABET.index(letter) for letter in normalize(text)]


def to_letters(numbers: Sequence[int]) -> str:
    return "".join(ALPHABET[number % MODULUS] for number in numbers)


@dataclass(frozen=True, slots=True)
class HillKey:
    """Square key matrix invertible modulo 26, with its inverse precomputed."""

    matrix: Matrix
    inverse: Matrix

    @classmethod
    def from_matrix(cls, rows: Sequence[Sequence[int]]) -> HillKey:
        try:
            matrix = as_matrix(rows)
            reduced = tuple(tuple(value % MODULUS for value in row) for row in matrix)

            return cls(reduced, inverse_mod(reduced, MODULUS))
        except ValueError as error:
            raise InvalidKeyError(f"key matrix: {error}") from error

    @classmethod
    def from_keyword(cls, keyword: str) -> HillKey:
        """Fills an n x n matrix row by row with the letters of the keyword."""
        numbers = to_numbers(keyword)
        size = math.isqrt(len(numbers))
        if size == 0 or size * size != len(numbers):
            raise InvalidKeyError("keyword length must be a perfect square (4, 9, 16...)")

        return cls.from_matrix([numbers[row * size : (row + 1) * size] for row in range(size)])

    @property
    def size(self) -> int:
        return len(self.matrix)


def _blocks_as_columns(numbers: Sequence[int], size: int) -> Matrix:
    return tuple(
        tuple(numbers[start + row] for start in range(0, len(numbers), size)) for row in range(size)
    )


def _columns_to_numbers(matrix: Matrix) -> list[int]:
    return [value for column in zip(*matrix, strict=True) for value in column]


def _apply(matrix: Matrix, numbers: Sequence[int]) -> str:
    if not numbers:
        return ""
    product = multiply(matrix, _blocks_as_columns(numbers, len(matrix)), MODULUS)

    return to_letters(_columns_to_numbers(product))


def pad(text: str, size: int) -> str:
    """Normalized text completed with X up to a multiple of the block size."""
    letters = normalize(text)

    return letters + FILLER * (-len(letters) % size)


def encrypt(plaintext: str, key: HillKey) -> str:
    return _apply(key.matrix, to_numbers(pad(plaintext, key.size)))


def decrypt(ciphertext: str, key: HillKey) -> str:
    """P = K^-1 C (mod 26); padding X letters stay at the end."""
    numbers = to_numbers(ciphertext)
    if len(numbers) % key.size:
        raise InvalidKeyError(f"ciphertext length must be a multiple of the block size {key.size}")

    return _apply(key.inverse, numbers)

"""Known plaintext attack: n independent blocks reveal an n x n key.

With plaintext blocks as the columns of P and their ciphertexts as the
columns of C, C = K P, so K = C P^-1 (mod 26) whenever P is invertible.
"""

from __future__ import annotations

from collections.abc import Sequence
from itertools import combinations, islice

from hill.cipher import MODULUS, HillKey, InvalidKeyError, encrypt, to_letters, to_numbers
from hill.modular import Matrix, SingularMatrixError, inverse_mod, multiply, transpose

MAX_COMBINATIONS = 5000


class AttackError(ValueError):
    """Raised when the known pairs do not determine a valid key."""


def _blocks(numbers: Sequence[int], size: int) -> list[tuple[int, ...]]:
    return [tuple(numbers[start : start + size]) for start in range(0, len(numbers), size)]


def recover_key(plaintext: str, ciphertext: str, size: int) -> HillKey:
    """Finds the key from matching plaintext and ciphertext fragments.

    Needs at least size blocks of size letters whose plaintext matrix is
    invertible modulo 26; the recovered key is checked against every pair.
    """
    plain, cipher = to_numbers(plaintext), to_numbers(ciphertext)
    usable = min(len(plain), len(cipher)) // size * size
    plain_blocks, cipher_blocks = _blocks(plain[:usable], size), _blocks(cipher[:usable], size)
    if len(plain_blocks) < size:
        raise AttackError(f"need at least {size * size} known letters for a {size} x {size} key")
    for chosen in islice(combinations(range(len(plain_blocks)), size), MAX_COMBINATIONS):
        p_matrix: Matrix = transpose(tuple(plain_blocks[index] for index in chosen))
        c_matrix: Matrix = transpose(tuple(cipher_blocks[index] for index in chosen))
        try:
            candidate = multiply(c_matrix, inverse_mod(p_matrix, MODULUS), MODULUS)
            key = HillKey.from_matrix(candidate)
        except (SingularMatrixError, InvalidKeyError):
            continue
        if to_numbers(encrypt(to_letters(plain[:usable]), key)) == cipher[:usable]:
            return key

    raise AttackError("no consistent invertible key explains the known pairs")

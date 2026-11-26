import pytest
from hypothesis import given
from hypothesis import strategies as st

from hill import HillKey, InvalidKeyError, decrypt, encrypt, normalize, pad

GYBNQKURP = HillKey.from_keyword("GYBNQKURP")
HILL = HillKey.from_keyword("HILL")


def test_wikipedia_three_by_three_example() -> None:
    assert encrypt("ACT", GYBNQKURP) == "POH"
    assert encrypt("CAT", GYBNQKURP) == "FIN"
    assert GYBNQKURP.inverse == ((8, 5, 10), (21, 8, 21), (21, 12, 8))


def test_wikipedia_two_by_two_example() -> None:
    assert HILL.matrix == ((7, 8), (11, 11))
    assert encrypt("short example", HILL) == "APADJTFTWLFJ"
    assert decrypt("APADJ TFTWLFJ", HILL) == "SHORTEXAMPLE"


def test_pads_with_x_to_complete_blocks() -> None:
    assert pad("Ñandú", 3) == "NANDUX"
    assert decrypt(encrypt("CAFE", GYBNQKURP), GYBNQKURP) == "CAFEXX"
    assert encrypt("", HILL) == ""


def test_reduces_matrix_entries_modulo_26() -> None:
    assert HillKey.from_matrix([[29, -23], [2, 31]]).matrix == ((3, 3), (2, 5))


@pytest.mark.parametrize(
    ("rows", "message"),
    [
        ([[2, 4], [6, 8]], "not invertible"),
        ([[13, 0], [0, 1]], "not invertible"),
        ([[1, 2, 3]], "square"),
    ],
)
def test_rejects_unusable_matrices(rows: list[list[int]], message: str) -> None:
    with pytest.raises(InvalidKeyError, match=message):
        HillKey.from_matrix(rows)


@pytest.mark.parametrize("keyword", ["", "ABC", "HELLO"])
def test_keyword_length_must_be_a_square(keyword: str) -> None:
    with pytest.raises(InvalidKeyError, match="perfect square"):
        HillKey.from_keyword(keyword)


def test_decrypt_requires_whole_blocks() -> None:
    with pytest.raises(InvalidKeyError, match="multiple of the block size 3"):
        decrypt("ABCD", GYBNQKURP)


@given(st.text(), st.sampled_from([GYBNQKURP, HILL, HillKey.from_matrix([[3, 3], [2, 5]])]))
def test_decrypt_inverts_encrypt(text: str, key: HillKey) -> None:
    assert decrypt(encrypt(text, key), key) == pad(text, key.size)
    assert normalize(text) == pad(text, key.size)[: len(normalize(text))]

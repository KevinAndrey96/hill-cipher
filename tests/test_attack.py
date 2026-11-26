import pytest
from hypothesis import given
from hypothesis import strategies as st

from hill import AttackError, HillKey, encrypt, recover_key

MESSAGE = "We attack the northern bridge at dawn, bring every engineer you can find"


def test_recovers_the_wikipedia_key_from_its_own_example() -> None:
    assert recover_key("shortexample", "APADJTFTWLFJ", 2).matrix == ((7, 8), (11, 11))


def test_recovers_a_three_by_three_key() -> None:
    key = HillKey.from_keyword("GYBNQKURP")

    assert recover_key(MESSAGE, encrypt(MESSAGE, key), 3) == key


def test_needs_enough_known_letters() -> None:
    with pytest.raises(AttackError, match="at least 9 known letters"):
        recover_key("ABCDEF", "ABCDEF", 3)


def test_rejects_pairs_that_no_key_explains() -> None:
    with pytest.raises(AttackError, match="no consistent invertible key"):
        recover_key("ABBAAB", "ABBACD", 2)


def test_rejects_plaintext_without_invertible_blocks() -> None:
    with pytest.raises(AttackError, match="no consistent invertible key"):
        recover_key("AAAAAAAA", "AAAAAAAA", 2)


invertible_2x2 = st.tuples(*(st.integers(0, 25) for _ in range(4))).filter(
    lambda v: (v[0] * v[3] - v[1] * v[2]) % 2 and (v[0] * v[3] - v[1] * v[2]) % 13
)


@given(invertible_2x2)
def test_recovers_any_invertible_two_by_two_key(values: tuple[int, int, int, int]) -> None:
    key = HillKey.from_matrix([values[:2], values[2:]])

    assert recover_key(MESSAGE, encrypt(MESSAGE, key), 2) == key

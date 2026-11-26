import io
import subprocess
import sys

import pytest

from hill.cli import main


def run(argv: list[str], stdin: str = "") -> tuple[int, str]:
    output = io.StringIO()
    status = main(argv, stdin=io.StringIO(stdin), stdout=output)

    return status, output.getvalue()


def test_encrypts_with_a_keyword_and_decrypts_with_a_matrix() -> None:
    assert run(["encrypt", "-k", "HILL", "short example"]) == (0, "APADJTFTWLFJ\n")
    assert run(["decrypt", "-m", "7 8 11 11"], "APADJTFTWLFJ") == (0, "SHORTEXAMPLE\n")


def test_accepts_comma_separated_matrices() -> None:
    assert run(["encrypt", "-m", "6,24,1,13,16,10,20,17,15", "ACT"]) == (0, "POH\n")


def test_attack_prints_the_key() -> None:
    assert run(["attack", "-n", "2", "shortexample", "APADJTFTWLFJ"]) == (0, " 7  8\n11 11\n")


@pytest.mark.parametrize(
    "argv",
    [
        ["encrypt", "-m", "2 4 6 8", "hola"],
        ["encrypt", "-m", "1 2 3", "hola"],
        ["encrypt", "-m", "a b c d", "hola"],
        ["decrypt", "-k", "HILL", "ABC"],
        ["attack", "AB", "CD"],
    ],
)
def test_reports_errors_with_exit_code_two(
    argv: list[str], capsys: pytest.CaptureFixture[str]
) -> None:
    assert run(argv) == (2, "")
    assert capsys.readouterr().err.startswith("error:")


def test_module_entry_point() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "hill", "encrypt", "-k", "GYBNQKURP", "CAT"],
        capture_output=True,
        text=True,
        check=True,
    )

    assert completed.stdout == "FIN\n"

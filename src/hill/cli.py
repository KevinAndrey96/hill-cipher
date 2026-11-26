"""Command line interface: encrypt, decrypt and the known plaintext attack."""

from __future__ import annotations

import argparse
import math
import sys
from collections.abc import Sequence
from typing import TextIO

from hill.attack import AttackError, recover_key
from hill.cipher import HillKey, InvalidKeyError, decrypt, encrypt


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hill", description="Cifrado de Hill de n x n.")
    commands = parser.add_subparsers(dest="command", required=True)
    for name, summary in (("encrypt", "cifrar"), ("decrypt", "descifrar")):
        command = commands.add_parser(name, help=summary)
        source = command.add_mutually_exclusive_group(required=True)
        source.add_argument("--matrix", "-m", help='matriz por filas, por ejemplo "3 3 2 5"')
        source.add_argument("--keyword", "-k", help="palabra de 4, 9, 16... letras")
        command.add_argument("text", nargs="?", help="texto; si se omite se lee de stdin")
    attack = commands.add_parser("attack", help="recuperar la clave con texto plano conocido")
    attack.add_argument("--size", "-n", type=int, default=2, help="tamaño del bloque")
    attack.add_argument("plaintext", help="fragmento de texto plano conocido")
    attack.add_argument("ciphertext", help="criptograma correspondiente")

    return parser


def _key(arguments: argparse.Namespace) -> HillKey:
    if arguments.keyword is not None:
        return HillKey.from_keyword(arguments.keyword)
    try:
        values = [int(value) for value in arguments.matrix.replace(",", " ").split()]
    except ValueError as error:
        raise InvalidKeyError("matrix entries must be integers") from error
    size = math.isqrt(len(values))
    if size * size != len(values):
        raise InvalidKeyError("matrix needs n x n integers")

    return HillKey.from_matrix([values[row * size : (row + 1) * size] for row in range(size)])


def _format(key: HillKey) -> str:
    return "\n".join(" ".join(f"{value:2d}" for value in row) for row in key.matrix)


def main(
    argv: Sequence[str] | None = None,
    stdin: TextIO | None = None,
    stdout: TextIO | None = None,
) -> int:
    arguments = _parser().parse_args(argv)
    target = stdout or sys.stdout
    try:
        if arguments.command == "attack":
            key = recover_key(arguments.plaintext, arguments.ciphertext, arguments.size)
            target.write(f"{_format(key)}\n")

            return 0
        text = arguments.text if arguments.text is not None else (stdin or sys.stdin).read()
        operation = encrypt if arguments.command == "encrypt" else decrypt
        target.write(operation(text, _key(arguments)) + "\n")
    except (InvalidKeyError, AttackError) as error:
        print(f"error: {error}", file=sys.stderr)

        return 2

    return 0

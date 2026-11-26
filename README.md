# Cifrado de Hill con álgebra lineal modular en Python

[![CI](https://github.com/KevinAndrey96/python-hill-cipher-linear-algebra/actions/workflows/ci.yml/badge.svg)](https://github.com/KevinAndrey96/python-hill-cipher-linear-algebra/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.12%20%7C%203.13%20%7C%203.14-3776AB)
![Cobertura](https://img.shields.io/badge/cobertura-100%25-brightgreen)
![mypy](https://img.shields.io/badge/mypy-strict-2A6DB2)
[![Licencia: MIT](https://img.shields.io/badge/licencia-MIT-yellow.svg)](LICENSE)

Implementación tipada y probada del **cifrado de Hill** para matrices clave de cualquier tamaño $n \times n$, con aritmética entera exacta en $\mathbb{Z}_{26}$: determinante por eliminación de Bareiss, matriz adjunta, inversa modular, validación de claves y el **ataque de texto plano conocido** que demuestra por qué este cifrado es lineal y, por tanto, débil.

## Contenido

- [El cifrado](#el-cifrado)
- [Inversa modular](#inversa-modular)
- [Ataque de texto plano conocido](#ataque-de-texto-plano-conocido)
- [Uso](#uso)
- [Arquitectura](#arquitectura)
- [Pruebas y calidad](#pruebas-y-calidad)
- [Historia del proyecto](#historia-del-proyecto)

## El cifrado

Lester S. Hill lo publicó en 1929. Con $A = 0, \dots, Z = 25$, el texto se divide en bloques de $n$ letras que se tratan como vectores columna y se multiplican por una matriz clave $K$:

$$
\mathbf{c} = K\,\mathbf{p} \pmod{26}, \qquad \mathbf{p} = K^{-1}\,\mathbf{c} \pmod{26}.
$$

Si el último bloque queda incompleto se rellena con X. Con la clave de Wikipedia `HILL`, que llena la matriz por filas:

$$
K = \begin{pmatrix} 7 & 8 \\ 11 & 11 \end{pmatrix}, \qquad
\texttt{SHORTEXAMPLE} \longmapsto \texttt{APADJTFTWLFJ}.
$$

Con la clave de $3 \times 3$ `GYBNQKURP`, `ACT` se cifra como `POH` y `CAT` como `FIN`.

## Inversa modular

Una matriz sirve como clave solo si es invertible módulo 26, es decir, si su determinante es coprimo con 26 (impar y no múltiplo de 13):

$$
\gcd\big(\det K \bmod 26,\; 26\big) = 1, \qquad
K^{-1} \equiv (\det K)^{-1}\,\operatorname{adj}(K) \pmod{26}.
$$

El determinante se calcula con la eliminación de Bareiss, que divide de forma exacta y nunca sale de los enteros, y el inverso de $\det K$ con `pow(d, -1, 26)`. Para `GYBNQKURP` el determinante es 441, que equivale a 25 módulo 26, y la inversa resulta

$$
K^{-1} = \begin{pmatrix} 8 & 5 & 10 \\ 21 & 8 & 21 \\ 21 & 12 & 8 \end{pmatrix}.
$$

La versión original de 2020 multiplicaba la adjunta por $1/\det K$ como número de punto flotante, lo cual solo es correcto cuando el determinante vale 1 módulo 26; con cualquier otra clave el descifrado devolvía letras equivocadas.

## Ataque de texto plano conocido

Si un atacante conoce $n$ bloques de texto plano cuyas columnas forman una matriz $P$ invertible y sus cifrados $C$, entonces $C = KP$ y la clave completa sale de una sola multiplicación:

$$
K = C\,P^{-1} \pmod{26}.
$$

`recover_key` busca entre los bloques conocidos una combinación con $P$ invertible, calcula el candidato y lo valida contra todos los pares. Doce letras del ejemplo de Wikipedia bastan para recuperar la clave `HILL`.

El ataque necesita bloques linealmente independientes módulo 2 y módulo 13. Un texto como `ATAQUEALAMANECER` no alcanza para una clave de $2 \times 2$: todos sus bloques empiezan por A, E o U, valores pares, así que ninguna combinación es invertible módulo 2 y la clave queda indeterminada en esa componente; `recover_key` lo informa con `AttackError` en lugar de devolver una clave adivinada.

## Uso

Requiere Python 3.12 o superior y [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run hill encrypt -k HILL "short example"
# APADJTFTWLFJ
uv run hill decrypt -m "7 8 11 11" APADJTFTWLFJ
# SHORTEXAMPLE
uv run hill encrypt -m "6,24,1,13,16,10,20,17,15" ACT
# POH
uv run hill attack -n 2 shortexample APADJTFTWLFJ
#  7  8
# 11 11
```

La clave se da como palabra (`--keyword`, de 4, 9, 16... letras) o como matriz por filas (`--matrix`). Si se omite el texto, se lee de la entrada estándar. Una matriz no invertible, un criptograma que no completa bloques o un ataque sin datos suficientes terminan con código 2 y un mensaje en la salida de error.

Como librería:

```python
from hill import HillKey, decrypt, encrypt, recover_key

clave = HillKey.from_matrix([[3, 3], [2, 5]])
cifrado = encrypt("Nos vemos en la plaza mayor", clave)   # 'DSNLWQSOZVHWAHXVKIUQPJ'
decrypt(cifrado, clave)                                   # 'NOSVEMOSENLAPLAZAMAYOR'
recover_key("Nos vemos en la plaza mayor", cifrado, 2)    # devuelve la misma clave
```

## Arquitectura

```text
src/hill/
  modular.py   matrices inmutables, Bareiss, adjunta, inversa y producto módulo m
  cipher.py    HillKey validada, relleno, cifrado y descifrado por bloques
  attack.py    recuperación de la clave con texto plano conocido
  cli.py       comandos encrypt, decrypt y attack
```

`HillKey` valida la matriz y precalcula su inversa al construirse, así que una clave inválida no puede llegar al cifrado. Sin dependencias externas; los errores se reportan con `InvalidKeyError`, `SingularMatrixError` y `AttackError`, subclases de `ValueError`.

## Pruebas y calidad

```bash
uv run pytest --cov
uv run ruff check src tests && uv run ruff format --check src tests
uv run mypy
```

42 pruebas con cobertura del 100 % de líneas y ramas. Además de los vectores de Wikipedia, las pruebas basadas en propiedades con Hypothesis comparan el determinante de Bareiss con la expansión de Laplace, comprueban $A\,\operatorname{adj}(A) = \det(A)\,I$ y $A A^{-1} \equiv I$ en matrices aleatorias de hasta $4 \times 4$, verifican que descifrar invierte al cifrar y que el ataque recupera cualquier clave invertible de $2 \times 2$. El pipeline de GitHub Actions ejecuta Ruff y mypy en modo estricto, las pruebas en Python 3.12, 3.13 y 3.14, una prueba de humo del comando instalado y la construcción del paquete con `twine check`.

## Historia del proyecto

El proyecto nació en abril de 2020 como un script interactivo de $2 \times 2$ con NumPy para la clase de criptografía, acompañado de un [video explicativo](https://youtu.be/QiWCjD9dOM4). Aquel script usaba vectores fila ($\mathbf{c} = \mathbf{p}K$, equivalente a usar $K^\top$ en la convención de columnas) y tenía el error de la inversa en punto flotante descrito arriba. En 2026 se reescribió como un paquete tipado sin dependencias, generalizado a $n \times n$, con la inversa modular correcta, validación de claves, el ataque de texto plano conocido y pruebas automatizadas; además se eliminaron del historial el entorno virtual, los archivos del IDE y un video de 43 MB que se habían versionado. El código original se conserva en el tag [`v0.1-python-coursework-2020`](https://github.com/KevinAndrey96/python-hill-cipher-linear-algebra/tree/v0.1-python-coursework-2020).

## Autor

**Kevin Andrey Herrera Silva** · [GitHub](https://github.com/KevinAndrey96)

## Licencia

Distribuido bajo la [licencia MIT](LICENSE).

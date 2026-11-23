# Cifrado Polialfabético de Hill (Matriz 2x2) en Python

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![NumPy](https://img.shields.io/badge/NumPy-Supported-013243.svg)](https://numpy.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Implementación interactiva en Python del **Cifrado de Hill** para bloques de tamaño $2$ ($m = 2$) mediante álgebra lineal modular y matrices bidimensionales con **NumPy**. El proyecto contempla el cifrado de digramas, cálculo modular de determinantes, obtención del inverso multiplicativo mediante el algoritmo extendido de Euclides, derivación de la matriz adjunta y descifrado completo.

---

## 🔐 Fundamento Teórico y Matemático

Inventado por el matemático estadounidense **Lester S. Hill** en 1929, el cifrado de Hill fue el primer cifrador polialfabético práctico basado en transformaciones lineales sobre el anillo conmutativo $\mathbb{Z}_{26}$ (alfabeto inglés clásico de 26 caracteres $A=0, B=1, \dots, Z=25$).

### 1. Proceso de Cifrado

El texto claro se particiona en vectores fila de digramas $\mathbf{P} = [p_1, p_2]$. La clave criptográfica es una matriz cuadrada invertible $\mathbf{K} \in \mathcal{M}_{2 \times 2}(\mathbb{Z}_{26})$:

$$\mathbf{K} = \begin{bmatrix} k_{11} & k_{12} \\ k_{21} & k_{22} \end{bmatrix}$$

El vector cifrado $\mathbf{C} = [c_1, c_2]$ se calcula multiplicando el vector de texto claro por la matriz clave módulo 26:

$$\mathbf{C} \equiv \mathbf{P} \cdot \mathbf{K} \pmod{26}$$

O en forma escalar:

$$\begin{cases}
c_1 = (p_1 k_{11} + p_2 k_{21}) \pmod{26} \\
c_2 = (p_1 k_{12} + p_2 k_{22}) \pmod{26}
\end{cases}$$

### 2. Condición de Invertibilidad de la Clave

Para que el mensaje cifrado pueda ser descifrado de forma única, la matriz clave $\mathbf{K}$ debe ser invertible en $\mathbb{Z}_{26}$. Esto exige que su determinante sea coprimo con 26:

$$\gcd(\det(\mathbf{K}) \pmod{26}, 26) = 1$$

Si $\gcd(\det(\mathbf{K}), 26) \ne 1$, la matriz no posee inverso multiplicativo y no puede ser utilizada como clave.

### 3. Proceso de Descifrado

El descifrado requiere calcular la matriz inversa modular $\mathbf{K}^{-1} \pmod{26}$:

$$\mathbf{K}^{-1} \equiv d^{-1} \cdot \text{adj}(\mathbf{K}) \pmod{26}$$

Donde:
1. $d = \det(\mathbf{K}) = (k_{11} k_{22} - k_{12} k_{21}) \pmod{26}$.
2. $d^{-1}$ es el inverso multiplicativo de $d$ en $\mathbb{Z}_{26}$, tal que $(d \cdot d^{-1}) \equiv 1 \pmod{26}$.
3. La matriz adjunta clásica para una matriz $2 \times 2$ es:

$$\text{adj}(\mathbf{K}) = \begin{bmatrix} k_{22} & -k_{12} \\ -k_{21} & k_{11} \end{bmatrix} \pmod{26}$$

El vector claro original se recupera mediante:

$$\mathbf{P} \equiv \mathbf{C} \cdot \mathbf{K}^{-1} \pmod{26}$$

---

## 📂 Estructura del Repositorio

```text
hill-cipher/
├── main.py          # Script principal con algoritmos interactivos de cifrado y descifrado
├── Cifrado.png      # Captura de pantalla de ejecucion del cifrado
├── Descifrado.png   # Captura de pantalla de ejecucion del descifrado
├── Descifrado2.png  # Validacion de casos de prueba adicionales
├── Video.txt        # Enlace a demostracion multimedia en YouTube
└── Cifrado de Hill.mp4 # Video explicativo local del algoritmo
```

---

## 🚀 Requisitos e Instalación

### Prerrequisitos

- **Python** (versión 3.8 o superior).
- Biblioteca **NumPy**.

### Instalación de Dependencias

```bash
pip install numpy
```

---

## 💻 Guía de Uso

Ejecuta el script principal:

```bash
python main.py
```

### 1. Cifrado

1. Selecciona la opción `1`.
2. Introduce el texto claro (los espacios se eliminan automáticamente y se convierte a mayúsculas).
3. Introduce los 4 valores enteros para la matriz clave $2 \times 2$:
   - Posición 0,0 ($k_{11}$)
   - Posición 0,1 ($k_{12}$)
   - Posición 1,0 ($k_{21}$)
   - Posición 1,1 ($k_{22}$)
4. El script imprimirá la matriz clave, la descomposición en digramas y el criptograma resultante.

### 2. Descifrado

1. Selecciona la opción `2`.
2. Introduce el criptograma a descifrar.
3. Introduce la misma matriz clave $2 \times 2$.
4. El script calculará el determinante, validará la coprimalidad, obtendrá el inverso modular y derivará el texto claro original.

---

## 📹 Demostración en Video

Demostración práctica del funcionamiento paso a paso en YouTube:
[Demostración en YouTube](https://youtu.be/4e0-F3E4zbc)

---

## 📄 Licencia

Distribuido bajo la Licencia MIT. Consulta el archivo `LICENSE` para más información.

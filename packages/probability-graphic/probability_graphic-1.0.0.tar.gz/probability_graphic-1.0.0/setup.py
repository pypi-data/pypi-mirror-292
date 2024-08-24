from setuptools import setup, find_packages

VERSION = "1.0.0"
DESCRIPTION = "Gráficas de probabilidad por consola"
LONG_DESCRIPTION = "Este módulo incluye funciones que generan y muestran gráficas de probabilidad por consola."

# Configurando
setup(
    name="probability_graphic",
    version=VERSION,
    author="Granpepinillo",
    author_email="granpepinillo@gmail.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=["python", "probabilidad", "graficas", "porcentajes"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
)

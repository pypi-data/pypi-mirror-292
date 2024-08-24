import os
from setuptools import setup, find_packages

setup(
    name="siemensfile",  # Cambiado a minúsculas
    version="0.1.10",
    packages=find_packages(where="src"),  # Especifica dónde buscar los paquetes
    package_dir={"": "src"},  # Indica que los paquetes están en el directorio src
    install_requires=[
        "numpy",
        "matplotlib",
        "pandas",
        "mri-nufft",
        "scipy",
        "tqdm",
        "tables",
        "gt-twixtools"
    ],
    author="Fernando Jose Ramirez",
    author_email="tu_email@example.com",
    description="Paquete para leer archivos .dat de Siemens y realizar reconstrucciones de imágenes.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/cenarius1985/SIEMENSFile",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.12.4',
)
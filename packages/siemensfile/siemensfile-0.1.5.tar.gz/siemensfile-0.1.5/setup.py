import os
import subprocess
from setuptools import setup, find_packages


setup(
    name="SIEMENSFile",
    version="0.1.5",
    packages=find_packages(),
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
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/cenarius1985/SIEMENSFile",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.12.4',
)
import os
import subprocess
from setuptools import setup, find_packages

# Instalar twixtools desde el directorio local
twixtools_dir = os.path.join(os.path.dirname(__file__), "twixtools")
if os.path.exists(twixtools_dir):
    print("Instalando twixtools desde el directorio local...")
    subprocess.check_call(["pip", "install", "."], cwd=twixtools_dir)
else:
    raise FileNotFoundError(f"No se encontró el directorio twixtools en la ruta {twixtools_dir}")

setup(
    name="SIEMENSFile",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "matplotlib",
        "pandas",
        "mri-nufft",
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
    python_requires='>=3.6',
)

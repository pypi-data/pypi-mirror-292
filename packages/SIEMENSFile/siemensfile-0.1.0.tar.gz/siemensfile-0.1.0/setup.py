from setuptools import setup, find_packages

setup(
    name="SIEMENSFile",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "matplotlib",
        "twixtools",
        "pandas",
        "mri-nufft",
    ],
    author="Fernando Jose Ramirez",
    author_email="tu_email@example.com",
    description="Paquete para leer archivos .dat de Siemens y realizar reconstrucciones de imágenes.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/tu_usuario/SIEMENSFile",  # Reemplaza con la URL de tu repositorio
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)



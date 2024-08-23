from setuptools import setup, find_packages

# Leer el contenido del archivo README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="KattoDev",  # Nombre del paquete
    version="0.1.0",  # Versión del paquete
    packages=find_packages(),
    install_requieres=[],
    author="Katto",  # Autor del paquete
    description="Una prueba para mi primer módulo en PyPI",
    long_descrption=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/YoshuDaza",
)


# setup.py

from setuptools import setup, find_packages

# Leer el archivo README para usarlo como descripción larga
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="llm_content_filter",
    version="0.2.6",
    description="A simple and customizable content filter for LLMs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Juan Carlos Lanas Ocampo",
    author_email="juancarlos.lanas.ocampo@gmail.com",
    url="https://github.com/jclanas2019/llm_content_filter",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",  # Indica que está en fase Beta
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: English",  # Indica el idioma natural del contenido
    ],
    keywords="LLM content filter NLP text moderation",  # Palabras clave para el paquete
    python_requires=">=3.6",
    install_requires=[
        "jsonschema>=3.2.0",  # Ejemplo de dependencia, si decides usar validación de JSON
    ],
    extras_require={
        "dev": ["check-manifest"],  # Herramientas adicionales para desarrollo
        "test": ["coverage"],  # Dependencias para pruebas
    },
    package_data={
        # Incluir cualquier archivo que no sea código, como archivos de datos
        "llm_content_filter": ["data/*.json"],
    },
    entry_points={
        "console_scripts": [
            "llm_content_filter=llm_content_filter.cli:main",  # Punto de entrada si tienes un script CLI
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/jclanas2019/llm_content_filter/issues",
        "Source": "https://github.com/jclanas2019/llm_content_filter/",
    },
)

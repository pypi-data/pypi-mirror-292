# setup.py

from setuptools import setup, find_packages

setup(
    name="llm_content_filter",
    version="0.1.0",
    description="A simple content filter for LLMs",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Tu Nombre",
    author_email="tu_email@example.com",
    url="https://github.com/tu_usuario/llm_content_filter",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[],
)

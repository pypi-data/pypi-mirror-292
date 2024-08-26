from setuptools import setup, find_packages
import os

# Lade den Inhalt der README.md als langbeschreibung für PyPI
with open(os.path.join(os.path.dirname(__file__), 'README.md'), 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="nova-codebox",  # Name des Pakets (wie es auf PyPI erscheinen soll)
    version="1.4",  # Version des Pakets
    author="NovaPorta",
    author_email="info@novaporta.de",
    description="Eine CodeBox-Komponente für PyQt5",
    long_description=long_description,  # Lange Beschreibung wird aus README.md gelesen
    long_description_content_type="text/markdown",  # Format der langen Beschreibung ist Markdown
    url="https://github.com/NovaPorta/PyQT5-Codebox/",  # GitHub-URL deines Projekts
    packages=find_packages(),  # Automatisch alle Python-Pakete finden
    install_requires=[  # Abhängigkeiten
        'PyQt5>=5.15',  # Deine Bibliothek benötigt PyQt5
    ],
    classifiers=[  # Metadaten zur Kategorisierung des Pakets
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  # Unterstützte Python-Versionen
)

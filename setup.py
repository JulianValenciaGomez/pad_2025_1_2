from setuptools import setup, find_packages
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="edu_pad",
    version="0.1.0",  # Versión incrementada
    author="Julian Valencia",
    author_email="julian.valencia@est.iudigital.edu.co",
    description="Scraper de citas con persistencia de datos e histórico",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "pandas>=1.4.0",
        "requests>=2.28.0",
        "beautifulsoup4>=4.11.0",
        "openpyxl>=3.0.0",
        "lxml>=4.9.0",
        "sqlite3>=2.6.0"  # Nuevo requerimiento
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=3.0",
            "flake8>=5.0",
            "black>=22.0"
        ],
        "historical": [  # Nuevo grupo de dependencias
            "python-dateutil>=2.8.2"
        ]
    },
    entry_points={
        'console_scripts': [
            'run-scraper=edu_pad.dataweb:main',  # Punto de entrada CLI
            'update-quotes=edu_pad.dataweb:main [historical]'  # Alternativo con extras
        ],
    },
    include_package_data=True,  # 👈 Incluye archivos no Python (importante para datos)
    package_data={
        'edu_pad': ['data/*', 'data/histórico/*'],  # Incluye estructura de directorios
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
        "Topic :: Utilities"
    ],
    project_urls={
        "Bug Reports": "https://github.com/JulianValenciaGomez/pad_2025_1_2/issues",
        "Source": "https://github.com/JulianValenciaGomez/pad_2025_1_2",
    },
)
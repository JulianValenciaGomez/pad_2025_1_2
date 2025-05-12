from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="edu_pad",
    version="0.0.1",
    author="Julian Valencia",
    author_email="julian.valencia@est.iudigital.edu.co",
    description="Programación para análisis de datos - Replicación de desarrollo en clase",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "pandas>=1.4.0",
        "openpyxl>=3.0.0",
        "requests>=2.28.0",
        "beautifulsoup4>=4.11.0",
        "lxml>=4.9.0"
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=3.0",
            "flake8>=5.0",
            "black>=22.0"
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    project_urls={
        "Bug Reports": "https://github.com/JulianValenciaGomez/pad_2025_1_2/issues",
        "Source": "https://github.com/JulianValenciaGomez/pad_2025_1_2",
        "Documentation": "https://github.com/JulianValenciaGomez/pad_2025_1_2#readme"
    },
)
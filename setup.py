from setuptools import setup, find_packages


setup(
    name="edu_pad",
    version="0.0.1",
    author="Julian Valencia",
    author_email="julian.valencia@est.iudigital.edu.co",
    description="Programación para analisis de datos, se replica lo desarrollado en clase",
    py_modules=["actividad1","actividad2"],
    install_requires=[
        "pandas",
        "openpyxl",
        "requests",
        "beautifulsoup4"
    ]
)
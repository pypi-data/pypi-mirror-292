from setuptools import setup, find_packages

setup(
    name="taxi_data",
    version="0.0.11",
    packages=find_packages(),
    install_requires=[
        "pydantic",
        "selenium",
        "folium",
        "beautifulsoup4",
    ],
    # other arguments
)
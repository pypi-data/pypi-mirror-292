from setuptools import setup, find_packages

setup(
    name="taxi_data",
    version="0.0.8",
    packages=find_packages(),
    install_requires=[
        "pydantic",
        "typing",
        "asyncio",
        "datetime",
        "selenium",
        "logging",
        "argparse",
        "folium",
        "pathlib",
        "beautifulsoup4",
    ],
    # other arguments
)
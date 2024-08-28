# from setuptools import setup, find_packages

# setup(
#     name="taxi_data",
#     version="0.0.11",
#     packages=find_packages(),
#     install_requires=[
#         "pydantic",
#         "selenium",
#         "folium",
#         "beautifulsoup4",
#     ],
#     # other arguments
# )

import subprocess
import sys
import os

def install_requirements(requirements_file: str = 'requirements.txt') -> None:
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while installing the packages: {e}")
    else:
        print("Requirements installed successfully.")


def main() -> None:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    requirements_file = f"{parent_dir}/requirements.txt"

    install_requirements(requirements_file)

if __name__ == "__main__":
        main()
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

def install_requirements(requirements_file: str = 'requirements.txt') -> None:
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while installing the packages: {e}")
    else:
        print("Requirements installed successfully.")


def main() -> None:
    install_requirements()
    
if __name__ == "__main__":
        main()
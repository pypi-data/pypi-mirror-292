from setuptools import find_packages, setup

setup(
    name="rpyt",  # Name of your package
    version="0.9",  # Initial version
    packages=find_packages(),  # Automatically find your packages
    include_package_data=True,  # Include additional files
    install_requires=[
        "fire",
    ],
    entry_points={
        "console_scripts": [
            "rpyt=rpyt.__main__:main",  # Assuming you have a main function in __main__.py
        ],
    },
    package_data={
        "": ["*.txt"],  # Include all .txt files in the package
    },
)

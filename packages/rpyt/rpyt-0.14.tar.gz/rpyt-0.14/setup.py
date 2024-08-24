from setuptools import find_namespace_packages, find_packages, setup

setup(
    name="rpyt",  # Name of your package
    version="0.14",
    packages=find_packages()
    + find_namespace_packages(),  # Automatically find your packages
    install_requires=[
        "fire",
    ],
    entry_points={
        "console_scripts": [
            "rpyt=rpyt.__main__:main",  # Assuming you have a main function in __main__.py
        ],
    },
    # Include additional files
    # needed to include additional files aside from the find_namespace_packages()
    # see: https://setuptools.pypa.io/en/latest/userguide/datafiles.html#subdirectory-for-data-files
    include_package_data=True,
    package_data={
        "rpyt.resources": ["*"],  # Include resources
    },
)

"""SetupTools configuration"""
import setuptools
import os

# Get version from environment variable or use a default
version = os.getenv('PACKAGE_VERSION', '0.0.0')
if len(version) == 0:
    version = '0.0.0'


setuptools.setup(
    long_description_content_type="text/markdown",
    package_dir={"": "src"},  # the start of the code folder
    version=version,
    packages=setuptools.find_packages(where="project-code"),
    setup_requires=["setuptools-git-versioning"],
    python_requires=">=3.7",
    install_requires=[
        "mdutils == 1.6.0",
        "mkdocs == 1.6.0",
        "pytoml == 0.1.21",
        "PyYAML == 6.0.1",
        "rich == 13.7.1",
        "typer == 0.12.3",
        "typing_extensions == 4.12.1",
        "Unidecode == 1.3.8"
    ],
    entry_points={
        "console_scripts": ["labrador=labrador.cli:app"]
    }
)

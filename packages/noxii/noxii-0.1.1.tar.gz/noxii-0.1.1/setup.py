import pathlib
import setuptools

setuptools.setup(
    name="noxii",
    version="0.1.1",
    description="Official wrapper for the Noxii API",
    # long_description=pathlib.Path("README.md").read_text(),
    # long_description_content_type="text/markdown",
    # url="https://aenoxic.de",
    author="Aenoxic",
    # author_email="contact@aenoxic.de",
    license="MIT License",
    project_urls={
        # "Documentation": ""
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Utilities"
    ],
    python_requires=">= 3.10",
    install_requires=["requests", "pymongo"],
    extras_require={
        # "excel": ["openpyxl"],
    },
    packages=setuptools.find_packages(),
    include_package_data=True,
    entry_points={"console_scripts": ["noxii = noxii.cli:main"]},
)
from setuptools import setup, find_packages

setup(
    name="pdfhextractor",
    version="0.0.1",
    author="Atul Dhingra",
    author_email="dhingratul92@gmail.com",
    url="https://github.com/dhingratul/pdf-highlights-extractor",
    description="An application that extracts highlights from pdfs as markdown files",
    packages=find_packages(),
    license="Apache-2.0",
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        # Pick your license as you wish (should match "license" above)
        "License :: OSI Approved :: Apache Software License",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    install_requires=["fitz"],
    entry_points={"console_scripts": ["pdfhextract = pdfhextract.core:main"]},
)

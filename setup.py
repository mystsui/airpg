from setuptools import setup, find_packages

setup(
    name="combat",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pytest>=7.4.3",
        "pytest-cov>=4.1.0",
        "pytest-xdist>=3.3.1",
        "pytest-benchmark>=4.0.0",
        "psutil>=5.9.6",
    ],
    extras_require={
        "dev": [
            "mypy>=1.7.1",
            "types-psutil>=5.9.5.17",
            "pylint>=3.0.2",
            "black>=23.11.0",
            "isort>=5.12.0",
            "ipython>=8.17.2",
            "ipdb>=0.13.13",
        ],
        "docs": [
            "mkdocs>=1.5.3",
            "mkdocs-material>=9.4.14",
        ],
    },
)

from setuptools import find_packages, setup


extras_test = [
    "hypothesis",
    "ruff",
    "pyproj",
    "pytest",
    "pytest-cov",
    "sphinx",
    "pytest-asyncio",
    "tox",
    "build",
    "vcrpy",
]


setup(
    name="whitebit_httpx_client",
    keywords=[
        "whitebit",
        "whitebit api",
        "whitebit client",
    ],
    use_scm_version=True,
    description="An asynchronous library for interacting with whitebit",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=("tests", "docs")),
    setup_requires=[
        "setuptools_scm",
    ],
    install_requires=[
        "httpx",
        "setuptools",
    ],
    extras_require={
        "test": extras_test,
    },
    url="https://github.com/Grommash9/whitebit_httpx_client",
    project_urls={
        "Documentation": "https://grommash9.github.io/whitebit_httpx_client/",
        "Source": "https://github.com/Grommash9/whitebit_httpx_client",
    },
    author="Oleksandr Prudnikov",
    author_email="prudnikov21@icloud.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)

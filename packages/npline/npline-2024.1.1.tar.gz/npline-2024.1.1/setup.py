import pathlib

from setuptools import find_packages, setup

here = pathlib.Path(__file__).parent.resolve()

# Read long description from the readme.md file
with open("README.md", encoding="utf-8") as f:
    readme = f.read()

with open("LICENSE", encoding="utf-8") as f:
    license_data = f.read()

setup(
    name="npline",
    version="2024.1.1",
    description="A package to help you sending a notification to LINE",
    long_description_content_type="text/markdown",
    long_description=readme,
    author="Nopporn Phantawee",
    author_email="n.phantawee@gmail.com",
    url="https://github.com/noppGithub/npline",
    license=license_data,
    packages=find_packages(exclude=("tests", "docs")),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3 :: Only",
    ],
    install_requires=["requests", "pytz"],
    extras_require={
        "dev": ["check-manifest"],
        "test": ["coverage"],
    },
    python_requires=">=3.6, <4",
)

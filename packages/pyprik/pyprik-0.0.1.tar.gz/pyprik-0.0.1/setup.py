from setuptools import find_packages, setup

with open("app/README.md", "r") as f:
    long_description = f.read()

setup(
    name="pyprik",
    version="0.0.1",
    description="pyprik ",
    package_dir={"": "app"},
    packages=find_packages(where="app"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Pruthvik",
    author_email="pruthvikmachhi7@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    install_requires=["pandas >= 2.1.4"],
    extras_require={
        "dev": ["pytest>=8.2.2", "twine>=5.1.1"],
    },
    python_requires=">=3.11",
)
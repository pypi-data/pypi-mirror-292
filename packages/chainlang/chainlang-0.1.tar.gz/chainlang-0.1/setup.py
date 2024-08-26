from setuptools import setup, find_packages

setup(
    name="chainlang",
    version="0.1",
    author="Prashant",
    author_email="vprashant5050@gmail.com",
    description="Modified version of langchain that fix the bug of langchain agent tool",
    url="https://github.com/vprashrex/chainlang.git",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)

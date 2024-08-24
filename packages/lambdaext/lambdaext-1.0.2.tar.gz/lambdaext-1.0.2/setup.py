from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="lambdaext",
    version="1.0.2",
    author="SoulCodingYanhun",
    author_email="zhuzhishengzhu6@outlook.com",
    description="A brief description of lambdaext",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SoulCodingYanhun/lambdaext",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
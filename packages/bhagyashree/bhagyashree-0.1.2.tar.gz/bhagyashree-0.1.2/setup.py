from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="bhagyashree",
    version="0.1.2",
    author="arpy8",
    description="aaauuuggghhhhhhhhh",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/arpy8/bhagyashree",
    packages=find_packages(),
    install_requires=["setuptools", "customtkinter", "pillow", "requests"],
    entry_points={
        "console_scripts": [
            "bhxg=bhagyashree.main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_data={"bhagyashree": ["assets/*.png", "assets/*.ico"]},
    include_package_data=True,
    license="MIT",
)

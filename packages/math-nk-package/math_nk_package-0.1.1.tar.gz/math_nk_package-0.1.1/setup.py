from setuptools import setup, find_packages

setup(
    name="math_nk_package",
    version="0.1.1",
    author="NILESH KISHORE",
    author_email="nileshkishore2001@gmail.com",
    description="A simple Python package for basic math operations and expression evaluation.",
    packages=find_packages(),  # This will automatically find the math_nk_package directory
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)


from setuptools import setup, find_packages

setup(
    name="mathsimplicity",
    version="1.0.3",
    packages=find_packages(),
    install_requires=[
        "numexpr",
    ],
    author="Mohamed Lotfi Hireche Benkert",
    author_email="mohamedhireche74@gmail.com",
    description="MathSimplicity is a Python package providing essential tools for basic mathematical computations, including prime factorization, range prime generation, fraction-to-decimal conversion, and GCD/LCM calculation.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/promoha90/mathsimplicity",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Education",
        "Topic :: Education",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)

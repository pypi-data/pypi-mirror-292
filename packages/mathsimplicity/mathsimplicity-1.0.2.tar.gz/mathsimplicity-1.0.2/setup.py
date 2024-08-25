import pathlib
import setuptools

setuptools.setup(
    name="mathsimplicity",
    version="1.0.2",
    description="MathSimplicity is a Python package providing essential tools for basic mathematical computations, including prime factorization, range prime generation, fraction-to-decimal conversion, and GCD/LCM calculation.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author="Mohamed Lotfi Hireche Benkert",
    author_email="mohamedhireche74@gmail.com",
    license="MIT",
    url="https://github.com/promoha90/mathsimplicity",
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Education",
        "Topic :: Education",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    python_requires='>=3.6',
    install_requires=[
        'numexpr>=2.7.3'
    ],
    packages=setuptools.find_packages()
)

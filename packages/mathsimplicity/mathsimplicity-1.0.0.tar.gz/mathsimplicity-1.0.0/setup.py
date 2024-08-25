from setuptools import setup, find_packages

setup(
    name="MathSimplicity",
    version="1.0.0",
    description="MathSimplicity is a Python package providing essential tools for basic mathematical computations, including prime factorization, range prime generation, fraction-to-decimal conversion, and GCD/LCM calculation.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author="Mohamed Lotfi Hireche Benkert",
    author_email="mohamedhireche74@gmail.com",
    license="MIT",
    url="https://github.com/promoha90/mathsimplicity",
    packages=find_packages(include=["mathsimplicity", "mathsimplicity.*"]),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Education",
        "Topic :: Education",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    keywords=[
        "math",
        "mathematics",
        "beginner",
        "education",
        "prime numbers",
        "fraction",
        "decimal",
        "GCD",
        "LCM",
        "programming",
        "math tools",
        "math utilities",
        "simple math",
        "math for beginners"
    ],
    python_requires='>=3.6',
    install_requires=[
        'numexpr>=2.7.3'
    ],
)

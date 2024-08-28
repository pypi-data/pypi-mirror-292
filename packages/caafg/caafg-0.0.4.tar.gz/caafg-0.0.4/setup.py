from setuptools import setup, find_packages

VERSION = '0.0.4'
DESCRIPTION = 'Context Aware Automated Feature Generators with LLMs'

setup(
    name="caafg",
    version=VERSION,
    author="Jaris Küken",
    author_email="jaris.kueken@gmail.com",
    description=DESCRIPTION,
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/jariskueken/caafg/",
    license="LICENSE.txt",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "remoteinference",
    ],
)

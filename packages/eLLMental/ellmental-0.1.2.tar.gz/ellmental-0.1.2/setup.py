from setuptools import setup, find_packages

setup(
    name="eLLMental",
    version="0.1.2",
    packages=find_packages(),
    install_requires=[
        "requests"
    ],
    author="eLLMental",
    author_email="info@theagilemonkeys.com",
    description="Pytohn SDK for eLLMental",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/theam/eLLMental_python_sdk",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

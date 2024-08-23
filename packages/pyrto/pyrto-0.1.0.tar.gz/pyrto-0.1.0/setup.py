from setuptools import setup, find_packages

setup(
    name="pyrto",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "beautifulsoup4",
        "Pillow",
    ],
    entry_points={
        'console_scripts': [
            'pyrto=pyrto.cli:main',
        ],
    },
    author="Shubham Shinde",
    author_email="shubhamshindesunil@gmail.com",
    description="A package to fetch vehicle details and images based on license plate numbers",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/shubhamshnd/pyrto",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
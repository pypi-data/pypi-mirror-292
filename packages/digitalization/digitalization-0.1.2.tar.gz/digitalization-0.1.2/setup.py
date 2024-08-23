from setuptools import setup, find_packages

setup(
    name="digitalization",
    version="0.1.2",
    packages=find_packages(),
    install_requires=[],  # Add any dependencies your package needs
    author="thangnt",
    author_email="mr.thangnt@gmail.com",
    description="A test package for ops automation",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/thangnt/digitalization",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)

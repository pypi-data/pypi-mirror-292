# setup.py

from setuptools import setup, find_packages

setup(
    name="dtmapi",  
    version="0.0.3",  
    packages=find_packages(),  
    install_requires=['requests', 'pandas'], 
    author="Luong Bang Tran",
    author_email="lutran@iom.int",
    long_description=open("README.md").read(),  
    long_description_content_type="text/markdown",  
    url="https://github.com/Displacement-Tracking-Matrix/dtmpy",  
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  
)

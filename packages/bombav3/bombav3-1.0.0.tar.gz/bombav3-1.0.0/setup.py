from setuptools import setup, find_packages

setup(
    name="bombav3", 
    version="1.0.0",  
    description="  Custom DDoS Tools Maded By IRELGTPS ", 
    long_description=open("README.md").read(), 
    long_description_content_type="text/markdown",
    author="IREL GTPS", 
    author_email="tnajooo5@gmail.com",
    url="https://github.com/IREL1337/BOMBAV3",
    packages=find_packages(), 
    classifiers=[
        "Programming Language :: Python :: 3", 
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",  
    ],
    python_requires=">=3.6",  
    install_requires=[
        "psutil",  
    ],
)

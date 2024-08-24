from setuptools import setup, find_packages
from datetime import datetime

setup(
    name="ayetms-cli-sau",
    version = f"0.1.dev{datetime.now().strftime('%Y%m%d%H%M%S')}",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "ayetms=ayetms_cli:main",
        ],
    },
    author="Saurabh Satapathy",
    author_email="saurabhsatapathy0@gmail.com",
    description="A CLI for AYETMS (As You Earn Time Management System)",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ayetms-cli",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ayetms_sau",  # Changed from "ayetms" to "ayetms_sau"
    version="0.1.1",
    author="Your Name",
    author_email="your.email@example.com",
    description="A CLI application for AYETMS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ayetms_sau",  # Update this URL
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "ayetms_sau=ayetms_sau.main:main",  # Changed from "ayetms" to "ayetms_sau"
        ],
    },
)
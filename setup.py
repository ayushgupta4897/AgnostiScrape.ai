from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="agnostiscrape",
    version="0.1.0",
    author="AgnostiScrape.ai Team",
    author_email="your.email@example.com",
    description="URL in, structured data out in one step—no selectors to maintain, no DOM dependencies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/AgnostiScrape.ai",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "playwright>=1.30.0",
        "pillow>=9.0.0",
        "google-generativeai>=0.3.0",
    ],
) 
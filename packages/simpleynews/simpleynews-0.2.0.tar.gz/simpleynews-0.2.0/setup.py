import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="simpleynews",
    version="0.2.0",
    author="Alexander Warth",
    author_email="alexander.warth@mailbox.org",
    description="A simple Yahoo Finance news scraper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/CochainComplex/simpleynews",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests",
        "beautifulsoup4",
        "pytz",
    ],
)
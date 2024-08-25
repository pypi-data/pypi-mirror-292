from setuptools import setup, find_packages

# Read the content of your README.md file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="onelineml",
    version="0.1.4",  # Increment version number as needed
    description="A tool for creating machine learning pipelines with custom preprocessing and model selection",
    long_description=long_description,  # Use the README.md as the long description
    long_description_content_type="text/markdown",  # This tells PyPI to interpret the README.md as Markdown
    author="Harivatsa G A",
    author_email="gaharivatsa@gmail.com",
    url="https://github.com/gaharivatsa/onelineml",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "numpy",
        "scikit-learn",
        "joblib"
    ],
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

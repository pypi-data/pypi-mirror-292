from setuptools import setup, find_packages

setup(
    name="onelineml",  # Project name
    version="0.1.1",
    description="A tool for creating machine learning pipelines with custom preprocessing and model selection",
    author="Harivatsa G A",  # Your name
    author_email="gaharivatsa@gmail.com",  # Your email
    url="https://github.com/gaharivatsa/easyml",  # GitHub URL
    packages=find_packages(),
    install_requires=[
        "pandas",
        "numpy",
        "scikit-learn",
        "joblib"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

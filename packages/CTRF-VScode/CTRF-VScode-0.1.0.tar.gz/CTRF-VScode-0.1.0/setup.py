from setuptools import setup, find_packages

setup(
    name="CTRF-VScode",  # replace this with the finalized file name.
    version="0.1.0",
    author="Srinivas M",
    author_email="maddimsetti34@gmail.com",  # Corrected key
    description="Please add the appropriate description",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",  # Corrected typo
    url="https://github.com/hemanth2410/CTRF-VScode",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",  # Corrected typo
    ],
    python_requires=">=3.9",  # Corrected key
    install_requires=[
        "matplotlib",
        "numpy",
        "pandas",
        "scikit-learn",
        "scipy",
        "pyeda",
    ],
    include_package_data=True,
)

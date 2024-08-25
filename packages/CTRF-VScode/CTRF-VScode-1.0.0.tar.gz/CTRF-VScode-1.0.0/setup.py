from setuptools import setup, find_packages

setup(
    name="CTRF-VScode",
    version="1.0.0",
    author="Srinivas M",
    author_email="maddimsetti34@gmail.com",
    description="Please add the appropriate description",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/hemanth2410/CTRF-VScode",
    
    # Adjusted to find packages in the 'CTRF-VScode' directory
    packages=find_packages(where="CTRF-VScode"),
    package_dir={"": "CTRF-VScode"},

    # If you want to include standalone Python modules
    py_modules=[
        "basic_functions",
        "bds",
        "eobds",
        "gmm_mml",
        "hellof",
        "IG_func",
        "obds",
        "predictf",
    ],

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
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

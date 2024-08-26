from setuptools import setup, find_packages

setup(
    name="CTRF-VScode",
    version="1.0.1",
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
        "CTRF-VScode/basic_functions",
        "CTRF-VScode/bds",
        "CTRF-VScode/eobds",
        "CTRF-VScode/gmm_mml",
        "CTRF-VScode/hellof",
        "CTRF-VScode/IG_func",
        "CTRF-VScode/obds",
        "CTRF-VScode/predictf",
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

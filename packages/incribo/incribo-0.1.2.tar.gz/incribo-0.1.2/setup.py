from setuptools import setup, find_packages


setup(
    name="incribo",
    version="0.1.2",
    author="Uma Venugopal",
    author_email="uma@incribo.com",
    description="Generate stateful embeddings for your AI",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(where="python_src"),
    package_dir={"": "python_src"},
    install_requires=[
        # add dependencies here
        "numpy>=1.9.0",
        "matplotlib>=3.9.1",
        "sentence-transformers>=3.0.1",
        "torch>=2.4.0",
        "incribo>=0.1.2"
    ],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    extras_require={
        "dev": ["pytest>=8.3.2", "twine>=5.1.1"],
        },
    python_requires=">=3.9",
    zip_safe=False,
)

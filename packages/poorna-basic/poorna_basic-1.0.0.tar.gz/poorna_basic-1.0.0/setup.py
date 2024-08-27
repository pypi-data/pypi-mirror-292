from setuptools import setup, find_packages

setup(
    name="poorna_basic",
    version="1.0.0",
    author="K_poorna_chandra_reddy",
    author_email="kottepoornachandrareddy@gmail.com",
    description="I created this package to reduse my work",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Poorna2411/machine_learning2411",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

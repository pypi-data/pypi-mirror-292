from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ontopascii",
    version="0.0.7",
    author="frantisek tomas",
    author_email="wfrantisektomas@gmail.com",
    url="https://github.com/frantisek-lucius-tomas/ontopascii",
    description="more on github",
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "Pillow>=9.0.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    include_package_data=True,
    license="MIT",
)

from setuptools import setup, find_packages

setup(
    name="docta-http-client",
    version="0.1.19",
    author="Tongzhou Jiang @ docta.ai",
    author_email="tojiang@docta.ai",
    description="A simple HTTP client for the Docta API.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/docta/docta-http-client",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "requests",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

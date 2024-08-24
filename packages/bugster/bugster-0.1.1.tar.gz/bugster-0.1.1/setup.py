from setuptools import setup, find_packages

setup(
    name="bugster",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "pytest",
        "playwright",
    ],
    entry_points={
        "pytest11": [
            "bugster = bugster.conftest",
        ],
    },
    author="Naquiao",
    author_email="ignacio@bugster.app",
    description="A Playwright-based testing framework with customer-specific configurations",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Bugsterapp/bugster-framework",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

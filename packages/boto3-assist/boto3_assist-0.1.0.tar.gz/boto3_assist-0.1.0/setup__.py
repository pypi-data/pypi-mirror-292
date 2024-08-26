from setuptools import setup, find_packages


def read_readme() -> str:
    """Read the readme"""
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
    return long_description


setup(
    name="boto3-assist",
    version="0.1.0",
    author="Eric Wilson",
    author_email="boto3-assist@geekcafe.com",
    description="Additional boto3 wrappers to make your life a little easier",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/geekcafe/boto3-assist",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=[
        "aws-lambda-powertools",
        "aws-xray-sdk",
        "boto3",
        "jsons",
        "python-dateutil",
        "python-dotenv",
        "pytz",
        "requests",
        "types-python-dateutil",
    ],
)

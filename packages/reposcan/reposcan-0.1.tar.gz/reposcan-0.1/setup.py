from setuptools import setup, find_packages

setup(
    name="reposcan",
    version="0.1",
    packages=find_packages(),
    install_requires=[],  # List your dependencies here
    author="Vincent Chau",
    author_email="vincent@singularitydevops.io",
    description="A simple example package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/SingularityDevOps/api-governance",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.0,<4.0',
)

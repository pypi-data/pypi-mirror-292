from setuptools import setup, find_packages

setup(
    name="randexcpy",  # Your package name
    version="0.1.0",  # Initial release version
    author="Don Johnson",  # Your name
    author_email="dj@codetestcode.io",  # Your email
    description="A library for executing actions at random times within a specified duration.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",  # Required for Markdown README files
    url="https://github.com/copleftdev/randexcpy",  # Your project's GitHub URL
    packages=find_packages(),  # Automatically find packages in your directory
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=[],  # Add your dependencies here
)

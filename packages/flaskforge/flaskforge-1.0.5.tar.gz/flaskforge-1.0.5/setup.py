from setuptools import setup, find_packages


def parse_requirements(filename):
    """Read a requirements file and return a list of dependencies."""
    with open(filename, "r") as file:
        return [
            line.strip() for line in file if line.strip() and not line.startswith("#")
        ]


setup(
    name="flaskforge",  # Package name
    version="1.0.5",  # Initial release version
    author="Kimsea Sok",  # Author's name
    author_email="basicblogtalk@gmail.com",  # Author's email
    description="A CLI tool for generating Flask resources",  # Short package description
    long_description=open("README.md").read(),  # Long description from README file
    long_description_content_type="text/markdown",  # Format of the long description
    url="https://github.com/kimseasok/flaskforge",  # Project repository URL
    packages=find_packages(),  # Automatically discover and include all packages
    classifiers=[
        "Development Status :: 3 - Alpha",  # Development stage
        "Intended Audience :: Developers",  # Target audience
        "License :: OSI Approved :: MIT License",  # License type
        "Programming Language :: Python :: 3",  # Supported Python versions
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",  # Minimum Python version required
    install_requires=parse_requirements(
        "requirements.txt"
    ),  # Dependencies from requirements.txt
    extras_require={
        "dev": [
            "pytest",  # Testing framework
            "sphinx",  # Documentation generator
        ],
    },
    entry_points={
        "console_scripts": [
            "flaskforge=flaskforge.flask_cli_tool:main",  # Corrected CLI command and entry point
        ],
    },
    include_package_data=True,  # Include files specified in MANIFEST.in
    package_data={
        "": ["*.txt", "*.rst", "*.yml", "Dockerfile"],  # Include text and reStructuredText files
    },
    zip_safe=False,  # Package is not zip-safe
)

from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="integrationos-authkit",
    version="1.0.1",
    author="IntegrationOS",
    author_email="dev@integrationos.com",
    description="Secure token generation for IntegrationOS AuthKit in Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/integration-os/authkit-python",
    packages=['integrationos'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.25.1",
    ],
)
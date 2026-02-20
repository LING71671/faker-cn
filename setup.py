from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="faker-cn",
    version="0.1.0",
    author="LING71671",
    author_email="your.email@example.com",
    description="The most rigorous and realistic Chinese Persona Provider for Python Faker.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LING71671/faker-cn",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "faker_cn": ["*.json", "*.gz"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
    ],
    python_requires='>=3.7',
    install_requires=[
        "Faker>=30.0.0",
    ],
)

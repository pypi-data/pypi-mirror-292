from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Reading the requirements.txt file
requirements_path = this_directory / "requirements.txt"
with open(requirements_path) as f:
    install_requires = f.read().splitlines()

setup(
    name='ui_demo_framework',
    version='1.1.1',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=install_requires,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Mrinal Gautam",
    author_email="mrinalsinghgautam@gmail.com",
    url="https://github.com/mrinal2323/UI_Demo_Framework",
    description="A demo UI framework for testing purposes.",
    license="MIT",
    keywords="testing ui framework",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

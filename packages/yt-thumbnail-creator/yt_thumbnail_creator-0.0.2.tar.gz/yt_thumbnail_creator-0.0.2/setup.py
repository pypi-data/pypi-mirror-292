from setuptools import setup, find_packages
import os

VERSION = '0.0.2'
DESCRIPTION = 'Generating Thumbnail for everyone'
LONG_DESCRIPTION = open('README.md').read()  # Make sure you have a README.md file
LONG_DESCRIPTION_CONTENT_TYPE = 'text/markdown'  # Assuming your README.md is in markdown format

# Setting up
setup(
    name="yt_thumbnail_creator",
    version=VERSION,
    author="S Likhith Sai",
    author_email="semalalikithsai@gmail.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESCRIPTION_CONTENT_TYPE,
    packages=find_packages(),
    install_requires=['groq', 'gradio_client', 'Pillow', 'rembg', 'colorama'],
    keywords=['python', 'video', 'youtube', 'thumbnail', 'photos', 'stable-diffusion'],
    classifiers=[
        "Development Status :: 3 - Alpha",  # Updated to reflect a more realistic status
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",  # Covers multiple OS platforms
    ],
)

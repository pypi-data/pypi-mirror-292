from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.1'
DESCRIPTION = 'Generating Thumbnail for everyone'
LONG_DESCRIPTION = 'A package that allows to everyone to build ai thumbnails'

# Setting up
setup(
    name="yt_thumbnail_creator",
    version=VERSION,
    author="S Likhith Sai",
    author_email="<semalalikithsai@gmail.com>",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['groq', 'gradio_client', 'Pillow', 'rembg', 'colorama'],
    keywords=['python', 'video', 'youtube', 'thumbnail', 'photos', 'stable-diffusion'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)

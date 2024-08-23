from setuptools import setup, find_packages

VERSION = '0.1.1'
DESCRIPTION = 'Generating Thumbnail for everyone'
LONG_DESCRIPTION = open('README.md').read()
LONG_DESCRIPTION_CONTENT_TYPE = 'text/markdown'

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
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Topic :: Multimedia :: Graphics",
    ],
    python_requires='>=3.7',
    include_package_data=True,
    package_data={'yt_thumbnail_creator': ['llm/*.jinja2']},
)
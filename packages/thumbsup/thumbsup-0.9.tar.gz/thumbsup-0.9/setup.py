from setuptools import setup, find_packages

setup(
    name="thumbsup",
    version="0.9",
    packages=find_packages(),
    install_requires=[
        "opencv-python",
    ],
    entry_points={
        "console_scripts": [
            "thumbsup=thumbsup.main:main",
        ],
    },
    author="Ethan Forvest",
    author_email="your.email@example.com",
    description="A CLI tool for generating thumbnails from video files.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ethanforvest/thumbsup",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.11',
)

from setuptools import setup, find_packages

setup(
    name="took",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "took=took.took:main",
        ],
    },
    install_requires=[],  # list any dependencies your tool needs
    author="loaojuz",
    author_email="",
    description="CLI tool to track time spent on tasks.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/joaohenriqueluz/took",  # link to the project's home page
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

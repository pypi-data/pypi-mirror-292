from setuptools import setup, find_packages

setup(
    name="VorosITG_sql_wrapper",
    version="0.1.8",
    packages=find_packages(),
    install_requires=[],  # List any dependencies here
    author="Vörös Bence",
    author_email="info@vorositg.hu",
    description="A simple SQLite database wrapper",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/VorosBence/VorosITG_sql_wrapper",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

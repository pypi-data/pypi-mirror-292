from setuptools import setup, find_packages

setup(
    name="vkyframework",
    version="0.1.3",
    packages=find_packages(),
    install_requires=[],
    include_package_data=True,
    description="vkyframework for python3 rest api",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author="Vivek Gajbhiye",
    author_email="vivekgajbhiye024@gmail.com",
    url="https://github.com/Automatex-testai/vkyframework",  # Replace with your actual URL
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

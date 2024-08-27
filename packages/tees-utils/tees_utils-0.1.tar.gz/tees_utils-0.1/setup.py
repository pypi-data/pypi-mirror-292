from setuptools import setup, find_packages

setup(
    name="tees-utils",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "azure-storage-blob",
        "python-dotenv",
        "requests",
        "Pillow",
        "pymongo"
    ],
    author="Divyansh",
    author_email="divyansh.24888@gmail.com",
    description="A utility package for managing Teesign Utils.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/teesign/teesign-utils",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
)

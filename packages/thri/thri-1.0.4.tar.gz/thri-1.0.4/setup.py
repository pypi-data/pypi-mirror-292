from setuptools import setup, find_packages

setup(
    name="thri",
    version="1.0.4",
    author="khiat Mohammed Abderrezzak",
    author_email="khiat.dev@gmail.com",
    license="MIT",
    description="Sophisticate Tree",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/thri/",
    packages=find_packages(),
    install_requires=[
        "linkedit>=1.1.1",
    ],
    keywords=[
        "tree",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.6",
)

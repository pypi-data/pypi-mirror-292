from setuptools import setup, find_packages

setup(
    name="lstack",
    version="1.1.0",
    author="khiat Mohammed Abderrezzak",
    author_email="khiat.dev@gmail.com",
    license="MIT",
    description="Sophisticate Linked Stack",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/lstack/",
    packages=find_packages(),
    install_requires=[
        "linkedit>=1.1.1",
    ],
    keywords=[
        "linked stack",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.6",
)

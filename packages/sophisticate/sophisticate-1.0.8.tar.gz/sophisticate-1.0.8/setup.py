from setuptools import setup, find_packages

setup(
    name="sophisticate",
    version="1.0.8",
    author="khiat Mohammed Abderrezzak",
    author_email="khiat.dev@gmail.com",
    license="MIT",
    description="Sophisticate Libraries Collection",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/sophisticate/",
    packages=find_packages(),
    install_requires=[
        "conf-mat>=1.0.9",
        "linkedit>=1.1.1",
        "cqueue>=1.1.1",
        "lstack>=1.0.9",
        "hashall>=1.0.2",
        "thri>=1.0.4",
        "heep>=1.0.1",
        "hashtbl>=1.0.3",
        "court-queue>=1.0.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
)

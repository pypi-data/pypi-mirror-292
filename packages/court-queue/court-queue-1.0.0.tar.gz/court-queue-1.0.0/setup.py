from setuptools import setup, find_packages

setup(
    name="court-queue",
    version="1.0.0",
    author="khiat Mohammed Abderrezzak",
    author_email="khiat.dev@gmail.com",
    license="Apache-2.0",
    description="Sophisticate Court Queue",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/court-queue/",
    packages=find_packages(),
    install_requires=[
        "tabulate>=0.9.0",
    ],
    keywords=[
        "court queue",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: Apache Software License",
    ],
    python_requires=">=3.6",
)

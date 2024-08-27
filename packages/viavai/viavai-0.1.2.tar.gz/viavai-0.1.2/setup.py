from setuptools import setup, find_packages


setup(
    name="viavai",
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    packages=find_packages(),
    description="A sample Python library called Viavai",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author="Sau1707",
    author_email="your.email@example.com",
    url="https://github.com/XLongLink/viavai",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.11',
)

from setuptools import setup, find_packages

setup(
    name="shared_dynamic_listing",
    version="0.1.2",
    description="This is Dynamically setup the preferences for by user and business",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Muhammad Shahbaz",
    author_email="ds.shahbaz.rajput@example.com",
    url="https://github.com/rubnawazgondal/expertmedicalpage-aks.git",  # Replace with your GitHub repo
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
